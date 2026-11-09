"""Build21: synthetic usability walkthrough and undo contract.
Static and HTTP checks only. NOT empirical older-adult usability evidence.
"""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"web"/"today.html").read_text(encoding="utf-8")
JS=(ROOT/"web"/"today.js").read_text(encoding="utf-8")
CSS=(ROOT/"web"/"today.css").read_text(encoding="utf-8")
class Build21Walkthrough(unittest.TestCase):
    def test_guidance_is_visible_and_numbered(self):
        self.assertIn('aria-labelledby="guide-heading"',HTML)
        self.assertIn('<ol>',HTML)
        for id in ("guide-one","guide-two","guide-three"):
            self.assertIn('id="'+id+'"',HTML)
    def test_undo_is_disabled_until_change(self):
        self.assertIn('id="undo" type="button" class="secondary" disabled',HTML)
        self.assertIn('node("undo").disabled=history.length===0',JS)
    def test_undo_restores_previous_set(self):
        self.assertIn('history.push(new Set(checked))',JS)
        self.assertIn('const prior=history.pop()',JS)
        self.assertIn('for(const id of prior)checked.add(id)',JS)
    def test_reset_clears_undo_history(self):
        self.assertIn('checked.clear();history.length=0',JS)
    def test_undo_restores_keyboard_focus(self):
        self.assertIn('node("undo").focus()',JS)
        self.assertIn('role="status" aria-live="polite"',HTML)
    def test_all_three_locales_have_walkthrough_and_undo(self):
        for phrase in ("体验操作说明","改变主意？可以撤销","Cara mencuba","Buat asal tindakan","Try this preview","Undo last change"):
            self.assertIn(phrase,JS)
    def test_no_recording_or_network_on_preview(self):
        for disallowed in ("fetch(", "localStorage.", "sessionStorage.", "indexedDB.", "XMLHttpRequest", "navigator.sendBeacon"):
            self.assertNotIn(disallowed,JS)
        self.assertNotIn('type="number"',HTML)
    def test_undo_disabled_style_exists(self):
        self.assertIn('button:disabled',CSS)
        self.assertIn('.guide',CSS)
    def test_legacy_safe_test_fixtures_still_present(self):
        server=(ROOT/"server.py").read_text(encoding="utf-8")
        self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",server)
        self.assertIn("path.startswith('/api/metabolic/')",server)

if __name__=="__main__": unittest.main()
