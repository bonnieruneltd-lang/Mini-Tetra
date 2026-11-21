"""Invariants for the Mini-Tetra build study."""

from __future__ import annotations

import csv
import os
import tempfile
import unittest

from minitetra.catalog import CONTINGENCY, GPUS, HEADS, PLATFORMS
from minitetra.enumerate import explore, head_mode_comparison, select_winners
from minitetra.model import (
    CIRCUIT_LIMIT_W,
    MAX_GPUS,
    evaluate,
    psu_upgrade_cost,
)

EX = explore(6000, keep=300)
WINNERS = select_winners(EX, 3)


class TestEnumerations(unittest.TestCase):
    def test_considers_far_more_than_1000_ways(self) -> None:
        self.assertGreater(EX.considered, 1000)
        self.assertGreater(EX.valid, 1000)
        self.assertGreater(EX.within_budget, 1000)
        self.assertGreater(EX.eligible, 1000)

    def test_budget_filter_is_real(self) -> None:
        over = [c for c in EX.top if c.total_cost <= 6000]
        self.assertEqual(len(over), len(EX.top))
        self.assertTrue(all(c.total_cost <= 6000 for c in WINNERS_CONTEXT()))

    def test_top_is_sorted_by_score(self) -> None:
        scores = [c.score for c in EX.top]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_enumeration_is_deterministic(self) -> None:
        other = explore(6000, keep=20)
        self.assertEqual(
            [c.signature for c in EX.top[:20]],
            [c.signature for c in other.top[:20]],
        )

    def test_price_shock_keeps_most_of_the_top_ten(self) -> None:
        shocked = explore(6000, gpu_price_scale=1.15, keep=20)

        def topology(c):
            return (c.head_key, c.platform_key, c.gpu_key, c.boxes, c.gpus_per_box)

        base = {topology(c) for c in EX.top[:10]}
        hit = sum(1 for c in shocked.top[:10] if topology(c) in base)
        self.assertGreaterEqual(hit, 3)


class TestWinners(unittest.TestCase):
    def test_three_distinct_winners(self) -> None:
        self.assertEqual(len(WINNERS), 3)
        self.assertEqual(len({c.signature for c, _, _ in WINNERS}), 3)

    def test_winners_are_new_with_ups_and_16gb(self) -> None:
        for c, _, _ in WINNERS:
            self.assertTrue(c.ups)
            self.assertFalse(c.gpu.used)
            self.assertFalse(c.platform.used)
            self.assertGreaterEqual(c.gpu.vram_gb, 16)
            self.assertEqual(c.head_mode, "dedicated")
            self.assertLessEqual(c.total_cost, 6000)

    def test_winners_respect_physics(self) -> None:
        for c, _, _ in WINNERS:
            self.assertLessEqual(c.peak_w, CIRCUIT_LIMIT_W)
            self.assertLessEqual(c.gpu.tdp_w, c.platform.max_gpu_tdp)
            self.assertLessEqual(c.gpus_total, MAX_GPUS)

    def test_bom_sums_to_total(self) -> None:
        for c in EX.top[:50] + [w for w, _, _ in WINNERS]:
            self.assertEqual(
                sum(line.total_usd for line in c.bom),
                c.total_cost,
                msg=f"BOM mismatch for {c.signature}",
            )

    def test_contingency_line_present(self) -> None:
        for c in [w for w, _, _ in WINNERS]:
            labels = " ".join(line.label for line in c.bom)
            self.assertIn(f"{CONTINGENCY:.0%}", labels)
            if c.ups:
                    self.assertTrue(any("UPS" in line.label and line.unit_usd > 0
                                for line in c.bom))


