"""Build25 isolated HTTP authorization sandbox — SYNTHETIC ONLY.

This module is not imported by server.py. In-memory accounts, HMAC test tokens,
and sample markers are NOT an identity provider or production patient records.
The token signing key is passed by the test harness and must NEVER be exposed
to callers. No HTTP route issues credentials.
"""
import base64
import hashlib
import hmac
import json
import secrets
import sqlite3
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

class Denied(PermissionError):
    pass

def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _unb64(value):
    if not isinstance(value,str) or len(value)>4096:raise Denied("TOKEN_INVALID")
    try:return base64.b64decode(value+"="*((-len(value))%4),altchars=b"-_",validate=True)
    except (ValueError,TypeError):raise Denied("TOKEN_INVALID")

class SandboxAuthority:
    """Test-only signer created by test code, never by an HTTP request."""
    def __init__(self,key):
        if not isinstance(key,bytes) or len(key)<32:raise ValueError("TEST_KEY_TOO_SHORT")
        self._key=key
    def mint(self,subject,scope,*,now=None,ttl=120):
        if subject not in ("ALICE","BOB","REVIEWER") or scope not in ("record:read","record:write","consent:write","review:read"):
            raise ValueError("SYNTHETIC_IDENTITY_ONLY")
        epoch=int(time.time() if now is None else now)
        claims={"sub":subject,"scope":scope,"aud":"missy-build25-sandbox","iss":"missy-local-test","iat":epoch,"exp":epoch+ttl}
        payload=_b64(json.dumps(claims,sort_keys=True,separators=(",",":")).encode())
        signature=_b64(hmac.new(self._key,payload.encode(),hashlib.sha256).digest())
        return payload+"."+signature
    def verify(self,token,*,now=None):
        if not isinstance(token,str) or len(token)>2000 or token.count(".")!=1:raise Denied("TOKEN_INVALID")
        payload,mac=token.split(".")
        expected=_b64(hmac.new(self._key,payload.encode(),hashlib.sha256).digest())
        if not hmac.compare_digest(mac,expected):raise Denied("BAD_SIGNATURE")
        try:claims=json.loads(_unb64(payload))
        except (ValueError,UnicodeError,TypeError):raise Denied("TOKEN_INVALID")
        if not isinstance(claims,dict) or set(claims)!={"sub","scope","aud","iss","iat","exp"}:
            raise Denied("TOKEN_CLAIMS_INVALID")
        if claims["sub"] not in ("ALICE","BOB","REVIEWER") or claims["scope"] not in ("record:read","record:write","consent:write","review:read"):
            raise Denied("TOKEN_SCOPE_INVALID")
        if claims["iss"]!="missy-local-test" or claims["aud"]!="missy-build25-sandbox":raise Denied("TOKEN_TARGET_INVALID")
        current=int(time.time() if now is None else now)
        if any(type(claims[key]) is not int for key in ("iat","exp")) or claims["iat"]>current+5 or claims["exp"]<=current or claims["exp"]-claims["iat"]>300:
            raise Denied("TOKEN_TIME_INVALID")
        return claims["sub"],claims["scope"]

class SandboxDB:
    def __init__(self):
        self.lock=threading.RLock()
        self.db=sqlite3.connect(":memory:",check_same_thread=False,isolation_level=None)
        self.db.executescript("""
        CREATE TABLE records(owner TEXT NOT NULL,kind TEXT NOT NULL,sample TEXT NOT NULL);
        CREATE TABLE consent(owner TEXT NOT NULL,grantee TEXT NOT NULL,purpose TEXT NOT NULL,active INTEGER NOT NULL,PRIMARY KEY(owner,grantee,purpose));
        CREATE TABLE audit(action TEXT NOT NULL,outcome TEXT NOT NULL,reason TEXT NOT NULL);
        """)
    def transaction(self,action,callback):
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                value=callback(self.db)
            except Denied as exc:
                self.db.execute("ROLLBACK")
                self.db.execute("BEGIN IMMEDIATE")
                self.db.execute("INSERT INTO audit VALUES(?,?,?)",(action,"DENY",str(exc)))
                self.db.execute("COMMIT")
                raise
            except BaseException:
                self.db.execute("ROLLBACK")
                raise
            self.db.execute("INSERT INTO audit VALUES(?,?,?)",(action,"ALLOW","SYNTHETIC_ONLY"))
            self.db.execute("COMMIT")
            return value
    def close(self):
        with self.lock:self.db.close()

def _require(scope,expected):
    if scope!=expected:raise Denied("SCOPE_DENIED")

