"""Synthetic-only local renal-care demonstration; no clinical decision making."""
import json, sqlite3, uuid, datetime, re, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'demo_case.json'
MAX_ML = 3000

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def demo_plan():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    if data.get('synthetic') is not True or data['plan'].get('clinician_review_status') != 'SYNTHETIC_DEMO_CONFIRMED':
        raise ValueError('DEMO_PLAN_INVALID')
    return data

def connect(db_path):
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=10000')
    conn.execute('CREATE TABLE IF NOT EXISTS observations (id TEXT PRIMARY KEY, ml INTEGER NOT NULL, source TEXT NOT NULL, confirmed_at TEXT NOT NULL)')
    conn.execute('CREATE TABLE IF NOT EXISTS reminders (id TEXT PRIMARY KEY, title TEXT NOT NULL, due_at TEXT NOT NULL, acknowledged INTEGER NOT NULL DEFAULT 0)')
    conn.commit()
    return conn

def summary(conn):
    plan = demo_plan()
    baseline = sum(x['volume_ml'] for x in plan['observations'] if x.get('confirmed_by_user'))
    added = conn.execute('SELECT COALESCE(SUM(ml),0) FROM observations').fetchone()[0]
    target = plan['plan']['fluid_record_target_ml']
    return {'synthetic': True, 'plan_id':plan['plan']['plan_id'], 'baseline_ml':baseline,
            'added_ml':added, 'recorded_ml':baseline+added, 'target_ml':target,
            'remaining_record_target_ml':max(0,target-baseline-added),
            'above_record_target_ml':max(0,baseline+added-target),
            'disclaimer':'Synthetic record target only, not medical advice. Unrecorded beverages, soup and food fluids may be missing.'}

def validate_extraction(obj):
    if not isinstance(obj,dict) or set(obj) != {'action','volume_ml','unit','confidence'}:
        raise ValueError('INVALID_MODEL_SCHEMA')
    if obj['action'] != 'LOG_FLUID' or obj['unit'] != 'ml':
        raise ValueError('UNSUPPORTED_ACTION_OR_UNIT')
    ml=obj['volume_ml']
    if isinstance(ml,bool) or not isinstance(ml,int) or not 1<=ml<=MAX_ML:
        raise ValueError('INVALID_VOLUME')
    if isinstance(obj['confidence'],bool) or not isinstance(obj['confidence'],(float,int)) or not 0<=obj['confidence']<=1:
        raise ValueError('INVALID_CONFIDENCE')
    if obj['confidence']<0.8:
        raise ValueError('LOW_CONFIDENCE')
    return ml


def validate_qvac_envelope(obj):
    """Fail closed if a subprocess response does not carry the expected QVAC contract.

    This is an application integrity check, not cryptographic proof of a genuine SDK call.
    """
    if not isinstance(obj,dict) or obj.get('engine') != 'QVAC_LOCAL':
        raise ValueError('QVAC_ENGINE_NOT_VERIFIED')
    if obj.get('model') != 'LLAMA_3_2_1B_INST_Q4_0':
        raise ValueError('QVAC_MODEL_NOT_VERIFIED')
    if type(obj.get('latency_ms')) is not int or obj['latency_ms'] < 0:
        raise ValueError('QVAC_LATENCY_INVALID')
    if obj.get('stop_reason') in ('error','cancelled','length'):
        raise ValueError('QVAC_GENERATION_INCOMPLETE')
    return validate_extraction(obj.get('parsed'))

