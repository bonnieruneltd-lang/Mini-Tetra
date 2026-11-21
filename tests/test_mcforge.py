"""Minecraft Forge cluster invariants and no-GPU checks."""

from __future__ import annotations

import unittest

from mcforge.model import MAX_INSTANCES_PER_NODE, RAM_PER_INSTANCE, THREADS_PER_INSTANCE, evaluate
from mcforge.report import build_payload, make_bom
from mcforge.search import explore, select_winners

EX = explore(6000)
WINNERS = select_winners(EX)
PAYLOAD = build_payload(6000, EX)


class TestSearch(unittest.TestCase):
    def test_more_than_1000_configurations(self) -> None:
        self.assertGreater(EX.considered, 1000)
        self.assertGreater(EX.valid, 1000)
        self.assertGreater(EX.within_budget, 1000)

    def test_winners_are_under_budget_with_head_and_ups(self) -> None:
        self.assertEqual(len(WINNERS), 3)
        for c, _, _ in WINNERS:
            self.assertLessEqual(c.total_cost, 6000)
            self.assertIsNotNone(c.head_key)
            self.assertTrue(c.ups)
            self.assertGreaterEqual(c.stability, 6.0)

    def test_no_gpus_anywhere(self) -> None:
        self.assertEqual(PAYLOAD["meta"]["gpus_required"], 0)
        for w in PAYLOAD["winners"]:
            self.assertEqual(w["gpus"], 0)
            self.assertNotIn("RTX", w["cpu"])
            self.assertNotIn("Radeon", w["cpu"])
        text = str(PAYLOAD)
        self.assertNotIn("RTX ", text)
        self.assertNotIn("GeForce", text)

    def test_instance_math(self) -> None:
        for c, _, _ in WINNERS:
            expected = min(
                c.ram_gb // RAM_PER_INSTANCE,
                c.cpu.threads // THREADS_PER_INSTANCE,
                MAX_INSTANCES_PER_NODE,
            )
            self.assertEqual(c.instances_per_node, expected)
            self.assertEqual(c.total_instances, c.nodes * expected)

    def test_bom_sums_to_total(self) -> None:
        for c, _, _ in WINNERS:
            self.assertEqual(sum(b.total_usd for b in make_bom(c)), c.total_cost)

    def test_best_instance_build_exists(self) -> None:
        self.assertTrue(EX.power)
        self.assertGreaterEqual(EX.power[0].total_instances,
                                max(c.total_instances for c in EX.top))

    def test_search_is_deterministic(self) -> None:
        again = explore(6000, keep=20)
        self.assertEqual(
            [c.signature for c in EX.top[:20]],
            [c.signature for c in again.top[:20]],
        )


class TestRules(unittest.TestCase):
    def test_socket_mismatch_is_rejected(self) -> None:
        self.assertIsNone(
            evaluate("r5_7600", "itx_lga1700", 64, "2tb", 1, "n100", "2.5gbe")
        )

    def test_ram_slots_are_respected(self) -> None:
        self.assertIsNone(
            evaluate("r5_7600", "itx_am5", 128, "2tb", 1, "n100", "2.5gbe")
        )

    def test_headless_is_not_scored(self) -> None:
        c = evaluate("r5_7600", "itx_am5", 64, "2tb", 1, None, "2.5gbe")
        self.assertIsNotNone(c)
        self.assertLess(c.stability, 7.0)

    def test_report_payload_shape(self) -> None:
        self.assertIn("winners", PAYLOAD)
        self.assertIn("exploration", PAYLOAD)
        self.assertIn("alternatives", PAYLOAD)
        self.assertEqual(PAYLOAD["exploration"]["considered"], EX.considered)
        self.assertEqual(len(PAYLOAD["winners"]), 3)


if __name__ == "__main__":
    unittest.main()
