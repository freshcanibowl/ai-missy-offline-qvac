"""Build27: real Chromium E2E checks for synthetic Functions UI.

No clinical data, live IDP, remote network calls or persistent test accounts.
Run via the separate browser CI workflow (not the Python-only regression).
"""
import threading
import unittest
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import server

class FunctionsBrowserE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(("127.0.0.1",0),server.Handler)
        cls.base=f"http://127.0.0.1:{cls.http.server_port}"
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True)
        cls.thread.start()
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True, args=["--no-sandbox"])
    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.http.shutdown();cls.http.server_close();cls.thread.join(timeout=5)
    def setUp(self):
        self.context=self.browser.new_context(viewport={"width":390,"height":844})
        self.page=self.context.new_page()
        self.errors=[]
        self.page.on("pageerror",lambda exc:self.errors.append(str(exc)))
        self.page.goto(self.base+"/today",wait_until="load")
    def tearDown(self):
        self.assertEqual(self.errors,[], "Unexpected JavaScript error")
        self.context.close()
    def toggle(self,key,value=True):
        loc=self.page.locator(f'#function-options input[data-feature="{key}"]')
        if value:loc.check()
        else:loc.uncheck()
        return loc
    def test_01_default_two_modules_and_synthetic_banner(self):
        self.assertTrue(self.page.locator("#demo-flag").is_visible())
        self.assertTrue(self.page.locator('#function-options input[data-feature="glucose"]').is_checked())
        self.assertTrue(self.page.locator('#function-options input[data-feature="pressure"]').is_checked())
        self.assertFalse(self.page.locator('#function-options input[data-feature="renal"]').is_checked())
        self.assertFalse(self.page.locator('#function-options input[data-feature="lipids"]').is_checked())
        self.assertEqual(self.page.locator("#tasks input").count(),4)
    def test_02_enable_kidney_and_lipids_renders_tasks(self):
        self.toggle("renal")
        self.toggle("lipids")
        self.assertEqual(self.page.locator("#tasks input").count(),6)
        self.assertTrue(self.page.locator('#tasks input[data-index="4"]').is_visible())
        self.assertTrue(self.page.locator('#tasks input[data-index="5"]').is_visible())
        self.assertIn("Kidney follow-up",self.page.locator("#tasks").inner_text())
    def test_03_turning_off_module_removes_sample_and_history(self):
        self.page.locator('#tasks input[data-index="1"]').check()
        self.assertFalse(self.page.locator("#undo").is_disabled())
        self.toggle("glucose",False)
        self.assertEqual(self.page.locator('#tasks input[data-index="1"]').count(),0)
        self.assertTrue(self.page.locator("#undo").is_disabled())
        self.toggle("glucose")
        self.assertFalse(self.page.locator('#tasks input[data-index="1"]').is_checked())
    def test_04_three_languages_and_display_choices(self):
        self.page.locator("#language").select_option("zh")
        self.assertEqual(self.page.locator("#functions-heading").inner_text(),"管理功能")
        self.toggle("renal")
        self.assertIn("肾脏复查任务",self.page.locator("#tasks").inner_text())
        self.page.locator("#language").select_option("ms")
        self.assertEqual(self.page.locator("#functions-heading").inner_text(),"Urus Fungsi")
        self.assertTrue(self.page.locator('#function-options input[data-feature="renal"]').is_checked())
        self.assertIn("Susulan buah pinggang",self.page.locator("#tasks").inner_text())
        self.page.locator("#language").select_option("en")
        self.assertEqual(self.page.locator("#functions-heading").inner_text(),"Manage Functions")
    def test_05_task_undo_reset_and_focus(self):
        item=self.page.locator('#tasks input[data-index="0"]')
        item.check()
        self.assertTrue(self.page.locator("#undo").is_enabled())
        self.assertEqual(self.page.evaluate('document.activeElement.dataset.index'),"0")
        self.page.locator("#undo").click()
        self.assertFalse(self.page.locator('#tasks input[data-index="0"]').is_checked())
        self.assertTrue(self.page.locator("#undo").is_disabled())
        self.page.locator('#tasks input[data-index="1"]').check()
        self.page.locator("#reset").click()
        self.assertFalse(self.page.locator('#tasks input[data-index="1"]').is_checked())
    def test_06_large_text_and_375px_no_overflow(self):
        self.page.locator("#large-text").click()
        self.assertEqual(self.page.locator("#large-text").get_attribute("aria-pressed"),"true")
        self.assertTrue(self.page.locator("body").evaluate("(node)=>node.classList.contains('large-type')"))
        self.page.set_viewport_size({"width":375,"height":812})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"),"Horizontal overflow detected")
    def test_07_reloading_does_not_persist_settings(self):
        self.toggle("lipids")
        self.toggle("pressure",False)
        self.page.reload(wait_until="load")
        self.assertFalse(self.page.locator('#function-options input[data-feature="lipids"]').is_checked())
        self.assertTrue(self.page.locator('#function-options input[data-feature="pressure"]').is_checked())
        state=self.page.evaluate("({ls:localStorage.length,ss:sessionStorage.length,idb:typeof indexedDB})")
        self.assertEqual(state["ls"],0)
        self.assertEqual(state["ss"],0)
    def test_08_no_unauthorised_network_access_from_ui(self):
        requests=[]
        self.page.on("request",lambda request:requests.append(request.url))
        self.toggle("renal")
        self.page.locator('#tasks input[data-index="4"]').check()
        self.page.locator("#language").select_option("zh")
        self.assertFalse(any("/api/" in url for url in requests),requests)
        response=self.page.request.get(self.base+"/api/metabolic/entries")
        self.assertEqual(response.status,403)
        self.assertEqual(response.json()["error"],"METABOLIC_AUTHORIZATION_UNAVAILABLE")

    def test_09_dashboard_defaults_to_enabled_modules(self):
        self.assertEqual(self.page.locator("#care-cards .care-card").count(),2)
        self.assertEqual(self.page.locator('#care-cards [data-care="glucose"]').count(),1)
        self.assertEqual(self.page.locator('#care-cards [data-care="pressure"]').count(),1)
        self.assertEqual(self.page.locator("#care-completed").inner_text(),"0")
        self.assertEqual(self.page.locator("#care-remaining").inner_text(),"2")
    def test_10_dashboard_updates_with_module_switches(self):
        self.toggle("renal")
        self.assertEqual(self.page.locator('#care-cards [data-care="renal"]').count(),1)
        self.assertEqual(self.page.locator("#care-remaining").inner_text(),"3")
        self.toggle("pressure",False)
        self.assertEqual(self.page.locator('#care-cards [data-care="pressure"]').count(),0)
        self.assertEqual(self.page.locator("#care-remaining").inner_text(),"2")
    def test_11_dashboard_updates_when_task_checked_and_undone(self):
        self.page.locator('#tasks input[data-index="1"]').check()
        self.assertEqual(self.page.locator("#care-completed").inner_text(),"1")
        self.assertEqual(self.page.locator("#care-remaining").inner_text(),"1")
        self.assertIn("Selected",self.page.locator('[data-care="glucose"]').inner_text())
        self.page.locator("#undo").click()
        self.assertEqual(self.page.locator("#care-completed").inner_text(),"0")
        self.assertEqual(self.page.locator("#care-remaining").inner_text(),"2")
    def test_12_dashboard_locales_and_action_focus(self):
        self.page.locator("#language").select_option("zh")
        self.assertEqual(self.page.locator("#care-heading").inner_text(),"今天的照护一览")
        self.page.locator('[data-care="glucose"] .care-task-link').click()
        self.assertEqual(self.page.evaluate("document.activeElement.dataset.index"),"1")
        self.page.locator("#language").select_option("ms")
        self.assertEqual(self.page.locator("#care-heading").inner_text(),"Ringkasan penjagaan hari ini")
        self.assertTrue(self.page.locator('[data-care="glucose"]').is_visible())
    def test_13_no_modules_empty_and_reloading_resets_dashboard(self):
        self.toggle("glucose",False)
        self.toggle("pressure",False)
        self.assertEqual(self.page.locator("#care-cards .care-card").count(),0)
        self.assertTrue(self.page.locator("#care-empty").is_visible())
        self.assertEqual(self.page.locator("#care-remaining").inner_text(),"0")
        self.page.reload(wait_until="load")
        self.assertEqual(self.page.locator("#care-cards .care-card").count(),2)
    def test_14_mobile_dashboard_has_no_overflow_with_large_text(self):
        self.toggle("renal")
        self.toggle("lipids")
        self.page.locator("#large-text").click()
        self.page.set_viewport_size({"width":375,"height":812})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        self.assertEqual(self.page.locator("#care-cards .care-card").count(),4)
    def test_15_dashboard_never_fetches_patient_data(self):
        traffic=[]
        self.page.on("request",lambda r:traffic.append(r.url))
        self.toggle("renal")
        self.page.locator('#tasks input[data-index="4"]').check()
        self.page.locator("#undo").click()
        self.page.locator("#reset").click()
        self.assertFalse(any("/api/" in url for url in traffic),traffic)

    def test_16_timeline_only_includes_enabled_modules(self):
        self.assertEqual(self.page.locator("#timeline-events .timeline-event").count(),2)
        self.assertEqual(self.page.locator('[data-event-id="SYN-GL-001"]').count(),1)
        self.assertEqual(self.page.locator('[data-event-id="SYN-BP-001"]').count(),1)
        self.assertEqual(self.page.locator('[data-event-id="SYN-RN-001"]').count(),0)
        self.toggle("renal")
        self.assertEqual(self.page.locator("#timeline-events .timeline-event").count(),3)
        self.toggle("glucose",False)
        self.assertEqual(self.page.locator('[data-event-id="SYN-GL-001"]').count(),0)
    def test_17_timeline_orders_by_observed_date_desc(self):
        self.toggle("lipids")
        self.toggle("renal")
        ids=self.page.locator("#timeline-events .timeline-event").evaluate_all("(nodes)=>nodes.map(x=>x.dataset.eventId)")
        self.assertEqual(ids,["SYN-LP-001","SYN-RN-001","SYN-GL-001","SYN-BP-001"])
        observed=self.page.locator("#timeline-events time").evaluate_all("(nodes)=>nodes.map(x=>x.dateTime)")
        self.assertEqual(observed,sorted(observed,reverse=True))
    def test_18_timeline_provenance_is_explainable(self):
        event=self.page.locator('[data-event-id="SYN-GL-001"]')
        self.assertIn("Not verified",event.inner_text())
        btn=event.locator("button.timeline-inspect")
        self.assertEqual(btn.get_attribute("aria-expanded"),"false")
        btn.click()
        self.assertEqual(btn.get_attribute("aria-expanded"),"true")
        self.assertTrue(event.locator("dl.timeline-provenance").is_visible())
        self.assertIn("SYN-EV-102",event.inner_text())
        self.assertIn("synthetic_patient_demo",event.inner_text())
        btn.click()
        self.assertFalse(event.locator("dl.timeline-provenance").is_visible())
    def test_19_timeline_language_and_no_module_empty_state(self):
        self.page.locator("#language").select_option("zh")
        self.assertEqual(self.page.locator("#timeline-heading").inner_text(),"照护时间线")
        self.assertIn("尚未验证",self.page.locator("#timeline-events").inner_text())
        self.page.locator("#language").select_option("ms")
        self.assertEqual(self.page.locator("#timeline-heading").inner_text(),"Garis masa penjagaan")
        self.toggle("pressure",False)
        self.toggle("glucose",False)
        self.assertEqual(self.page.locator("#timeline-events .timeline-event").count(),0)
        self.assertTrue(self.page.locator("#timeline-empty").is_visible())
    def test_20_timeline_is_immutable_demo_not_checkin_history(self):
        self.toggle("renal")
        initial=self.page.locator("#timeline-events .timeline-event").count()
        self.page.locator('#tasks input[data-index="4"]').check()
        self.page.locator("#undo").click()
        self.page.locator("#reset").click()
        self.assertEqual(self.page.locator("#timeline-events .timeline-event").count(),initial)
        self.page.reload()
        self.assertEqual(self.page.locator("#timeline-events .timeline-event").count(),2)
    def test_21_contract_rejects_invalid_and_untrusted_events(self):
        result=self.page.evaluate("""() => ({
         valid:timelineObservations.every(isValidTimelineObservation),
         falseSynthetic:isValidTimelineObservation({...timelineObservations[0],synthetic:false}),
         wrongScope:isValidTimelineObservation({...timelineObservations[0],scope:'patient'}),
         futureRecorded:isValidTimelineObservation({...timelineObservations[0],recordedAt:'2026-09-01T00:00:00+08:00'}),
         missingProvenance:isValidTimelineObservation({...timelineObservations[0],evidenceId:''}),
         wrongDomain:isValidTimelineObservation({...timelineObservations[0],module:'medication'}),
         invalidDate:isValidTimelineObservation({...timelineObservations[0],observedAt:'tomorrow'})
        })""")
        self.assertTrue(result["valid"])
        for key in ("falseSynthetic","wrongScope","futureRecorded","missingProvenance","wrongDomain","invalidDate"):
            self.assertFalse(result[key],key)
    def test_22_timeline_no_patient_api_no_mobile_overflow(self):
        requests=[]
        self.page.on("request",lambda r:requests.append(r.url))
        self.toggle("renal")
        self.page.locator('[data-event-id="SYN-RN-001"] button.timeline-inspect').click()
        self.page.locator("#language").select_option("zh")
        self.page.locator("#large-text").click()
        self.page.set_viewport_size({"width":375,"height":812})
        self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
        self.assertFalse(any("/api/" in u for u in requests),requests)

if __name__=="__main__":
    unittest.main()
