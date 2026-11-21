"""Extended catalog: 500+ models, pruning, and the power-first search."""

from __future__ import annotations

import unittest

from minitetra.enumerate import select_power_winners
from minitetra.extended import (
    CATALOG,
    VARIANT_STATS,
    explore_extended,
    power_analysis,
)
from minitetra.model import evaluate
from minitetra.variants import (
    HEAD_SHORTLIST,
    build_extended_catalog,
    pruned_catalog,
)

EX = explore_extended(6000, keep=30, max_boxes=2)


class TestVariantCatalog(unittest.TestCase):
    def test_adds_at_least_500_models(self) -> None:
        catalog, stats = build_extended_catalog()
        self.assertGreaterEqual(stats["total_added"], 500)
        self.assertEqual(stats["total_added"],
                         stats["added_gpus"] + stats["added_platforms"] + stats["added_heads"])
        self.assertEqual(len(catalog.gpus), stats["base_gpus"] + stats["added_gpus"])
        self.assertEqual(len(catalog.platforms),
                         stats["base_platforms"] + stats["added_platforms"])

    def test_every_reference_resolves(self) -> None:
        catalog, _ = build_extended_catalog()
        for platform in catalog.platforms.values():
            for key in platform.gpu_choices:
                self.assertIn(key, catalog.gpus)
            if platform.fixed_gpu:
                self.assertIn(platform.fixed_gpu, catalog.gpus)
        for head in catalog.heads.values():
            if head.has_gpu:
                self.assertIn(head.has_gpu, catalog.gpus)

    def test_keys_are_unique(self) -> None:
        catalog, _ = build_extended_catalog()
        self.assertEqual(len(catalog.platforms), len(set(catalog.platforms)))
        self.assertEqual(len(catalog.gpus), len(set(catalog.gpus)))
        self.assertEqual(len(catalog.heads), len(set(catalog.heads)))

    def test_pruning_keeps_tradeoffs(self) -> None:
        catalog, _ = build_extended_catalog()
        pruned, stats = pruned_catalog(catalog, HEAD_SHORTLIST)
        self.assertGreater(stats["gpus_after"], 0)
        self.assertLess(stats["gpus_after"], stats["gpus_before"])
        self.assertGreater(stats["platforms_after"], 0)
        self.assertLess(stats["platforms_after"], stats["platforms_before"])
        self.assertGreater(stats["heads_after"], 0)
        self.assertLessEqual(stats["heads_after"], len(HEAD_SHORTLIST))


class TestVariantEvaluation(unittest.TestCase):
    def test_four_gpu_custom_pc(self) -> None:
        catalog, _ = build_extended_catalog()
        platform_key = next(
            key for key, p in catalog.platforms.items()
            if p.gpu_slots == 4 and "rtx5070ti_16_zotac" in p.gpu_choices
        )
        candidate = evaluate(
            "ms01_head", "dedicated", platform_key, "rtx5070ti_16_zotac",
            1, 3, "2.5gbe", "shared_nvme", False, True,
            catalog=catalog,
        )
        self.assertIsNotNone(candidate)
        self.assertIn("Zotac", candidate.gpu.name)
        self.assertEqual(candidate.gpus_total, 3)
        self.assertLessEqual(candidate.total_cost, 6000)
        self.assertEqual(sum(line.total_usd for line in candidate.bom),
                         candidate.total_cost)
        self.assertEqual(candidate.platform.gpu_slots, 4)

    def test_variant_search_finds_more_power(self) -> None:
        self.assertGreater(EX.within_budget, 0)
        best_perf = max(c.perf_index for c in EX.power_top)
        self.assertGreater(best_perf, 648.0)  # base-catalog best
        winners = select_power_winners(EX, 3)
        self.assertTrue(winners)
        for candidate, label, _ in winners:
            self.assertFalse(candidate.gpu.used)
            self.assertTrue(candidate.ups)
            self.assertLessEqual(candidate.total_cost, 6000)
            self.assertIn(label, {"Best overall", "Best raw power",
                                  "Most resilient", "Runner-up"})

    def test_power_analysis_prefers_compute(self) -> None:
        analysis = power_analysis(EX)
        self.assertIn("best_raw_power", analysis)
        self.assertIn("best_efficiency", analysis)
        self.assertGreater(analysis["efficiency_index"], 0)
        self.assertGreaterEqual(
            analysis["best_raw_power"]["perf_index"], EX.top[0].perf_index
        )

    def test_global_extended_catalog_is_stable(self) -> None:
        self.assertGreaterEqual(VARIANT_STATS["total_added"], 500)
        self.assertEqual(len(CATALOG.gpus), VARIANT_STATS["base_gpus"] + VARIANT_STATS["added_gpus"])


if __name__ == "__main__":
    unittest.main()
