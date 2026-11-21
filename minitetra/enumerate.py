"""Exhaustive enumeration of the build space, plus the head-node analysis."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from .catalog import BASE_CATALOG, Catalog, FABRICS, GPUS, HEADS, PLATFORMS, STORAGE
from .model import MAX_BOXES, MAX_GPUS, Candidate, evaluate, make_bom


@dataclass
class Exploration:
    budget: int
    gpu_price_scale: float
    considered: int = 0
    valid: int = 0
    within_budget: int = 0
    eligible: int = 0
    top: list[Candidate] = field(default_factory=list)
    pure_mini: list[Candidate] = field(default_factory=list)
    resilient: list[Candidate] = field(default_factory=list)
    power_top: list[Candidate] = field(default_factory=list)
    power_stable_top: list[Candidate] = field(default_factory=list)
    alternatives: dict[str, Candidate] = field(default_factory=dict)
    stats: dict = field(default_factory=dict)
    catalog: Catalog = BASE_CATALOG
    group_best: dict[str, Candidate] = field(default_factory=dict)

    @property
    def best(self) -> Candidate:
        return self.top[0]


def explore(
    budget: int = 6000,
    gpu_price_scale: float = 1.0,
    keep: int = 2000,
    catalog: Catalog | None = None,
    ups_options: tuple[bool, ...] = (True, False),
    ha_options: tuple[bool, ...] = (False, True),
    max_boxes: int = MAX_BOXES,
    min_vram: int = 16,
    eval_min_vram: int = 0,
    fabric_options: tuple[str, ...] | None = None,
    storage_options: tuple[str, ...] | None = None,
    require_cuda: bool = False,
) -> Exploration:
    cat = catalog or BASE_CATALOG
    ex = Exploration(budget=budget, gpu_price_scale=gpu_price_scale, catalog=cat)
    main_heap: list[tuple[float, int, str, Candidate]] = []
    mini_heap: list[tuple[float, int, str, Candidate]] = []
    res_heap: list[tuple[float, float, int, str, Candidate]] = []
    power_heap: list[tuple[float, float, int, str, Candidate]] = []
    stable_heap: list[tuple[float, float, int, str, Candidate]] = []
    by_fabric: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    group: dict[str, Candidate] = {}
    alternatives: dict[str, Candidate] = {}

    def keep_alt(key: str, candidate: Candidate) -> None:
        current = alternatives.get(key)
        if current is None or (candidate.score, -candidate.total_cost) > (current.score, -current.total_cost):
            alternatives[key] = candidate

    for platform_key, platform in cat.platforms.items():
        gpu_keys = (platform.fixed_gpu,) if platform.fixed_gpu else platform.gpu_choices
        for gpu_key in gpu_keys:
            if gpu_key not in cat.gpus:
                continue
            gpu = cat.gpus[gpu_key]
            if gpu.tdp_w > platform.max_gpu_tdp or gpu.vram_gb < eval_min_vram:
                continue
            for gpus_per_box in range(1, platform.gpu_slots + 1):
                if platform.fixed_gpu and gpus_per_box != 1:
                    continue
                for boxes in range(1, max_boxes + 1):
                    if boxes * gpus_per_box > MAX_GPUS:
                        break
                    for fabric_key in (fabric_options or tuple(cat.fabrics)):
                        for storage_key in (storage_options or tuple(cat.storage)):
                            for ups in ups_options:
                                for mode in ("dedicated", "homogeneous"):
                                    head_options = tuple(cat.heads) if mode == "dedicated" else (None,)
                                    for head_key in head_options:
                                        for ha in (ha_options if mode == "dedicated" else (False,)):
                                            ex.considered += 1
                                            c = evaluate(
                                                head_key, mode, platform_key, gpu_key,
                                                boxes, gpus_per_box, fabric_key,
                                                storage_key, ha, ups,
                                                gpu_price_scale, detailed=False,
                                                catalog=cat,
                                            )
                                            if c is None:
                                                continue
                                            ex.valid += 1
                                            if c.total_cost > budget:
                                                continue
                                            ex.within_budget += 1
                                            by_fabric[fabric_key] = by_fabric.get(fabric_key, 0) + 1
                                            by_mode[mode] = by_mode.get(mode, 0) + 1
                                            by_platform[platform_key] = by_platform.get(platform_key, 0) + 1

                                            if require_cuda and gpu.vendor != "nvidia":
                                                if (ups and not gpu.used and not platform.used
                                                        and gpu.vram_gb >= min_vram):
                                                    keep_alt("non_cuda", c)
                                                continue

                                            if ups:
                                                if gpu.used or platform.used:
                                                    keep_alt("value_used", c)
                                                if (c.head_mode == "homogeneous"
                                                        and not gpu.used and gpu.vram_gb >= 16):
                                                    keep_alt("no_separate_head", c)
                                                if (gpu.vram_gb >= 24 and boxes <= 3
                                                        and not gpu.used and not platform.used
                                                        and c.head_mode == "dedicated"
                                                        and not cat.heads[c.head_key].has_gpu):
                                                    keep_alt("vram_first", c)

                                            gkey = f"{gpu_key}|{c.gpus_total}|{fabric_key}|{mode}"
                                            prev = group.get(gkey)
                                            if prev is None or (c.score, -c.total_cost) > (prev.score, -prev.total_cost):
                                                group[gkey] = c

                                            # Podium baseline: UPS, new hardware with
                                            # warranty, and >=16 GB per GPU so Flux dev
                                            # fits without aggressive offload.
                                            if (not ups or gpu.used or platform.used
                                                    or gpu.vram_gb < min_vram):
                                                continue
                                            ex.eligible += 1
                                            pitem = (c.perf_index, c.score, -c.total_cost,
                                                     c.signature, c)
                                            if len(power_heap) < 100:
                                                heapq.heappush(power_heap, pitem)
                                            elif pitem[:4] > power_heap[0][:4]:
                                                heapq.heapreplace(power_heap, pitem)
                                            if c.stability >= 6.0:
                                                sitem = (c.perf_index, c.score, -c.total_cost,
                                                         c.signature, c)
                                                if len(stable_heap) < 100:
                                                    heapq.heappush(stable_heap, sitem)
                                                elif sitem[:4] > stable_heap[0][:4]:
                                                    heapq.heapreplace(stable_heap, sitem)
                                            item = (c.score, -c.total_cost, c.signature, c)
                                            if len(main_heap) < keep:
                                                heapq.heappush(main_heap, item)
                                            elif item[:3] > main_heap[0][:3]:
                                                heapq.heapreplace(main_heap, item)

                                            if (c.pure_mini and c.boxes >= 3
                                                    and c.head_mode == "dedicated"):
                                                if len(mini_heap) < 50:
                                                    heapq.heappush(mini_heap, item)
                                                elif item[:3] > mini_heap[0][:3]:
                                                    heapq.heapreplace(mini_heap, item)

                                            if (c.gpus_per_box == 1 and c.boxes >= 3
                                                    and c.head_mode == "dedicated"
                                                    and c.stability >= 8.5):
                                                ritem = (c.score, c.stability, -c.total_cost,
                                                         c.signature, c)
                                                if len(res_heap) < 50:
                                                    heapq.heappush(res_heap, ritem)
                                                elif ritem[:4] > res_heap[0][:4]:
                                                    heapq.heapreplace(res_heap, ritem)

    top = [item[3] for item in sorted(main_heap, key=lambda x: (-x[0], -x[1], x[2]))]
    mini = [item[3] for item in sorted(mini_heap, key=lambda x: (-x[0], -x[1], x[2]))]
    res = [item[4] for item in sorted(res_heap, key=lambda x: (-x[0], -x[1], -x[2], x[3]))]
    for c in top + mini + res:
        c.bom = make_bom(c)
    ex.top = top
    ex.pure_mini = mini
    ex.resilient = res
    ex.power_top = [
        item[4] for item in sorted(
            power_heap, key=lambda x: (-x[0], -x[1], -x[2], x[3])
        )
    ]
    ex.power_stable_top = [
        item[4] for item in sorted(
            stable_heap, key=lambda x: (-x[0], -x[1], -x[2], x[3])
        )
    ]
    ex.alternatives = alternatives
    ex.group_best = group
    ex.stats = {
        "min_vram": min_vram,
        "by_fabric": by_fabric,
        "by_head_mode": by_mode,
        "by_platform": by_platform,
        "max_score": top[0].score if top else 0.0,
        "median_top_score": top[len(top) // 2].score if top else 0.0,
    }
    return ex


def select_winners(ex: Exploration, count: int = 3) -> list[tuple[Candidate, str, str]]:
    """Pick a diverse podium: overall, pure mini-PC, most resilient.

    Returns (candidate, label, rationale) sorted by score.
    """
    picks: list[tuple[Candidate, str, str]] = []
    if not ex.top:
        return []
    best = ex.top[0]
    picks.append((
        best,
        "Best overall",
        "Highest weighted score: the most aggregate 16 GB+ throughput and VRAM "
        "that fits the budget, circuit and compatibility limits.",
    ))
    chosen = {best.signature}

    if ex.pure_mini:
        mini = ex.pure_mini[0]
        picks.append((
            mini,
            "Best pure mini-PC",
            "Highest score among builds where every box is a NUC-class mini PC, "
            "there are at least three worker nodes and all hardware is new.",
        ))
        chosen.add(mini.signature)

    floor = best.score * 0.88
    pool = [c for c in ex.resilient if c.signature not in chosen and c.score >= floor]
    if pool:
        res = max(pool, key=lambda c: (c.score, c.stability, -c.total_cost))
        picks.append((
            res,
            "Most resilient",
            "Best score among builds with one GPU per chassis, at least three nodes and "
            "stability >= 8.5, so no single failure removes more than a third of the fleet.",
        ))
        chosen.add(res.signature)

    for c in ex.top:
        if len(picks) >= count:
            break
        if c.signature not in chosen:
            picks.append((c, "Runner-up", "Next-best distinct topology."))
            chosen.add(c.signature)
    picks.sort(key=lambda item: -item[0].score)
    return picks[:count]


def select_power_winners(
    ex: Exploration,
    count: int = 3,
    stability_floor: float = 6.0,
) -> list[tuple[Candidate, str, str]]:
    """Podium for the variant study: balanced, raw power, resilient."""
    if not ex.top:
        return []
    picks: list[tuple[Candidate, str, str]] = []
    best = ex.top[0]
    picks.append((
        best, "Best overall",
        "Highest weighted score after the full variant search.",
    ))
    chosen = {best.signature}

    source = ex.power_stable_top or ex.power_top or ex.top
    power_pool = [
        c for c in source
        if c.signature not in chosen and c.stability >= stability_floor
    ]
    if power_pool:
        power = max(
            power_pool,
            key=lambda c: (c.perf_index, c.stability, -c.total_cost),
        )
        picks.append((
            power, "Best raw power",
            f"Highest aggregate GPU index with stability >= {stability_floor:.1f}; "
            "this is the build to pick when throughput matters more than uptime.",
        ))
        chosen.add(power.signature)

    floor = best.score * 0.88
    pool = [
        c for c in ex.resilient
        if c.signature not in chosen and c.score >= floor
    ]
    if pool:
        res = max(pool, key=lambda c: (c.score, c.stability, -c.total_cost))
        picks.append((
            res, "Most resilient",
            "Best score among one-GPU-per-chassis builds with at least three nodes "
            "and stability >= 8.5.",
        ))
        chosen.add(res.signature)

    for c in ex.top:
        if len(picks) >= count:
            break
        if c.signature not in chosen:
            picks.append((c, "Runner-up", "Next-best distinct topology."))
            chosen.add(c.signature)
    picks.sort(key=lambda item: -item[0].score)
    return picks[:count]


def head_ladder(
    platform_key: str,
    gpu_key: str,
    boxes: int,
    gpus_per_box: int,
    fabric_key: str,
    storage_key: str,
    ups: bool = True,
    gpu_price_scale: float = 1.0,
    budget: int = 6000,
    catalog: Catalog | None = None,
) -> list[dict]:
    """Every head option for one fixed worker fleet, plus the no-separate-head case."""
    cat = catalog or BASE_CATALOG
    rows: list[dict] = []
    for head_key, head in cat.heads.items():
        c = evaluate(head_key, "dedicated", platform_key, gpu_key, boxes, gpus_per_box,
                     fabric_key, storage_key, False, ups, gpu_price_scale, catalog=cat)
        if c is None:
            continue
        rows.append({
            "head_key": head_key,
            "head": head.name,
            "head_kind": head.kind,
            "mode": "dedicated",
            "head_cost": c.head_cost,
            "total_cost": c.total_cost,
            "perf_index": round(c.perf_index, 1),
            "stability": round(c.stability, 2),
            "score": round(c.score, 2),
            "within_budget": c.total_cost <= budget,
        })
    hom = evaluate(None, "homogeneous", platform_key, gpu_key, boxes, gpus_per_box,
                   fabric_key, storage_key, False, ups, gpu_price_scale, catalog=cat)
    if hom is not None:
        rows.append({
            "head_key": None,
            "head": f"{PLATFORMS[platform_key].name} (first node is also head)",
            "head_kind": "homogeneous",
            "mode": "homogeneous",
            "head_cost": 0,
            "total_cost": hom.total_cost,
            "perf_index": round(hom.perf_index, 1),
            "stability": round(hom.stability, 2),
            "score": round(hom.score, 2),
            "within_budget": hom.total_cost <= budget,
        })
    rows.sort(key=lambda r: (not r["within_budget"], -r["score"]))
    return rows


def head_mode_comparison(
    platform_key: str,
    gpu_key: str,
    fabric_key: str,
    storage_key: str,
    gpu_counts: tuple[int, ...] = (2, 3, 4, 6),
    ups: bool = True,
    gpu_price_scale: float = 1.0,
    budget: int = 6000,
    catalog: Catalog | None = None,
) -> list[dict]:
    """Three ways to place the head at an equal GPU count.

    1. dedicated non-GPU head  2. head with its own GPU  3. a worker as head.
    """
    cat = catalog or BASE_CATALOG
    out: list[dict] = []
    for n in gpu_counts:
        ded_all = [
            (key, c) for key in cat.heads for c in (
                evaluate(key, "dedicated", platform_key, gpu_key, n, 1, fabric_key,
                         storage_key, False, ups, gpu_price_scale, catalog=cat),
            ) if c is not None
        ]
        ded = [(k, c) for k, c in ded_all if not cat.heads[k].has_gpu]
        gpu_heads = [(k, c) for k, c in ded_all if cat.heads[k].has_gpu]
        hom = evaluate(None, "homogeneous", platform_key, gpu_key, n, 1, fabric_key,
                       storage_key, False, ups, gpu_price_scale, catalog=cat)
        if not ded:
            continue
        dk, d = max(ded, key=lambda kc: (kc[1].score, -kc[1].total_cost))
        gk, g = (max(gpu_heads, key=lambda kc: (kc[1].score, -kc[1].total_cost))
                 if gpu_heads else (None, None))
        delta_score = round(d.score - hom.score, 2) if hom else None
        delta_stability = round(d.stability - hom.stability, 2) if hom else None
        delta_cost = (d.total_cost - hom.total_cost) if hom else None
        if hom is None:
            verdict = "keep head separate"
        elif delta_stability is not None and delta_stability >= 1.0 and (delta_score or 0) >= -1.5:
            verdict = "keep head separate (reliability wins)"
        elif (delta_score or 0) > 0:
            verdict = "keep head separate"
        else:
            verdict = "merge head into a worker"
        out.append({
            "gpus": n,
            "dedicated_head": d.head.name,
            "dedicated_cost": d.total_cost,
            "dedicated_score": round(d.score, 2),
            "dedicated_stability": round(d.stability, 2),
            "dedicated_perf": round(d.perf_index, 1),
            "dedicated_in_budget": d.total_cost <= budget,
            "gpu_head": g.head.name if g else None,
            "gpu_head_cost": g.total_cost if g else None,
            "gpu_head_score": round(g.score, 2) if g else None,
            "gpu_head_stability": round(g.stability, 2) if g else None,
            "gpu_head_perf": round(g.perf_index, 1) if g else None,
            "homogeneous_cost": hom.total_cost if hom else None,
            "homogeneous_score": round(hom.score, 2) if hom else None,
            "homogeneous_stability": round(hom.stability, 2) if hom else None,
            "homogeneous_perf": round(hom.perf_index, 1) if hom else None,
            "homogeneous_in_budget": (hom.total_cost <= budget) if hom else False,
            "delta_score": delta_score,
            "delta_stability": delta_stability,
            "delta_cost": delta_cost,
            "verdict": verdict,
        })
    return out
