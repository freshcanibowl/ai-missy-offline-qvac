"""Build25 actual localhost HTTP negative tests. Synthetic-only credentials/data."""
import json
import threading
import time
import unittest
import urllib.error
import urllib.request
from metabolic.http_sandbox import make_test_server

class Build25HttpSandboxTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server,cls.auth,cls.db=make_test_server()
  cls.port=cls.server.server_port
  cls.base=f"http://127.0.0.1:{cls.port}"
  cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
  cls.thread.start()
 @classmethod
 def tearDownClass(cls):
  cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=4);cls.db.close()
 def token(self,person,scope,**kwargs):return self.auth.mint(person,scope,**kwargs)
 def call(self,path,*,method="GET",body=None,token=None,origin=None,host=None):
  headers={}
  if token is not None:headers["Authorization"]="Bearer "+token
  if host is not None:headers["Host"]=host
  if method=="POST":
   headers["Content-Type"]="application/json"
   headers["Origin"]=self.base if origin is None else origin
  data=json.dumps(body or {}).encode() if method=="POST" else None
  req=urllib.request.Request(self.base+path,data=data,headers=headers,method=method)
  try:
   with urllib.request.urlopen(req,timeout=3) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_01_missing_token_denied(self):
  self.assertEqual(self.call("/sandbox/own")[0],403)
 def test_02_unsigned_claims_denied(self):
  self.assertEqual(self.call("/sandbox/own",token="eyJzdWIiOiJB.." )[0],403)
 def test_03_wrong_scope_denied(self):
  self.assertEqual(self.call("/sandbox/own",token=self.token("ALICE","record:write"))[0],403)
 def test_04_owner_writes_synthetic(self):
  code,_=self.call("/sandbox/add",method="POST",token=self.token("ALICE","record:write"),body={"owner":"ALICE","kind":"blood_pressure","sample":"SAMPLE_A"})
  self.assertEqual(code,201)
 def test_05_owner_reads_own(self):
  self.test_04_owner_writes_synthetic()
  code,body=self.call("/sandbox/own",token=self.token("ALICE","record:read"))
  self.assertEqual(code,200);self.assertIn(["blood_pressure","SAMPLE_A"],body["items"])
 def test_06_bob_cannot_write_alice(self):
  code,_=self.call("/sandbox/add",method="POST",token=self.token("BOB","record:write"),body={"owner":"ALICE","kind":"blood_pressure","sample":"SAMPLE_A"})
  self.assertEqual(code,403)
 def test_07_bob_cannot_read_alice(self):
  code,body=self.call("/sandbox/own",token=self.token("BOB","record:read"))
  self.assertEqual(code,200);self.assertNotIn(["blood_pressure","SAMPLE_A"],body["items"])
 def test_08_no_preview_before_consent(self):
  self.assertEqual(self.call("/sandbox/review",method="POST",token=self.token("REVIEWER","review:read"),body={"owner":"BOB"})[0],403)
 def test_09_grant_then_revoke_and_replay(self):
  owner=self.token("BOB","consent:write")
  reviewer=self.token("REVIEWER","review:read")
  self.assertEqual(self.call("/sandbox/consent",method="POST",token=owner,body={"grantee":"REVIEWER","active":True})[0],200)
  status,body=self.call("/sandbox/review",method="POST",token=reviewer,body={"owner":"BOB"})
  self.assertEqual(status,200);self.assertEqual(body["transfer_status"],"NOT_SENT");self.assertFalse(body["permission_to_transfer"])
  self.assertEqual(self.call("/sandbox/consent",method="POST",token=owner,body={"grantee":"REVIEWER","active":False})[0],200)
  for _ in range(2):self.assertEqual(self.call("/sandbox/review",method="POST",token=reviewer,body={"owner":"BOB"})[0],403)
 def test_10_no_cross_subject_review(self):
  reviewer=self.token("REVIEWER","review:read")
  self.assertEqual(self.call("/sandbox/review",method="POST",token=reviewer,body={"owner":"UNKNOWN"})[0],403)
 def test_11_free_text_rejected(self):
  self.assertEqual(self.call("/sandbox/add",method="POST",token=self.token("ALICE","record:write"),body={"owner":"ALICE","kind":"blood_pressure","sample":"my real phone"})[0],403)
 def test_12_token_expired_rejected(self):
  t=self.token("ALICE","record:read",now=1000,ttl=2)
  self.assertEqual(self.call("/sandbox/own",token=t)[0],403)
 def test_13_forged_signature_rejected(self):
  t=self.token("ALICE","record:read")
  self.assertEqual(self.call("/sandbox/own",token=t[:-1]+("A" if t[-1]!="A" else "B"))[0],403)
 def test_14_fake_host_rejected(self):
  self.assertEqual(self.call("/sandbox/own",token=self.token("ALICE","record:read"),host="evil.example")[0],403)
 def test_15_wrong_origin_rejected(self):
  self.assertEqual(self.call("/sandbox/add",method="POST",token=self.token("ALICE","record:write"),origin="https://evil.example",body={"owner":"ALICE","kind":"blood_pressure","sample":"SAMPLE_A"})[0],403)
 def test_16_unknown_endpoint_404(self):
  self.assertEqual(self.call("/sandbox/unknown")[0],404)
 def test_17_true_metabolic_routes_unchanged(self):
  import server
  import inspect
  src=inspect.getsource(server.Handler)
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",src)
  self.assertIn("path.startswith('/api/metabolic/')",src)
 def test_18_consent_boolean_string_rejected(self):
  self.assertEqual(self.call("/sandbox/consent",method="POST",token=self.token("BOB","consent:write"),body={"grantee":"REVIEWER","active":"true"})[0],403)
 def test_19_extra_request_fields_denied(self):
  self.assertEqual(self.call("/sandbox/add",method="POST",token=self.token("ALICE","record:write"),body={"owner":"ALICE","kind":"blood_pressure","sample":"SAMPLE_A","role":"admin"})[0],403)
 def test_20_no_identity_issuance_http_route(self):
  self.assertEqual(self.call("/sandbox/mint",method="POST",body={"sub":"ALICE"})[0],404)
