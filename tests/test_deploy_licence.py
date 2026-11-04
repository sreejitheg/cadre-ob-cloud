"""COB-196: a gateway licensed for the modules a page needs needs no trial."""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "hmi"))

import deploy  # noqa: E402

# the shape the real 8.3.6 gateway answered on 2026-10-30, keys cut to those read
LICENSED = {"items": [
    {"id": "com.inductiveautomation.perspective", "name": "Perspective", "state": "ACTIVE", "licenseState": "Activated"},
    {"id": "cadre.hmi.ob", "name": "Cadre HMI Components", "state": "ACTIVE", "licenseState": "Free"},
    {"id": "com.inductiveautomation.sfc", "name": "SFC", "state": "ACTIVE", "licenseState": "Trial"},
    {"id": "com.inductiveautomation.vision", "name": "Vision", "state": "INACTIVE", "licenseState": "n/a"},
], "metadata": {"total": 4, "matching": 4, "limit": -1, "offset": 0}}


class LicenceTests(unittest.TestCase):
    def test_states_by_id_and_name(self):
        states = deploy.module_states(LICENSED)
        self.assertEqual(states["cadre.hmi.ob"], "free")
        self.assertEqual(states["perspective"], "activated")
        self.assertEqual(states["vision"], "inactive")  # a disabled module counts for nothing
        self.assertEqual(deploy.module_states({"status": 500}), {})

    def test_licensed_needs_activated_mode_and_every_module(self):
        activated = {"licenseMode": "Activated", "trialSecondsLeft": 100, "expired": False}
        self.assertTrue(deploy.licensed(activated, read=lambda: LICENSED))
        self.assertFalse(deploy.licensed(activated, ["com.inductiveautomation.sfc"], read=lambda: LICENSED))
        self.assertFalse(deploy.licensed(activated, ["com.inductiveautomation.vision"], read=lambda: LICENSED))
        self.assertFalse(deploy.licensed({**activated, "licenseMode": "Trial"}, read=lambda: LICENSED))

        def broken():
            raise OSError("unreachable")
        self.assertFalse(deploy.licensed(activated, read=broken))

    def test_ensure_trial_leaves_a_licensed_gateway_alone(self):
        read = {"licenseMode": "Activated", "trialSecondsLeft": 100, "expired": False}
        with mock.patch.object(deploy, "trial", return_value=read) as trial, \
                mock.patch.object(deploy, "modules", return_value=LICENSED):
            out = deploy.ensure_trial(900)
        self.assertTrue(out["licensed"])
        self.assertTrue(out["rule"].startswith("licensed: "))
        trial.assert_called_once_with()  # one read, no reset

    def test_ensure_trial_keeps_the_rules_in_trial_mode(self):
        calls = []

        def trial(reset=False):
            calls.append(reset)
            return {"licenseMode": "Trial", "trialSecondsLeft": 5000, "expired": False}
        with mock.patch.object(deploy, "trial", side_effect=trial), \
                mock.patch.object(deploy, "modules", side_effect=AssertionError("not read in trial mode")):
            out = deploy.ensure_trial(900)
        self.assertNotIn("licensed", out)
        self.assertEqual(calls, [False])


if __name__ == "__main__":
    unittest.main()
