"""Gate G8 waits for the view state badges of embedded views that are still loading (spike T2, 2026-11-03)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "compare"))
import capture  # noqa: E402


class FakeBadges:
    def __init__(self, counts):
        self.counts, self.waited = list(counts), 0

    def count(self):
        return self.counts[0]

    def locator(self, selector):
        return self

    def wait_for_timeout(self, ms):
        self.waited += ms
        if len(self.counts) > 1:
            self.counts.pop(0)


class SettleBadgesTests(unittest.TestCase):
    def test_loading_badges_that_clear_are_waited_for(self):
        page = FakeBadges([82, 40, 0])
        self.assertEqual(capture.settle_badges(page, cap_ms=60000, step_ms=1000), 2000)
        self.assertEqual(page.count(), 0)

    def test_a_badge_that_stays_is_still_counted(self):
        page = FakeBadges([3])
        self.assertIsNone(capture.settle_badges(page, cap_ms=5000, step_ms=1000))
        self.assertEqual(page.waited, 5000)
        self.assertEqual(page.count(), 3)          # the verdict reads it and fails, as before

    def test_a_clean_page_is_not_delayed(self):
        page = FakeBadges([0])
        self.assertEqual(capture.settle_badges(page), 0)
        self.assertEqual(page.waited, 0)


if __name__ == "__main__":
    unittest.main()
