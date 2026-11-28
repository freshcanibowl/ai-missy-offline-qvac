"""Build20: accessibility-contract checks for synthetic-only Today with Missy.
These static tests are not a substitute for screen-reader or real-user validation.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"web"/"today.html").read_text(encoding="utf-8")
JS=(ROOT/"web"/"today.js").read_text(encoding="utf-8")
CSS=(ROOT/"web"/"today.css").read_text(encoding="utf-8")

class TodayAccessibilityTests(unittest.TestCase):
    def test_text_resize_is_opt_in_and_communicates_pressed_state(self):
        self.assertIn('id="large-text"',HTML)
        self.assertIn('aria-pressed="false"',HTML)
        self.assertIn('setAttribute("aria-pressed"',JS)
        self.assertIn('classList.toggle("large-type"',JS)

    def test_language_selector_keeps_label(self):
        self.assertIn('for="language"',HTML)
        for locale in ('en: {','zh: {','ms: {'):
            self.assertIn(locale,JS)

    def test_task_choice_does_not_save_or_transmit(self):
        for forbidden in ('fetch(', 'localStorage.', 'sessionStorage.', 'indexedDB.', 'sendBeacon(', 'XMLHttpRequest'):
            self.assertNotIn(forbidden,JS)
        self.assertIn('const checked=new Set()',JS)

    def test_no_unverified_clinical_targets_or_input_fields(self):
        self.assertNotIn('type="number"',HTML)
        self.assertNotIn('<form',HTML)
        self.assertIn('SYNTHETIC PREVIEW',HTML)

    def test_skip_and_nonjudgmental_copy_present(self):
        self.assertIn('id="skip-note"',HTML)
        self.assertIn('不会为健康状况评分',JS)
        self.assertIn('tidak memberi skor kesihatan',JS)
        self.assertIn('does not grade your health',JS)

    def test_task_keeps_keyboard_focus_after_rerender(self):
        self.assertIn('input.dataset.index=String(i)',JS)
        self.assertIn('paint(i)',JS)
        self.assertIn('next.focus()',JS)

    def test_language_and_status_accessible(self):
        self.assertIn('document.documentElement.lang=',JS)
        self.assertIn('aria-live="polite" aria-atomic="true"',HTML)

    def test_reduced_motion_and_visible_focus(self):
        self.assertIn('prefers-reduced-motion:reduce',CSS)
        self.assertIn('.task input:focus-visible',CSS)

if __name__=="__main__":
    unittest.main()