def verify_original_text(text, ml):
    # Model cannot hallucinate an explicit quantity that the patient did not say.
    if not isinstance(text,str) or len(text)>240:
        raise ValueError('INVALID_INPUT')
    # Reject negated/cancelled or instruction-like inputs; do not record a denied action.
    if re.search(r'\b(?:do not|don\'t|did not|didn\'t|never|cancel|ignore|instead of|not log)\b|(?:不要|别记录|別記錄|取消|没喝|沒喝|不记录|不記錄)',text,re.I):
        raise ValueError('NEGATED_OR_CANCELLED_LOG')
    # Build 08: avoid recording hypothetical, historical, spilled or questioned volumes
    # as today's consumed fluid. This is intentionally conservative; ask for a new
    # explicit log instead of guessing a time or consumption event.
    if re.search(
        r'\b(?:yesterday|tomorrow|last night|last week|next week|later|'
        r'will drink|going to drink|plan to|planning to|might drink|'
        r'spilled|spilt|poured out|discarded|did not consume|'
        r'have not drunk|haven.t drunk|should i|can i|how much|if i)\b'
        r'|(?:昨天|昨日|明天|下周|下週|打算|准备喝|準備喝|将要喝|將要喝|没喝|沒喝|洒了|灑了|倒掉|如果|可以喝吗|能喝吗|多少)',
        text, re.I):
        raise ValueError('NON_CURRENT_OR_HYPOTHETICAL_LOG')
    if '?' in text or '？' in text:
        raise ValueError('QUESTION_NOT_LOG')
    if not re.search(r'\b(?:log|record|add|track|drank|drink|consumed|had)\b|(?:记录|記錄|记下|記下|喝了|饮用|飲用)', text, re.I):
        raise ValueError('EXPLICIT_LOG_OR_CONSUMPTION_REQUIRED')
    # Strict MVP supports explicit ml or mL or 毫升; no implicit cups or servings.
    matches=re.findall(r'(?<!\d)(\d{1,4})\s*(?:ml|毫升)(?![a-z])',text,re.I)
    if len(matches)!=1 or int(matches[0])!=ml:
        raise ValueError('INPUT_QUANTITY_NOT_VERIFIED')
    if not re.search(r'(水|饮|喝|记录|記|log|water|fluid|drink)',text,re.I):
        raise ValueError('NOT_FLUID_OBSERVATION')
    return True

def confirm(conn, ml, source, request_id):
    if isinstance(ml,bool) or not isinstance(ml,int) or not 1<=ml<=MAX_ML:
        raise ValueError('INVALID_VOLUME')
    if not isinstance(source,str) or not 1<=len(source)<=240:
        raise ValueError('INVALID_SOURCE')
    try: uuid.UUID(request_id)
    except (TypeError,ValueError,AttributeError): raise ValueError('INVALID_REQUEST_ID')
    with conn:
        cur=conn.execute('INSERT OR IGNORE INTO observations (id,ml,source,confirmed_at) VALUES (?,?,?,?)', (request_id,ml,source,utcnow()))
    if cur.rowcount==0:
        raise ValueError('REPLAY_REJECTED')
    return {'event_id':request_id, 'persisted':True, 'summary':summary(conn)}

def food_lookup(name):
    # Explicitly no numeric potassium/phosphorus guesses or safe/unsafe categorization.
    catalog={'banana':{'name':'Banana / 香蕉','source':'Demo food index; nutrient values intentionally absent'},
             '香蕉':{'name':'Banana / 香蕉','source':'Demo food index; nutrient values intentionally absent'},
             'rice':{'name':'Rice / 米饭','source':'Demo food index; nutrient values intentionally absent'},
             '米饭':{'name':'Rice / 米饭','source':'Demo food index; nutrient values intentionally absent'}}
    item=catalog.get(str(name).strip().lower())
    if not item:
        return {'status':'INSUFFICIENT_DATA','message':'Food or preparation not found in the local demo index. Ask a renal dietitian for individual guidance.'}
    return {'status':'INSUFFICIENT_DATA','food':item['name'],'source':item['source'],
            'message':'This offline demo has no verified nutrient amount or individual potassium allowance. It cannot determine a safe portion.'}

def add_reminder(conn,title,due_at):
    if not isinstance(title,str) or not 1<=len(title)<=80:
        raise ValueError('INVALID_REMINDER_TITLE')
    try: due=datetime.datetime.fromisoformat(due_at.replace('Z','+00:00'))
    except (ValueError,AttributeError): raise ValueError('INVALID_REMINDER_DATE')
    if due.tzinfo is None: raise ValueError('TIMEZONE_REQUIRED')
    if not datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(minutes=1) <= due <= datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=2):
        raise ValueError('REMINDER_TIME_OUT_OF_RANGE')
    id=str(uuid.uuid4())
    with conn:conn.execute('INSERT INTO reminders(id,title,due_at) VALUES(?,?,?)',(id,title,due.isoformat()))
    return {'id':id,'title':title,'due_at':due.isoformat()}

def reminders(conn):
    return [dict(row) for row in conn.execute('SELECT id,title,due_at,acknowledged FROM reminders ORDER BY due_at')]

def acknowledge(conn, id):
    with conn: n=conn.execute('UPDATE reminders SET acknowledged=1 WHERE id=? AND acknowledged=0',(id,)).rowcount
    if n!=1: raise ValueError('REMINDER_NOT_PENDING')
    return {'acknowledged':True,'id':id}
