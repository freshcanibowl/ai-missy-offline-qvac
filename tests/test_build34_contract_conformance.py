"""Build34: fail-closed gate for independently sourced contract discrepancies.

The file is a dated source-inspection snapshot, NOT live integration proof.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=json.loads((ROOT/"evidence"/"build34_contract_conformance.json").read_text(encoding="utf-8"))
class IndependentConformanceBuild34(unittest.TestCase):
 def test_01_schema_and_synthetic_boundary(self):
  self.assertEqual(EVIDENCE["schema"],"ai-missy.build34.conformance-audit.v1")
  self.assertIs(EVIDENCE["synthetic_only"],True)
 def test_02_release_fails_closed(self):
  self.assertEqual(EVIDENCE["release_gate"],"NO_GO")
 def test_03_sources_have_repository_paths_and_blob_shas(self):
  for source in EVIDENCE["source_evidence"]:
   self.assertIn("/",source["repo"])
   self.assertTrue(source["path"])
   self.assertEqual(source["status"],"SOURCE_INSPECTED")
   self.assertTrue(source["facts"])
   if source["repo"]!="freshcanibowl/ai-missy-offline-qvac":
    self.assertRegex(source["sha"],r"^[a-f0-9]{40}$")
 def test_04_unverified_is_not_promoted_to_pass(self):
  self.assertFalse(any(g["status"]=="PASS" for g in EVIDENCE["gates"]))
 def test_05_required_eight_gates(self):
  self.assertEqual({g["id"] for g in EVIDENCE["gates"]},set("G"+str(x) for x in range(1,9)))
 def test_06_explicit_enum_mismatch(self):
  gates={g["id"]:g for g in EVIDENCE["gates"]}
  self.assertEqual(gates["G3"]["status"],"MISMATCH")
 def test_07_explicit_intake_mismatch(self):
  gates={g["id"]:g for g in EVIDENCE["gates"]}
  self.assertEqual(gates["G4"]["status"],"MISMATCH")
 def test_08_actual_ace_consent_unverified(self):
  gates={g["id"]:g for g in EVIDENCE["gates"]}
  self.assertEqual(gates["G2"]["status"],"NOT_VERIFIED")
 def test_09_actual_pair_ack_unverified(self):
  gates={g["id"]:g for g in EVIDENCE["gates"]}
  self.assertEqual(gates["G1"]["status"],"NOT_VERIFIED")
 def test_10_real_loopback_unverified(self):
  gates={g["id"]:g for g in EVIDENCE["gates"]}
  self.assertEqual(gates["G7"]["status"],"NOT_VERIFIED")
 def test_11_gate_evidence_required(self):
  self.assertTrue(all(g["required_evidence"] for g in EVIDENCE["gates"]))
 def test_12_no_real_api_added(self):
  server=(ROOT/"server.py").read_text(encoding="utf-8")
  self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",server)
  self.assertNotIn("/api/handoff",server)
 def test_13_no_fake_ace_endpoint_claim(self):
  source=json.dumps(EVIDENCE)
  self.assertNotIn('"release_gate": "GO"',source)
 def test_14_source_review_contains_real_pair_intake_contract(self):
  self.assertTrue(any(s["repo"]=="freshcanibowl/pair-renal-care"
      and s["path"]=="web/intake.js" and "pair.renal-intake.v1" in s["facts"]
      for s in EVIDENCE["source_evidence"]))
 def test_15_source_review_contains_ace_shared_contracts(self):
  self.assertTrue(any(s["repo"]=="freshcanibowl/ACE"
      and s["path"]=="packages/contracts-schema/src/index.js"
      and "ace.consent/0.1" in s["facts"] for s in EVIDENCE["source_evidence"]))
if __name__=="__main__": unittest.main()
