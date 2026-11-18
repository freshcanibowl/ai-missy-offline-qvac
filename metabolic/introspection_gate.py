"""Build23 — Opaque bearer-token introspection adapter. NOT connected to HTTP.

An identity is created ONLY after a configured, authenticated HTTPS introspection
response passes validation. No client-supplied identity/consent headers are trusted.
The adapter alone is NOT a clinical access control or patient binding solution.
"""
from dataclasses import dataclass
import base64
import json
import math
import secrets
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

class IdentityRejected(PermissionError):
    pass

@dataclass(frozen=True)
class IdentityConfig:
    issuer: str
    audience: str
    introspection_url: str
    client_id: str
    client_secret: str

    def validate(self):
        from urllib.parse import urlsplit
        for url in (self.issuer, self.introspection_url):
            parts=urlsplit(url)
            if parts.scheme!="https" or not parts.hostname or parts.username or parts.password or parts.fragment:
                raise IdentityRejected("HTTPS_TRUST_CONFIG_REQUIRED")
        if any(not isinstance(x,str) or not x or len(x)>512 for x in (self.audience,self.client_id,self.client_secret)):
            raise IdentityRejected("INTROSPECTION_CONFIG_REQUIRED")

@dataclass(frozen=True)
class VerifiedIdentity:
    issuer: str
    subject: str
    audience: str
    expires_at: int
    scopes: frozenset[str]
    # This object is not secure if caller code can freely construct it.
    # Require a trusted module boundary and reverify at authorization time.

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise IdentityRejected("INTROSPECTION_REDIRECT_DENIED")

def _post_introspection(config, token):
    auth=base64.b64encode((config.client_id+":"+config.client_secret).encode()).decode("ascii")
    request=urllib.request.Request(config.introspection_url,
        data=urllib.parse.urlencode({"token":token,"token_type_hint":"access_token"}).encode(),
        headers={"Authorization":"Basic "+auth,"Content-Type":"application/x-www-form-urlencoded","Accept":"application/json"},
        method="POST")
    opener=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        _NoRedirect(),
    )
    with opener.open(request,timeout=4) as response:
        if response.status!=200:raise IdentityRejected("INTROSPECTION_HTTP_REJECTED")
        if response.headers.get_content_type()!="application/json":raise IdentityRejected("INTROSPECTION_CONTENT_TYPE_REJECTED")
        content=response.read(8193)
        if len(content)>8192:raise IdentityRejected("INTROSPECTION_TOO_LARGE")
        return json.loads(content)

def verify_bearer(token, config: IdentityConfig | None, *, transport=None, now=None):
    """Default transport uses verified TLS. Injectable transport is TEST-ONLY.

    Never inject a caller-controlled transport in any server or production entrypoint.
    """
    if not isinstance(config,IdentityConfig):raise IdentityRejected("IDENTITY_BACKEND_NOT_CONFIGURED")
    config.validate()
    if not isinstance(token,str) or not 8<=len(token)<=4096 or any(c.isspace() for c in token):
        raise IdentityRejected("TOKEN_SHAPE_REJECTED")
    if transport is None:
        transport=_post_introspection
    try:
        data=transport(config,token)
    except (urllib.error.URLError,TimeoutError,OSError,ValueError,TypeError,KeyError) as exc:
        raise IdentityRejected("INTROSPECTION_FAILED") from exc
    if not isinstance(data,dict) or data.get("active") is not True:
        raise IdentityRejected("TOKEN_INACTIVE")
    if data.get("iss")!=config.issuer:raise IdentityRejected("ISSUER_MISMATCH")
    aud=data.get("aud")
    if isinstance(aud,str): aud=[aud]
    if not isinstance(aud,list) or config.audience not in aud or any(not isinstance(x,str) for x in aud):
        raise IdentityRejected("AUDIENCE_MISMATCH")
    sub=data.get("sub")
    if not isinstance(sub,str) or not 1<=len(sub)<=128 or sub.strip()!=sub:
        raise IdentityRejected("SUBJECT_INVALID")
    expiry=data.get("exp")
    current=time.time() if now is None else now
    if isinstance(expiry,bool) or not isinstance(expiry,(int,float)) or not math.isfinite(expiry) or expiry<=current:
        raise IdentityRejected("TOKEN_EXPIRED")
    nbf=data.get("nbf")
    if nbf is not None and (isinstance(nbf,bool) or not isinstance(nbf,(int,float)) or not math.isfinite(nbf) or nbf>current):
        raise IdentityRejected("TOKEN_NOT_YET_VALID")
    scope=data.get("scope","")
    if not isinstance(scope,str) or len(scope)>4096:
        raise IdentityRejected("SCOPE_INVALID")
    scopes=frozenset(scope.split())
    if "missy:daily:read" not in scopes:
        raise IdentityRejected("MISSING_SCOPE")
    return VerifiedIdentity(config.issuer,sub,config.audience,int(expiry),scopes)

def test_only_no_patient_access(_identity):
    """Identity verification does not establish consent or record ownership."""
    raise IdentityRejected("PATIENT_BINDING_AND_CONSENT_NOT_CONNECTED")
