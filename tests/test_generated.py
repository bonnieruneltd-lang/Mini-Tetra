"""2,000 generated configuration tests.

Each case samples the catalog deterministically (seed 20261121), evaluates it, and
asserts the invariants that must hold for every build: budget arithmetic, BOM
reconciliation, circuit/PSU limits, VRAM/chassis compatibility, score bounds,
UPS sizing and determinism. Invalid combinations must be rejected for a physical
reason, not silently scored.
"""

from __future__ import annotations

import random
import unittest

from minitetra.catalog import FABRICS, GPUS, HEADS, PLATFORMS, STORAGE
from minitetra.model import (
    CIRCUIT_LIMIT_W,
    MAX_BOXES,
    MAX_GPUS,
    evaluate,
    psu_upgrade_cost,
    ups_spec,
)

SEED = 20261121
CASE_COUNT = 2000


def _peak(kwargs: dict) -> float:
    platform = PLATFORMS[kwargs["platform_key"]]
    gpu = GPUS[kwargs["gpu_key"]]
    peak = kwargs["boxes"] * (
        platform.idle_w + platform.cpu_load_w
        + kwargs["gpus_per_box"] * gpu.tdp_w * 0.95 + 15
    )
    if kwargs["head_key"]:
        peak += HEADS[kwargs["head_key"]].load_w
    return peak


def _psu(kwargs: dict):
    platform = PLATFORMS[kwargs["platform_key"]]
    gpu = GPUS[kwargs["gpu_key"]]
    need = 150 + platform.cpu_load_w + kwargs["gpus_per_box"] * gpu.tdp_w * 1.4
    return psu_upgrade_cost(platform.psu_included_w, need)


def sample_cases(count: int = CASE_COUNT, seed: int = SEED) -> list[dict]:
    rng = random.Random(seed)
    cases: list[dict] = []
    seen: set[tuple] = set()
    attempts = 0
    limit = count * 300
    while len(cases) < count and attempts < limit:
        attempts += 1
        platform_key = rng.choice(tuple(PLATFORMS))
        platform = PLATFORMS[platform_key]
        gpu_keys = (platform.fixed_gpu,) if platform.fixed_gpu else platform.gpu_choices
        gpu_key = rng.choice(gpu_keys)
        gpus_per_box = 1 if platform.fixed_gpu else rng.randint(1, platform.gpu_slots)
        boxes = rng.randint(1, MAX_BOXES)
        if boxes * gpus_per_box > MAX_GPUS:
            continue
        head_mode = rng.choice(("dedicated", "homogeneous"))
        if head_mode == "homogeneous":
            if boxes < 2:
                continue
            head_key, ha = None, False
        else:
            head_key = rng.choice(tuple(HEADS))
            ha = rng.random() < 0.15
        case = {
            "head_key": head_key,
            "head_mode": head_mode,
            "platform_key": platform_key,
            "gpu_key": gpu_key,
            "boxes": boxes,
            "gpus_per_box": gpus_per_box,
            "fabric_key": rng.choice(tuple(FABRICS)),
            "storage_key": rng.choice(tuple(STORAGE)),
            "ha": ha,
            "ups": rng.random() < 0.8,
            "gpu_price_scale": 1.0,
            "detailed": True,
        }
        key = (
            head_key, head_mode, platform_key, gpu_key, boxes, gpus_per_box,
            case["fabric_key"], case["storage_key"], ha, case["ups"],
        )
        if key in seen:
            continue
        seen.add(key)
        cases.append(case)
    if len(cases) != count:
        raise RuntimeError(f"only sampled {len(cases)} unique cases")
    return cases


CASES = sample_cases()


def _make_test(kwargs: dict):
    def test(self) -> None:
        platform = PLATFORMS[kwargs["platform_key"]]
        gpu = GPUS[kwargs["gpu_key"]]
        expected_peak = _peak(kwargs)

        candidate = evaluate(**kwargs)

        if gpu.tdp_w > platform.max_gpu_tdp:
            self.assertIsNone(candidate)
            return

        if candidate is None:
            # A structurally valid case may only be rejected for power reasons.
            self.assertTrue(
                expected_peak > CIRCUIT_LIMIT_W or _psu(kwargs) is None,
                msg=f"rejected without a power reason: {kwargs}",
            )
            return

        self.assertLessEqual(candidate.peak_w, CIRCUIT_LIMIT_W)
        self.assertLessEqual(candidate.gpu.tdp_w, candidate.platform.max_gpu_tdp)
        self.assertLessEqual(candidate.gpus_total, MAX_GPUS)
        self.assertLessEqual(candidate.gpus_per_box, candidate.platform.gpu_slots)

        self.assertGreater(candidate.total_cost, 0)
        self.assertEqual(
            sum(line.total_usd for line in candidate.bom), candidate.total_cost
        )
        self.assertGreaterEqual(candidate.stability, 0.0)
        self.assertLessEqual(candidate.stability, 10.0)
        self.assertGreater(candidate.score, 0.0)
        self.assertLessEqual(candidate.score, 100.0)
        for name, value in candidate.components.items():
            self.assertGreaterEqual(value, 0.0, msg=name)
            self.assertLessEqual(value, 100.0001, msg=name)

        if candidate.ups:
            price, label = ups_spec(candidate.peak_w)
            self.assertEqual(candidate.ups_cost, price)
            self.assertEqual(candidate.ups_label, label)
        else:
            self.assertEqual(candidate.ups_cost, 0)
            self.assertEqual(candidate.ups_label, "none")

        again = evaluate(**kwargs)
        self.assertEqual(candidate.signature, again.signature)
        self.assertEqual(candidate.total_cost, again.total_cost)
        self.assertAlmostEqual(candidate.score, again.score, places=6)

    test.__name__ = "test_generated_case"
    test.__doc__ = (
        f"{kwargs['head_mode']} head={kwargs['head_key']} "
        f"{kwargs['boxes']}x {kwargs['platform_key']} "
        f"gpu={kwargs['gpu_key']} x{kwargs['gpus_per_box']} "
        f"{kwargs['fabric_key']}/{kwargs['storage_key']} ups={kwargs['ups']}"
    )
    return test


class TestGeneratedMatrix(unittest.TestCase):
    def test_case_count(self) -> None:
        self.assertEqual(len(CASES), CASE_COUNT)
        self.assertEqual(len({tuple(sorted(c.items())) for c in CASES}), CASE_COUNT)

    def test_matrix_covers_every_platform_and_gpu_class(self) -> None:
        selectable = set()
        for platform in PLATFORMS.values():
            selectable.update(
                (platform.fixed_gpu,) if platform.fixed_gpu else platform.gpu_choices
            )
        self.assertEqual({c["platform_key"] for c in CASES}, set(PLATFORMS))
        self.assertEqual({c["gpu_key"] for c in CASES}, selectable)
        self.assertEqual({c["fabric_key"] for c in CASES}, set(FABRICS))
        self.assertEqual({c["storage_key"] for c in CASES}, set(STORAGE))
        # The three catalog GPUs no chassis can host are deliberately absent.
        self.assertEqual(set(GPUS) - selectable, {"rtx5090_32", "rtx5080_16", "rx7900xtx_24"})

    def test_matrix_has_both_head_modes(self) -> None:
        self.assertEqual({c["head_mode"] for c in CASES}, {"dedicated", "homogeneous"})


for index, case in enumerate(CASES):
    setattr(TestGeneratedMatrix, f"test_case_{index:04d}", _make_test(case))


if __name__ == "__main__":
    unittest.main()
