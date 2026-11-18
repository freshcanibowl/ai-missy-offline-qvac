"""Build 19: synthetic Today with Missy static UI and deny-all regression."""
import threading
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
import server

ROOT=Path(__file__).resolve().parents[1]

class TodayPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(("127.0.0.1",0),server.Handler)
        cls.port=cls.http.server_address[1]
        cls.worker=threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.worker.join(timeout=5)

    def get(self,path):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}",timeout=4) as r:
                return r.status,r.headers,r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code,e.headers,e.read().decode("utf-8")

    def test_page_served(self):
        status,headers,body=self.get("/today")
        self.assertEqual(status,200)
        self.assertIn("text/html",headers["Content-Type"])
        self.assertIn("SYNTHETIC PREVIEW",body)

    def test_script_and_style(self):
        for path,mime in [("/today.js","javascript"),("/today.css","text/css")]:
            with self.subTest(path=path):
                status,headers,body=self.get(path)
                self.assertEqual(status,200)
                self.assertIn(mime,headers["Content-Type"])
                self.assertTrue(body)

    def test_languages_exist(self):
        text=(ROOT/"web"/"today.js").read_text(encoding="utf-8")
        for phrase in ("en: {","zh: {","ms: {","今天，照顾自己一点点","Satu langkah kecil"):
            self.assertIn(phrase,text)

    def test_no_browser_or_network_persistence(self):
        js=(ROOT/"web"/"today.js").read_text(encoding="utf-8")
        for banned in ("localStorage.", "sessionStorage.", "indexedDB.", "fetch(", "XMLHttpRequest", "navigator.sendBeacon"):
            self.assertNotIn(banned,js)

    def test_no_medical_value_entry(self):
        html=(ROOT/"web"/"today.html").read_text(encoding="utf-8")
        self.assertNotIn('type="number"',html)
        self.assertNotIn("<form",html)

    def test_metabolic_entries_still_blocked(self):
        code,_,body=self.get("/api/metabolic/entries")
        self.assertEqual(code,403)
        self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",body)

    def test_pair_export_still_blocked(self):
        code,_,body=self.get("/api/metabolic/pair-preview")
        self.assertEqual(code,403)
        self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",body)

    def test_legacy_ui_preserved(self):
        code,_,body=self.get("/")
        self.assertEqual(code,200)
        self.assertIn("AI Missy Offline",body)
