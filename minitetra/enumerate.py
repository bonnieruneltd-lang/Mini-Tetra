"""Exhaustive enumeration of the build space, plus the head-node analysis."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from .catalog import FABRICS, GPUS, HEADS, PLATFORMS, STORAGE
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
    alternatives: dict[str, Candidate] = field(default_factory=dict)
    stats: dict = field(default_factory=dict)
    group_best: dict[str, Candidate] = field(default_factory=dict)

    @property
    def best(self) -> Candidate:
        return self.top[0]


def explore(
    budget: int = 6000,
    gpu_price_scale: float = 1.0,
    keep: int = 2000,
) -> Exploration:
    ex = Exploration(budget=budget, gpu_price_scale=gpu_price_scale)
    main_heap: list[tuple[float, int, str, Candidate]] = []
    mini_heap: list[tuple[float, int, str, Candidate]] = []
    res_heap: list[tuple[float, float, int, str, Candidate]] = []
    by_fabric: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    group: dict[str, Candidate] = {}
    alternatives: dict[str, Candidate] = {}

    def keep_alt(key: str, candidate: Candidate) -> None:
        current = alternatives.get(key)
        if current is None or (candidate.score, -candidate.total_cost) > (current.score, -current.total_cost):
            alternatives[key] = candidate

    for platform_key, platform in PLATFORMS.items():
        gpu_keys = (platform.fixed_gpu,) if platform.fixed_gpu else platform.gpu_choices
        for gpu_key in gpu_keys:
            gpu = GPUS[gpu_key]
            if gpu.tdp_w > platform.max_gpu_tdp:
                continue
            for gpus_per_box in range(1, platform.gpu_slots + 1):
                if platform.fixed_gpu and gpus_per_box != 1:
                    continue
                for boxes in range(1, MAX_BOXES + 1):
                    if boxes * gpus_per_box > MAX_GPUS:
                        break
                    for fabric_key in FABRICS:
                        for storage_key in STORAGE:
                            for ups in (True, False):
                                for mode in ("dedicated", "homogeneous"):
                                    head_options = tuple(HEADS) if mode == "dedicated" else (None,)
                                    for head_key in head_options:
                                        for ha in ((False, True) if mode == "dedicated" else (False,)):
                                            ex.considered += 1
                                            c = evaluate(
                                                head_key, mode, platform_key, gpu_key,
                                                boxes, gpus_per_box, fabric_key,
                                                storage_key, ha, ups,
                                                gpu_price_scale, detailed=False,
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

                                            if ups:
                                                if gpu.used or platform.used:
                                                    keep_alt("value_used", c)
                                                if (c.head_mode == "homogeneous"
                                                        and not gpu.used and gpu.vram_gb >= 16):
                                                    keep_alt("no_separate_head", c)
                                                if (gpu.vram_gb >= 24 and boxes <= 3
                                                        and c.head_mode == "dedicated"
                                                        and not HEADS[c.head_key].has_gpu):
                                                    keep_alt("vram_first", c)

                                            gkey = f"{gpu_key}|{c.gpus_total}|{fabric_key}|{mode}"
                                            prev = group.get(gkey)
                                            if prev is None or (c.score, -c.total_cost) > (prev.score, -prev.total_cost):
                                                group[gkey] = c

                                            # Podium baseline: UPS, new hardware with
                                            # warranty, and >=16 GB per GPU so Flux dev
                                            # fits without aggressive offload.
                                            if (not ups or gpu.used or platform.used
                                                    or gpu.vram_gb < 16):
                                                continue
                                            ex.eligible += 1
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
    ex.alternatives = alternatives
    ex.group_best = group
    ex.stats = {
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
) -> list[dict]:
    """Every head option for one fixed worker fleet, plus the no-separate-head case."""
    rows: list[dict] = []
    for head_key, head in HEADS.items():
        c = evaluate(head_key, "dedicated", platform_key, gpu_key, boxes, gpus_per_box,
                     fabric_key, storage_key, False, ups, gpu_price_scale)
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
                   fabric_key, storage_key, False, ups, gpu_price_scale)
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
) -> list[dict]:
    """Three ways to place the head at an equal GPU count.

    1. dedicated non-GPU head  2. head with its own GPU  3. a worker as head.
    """
    out: list[dict] = []
    for n in gpu_counts:
        ded_all = [
            (key, c) for key in HEADS for c in (
                evaluate(key, "dedicated", platform_key, gpu_key, n, 1, fabric_key,
                         storage_key, False, ups, gpu_price_scale),
            ) if c is not None
        ]
        ded = [(k, c) for k, c in ded_all if not HEADS[k].has_gpu]
        gpu_heads = [(k, c) for k, c in ded_all if HEADS[k].has_gpu]
        hom = evaluate(None, "homogeneous", platform_key, gpu_key, n, 1, fabric_key,
                       storage_key, False, ups, gpu_price_scale)
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
