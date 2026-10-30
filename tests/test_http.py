"""Local HTTP integration gates, without faking QVAC inference."""
import json, os, socket, subprocess, sys, tempfile, time, unittest, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        sock=socket.socket();sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1];sock.close()
        cls.base=f'http://127.0.0.1:{cls.port}'
        env=os.environ.copy();env['MISSY_DB_PATH']=str(Path(cls.temp.name)/'http-test.sqlite3');env['MISSY_PORT']=str(cls.port)
        cls.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py')],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(80):
            try:
                with urllib.request.urlopen(cls.base+'/api/session',timeout=.25) as r:
                    cls.token=json.load(r)['token'];break
            except Exception:time.sleep(.05)
        else:
            cls.proc.terminate();raise RuntimeError('SERVER_STARTUP_FAILED')
    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:cls.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:cls.proc.kill()
        cls.temp.cleanup()
    def request(self,path,body=None,token=None,origin=None):
        headers={}
        if body is not None:
            headers={'Content-Type':'application/json','X-Missy-Token':token if token is not None else self.token,'Origin':origin if origin is not None else self.base}
        req=urllib.request.Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=5) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as e:return e.code,json.load(e)
    def test_status_is_synthetic(self):
        code,r=self.request('/api/status');self.assertEqual(code,200);self.assertTrue(r['summary']['synthetic'])
    def test_confirm_cannot_bypass_qvac(self):
        code,r=self.request('/api/confirm',{'request_id':'00000000-0000-4000-8000-000000000000','volume_ml':200,'source':'Log 200 ml water'})
        self.assertEqual(code,422);self.assertEqual(r['error'],'NO_VALID_QVAC_PENDING_CONFIRMATION')
    def test_origin_rejected(self):
        code,r=self.request('/api/food',{'name':'banana'},origin='https://evil.example');self.assertEqual(code,403)
    def test_token_rejected(self):
        code,r=self.request('/api/food',{'name':'banana'},token='invalid');self.assertEqual(code,403)
    def test_food_fail_closed(self):
        code,r=self.request('/api/food',{'name':'banana'});self.assertEqual(code,200);self.assertEqual(r['status'],'INSUFFICIENT_DATA')
    def test_reminder_persists_via_http(self):
        from datetime import datetime,timezone,timedelta
        due=(datetime.now(timezone.utc)+timedelta(minutes=2)).isoformat()
        code,r=self.request('/api/reminder',{'title':'Check synthetic plan','due_at':due});self.assertEqual(code,200)
        code,s=self.request('/api/status');self.assertTrue(any(x['id']==r['id'] for x in s['reminders']))
        code,a=self.request('/api/ack',{'id':r['id']});self.assertEqual(code,200);self.assertTrue(a['acknowledged'])
    def test_synthetic_export_requires_token_and_is_minimized(self):
        code, rejected = self.request('/api/export', {}, token='invalid')
        self.assertEqual(code, 403)
        self.assertEqual(rejected['error'], 'TOKEN_REJECTED')
        code, exported = self.request('/api/export', {})
        self.assertEqual(code, 200)
        self.assertTrue(exported['synthetic'])
        self.assertEqual(exported['schema_version'], 'ai-missy.synthetic-care.v1')
        self.assertNotIn('source', exported)
        self.assertNotIn('reminders', exported)
        self.assertNotIn('reminder_titles', exported)
        code, invalid = self.request('/api/export', {'unexpected': True})
        self.assertEqual(code, 422)
        self.assertEqual(invalid['error'], 'EXPORT_REQUEST_MUST_BE_EMPTY')

    def test_synthetic_timeline_is_token_protected(self):
        code, denied = self.request('/api/timeline', {}, token='invalid')
        self.assertEqual(code, 403)
        self.assertEqual(denied['error'], 'TOKEN_REJECTED')
        code, result = self.request('/api/timeline', {'limit': 10, 'offset': 0})
        self.assertEqual(code, 200)
        self.assertTrue(result['synthetic'])
        self.assertEqual(result['schema_version'], 'ai-missy.synthetic-timeline.v1')
        self.assertNotIn('source', result)
        code, invalid = self.request('/api/timeline', {'limit': 100})
        self.assertEqual(code, 422)
        self.assertEqual(invalid['error'], 'INVALID_TIMELINE_LIMIT')
        code, extra = self.request('/api/timeline', {'patient_id': 'unexpected'})
        self.assertEqual(code, 422)
        self.assertEqual(extra['error'], 'TIMELINE_REQUEST_INVALID')

    def test_invalid_path(self):
        code,r=self.request('/api/unknown',{});self.assertEqual(code,404)
    def test_local_ui_has_no_external_assets(self):
        code,r=self.request('/api/status');self.assertEqual(code,200)
        html=(ROOT/'web'/'index.html').read_text(encoding='utf-8')
        self.assertNotIn('https://',html)
        self.assertNotIn('http://',html)

if __name__=='__main__':unittest.main()
