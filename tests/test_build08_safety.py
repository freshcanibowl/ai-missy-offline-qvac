"""Conservative fluid record semantics: never silently treat a question or past/future event as today's intake."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core import verify_original_text

class Build08SafetyTests(unittest.TestCase):
    def test_english_positive_log(self):
        self.assertTrue(verify_original_text('Log 200 ml water', 200))
    def test_chinese_positive_log(self):
        self.assertTrue(verify_original_text('记录200毫升水', 200))
    def test_consumed_positive_log(self):
        self.assertTrue(verify_original_text('I drank 200 ml water', 200))
    def test_future_not_recorded(self):
        with self.assertRaisesRegex(ValueError, 'NON_CURRENT_OR_HYPOTHETICAL_LOG'):
            verify_original_text('I will drink 200 ml water tomorrow', 200)
    def test_past_not_today(self):
        with self.assertRaisesRegex(ValueError, 'NON_CURRENT_OR_HYPOTHETICAL_LOG'):
            verify_original_text('Yesterday I drank 200 ml water', 200)
    def test_spilled_not_consumed(self):
        with self.assertRaisesRegex(ValueError, 'NON_CURRENT_OR_HYPOTHETICAL_LOG'):
            verify_original_text('I spilled 200 ml water', 200)
    def test_question_not_recorded(self):
        with self.assertRaisesRegex(ValueError, 'NON_CURRENT_OR_HYPOTHETICAL_LOG'):
            verify_original_text('Can I drink 200 ml water?', 200)
    def test_quantity_only_not_recorded(self):
        with self.assertRaisesRegex(ValueError, 'EXPLICIT_LOG_OR_CONSUMPTION_REQUIRED'):
            verify_original_text('200 ml water', 200)
    def test_chinese_tomorrow_not_recorded(self):
        with self.assertRaisesRegex(ValueError, 'NON_CURRENT_OR_HYPOTHETICAL_LOG'):
            verify_original_text('明天记录200毫升水', 200)
    def test_chinese_question_not_recorded(self):
        with self.assertRaisesRegex(ValueError, 'QUESTION_NOT_LOG'):
            verify_original_text('我可以喝200毫升水吗？', 200)

if __name__ == '__main__': unittest.main()
