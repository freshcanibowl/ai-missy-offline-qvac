import unittest
from dataclasses import replace
from metabolic.introspection_gate import IdentityConfig, IdentityRejected, verify_bearer, test_only_no_patient_access
C=IdentityConfig("https://identity.example.test","missy-api","https://identity.example.test/oauth/introspect","client","local-placeholder-not-secret")
TOKEN="opaque-token-synthetic"
CLAIMS={"active":True,"iss":C.issuer,"aud":C.audience,"sub":"synthetic-user-1","exp":2000000000,"nbf":1000000000,"scope":"missy:daily:read"}
def transport(_config,_token):return CLAIMS.copy()
class IntrospectionTests(unittest.TestCase):
 def verify(self,claims=CLAIMS,config=C):
  return verify_bearer(TOKEN,config,transport=lambda _c,_t:claims,now=1900000000)
 def reject(self,claims,config=C):
  with self.assertRaises(IdentityRejected):self.verify(claims,config)
 def test_verified_claims_fixture(self):
  self.assertEqual(self.verify().subject,"synthetic-user-1")
 def test_no_backend(self):
  with self.assertRaises(IdentityRejected):verify_bearer(TOKEN,None,transport=transport,now=1900000000)
 def test_bad_http_endpoint(self):
  self.reject(CLAIMS,replace(C,introspection_url="http://identity.example.test/check"))
 def test_url_credentials_denied(self):
  self.reject(CLAIMS,replace(C,introspection_url="https://user:pass@identity.example.test/check"))
 def test_url_fragment_denied(self):
  self.reject(CLAIMS,replace(C,introspection_url="https://identity.example.test/check#fragment"))
 def test_inactive(self):self.reject(dict(CLAIMS,active=False))
 def test_claimed_active_string_denied(self):self.reject(dict(CLAIMS,active="true"))
 def test_issuer_mismatch(self):self.reject(dict(CLAIMS,iss="https://attacker.example"))
 def test_audience_mismatch(self):self.reject(dict(CLAIMS,aud="other-app"))
 def test_audience_list_allowed(self):self.assertEqual(self.verify(dict(CLAIMS,aud=["other-app",C.audience])).subject,"synthetic-user-1")
 def test_missing_subject(self):self.reject(dict(CLAIMS,sub=""))
 def test_subject_whitespace(self):self.reject(dict(CLAIMS,sub=" synthetic "))
 def test_expired(self):self.reject(dict(CLAIMS,exp=1800000000))
 def test_exp_bool(self):self.reject(dict(CLAIMS,exp=True))
 def test_not_before_future(self):self.reject(dict(CLAIMS,nbf=1999999999))
 def test_missing_scope(self):self.reject(dict(CLAIMS,scope="missy:daily:write"))
 def test_bad_scope_type(self):self.reject(dict(CLAIMS,scope=["missy:daily:read"]))
 def test_claims_not_mapping(self):
  with self.assertRaises(IdentityRejected):self.verify("active")
 def test_invalid_token_whitespace(self):
  with self.assertRaises(IdentityRejected):verify_bearer("a token with spaces",C,transport=transport,now=1900000000)
 def test_introspection_exception_fails_closed(self):
  def fail(*_):raise OSError("synthetic error")
  with self.assertRaises(IdentityRejected):verify_bearer(TOKEN,C,transport=fail,now=1900000000)
 def test_verified_identity_is_not_consent(self):
  with self.assertRaises(IdentityRejected):test_only_no_patient_access(self.verify())
 def test_untrusted_transport_cannot_enable_server(self):
  from pathlib import Path
  server=(Path(__file__).resolve().parents[1]/"server.py").read_text()
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",server)
  self.assertIn("path.startswith('/api/metabolic/')",server)
if __name__=="__main__":unittest.main()
