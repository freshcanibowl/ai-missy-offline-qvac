"""Loopback-only demo server; synthetic data; do not expose to public networks."""
import os, json, secrets, subprocess, sys, uuid, urllib.parse, time, threading
from pathlib import Path
from contextlib import closing
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from core import connect,summary,validate_qvac_envelope,verify_original_text,confirm,food_lookup,add_reminder,reminders,acknowledge
from care_export import build_synthetic_export
ROOT=Path(__file__).resolve().parent
DB=Path(os.environ.get('MISSY_DB_PATH',str(ROOT/'missy_demo.sqlite3')))
TOKEN=secrets.token_urlsafe(32)
MAX_BODY=4096
PENDING={}
PENDING_LOCK=threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def log_message(self,format,*args):
        print('MISSY HTTP',self.command,self.path,self.address_string())
    def response(self,data,status=200):
        payload=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status)
        for k,v in {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'",'Content-Length':str(len(payload))}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(payload)
    def host_ok(self):return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def do_GET(self):
        if not self.host_ok():return self.response({'error':'HOST_REJECTED'},403)
        path=urllib.parse.urlsplit(self.path).path
        if path in ('/','/app.js','/style.css'):
            name={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[path]
            data=(ROOT/'web'/name).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type',{'index.html':'text/html; charset=utf-8','app.js':'application/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[name])
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers();return self.wfile.write(data)
        if path=='/api/session':return self.response({'token':TOKEN,'synthetic':True})
        if path=='/api/status':
            with closing(connect(DB)) as c:return self.response({'summary':summary(c),'reminders':reminders(c),'qvac_status':'NOT_TESTED_ON_THIS_DEVICE'})
        return self.response({'error':'NOT_FOUND'},404)
    def do_POST(self):
        if not self.host_ok() or self.headers.get('Origin') not in (f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
            return self.response({'error':'ORIGIN_REJECTED'},403)
        if not secrets.compare_digest(self.headers.get('X-Missy-Token',''),TOKEN):return self.response({'error':'TOKEN_REJECTED'},403)
        try:
            length=int(self.headers.get('Content-Length','-1'))
            if not 0<=length<=MAX_BODY: return self.response({'error':'BODY_SIZE_REJECTED'},413)
            if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.response({'error':'JSON_REQUIRED'},415)
            obj=json.loads(self.rfile.read(length))
            if not isinstance(obj,dict):raise ValueError('OBJECT_REQUIRED')
            path=urllib.parse.urlsplit(self.path).path
            if path=='/api/parse':
                text=obj.get('text')
                if not isinstance(text,str) or not 1<=len(text)<=240:raise ValueError('INVALID_INPUT')
                try:
                    p=subprocess.run(['node',str(ROOT/'scripts'/'qvac-parse.mjs'),json.dumps({'text':text})],cwd=ROOT,capture_output=True,text=True,timeout=150,check=True)
                except (OSError,subprocess.TimeoutExpired,subprocess.CalledProcessError):
                    return self.response({'error':'QVAC_INFERENCE_UNAVAILABLE','note':'No simulated fallback. Install and preload QVAC while online, then disconnect.'},503)
                try:
                    result=json.loads(p.stdout)
                    ml=validate_qvac_envelope(result)
                except (ValueError,TypeError,json.JSONDecodeError):
                    return self.response({'error':'QVAC_RESULT_INVALID','note':'Model response failed local integrity checks. No record was created.'},503)
                verify_original_text(text,ml)
                rid=str(uuid.uuid4())
                with PENDING_LOCK:
                    # Bound memory even if a client repeatedly requests extractions.
                    now = time.monotonic()
                    for key, item in list(PENDING.items()):
                        if item['expires'] < now:
                            del PENDING[key]
                    if len(PENDING) >= 100:
                        raise ValueError('TOO_MANY_PENDING_REQUESTS')
                    PENDING[rid] = {'ml':ml,'text':text,'expires':now+300}
                return self.response({'pending':{'volume_ml':ml,'source':text,'request_id':rid},'proof':{'engine':result['engine'],'model':result['model'],'latency_ms':result['latency_ms']},'needs_confirmation':True})
            with closing(connect(DB)) as c:
                if path=='/api/export':
                    if obj: raise ValueError('EXPORT_REQUEST_MUST_BE_EMPTY')
                    return self.response(build_synthetic_export(c))
                if path=='/api/confirm':
                    rid=obj.get('request_id')
                    with PENDING_LOCK:
                        item=PENDING.get(rid) if isinstance(rid,str) else None
                        if not item or item['expires']<time.monotonic() or obj.get('volume_ml')!=item['ml'] or obj.get('source')!=item['text']:
                            raise ValueError('NO_VALID_QVAC_PENDING_CONFIRMATION')
                        # Only consume pending after SQLite has committed successfully.
                        # Holding the lock prevents simultaneous confirmation/replay.
                        result = confirm(c,item['ml'],item['text'],rid)
                        PENDING.pop(rid)
                    return self.response(result)
                if path=='/api/food':return self.response(food_lookup(obj.get('name','')))
                if path=='/api/reminder':return self.response(add_reminder(c,obj.get('title'),obj.get('due_at')))
                if path=='/api/ack':return self.response(acknowledge(c,obj.get('id')))
            return self.response({'error':'NOT_FOUND'},404)
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as e:return self.response({'error':str(e)},422)
        except Exception as e:
            print('SERVER_ERROR',type(e).__name__,file=sys.stderr)
            return self.response({'error':'SERVER_FAILURE'},500)

if __name__=='__main__':
    port=int(os.environ.get('MISSY_PORT','8766'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'AI Missy synthetic local demo: http://127.0.0.1:{port}',flush=True)
    print('Local tab must stay open for browser reminders; no clinical advice; no QVAC fallback.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
