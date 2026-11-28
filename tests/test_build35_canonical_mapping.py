"""Build35 proposed mapping tests; NOT upstream conformance certification."""
import unittest
from dataclasses import replace
from metabolic.canonical_mapping import (
    MappingDenied, proposed_escalation_map,verify_escalation_response,
    SyntheticMeasurement,SyntheticExtraction,prepare_pair_intake_preview,
    refuse_unverified_observation,refuse_ace_edge_capture_without_wire_contract)
from metabolic.longitudinal_memory import Observation

SUB="SYN-PATIENT-001"
def fixture(**overrides):
    fields=dict(schema="missy.synthetic-extraction.v1",document_id="SYN-DOC-001",
       captured_at="2026-11-20T08:00:00+08:00",subject=SUB,declared_deidentified=True,
       identifiers_retained=(),agent_role="extract_and_normalize_only",
       clinical_inference_performed=False,human_confirmed=True,
       confirmed_by="SYN-HUMAN-001",
       measurements=(SyntheticMeasurement("creatinine",92.0,"umol/L",0.99,"SYN-EV-001"),))
    fields.update(overrides)
    return SyntheticExtraction(**fields)
def run(data,**overrides):
    return prepare_pair_intake_preview(data,expected_subject=overrides.get("expected_subject",SUB),
                authorization_verified=overrides.get("authorization_verified",True))

class Build35MappingTests(unittest.TestCase):
 def test_01_valid_synthetic_fixture_constructed(self):
    data=run(fixture())
    self.assertEqual(data["schema_version"],"pair.renal-intake.v1")
    self.assertEqual(data["measurements"][0]["code"],"creatinine")
    self.assertEqual(data["assurance"]["release_gate"],"NO_GO")
 def test_02_not_automatically_real_clinical_data(self):
    self.assertTrue(run(fixture())["synthetic"])
    self.assertEqual(run(fixture())["assurance"]["target"],"offline_fixture_only")
 def test_03_proposed_three_escalation_levels(self):
    self.assertEqual(proposed_escalation_map("review_context",confirmed_by_rule_engine=True),"monitor")
    self.assertEqual(proposed_escalation_map("prompt_medical_review",confirmed_by_rule_engine=True),"prompt_medical_review")
    self.assertEqual(proposed_escalation_map("urgent_professional_assessment",confirmed_by_rule_engine=True),"urgent_review")
 def test_04_unknown_escalation_fails_closed(self):
    with self.assertRaises(MappingDenied):
      proposed_escalation_map("none",confirmed_by_rule_engine=True)
 def test_05_rule_engine_authority_required(self):
    with self.assertRaises(MappingDenied):
      proposed_escalation_map("urgent_professional_assessment",confirmed_by_rule_engine=False)
 def test_06_ace_downgrade_rejected(self):
    with self.assertRaises(MappingDenied):
      verify_escalation_response(pair_state="urgent_professional_assessment",ace_state="monitor",
       explanation_pair_state="urgent_professional_assessment",confirmed_by_rule_engine=True)
 def test_07_missy_override_rejected(self):
    with self.assertRaises(MappingDenied):
      verify_escalation_response(pair_state="urgent_professional_assessment",ace_state="urgent_review",
       explanation_pair_state="review_context",confirmed_by_rule_engine=True)
 def test_08_correct_escalation_passes(self):
    self.assertTrue(verify_escalation_response(pair_state="urgent_professional_assessment",
       ace_state="urgent_review",explanation_pair_state="urgent_professional_assessment",confirmed_by_rule_engine=True))
 def test_09_real_record_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),synthetic=False))
 def test_10_cross_subject_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),subject="SYN-PATIENT-002"))
 def test_11_missing_authorization_rejected(self):
    with self.assertRaises(MappingDenied):run(fixture(),authorization_verified=False)
 def test_12_missing_human_confirmation_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),human_confirmed=False))
 def test_13_missing_confirming_identity_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),confirmed_by=""))
 def test_14_identifiers_retained_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),identifiers_retained=("name",)))
 def test_15_not_deidentified_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),declared_deidentified=False))
 def test_16_clinical_inference_by_extraction_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),clinical_inference_performed=True))
 def test_17_bad_agent_role_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),agent_role="clinical_decider"))
 def test_18_missing_measurements_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=()))
 def test_19_missing_creatinine_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("egfr",49,"mL/min/1.73m2",.99,"SYN-EV-001"),)))
 def test_20_wrong_unit_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("creatinine",92,"mmHg",.99,"SYN-EV-001"),)))
 def test_21_low_confidence_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("creatinine",92,"umol/L",.9,"SYN-EV-001"),)))
 def test_22_nonfinite_value_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("creatinine",float("nan"),"umol/L",.99,"SYN-EV-001"),)))
 def test_23_boolean_value_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("creatinine",True,"umol/L",.99,"SYN-EV-001"),)))
 def test_24_duplicate_code_rejected(self):
    m=fixture().measurements[0]
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(m,m)))
 def test_25_unknown_code_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("hba1c",9,"% ",.99,"SYN-EV-001"),)))
 def test_26_missing_provenance_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),measurements=(SyntheticMeasurement("creatinine",92,"umol/L",.99,""),)))
 def test_27_invalid_document_date_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),captured_at="tomorrow"))
 def test_28_invalid_schema_rejected(self):
    with self.assertRaises(MappingDenied):run(replace(fixture(),schema="pair.renal-intake.v1"))
 def test_29_unverified_longitudinal_event_cannot_be_cast_as_lab(self):
    obs=Observation("SYN-GL-001","glucose","check_in","2026-11-20T08:00:00+08:00",
           "2026-11-20T08:05:00+08:00","synthetic_patient_demo","SYN-EV-001")
    with self.assertRaises(MappingDenied):refuse_unverified_observation(obs)
 def test_30_ace_draft_has_no_direct_ingestion_permission(self):
    with self.assertRaises(MappingDenied):refuse_ace_edge_capture_without_wire_contract()
 def test_31_multiple_measurements_with_sources(self):
    m=fixture().measurements[0]
    values=run(replace(fixture(),measurements=(m,SyntheticMeasurement("potassium",4.1,"mmol/L",.98,"SYN-EV-002"))))
    self.assertEqual(len(values["measurements"]),2)
 def test_32_no_patient_identifiers_in_output(self):
    result=run(fixture())
    self.assertNotIn("patientRef",result)
    self.assertNotIn("subject",result)
    self.assertEqual(result["privacy"]["identifiers_retained"],[])
 def test_33_synthetic_conformance_only_no_live_route(self):
    from pathlib import Path
    src=Path("server.py").read_text()
    self.assertIn("METABOLIC_AUTHORIZATION_UNAVAILABLE",src)
    self.assertNotIn("/api/handoff",src)
 def test_34_no_network_or_storage(self):
    from pathlib import Path
    src=Path("metabolic/canonical_mapping.py").read_text()
    self.assertNotIn("import requests",src)
    self.assertNotIn("sqlite3",src)
    self.assertNotIn("urlopen(",src)
 def test_35_invalid_consent_subject_is_not_silent(self):
    with self.assertRaises(MappingDenied):run(fixture(),expected_subject="SYN-PATIENT-OTHER")
if __name__=="__main__":unittest.main()
