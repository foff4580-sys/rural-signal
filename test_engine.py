#!/usr/bin/env python3

import copy
import unittest

import engine


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in engine.load_fixtures()}

    def valid(self, case):
        value = dict(case["locked"])
        value.update(
            plain_summary=" | ".join(case["summary_required_terms"]),
            do_now=[case["allowed_actions"][0]],
            unknowns=[case["allowed_unknowns"][0]],
            sms=" | ".join(case["sms_required_terms"]),
        )
        return value

    def test_control_outputs(self):
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                self.assertEqual([], engine.validate_output(case, self.valid(case)))

    def test_locked_location_cannot_change(self):
        case = self.cases["official_flash_flood"]
        value = self.valid(case)
        value["location"] = "County Road 21"
        self.assertTrue(engine.validate_output(case, value))

    def test_invented_time_is_rejected(self):
        case = self.cases["official_flash_flood"]
        value = self.valid(case)
        value["sms"] += " Clear at 5:00 PM"
        self.assertTrue(any("time absent" in error for error in engine.validate_output(case, value)))

    def test_unsupported_action_is_rejected(self):
        case = self.cases["official_road_closure"]
        value = self.valid(case)
        value["do_now"] = ["Drive through slowly."]
        self.assertTrue(any("unsupported action" in error for error in engine.validate_output(case, value)))

    def test_unverified_report_cannot_become_official(self):
        case = self.cases["unverified_loose_cow"]
        value = self.valid(case)
        value["source_status"] = "OFFICIAL"
        self.assertTrue(engine.validate_output(case, value))

    def test_sms_limit(self):
        case = self.cases["unverified_loose_cow"]
        value = self.valid(case)
        value["sms"] += " x" * 100
        self.assertTrue(any("limit is 160" in error for error in engine.validate_output(case, value)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
