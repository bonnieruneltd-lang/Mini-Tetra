"""Variant search: 500+ models, Pareto pruning, power-first podium."""

from __future__ import annotations

from .catalog import Catalog
from .enumerate import Exploration, explore, select_power_winners
from .variants import HEAD_SHORTLIST, build_extended_catalog, pruned_catalog

CATALOG, VARIANT_STATS = build_extended_catalog()


def explore_extended(
    budget: int = 6000,
    gpu_price_scale: float = 1.0,
    keep: int = 1000,
    max_boxes: int = 4,
    min_vram: int = 16,
    catalog: Catalog | None = None,
) -> Exploration:
    """Search the extended catalog after dominance pruning.

    The full Cartesian product of 600+ platforms and 170+ GPUs is billions of
    combinations. Pareto pruning removes hardware that is worse on every axis
    (price, throughput, power, VRAM, slots, I/O) and keeps the trade-offs, which
    brings the search to a few hundred thousand builds.
    """
    base = catalog or CATALOG
    pruned, pruning = pruned_catalog(base, HEAD_SHORTLIST)
    ex = explore(
        budget,
        gpu_price_scale=gpu_price_scale,
        keep=keep,
        catalog=pruned,
        ups_options=(True,),
        ha_options=(False,),
        max_boxes=max_boxes,
        min_vram=min_vram,
        eval_min_vram=12,
        fabric_options=("2.5gbe", "5gbe", "10gbe", "25gbe"),
        storage_options=("shared_nvme", "local", "nvme_raid"),
        require_cuda=True,
    )
    ex.stats["variants"] = VARIANT_STATS if base is CATALOG else {}
    ex.stats["pruning"] = pruning
    return ex


def power_analysis(ex: Exploration) -> dict:
    """Best raw compute, best performance per watt, and the stability floor."""
    if not ex.top:
        return {}
    best = ex.top[0]
    source = ex.power_stable_top or ex.power_top or ex.top
    pool = [c for c in source if c.stability >= 6.0] or list(source)
    power = max(pool, key=lambda c: (c.perf_index, c.stability, -c.total_cost))
    near = [c for c in ex.top if c.score >= best.score * 0.85]
    efficient = max(near, key=lambda c: (c.perf_index / c.peak_w, c.score))
    stable_pool = [c for c in ex.resilient if c.stability >= 8.5]
    if not stable_pool:
        stable_pool = [c for c in ex.top if c.stability >= 8.5]
    stable_power = max(
        stable_pool,
        key=lambda c: (c.perf_index, c.score),
        default=power,
    )
    return {
        "best_raw_power": power.summary(),
        "best_efficiency": efficient.summary(),
        "efficiency_index": round(efficient.perf_index / efficient.peak_w, 4),
        "best_power_at_high_stability": stable_power.summary(),
        "stability_floor": 7.0,
    }


__all__ = [
    "CATALOG",
    "VARIANT_STATS",
    "explore_extended",
    "power_analysis",
    "select_power_winners",
]