def make_handler(authority,store):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def reply(self,status,data):
            raw=json.dumps(data,separators=(",",":")).encode()
            self.send_response(status)
            self.send_header("Content-Type","application/json")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        def dispatch(self):
            if self.client_address[0] not in ("127.0.0.1","::1"):return self.reply(403,{"error":"LOOPBACK_ONLY"})
            if self.headers.get("Host") not in (f"127.0.0.1:{self.server.server_port}",f"localhost:{self.server.server_port}"):
                return self.reply(403,{"error":"HOST_REJECTED"})
            path=urlsplit(self.path)
            if path.query or path.fragment:return self.reply(400,{"error":"QUERY_NOT_ALLOWED"})
            if path.path not in ("/sandbox/own","/sandbox/add","/sandbox/consent","/sandbox/review"):
                return self.reply(404,{"error":"NOT_FOUND"})
            try:
                header=self.headers.get("Authorization","")
                if not header.startswith("Bearer "):raise Denied("BEARER_REQUIRED")
                actor,scope=authority.verify(header[7:])
                if self.command=="POST":
                    if self.headers.get("Origin") not in (f"http://127.0.0.1:{self.server.server_port}",f"http://localhost:{self.server.server_port}"):
                        raise Denied("ORIGIN_REQUIRED")
                    n=self.headers.get("Content-Length","")
                    if not n.isdecimal() or int(n)>1024:raise Denied("BODY_SIZE_REJECTED")
                    if self.headers.get("Content-Type","").split(";")[0]!="application/json":raise Denied("JSON_REQUIRED")
                    body=json.loads(self.rfile.read(int(n)))
                    if not isinstance(body,dict):raise Denied("OBJECT_REQUIRED")
                else:body={}
                if path.path=="/sandbox/own" and self.command=="GET":
                    _require(scope,"record:read")
                    def op(db):return db.execute("SELECT kind,sample FROM records WHERE owner=?",(actor,)).fetchall()
                    result=store.transaction("own",op)
                    return self.reply(200,{"synthetic":True,"items":result})
                if path.path=="/sandbox/add" and self.command=="POST":
                    _require(scope,"record:write")
                    if set(body)!={"owner","kind","sample"} or body["owner"]!=actor or body["kind"] not in ("blood_pressure","blood_glucose") or body["sample"] not in ("SAMPLE_A","SAMPLE_B"):
                        raise Denied("OWNER_OR_SAMPLE_REJECTED")
                    def op(db):db.execute("INSERT INTO records VALUES(?,?,?)",(actor,body["kind"],body["sample"]));return True
                    store.transaction("add",op)
                    return self.reply(201,{"synthetic":True,"written":True})
                if path.path=="/sandbox/consent" and self.command=="POST":
                    _require(scope,"consent:write")
                    if set(body)!={"grantee","active"} or body["grantee"]!="REVIEWER" or type(body["active"]) is not bool or actor=="REVIEWER":
                        raise Denied("CONSENT_REJECTED")
                    def op(db):
                        db.execute("INSERT INTO consent VALUES(?,?,?,?) ON CONFLICT(owner,grantee,purpose) DO UPDATE SET active=excluded.active",(actor,"REVIEWER","care_review",int(body["active"])))
                        return True
                    store.transaction("consent",op)
                    return self.reply(200,{"synthetic":True,"consent_active":body["active"]})
                if path.path=="/sandbox/review" and self.command=="POST":
                    _require(scope,"review:read")
                    if set(body)!={"owner"} or body["owner"] not in ("ALICE","BOB") or actor!="REVIEWER":
                        raise Denied("REVIEW_SUBJECT_REJECTED")
                    def op(db):
                        row=db.execute("SELECT active FROM consent WHERE owner=? AND grantee=? AND purpose='care_review'",(body["owner"],actor)).fetchone()
                        if not row or row[0]!=1:raise Denied("CONSENT_INACTIVE")
                        return db.execute("SELECT kind,sample FROM records WHERE owner=?",(body["owner"],)).fetchall()
                    rows=store.transaction("review",op)
                    return self.reply(200,{"synthetic":True,"items":rows,"transfer_status":"NOT_SENT","permission_to_transfer":False,"clinical_review":"REQUIRED"})
                return self.reply(405,{"error":"METHOD_NOT_ALLOWED"})
            except (Denied,UnicodeError,ValueError,TypeError,json.JSONDecodeError) as exc:
                return self.reply(403,{"error":"ACCESS_DENIED"})
            except Exception:
                return self.reply(500,{"error":"SERVER_FAILURE"})
        def do_GET(self):self.dispatch()
        def do_POST(self):self.dispatch()
    return Handler

def make_test_server(key=None):
    key=secrets.token_bytes(32) if key is None else key
    authority=SandboxAuthority(key)
    store=SandboxDB()
    server=ThreadingHTTPServer(("127.0.0.1",0),make_handler(authority,store))
    return server,authority,store
