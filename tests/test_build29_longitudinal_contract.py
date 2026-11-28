"""Build29: synthetically sourced longitudinal care UI and safety gates.

These static tests do not validate clinical correctness or actual users.
"""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=(ROOT/"web"/"today.js").read_text(encoding="utf-8")
HTML=(ROOT/"web"/"today.html").read_text(encoding="utf-8")
CSS=(ROOT/"web"/"today.css").read_text(encoding="utf-8")
SERVER=(ROOT/"server.py").read_text(encoding="utf-8")
class LongitudinalSyntheticContract(unittest.TestCase):
 def test_timeline_section_visible(self):
  for marker in ('id="longitudinal-panel"','id="timeline-events"','id="timeline-empty"','id="timeline-boundary"'):
   self.assertIn(marker,HTML)
 def test_all_four_modules_have_fixtures(self):
  for val in ('module:"pressure"','module:"glucose"','module:"renal"','module:"lipids"'):
   self.assertIn(val,JS)
 def test_record_provenance_and_lifecycle_required(self):
  for val in ('observedAt','recordedAt','evidenceId','source','confirmation','synthetic:true','scope:"demo_only"'):
   self.assertIn(val,JS)
 def test_temporal_and_provenance_validation(self):
  for val in ('isValidTimelineObservation','Date.parse(e.observedAt)<=Date.parse(e.recordedAt)','e.confirmation==="unverified"','e.scope==="demo_only"'):
   self.assertIn(val,JS)
 def test_no_medical_numbers_or_record_entry(self):
  self.assertNotIn('type="number"',HTML)
  self.assertNotIn('<form',HTML)
  for bad in ('fetch(', 'localStorage.', 'sessionStorage.', 'indexedDB.', 'XMLHttpRequest'):
   self.assertNotIn(bad,JS)
 def test_untrusted_medical_api_is_still_blocked(self):
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",SERVER)
  self.assertIn("path.startswith('/api/metabolic/')",SERVER)
 def test_multilingual_timeline(self):
  for marker in ("Care timeline","照护时间线","Garis masa penjagaan","尚未验证","Not verified"):
   self.assertIn(marker,JS)
 def test_timeline_uses_read_only_dom_without_html_injection(self):
  self.assertIn("details.hidden=true",JS)
  self.assertIn("data.textContent=value",JS)
  self.assertIn("paintTimeline(locale)",JS)
  self.assertNotIn("innerHTML",JS)
 def test_viewport_styles(self):
  self.assertIn(".timeline-provenance",CSS)
  self.assertIn(".large-type .timeline-provenance",CSS)
if __name__=="__main__": unittest.main()
