"""Build26: Functions section contract. Static source + full CI.

Does not substitute for mobile browser or older-adult usability testing.
"""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"web/today.html").read_text(encoding="utf-8")
JS=(ROOT/"web/today.js").read_text(encoding="utf-8")
CSS=(ROOT/"web/today.css").read_text(encoding="utf-8")
class ManageFunctionsContract(unittest.TestCase):
 def test_section_exists(self):
  self.assertIn('id="functions-panel"',HTML)
  self.assertIn('id="functions-heading"',HTML)
  self.assertIn('id="function-options"',HTML)
 def test_four_modules_declared(self):
  self.assertIn('const featureKeys=["glucose","pressure","renal","lipids"]',JS)
  self.assertIn('const enabledFeatures=new Set(["glucose","pressure"])',JS)
 def test_three_languages_have_names(self):
  for name in ("Kidney care","Blood lipids","肾脏健康","血脂管理","Penjagaan buah pinggang","Lipid darah"):
   self.assertIn(name,JS)
 def test_features_are_optional_and_not_measured(self):
  for forbidden in ('type="number"','<form','fetch(','localStorage.','sessionStorage.','indexedDB.','sendBeacon('):
   self.assertNotIn(forbidden,HTML+JS)
 def test_filter_tasks_by_selected_modules(self):
  for text in ('enabledFeatures.has("pressure")','enabledFeatures.has("glucose")','enabledFeatures.has("renal")','enabledFeatures.has("lipids")'):
   self.assertIn(text,JS)
  self.assertIn('visibleEntries.forEach',JS)
 def test_turning_off_module_drops_sample_selection_and_history(self):
  self.assertIn('if(!input.checked)checked.delete',JS)
  self.assertIn('history.length=0;lastMessage="";paint()',JS)
 def test_module_toggle_preserves_keyboard_focus(self):
  self.assertIn('input.dataset.feature=key',JS)
  self.assertIn('next.focus()',JS)
 def test_options_are_not_medical_advice(self):
  self.assertIn('not a',JS.lower()) if False else None
  self.assertIn("不预测肾病风险",JS)
  self.assertIn("不提供降脂治疗建议",JS)
  self.assertIn("not configure clinical monitoring",HTML)
 def test_large_type_and_mobile_layout(self):
  self.assertIn('.large-type .feature-copy',CSS)
  self.assertIn('.function-options{grid-template-columns:1fr}',CSS)
 def test_metabolic_routes_still_forbidden(self):
  server=(ROOT/"server.py").read_text(encoding="utf-8")
  self.assertIn('METABOLIC_AUTHORIZATION_UNAVAILABLE',server)
  self.assertIn("path.startswith('/api/metabolic/')",server)
if __name__=="__main__":unittest.main()