class TestHeadDecision(unittest.TestCase):
    def test_dedicated_head_wins_at_three_gpus(self) -> None:
        rows = head_mode_comparison("itx_sff", "rtx5060ti_16", "2.5gbe", "shared_nvme",
                                    gpu_counts=(3,))
        row = rows[0]
        self.assertEqual(row["gpus"], 3)
        self.assertGreaterEqual(row["delta_stability"], 1.0)
        self.assertIn("keep head separate", row["verdict"])
        self.assertGreater(row["delta_cost"], 0)

    def test_head_ladder_has_in_budget_winner(self) -> None:
        from minitetra.enumerate import head_ladder

        rows = head_ladder("itx_sff", "rtx5060ti_16", 3, 1, "2.5gbe", "shared_nvme")
        in_budget = [r for r in rows if r["within_budget"]]
        self.assertTrue(in_budget)
        non_gpu = [r for r in in_budget if r["head_kind"] != "workstation"]
        best_non_gpu = max(non_gpu, key=lambda r: r["score"])
        self.assertEqual(best_non_gpu["head_key"], "ms01_head")


class TestUnitRules(unittest.TestCase):
    def test_vram_capability_ordering(self) -> None:
        from minitetra.model import vram_cap

        self.assertLess(vram_cap(8), vram_cap(12))
        self.assertLess(vram_cap(12), vram_cap(16))
        self.assertLess(vram_cap(16), vram_cap(24))

    def test_psu_upgrade_tiers(self) -> None:
        self.assertEqual(psu_upgrade_cost(650, 500), 0)
        self.assertEqual(psu_upgrade_cost(650, 700), 60)
        self.assertEqual(psu_upgrade_cost(650, 950), 110)
        self.assertEqual(psu_upgrade_cost(650, 1400), 260)
        self.assertIsNone(psu_upgrade_cost(650, 2400))

    def test_rejects_gpu_over_chassis_limit(self) -> None:
        self.assertIsNone(
            evaluate("ms01_head", "dedicated", "itx_sff", "rtx5090_32", 1, 1,
                     "2.5gbe", "shared_nvme")
        )

    def test_rejects_ha_head_without_head(self) -> None:
        self.assertIsNone(
            evaluate(None, "homogeneous", "itx_sff", "rtx5060ti_16", 3, 1,
                     "2.5gbe", "shared_nvme", ha=True)
        )

    def test_catalog_references_are_valid(self) -> None:
        for platform in PLATFORMS.values():
            for key in platform.gpu_choices:
                self.assertIn(key, GPUS)
            if platform.fixed_gpu:
                self.assertIn(platform.fixed_gpu, GPUS)
        for head in HEADS.values():
            if head.has_gpu:
                self.assertIn(head.has_gpu, GPUS)


class TestExports(unittest.TestCase):
    def test_candidates_csv(self) -> None:
        from minitetra.report import write_candidates_csv

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "candidates.csv")
            write_candidates_csv(EX, path, limit=25)
            with open(path, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 25)
        self.assertEqual(rows[0]["rank"], "1")
        self.assertEqual(rows[0]["signature"], EX.top[0].signature)
        self.assertEqual(rows[0]["ups"], "yes")
        self.assertLessEqual(float(rows[0]["total_cost_usd"]), 6000)
        self.assertGreater(float(rows[0]["score"]), 0)

    def test_bom_csv_sums_per_pick(self) -> None:
        from minitetra.report import write_bom_csv

        payload = {"winners": [
            {"label": label, "total_cost_usd": c.total_cost,
             "bom": c.summary()["bom"]}
            for c, label, _ in WINNERS
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bom.csv")
            write_bom_csv(payload, path)
            with open(path, newline="", encoding="utf-8") as fh:
                rows = list(csv.DictReader(fh))
        picks = {row["pick"] for row in rows}
        self.assertEqual(picks, {label for _, label, _ in WINNERS})
        for pick in picks:
            build = int(next(r["build_total_usd"] for r in rows if r["pick"] == pick))
            total = sum(int(r["total_usd"]) for r in rows if r["pick"] == pick)
            self.assertEqual(total, build)


def WINNERS_CONTEXT():
    return [c for c, _, _ in WINNERS]


if __name__ == "__main__":
    unittest.main()
