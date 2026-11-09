"""Build17 loopback HTTP regression: metabolic data routes remain DENY-ALL.
Runs against actual server.Handler on the branch; never uses patient data.
"""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch
import server

class TestMetabolicHttpGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.http.server_address[1]
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join(timeout=5)

    def request(self, path, method="GET", body=None, headers=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        elif method == "POST":
            data = b"{}"
        else:
            data = None
        request = urllib.request.Request(url, data=data, method=method, headers=headers or {})
        try:
            with urllib.request.urlopen(request, timeout=4) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_blocked_entries_get(self):
        status, obj = self.request("/api/metabolic/entries")
        self.assertEqual(status, 403)
        self.assertEqual(obj["error"], "METABOLIC_AUTHORIZATION_UNAVAILABLE")

    def test_blocked_preview_get(self):
        status, obj = self.request("/api/metabolic/pair-preview?synthetic=true")
        self.assertEqual(status, 403)
        self.assertEqual(obj["error"], "METABOLIC_AUTHORIZATION_UNAVAILABLE")

    def test_blocked_entry_write(self):
        status, obj = self.request("/api/metabolic/entries", "POST", {"synthetic": True, "value": 120})
        self.assertEqual(status, 403)
        self.assertEqual(obj["error"], "METABOLIC_AUTHORIZATION_UNAVAILABLE")

    def test_fake_session_cannot_bypass(self):
        status, session = self.request("/api/session")
        self.assertEqual(status, 200)
        status, obj = self.request("/api/metabolic/entries", "POST", {"synthetic": True}, {
            "X-Missy-Token": session["token"],
            "Origin": f"http://127.0.0.1:{self.port}",
            "Content-Type": "application/json",
            "X-Verified-Identity": "true",
            "X-Consent": "true",
        })
        self.assertEqual(status, 403)
        self.assertEqual(obj["error"], "METABOLIC_AUTHORIZATION_UNAVAILABLE")

    def test_legacy_status_available(self):
        status, obj = self.request("/api/status")
        self.assertEqual(status, 200)
        self.assertTrue(obj["summary"]["synthetic"])

    def test_legacy_static_page_available(self):
        req=urllib.request.Request(f"http://127.0.0.1:{self.port}/")
        with urllib.request.urlopen(req,timeout=4) as resp:
            self.assertEqual(resp.status,200)
            self.assertIn(b"<",resp.read())

    def test_unknown_endpoint_still_404(self):
        status, obj = self.request("/api/not-a-route")
        self.assertEqual(status, 404)

    def test_exact_prefix_not_confused(self):
        status, obj = self.request("/api/metabolic-evil")
        self.assertEqual(status, 404)

if __name__ == "__main__":
    unittest.main()
