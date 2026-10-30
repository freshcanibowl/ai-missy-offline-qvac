import unittest,tempfile,uuid,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import connect,summary,validate_extraction,verify_original_text,confirm,food_lookup,add_reminder,reminders,acknowledge
from datetime import datetime,timezone,timedelta

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'demo.sqlite3'
        self.conn=connect(self.path)
    def tearDown(self):self.conn.close();self.temp.cleanup()
    def test_baseline(self):
        s=summary(self.conn)
        self.assertEqual((s['recorded_ml'],s['remaining_record_target_ml']),(700,300))
    def test_confirm_persists_after_reconnect(self):
        confirm(self.conn,200,'Log 200 ml water',str(uuid.uuid4()))
        self.conn.close();self.conn=connect(self.path)
        self.assertEqual(summary(self.conn)['recorded_ml'],900)
    def test_replay_rejected(self):
        rid=str(uuid.uuid4());confirm(self.conn,200,'Log 200 ml water',rid)
        with self.assertRaisesRegex(ValueError,'REPLAY'):confirm(self.conn,200,'Log 200 ml water',rid)
    def test_reject_invalid_volume(self):
        for v in (True,-1,0,3001,'200',2.4):
            with self.subTest(v=v),self.assertRaises(ValueError):confirm(self.conn,v,'water',str(uuid.uuid4()))
    def test_model_schema_valid(self):
        self.assertEqual(validate_extraction({'action':'LOG_FLUID','volume_ml':200,'unit':'ml','confidence':0.95}),200)
    def test_model_schema_extra_rejected(self):
        with self.assertRaises(ValueError):validate_extraction({'action':'LOG_FLUID','volume_ml':200,'unit':'ml','confidence':1,'diagnosis':'safe'})
    def test_model_low_confidence_rejected(self):
        with self.assertRaises(ValueError):validate_extraction({'action':'LOG_FLUID','volume_ml':200,'unit':'ml','confidence':0.2})
    def test_hallucinated_volume_rejected(self):
        with self.assertRaises(ValueError):verify_original_text('I had a glass of water',200)
    def test_mismatch_rejected(self):
        with self.assertRaises(ValueError):verify_original_text('Log 300 ml water',200)
    def test_explicit_chinese_accepted(self):
        self.assertTrue(verify_original_text('记录200毫升水',200))
    def test_multiple_numbers_rejected(self):
        with self.assertRaises(ValueError):verify_original_text('Log 200 ml and 300 ml water',200)
    def test_negated_english_log_rejected(self):
        with self.assertRaisesRegex(ValueError,'NEGATED'):verify_original_text('Do not log 200 ml water',200)
    def test_negated_chinese_log_rejected(self):
        with self.assertRaisesRegex(ValueError,'NEGATED'):verify_original_text('不要记录200毫升水',200)
    def test_food_no_invented_amount(self):
        self.assertEqual(food_lookup('banana')['status'],'INSUFFICIENT_DATA')
        self.assertNotIn('mg',str(food_lookup('banana')))
    def test_unknown_food(self):self.assertEqual(food_lookup('xyz')['status'],'INSUFFICIENT_DATA')
    def test_reminder_persists(self):
        due=(datetime.now(timezone.utc)+timedelta(minutes=2)).isoformat()
        r=add_reminder(self.conn,'Review saved care checklist',due)
        self.conn.close();self.conn=connect(self.path)
        self.assertEqual(reminders(self.conn)[0]['id'],r['id'])
        self.assertTrue(acknowledge(self.conn,r['id'])['acknowledged'])
    def test_duplicate_ack_rejected(self):
        r=add_reminder(self.conn,'Review', (datetime.now(timezone.utc)+timedelta(minutes=2)).isoformat())
        acknowledge(self.conn,r['id'])
        with self.assertRaises(ValueError):acknowledge(self.conn,r['id'])
    def test_reminder_timezone_required(self):
        with self.assertRaises(ValueError):add_reminder(self.conn,'Review','2026-10-29T20:00:00')
if __name__=='__main__':unittest.main()
