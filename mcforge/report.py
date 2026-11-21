"""JSON + Markdown report for the Minecraft Forge cluster."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone

from .catalog import CONTINGENCY, STORAGE_OPTIONS
from .model import RAM_OPTIONS_PRICES, Candidate, WEIGHTS
from .search import Exploration, explore, select_winners


@dataclass(frozen=True)
class BomLine:
    label: str
    qty: int
    unit_usd: int

    @property
    def total_usd(self) -> int:
        return self.qty * self.unit_usd


def make_bom(c: Candidate) -> tuple[BomLine, ...]:
    devices = c.nodes + (1 if c.head else 0)
    storage_tb, storage_price = STORAGE_OPTIONS[c.storage_key]
    fabric = c.catalog.fabrics[c.fabric_key]
    lines = [
        BomLine(f"Node: {c.chassis.name} + {c.cpu.name}", c.nodes,
                c.chassis.base_price + c.cpu.price),
        BomLine(f"DDR5 kit, {c.ram_gb} GB", c.nodes, RAM_OPTIONS_PRICES[c.ram_gb][0]),
        BomLine(f"NVMe, {storage_tb} TB", c.nodes, storage_price),
    ]
    if c.raid:
        lines.append(BomLine("RAID 1 mirror NVMe", c.nodes, storage_price))
    if c.head:
        lines.append(BomLine(f"Head: {c.head.name}", 1, c.head.price))
    lines.append(BomLine(f"Switch: {fabric.name}", math.ceil(devices / 8), fabric.switch_price))
    lines.append(BomLine("Cables", devices, fabric.cable_cost))
    if c.adapter_count:
        lines.append(BomLine("Network adapters", c.adapter_count, fabric.adapter_cost))
    if c.ups:
        lines.append(BomLine(f"UPS, {c.ups_label}", 1, c.ups_cost))
    lines.append(BomLine(f"Contingency {CONTINGENCY:.0%}", 1, c.total_cost - c.subtotal))
    return tuple(lines)


def _summary(c: Candidate) -> dict:
    return {**c.summary(), "bom": [
        {"label": b.label, "qty": b.qty, "unit_usd": b.unit_usd, "total_usd": b.total_usd}
        for b in make_bom(c)
    ]}


def build_payload(budget: int = 6000, ex=None) -> dict:
    ex = ex or explore(budget)
    winners = select_winners(ex)
    best = winners[0][0] if winners else None
    value = max(ex.top, key=lambda c: c.total_instances / c.total_cost)
    tick_pool = [c for c in ex.top if c.total_instances >= 8] or ex.top
    tick = max(tick_pool, key=lambda c: (c.tick_index, c.total_instances))
    single = [c for c in ex.top if c.nodes == 1]
    single_best = max(single, key=lambda c: c.score) if single else None
    alternatives = {
        "best_value": _summary(value),
        "best_tick": _summary(tick),
        "single_node": _summary(single_best) if single_best else None,
    }
    payload = {
        "meta": {
            "name": "Mini-Tetra Minecraft Forge cluster study",
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "budget_usd": budget,
            "workload": "multiple Minecraft Forge server instances",
            "gpus_required": 0,
            "weights": WEIGHTS,
            "catalog": {
                "cpus": len(ex.catalog.cpus),
                "chassis": len(ex.catalog.chassis),
                "heads": len(ex.catalog.heads),
            },
        },
        "exploration": {
            "considered": ex.considered,
            "valid": ex.valid,
            "within_budget": ex.within_budget,
            "eligible": ex.eligible,
        },
        "winners": [
            {"rank": i + 1, "label": label, "rationale": why, **_summary(c)}
            for i, (c, label, why) in enumerate(winners)
        ],
        "alternatives": alternatives,
        "stats": ex.stats,
    }
    return payload


def _money(v: float | int | None) -> str:
    return "-" if v is None else f"${v:,.0f}"


def render_markdown(payload: dict) -> str:
    meta = payload["meta"]
    ex = payload["exploration"]
    out: list[str] = []
    out.append("# Minecraft Forge cluster — no GPU required")
    out.append("")
    out.append(
        f"Budget **{_money(meta['budget_usd'])}** · {ex['considered']:,} configurations "
        f"enumerated · {ex['within_budget']:,} inside budget · "
        f"**{meta['gpus_required']} GPUs**."
    )
    out.append("")
    out.append(
        "This study is for multiple **Minecraft Forge** servers. The tick loop is "
        "single-thread CPU work; each modpack needs ~8 GB RAM; world and chunk I/O "
        "wants NVMe. A discrete GPU does nothing for a dedicated server."
    )
    out.append("")
    out.append("| Pick | CPU × nodes | RAM/node | Instances | Tick | Stability | Cost |")
    out.append("|---|---|---:|---:|---:|---:|---:|")
    for w in payload["winners"]:
        out.append(
            f"| {w['label']} | {w['cpu']} × {w['nodes']} | {w['ram_gb_per_node']} GB | "
            f"{w['total_instances']} | {w['tick_index']:.0f} | {w['stability']:.2f} | "
            f"{_money(w['total_cost_usd'])} |"
        )
    out.append("")

    out.append("## Why no GPU?")
    out.append("")
    out.append(
        "Minecraft's server tick runs on one thread per dimension; Forge mods add CPU "
        "work, not shader work. A GPU helps the *client* render frames, not the "
        "server simulate ticks. The integrated GPU on every CPU here is enough for "
        "console access, and spending $500-2,000 on a card would take RAM, NVMe or a "
        "whole second node away from the cluster."
    )
    out.append("")

    for w in payload["winners"]:
        out.append(f"## {w['label']}: {w['cpu']} × {w['nodes']} — {_money(w['total_cost_usd'])}")
        out.append("")
        out.append(w["rationale"])
        out.append("")
        out.append(f"- Nodes: **{w['nodes']}× {w['chassis']}**")
        out.append(f"- Head: **{w['head']}**")
        out.append(
            f"- Memory: {w['ram_gb_per_node']} GB/node ({w['total_ram_gb']} GB total) · "
            f"storage {w['total_storage_tb']} TB NVMe"
        )
        out.append(
            f"- Forge instances: {w['instances_per_node']}/node → **{w['total_instances']} total**"
        )
        out.append(
            f"- Network: {w['fabric']} · RAID 1: {'yes' if w['raid'] else 'no'} · "
            f"UPS: {'yes' if w['ups'] else 'no'}"
        )
        out.append(f"- Peak draw: {w['peak_w']:.0f} W · idle: {w['idle_w']:.0f} W")
        out.append("")
        out.append("| Item | Qty | Unit | Total |")
        out.append("|---|---:|---:|---:|")
        for b in w["bom"]:
            out.append(f"| {b['label']} | {b['qty']} | {_money(b['unit_usd'])} | {_money(b['total_usd'])} |")
        out.append(f"| **Total** | | | **{_money(w['total_cost_usd'])}** |")
        out.append("")
        if w["stability_notes"]:
            out.append("Notes:")
            for note in w["stability_notes"]:
                out.append(f"- {note}")
            out.append("")

    out.append("## Software stack")
    out.append("")
    out.append(
        "- **Panel:** Pterodactyl (panel + Wings per node) or Crafty Controller. "
        "One allocation per Forge instance, 8 GB RAM and 2 threads each."
    )
    out.append(
        "- **Java:** Eclipse Temurin 21 for Minecraft 1.20.5+; keep the exact Forge "
        "and modpack versions pinned per instance."
    )
    out.append(
        "- **Storage:** world + mods + backups on NVMe. Run `restic` or the panel's "
        "backup job to the head/NAS; test a restore."
    )
    out.append(
        "- **Tuning:** Spark for tick profiling, Chunky for chunk pre-generation, "
        "`view-distance=8`, `simulation-distance=6`, and a modest player cap per pack."
    )
    out.append(
        "- **Network:** 2.5 GbE is plenty for players; the extra bandwidth is for "
        "backups and panel traffic. A Velocity proxy is optional if the packs share "
        "one player identity."
    )
    out.append("")

    alts = payload.get("alternatives") or {}
    if alts:
        out.append("## Alternatives")
        out.append("")
        out.append("| Option | Build | Instances | Tick | Cost |")
        out.append("|---|---|---:|---:|---:|")
        labels = {
            "best_value": "Best instances per dollar",
            "best_tick": "Best tick headroom",
            "single_node": "Single-node (simplest)",
        }
        for key, label in labels.items():
            a = alts.get(key)
            if not a:
                continue
            out.append(
                f"| {label} | {a['cpu']} × {a['nodes']}, {a['ram_gb_per_node']} GB | "
                f"{a['total_instances']} | {a['tick_index']:.0f} | "
                f"{_money(a['total_cost_usd'])} |"
            )
        out.append("")
    out.append("## Notes")
    out.append("")
    out.append(
        f"Scoring: capacity {WEIGHTS['capacity']:.0%}, tick {WEIGHTS['tick']:.0%}, "
        f"memory {WEIGHTS['memory']:.0%}, storage {WEIGHTS['storage']:.0%}, "
        f"stability {WEIGHTS['stability']:.0%}, value {WEIGHTS['value']:.0%}. "
        "Prices are Nov 2026 planning estimates with a 7% contingency."
    )
    out.append("")
    return "\n".join(out)
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(payload))


def write_reports(payload: dict, json_path: str, md_path: str) -> None:
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(payload))
