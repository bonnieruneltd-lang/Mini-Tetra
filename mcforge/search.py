"""Enumerate Minecraft Forge cluster configurations within a budget."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from .catalog import BASE_CATALOG, Catalog
from .model import Candidate, evaluate

MAX_NODES = 6


@dataclass
class Exploration:
    budget: int
    considered: int = 0
    valid: int = 0
    within_budget: int = 0
    eligible: int = 0
    top: list[Candidate] = field(default_factory=list)
    resilient: list[Candidate] = field(default_factory=list)
    power: list[Candidate] = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    catalog: Catalog = BASE_CATALOG

    @property
    def best(self) -> Candidate:
        return self.top[0]


def explore(budget: int = 6000, keep: int = 500, catalog: Catalog | None = None) -> Exploration:
    cat = catalog or BASE_CATALOG
    ex = Exploration(budget=budget, catalog=cat)
    main: list[tuple[float, int, str, Candidate]] = []
    res: list[tuple[float, float, int, str, Candidate]] = []
    power: list[tuple[int, float, int, str, Candidate]] = []

    for cpu_key in cat.cpus:
        for chassis_key, chassis in cat.chassis.items():
            if cat.cpus[cpu_key].socket not in chassis.sockets:
                continue
            for ram_gb, ram_slots in ((32, 2), (64, 2), (96, 2),
                                      (128, 4), (192, 4), (256, 8)):
                if ram_slots > chassis.ram_slots or ram_gb > chassis.max_ram_gb:
                    continue
                for storage_key in ("1tb", "2tb", "4tb", "8tb"):
                    for nodes in range(1, MAX_NODES + 1):
                        for head_key in (None, "n100", "n305", "um890", "ms01", "used_sff"):
                            for fabric_key in cat.fabrics:
                                for raid in (False, True):
                                    for ups in (True, False):
                                        ex.considered += 1
                                        c = evaluate(
                                            cpu_key, chassis_key, ram_gb, storage_key,
                                            nodes, head_key, fabric_key, raid, ups,
                                            catalog=cat,
                                        )
                                        if c is None:
                                            continue
                                        ex.valid += 1
                                        if c.total_cost > budget:
                                            continue
                                        ex.within_budget += 1
                                        if not ups or head_key is None:
                                            continue
                                        ex.eligible += 1
                                        item = (c.score, -c.total_cost, c.signature, c)
                                        if len(main) < keep:
                                            heapq.heappush(main, item)
                                        elif item[:3] > main[0][:3]:
                                            heapq.heapreplace(main, item)
                                        if (nodes >= 3 and head_key is not None
                                                and c.stability >= 8.0):
                                            ritem = (c.score, c.stability, -c.total_cost,
                                                     c.signature, c)
                                            if len(res) < 50:
                                                heapq.heappush(res, ritem)
                                            elif ritem[:4] > res[0][:4]:
                                                heapq.heapreplace(res, ritem)
                                        if head_key is not None and c.tick_index >= 65:
                                            pitem = (c.total_instances, c.tick_index,
                                                     -c.total_cost, c.signature, c)
                                            if len(power) < 50:
                                                heapq.heappush(power, pitem)
                                            elif pitem[:4] > power[0][:4]:
                                                heapq.heapreplace(power, pitem)

    ex.top = [i[3] for i in sorted(main, key=lambda x: (-x[0], -x[1], x[2]))]
    ex.resilient = [i[4] for i in sorted(res, key=lambda x: (-x[0], -x[1], -x[2], x[3]))]
    ex.power = [i[4] for i in sorted(power, key=lambda x: (-x[0], -x[1], -x[2], x[3]))]
    ex.stats = {
        "cpus": len(cat.cpus),
        "chassis": len(cat.chassis),
        "heads": len(cat.heads),
        "max_instances": max((c.total_instances for c in ex.power), default=0),
    }
    return ex


def select_winners(ex: Exploration) -> list[tuple[Candidate, str, str]]:
    if not ex.top:
        return []
    picks: list[tuple[Candidate, str, str]] = []
    best = ex.top[0]
    picks.append((best, "Best overall",
                  "Highest weighted score: instance capacity, tick performance and stability."))
    chosen = {best.signature}

    power = next((c for c in ex.power if c.signature not in chosen), None)
    if power:
        picks.append((power, "Most instances",
                      "Maximum Forge instances while keeping estimated tick index >= 65."))
        chosen.add(power.signature)

    res_pool = [c for c in ex.resilient if c.signature not in chosen
                and c.score >= best.score * 0.85]
    if res_pool:
        res = max(res_pool, key=lambda c: (c.score, c.stability, -c.total_cost))
        picks.append((res, "Most resilient",
                      "Best score among 3+ node builds with a dedicated head and stability >= 8."))
        chosen.add(res.signature)

    for c in ex.top:
        if len(picks) >= 3:
            break
        if c.signature not in chosen:
            picks.append((c, "Runner-up", "Next-best distinct topology."))
            chosen.add(c.signature)
    picks.sort(key=lambda item: -item[0].score)
    return picks[:3]
