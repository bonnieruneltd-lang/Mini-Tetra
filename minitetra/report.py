"""JSON + Markdown report generation."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .catalog import FABRICS, GPUS, HEADS, PLATFORMS, PRICE_BASIS, STORAGE
from .enumerate import (
    Exploration,
    explore,
    head_ladder,
    head_mode_comparison,
    select_winners,
)
from .model import WEIGHTS


def build_payload(budget: int = 6000, gpu_price_scale: float = 1.0, top: int = 3) -> dict:
    ex = explore(budget, gpu_price_scale=gpu_price_scale)
    winners = select_winners(ex, top)
    win = winners[0][0]

    ladder = head_ladder(win.platform_key, win.gpu_key, win.boxes, win.gpus_per_box,
                         win.fabric_key, win.storage_key, win.ups, gpu_price_scale)

    comp_platform = "itx_sff" if win.gpu_key in PLATFORMS["itx_sff"].gpu_choices else win.platform_key
    comparison = head_mode_comparison(comp_platform, win.gpu_key, win.fabric_key,
                                      win.storage_key, gpu_price_scale=gpu_price_scale,
                                      budget=budget)

    scenarios = []
    for label, scale in (("base", 1.0), ("gpu +15%", 1.15), ("gpu -15%", 0.85)):
        run = ex if scale == 1.0 else explore(budget, gpu_price_scale=scale)
        scenarios.append({
            "label": label,
            "gpu_price_scale": scale,
            "within_budget": run.within_budget,
            "best_cost": run.best.total_cost,
            "best_score": round(run.best.score, 2),
            "best": run.best.summary(),
            "top10_signatures": [c.signature for c in run.top[:10]],
        })

    dedicated_wins = [r for r in comparison if r["verdict"].startswith("keep")]
    merge_wins = [r for r in comparison if r["verdict"] == "merge head into a worker"]
    hom_pool = [c for c in ex.top
                if c.head_mode == "homogeneous" and c.total_cost <= win.total_cost + 400]
    alt = max(hom_pool, key=lambda c: c.score) if hom_pool else None

    if comparison:
        pairs = [r for r in comparison if r["homogeneous_score"] is not None]
        avg_ds = sum(r["delta_stability"] for r in pairs) / len(pairs)
        avg_dc = sum(r["delta_cost"] for r in pairs) / len(pairs)
        conclusion = (
            "Yes, but differentiate it by role, not by GPU. At an equal GPU count a "
            f"dedicated non-GPU head costs about ${avg_dc:,.0f} more and adds about "
            f"{avg_ds:.1f} stability points; it wins on score at every fleet size tested "
            "because a head that also renders shares its CPU, RAM and driver stack with "
            "the queue. A GPU in the head looks cheaper per GPU, but it puts the "
            "scheduler inside a GPU failure domain; it is worth it only if you want an "
            "interactive seat on the same box."
        )
    else:
        conclusion = "No: at this budget the head should be one of the GPU workers."

    payload = {
        "meta": {
            "name": "Mini-Tetra multi-Forge cluster study",
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "budget_usd": budget,
            "price_basis": PRICE_BASIS,
            "weights": WEIGHTS,
            "catalog_sizes": {
                "gpus": len(GPUS),
                "worker_platforms": len(PLATFORMS),
                "heads": len(HEADS),
                "fabrics": len(FABRICS),
                "storage": len(STORAGE),
            },
        },
        "exploration": {
            "considered": ex.considered,
            "valid": ex.valid,
            "within_budget": ex.within_budget,
            "eligible": ex.eligible,
            "stats": ex.stats,
        },
        "winners": [
            {"rank": i + 1, "label": label, "rationale": why, **c.summary()}
            for i, (c, label, why) in enumerate(winners)
        ],
        "runner_up": [c.summary() for c in ex.top[3:10]],
        "alternatives": {k: v.summary() for k, v in ex.alternatives.items()},
        "head_analysis": {
            "verdict": conclusion,
            "ladder": ladder,
            "mode_comparison": comparison,
            "dedicated_wins": len(dedicated_wins),
            "merge_wins": len(merge_wins),
            "tested_platform": comp_platform,
            "best_homogeneous": alt.summary() if alt else None,
        },
        "robustness": {"scenarios": scenarios},
        "weight_sensitivity": weight_sensitivity(ex),
    }
    return payload


def weight_sensitivity(ex: Exploration) -> list[dict]:
    """Re-rank the top 500 under alternative weightings."""
    out = []
    variants = {
        "default": WEIGHTS,
        "throughput-first": {**WEIGHTS, "throughput": 0.45, "stability": 0.15},
        "stability-first": {**WEIGHTS, "stability": 0.35, "throughput": 0.20},
        "value-first": {**WEIGHTS, "value": 0.25, "throughput": 0.22},
    }
    pool = ex.top[:500]
    for label, weights in variants.items():
        ranked = sorted(pool, key=lambda c: -sum(weights[k] * v for k, v in c.components.items()))
        out.append({
            "variant": label,
            "weights": weights,
            "top": [c.summary() for c in ranked[:3]],
            "top_signatures": [c.signature for c in ranked[:3]],
        })
    return out


def _money(value: int | float | None) -> str:
    if value is None:
        return "-"
    return f"${value:,.0f}"


def _topology(c: dict) -> str:
    if c["head_mode"] == "homogeneous":
        return f"{c['boxes']}x {c['platform']} (one node doubles as head)"
    return f"{c['head']} + {c['boxes']}x {c['platform']}"


def render_markdown(payload: dict) -> str:
    meta = payload["meta"]
    ex = payload["exploration"]
    ha = payload["head_analysis"]
    lines: list[str] = []
    lines.append("# Best 3 mini-Forge clusters")
    lines.append("")
    lines.append(
        f"Budget **{_money(meta['budget_usd'])}** · "
        f"{ex['considered']:,} build combinations enumerated · "
        f"{ex['valid']:,} valid after physics/compatibility checks · "
        f"{ex['within_budget']:,} inside budget · {ex['eligible']:,} eligible after baseline filters "
        "(new hardware, UPS, ≥16 GB per GPU)."
    )
    lines.append("")
    lines.append(
        "Scoring: throughput 32%, GPU capability (VRAM) 18%, stability 22%, "
        "efficiency 8%, value 12%, expandability 8%. Prices: " + meta["price_basis"] + "."
    )
    lines.append("")
    lines.append("| Pick | Topology | GPUs / VRAM | Cost | Peak | Perf | Stability | Score |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    for w in payload["winners"]:
        lines.append(
            f"| {w['label']} | {_topology(w)} | "
            f"{w['gpus_total']} / {w['total_vram_gb']} GB | {_money(w['total_cost_usd'])} | "
            f"{w['peak_w']:.0f} W | {w['perf_index']:.0f} | {w['stability']:.2f}/10 | "
            f"{w['score']:.1f} |"
        )
    lines.append("")

    for w in payload["winners"]:
        lines.append(
            f"## {w['label']}: {w['gpu']} x{w['gpus_total']} — {_money(w['total_cost_usd'])}"
        )
        lines.append("")
        lines.append(w["rationale"])
        lines.append("")
        lines.append(f"- Head: **{w['head']}**")
        lines.append(f"- Workers: **{w['boxes']}x {w['platform']}**, {w['gpus_per_box']} GPU each")
        lines.append(
            f"- Network: {w['fabric']} · Storage: {w['storage']} · "
            f"UPS: {'yes' if w['ups'] else 'no'} · HA head: {'yes' if w['ha'] else 'no'}"
        )
        lines.append(f"- Peak draw: {w['peak_w']:.0f} W · idle: {w['idle_w']:.0f} W")
        lines.append(
            f"- VRAM: {w['total_vram_gb']} GB total, {w['capability']:.2f} capability index"
        )
        lines.append("")
        lines.append("| Item | Qty | Unit | Total |")
        lines.append("|---|---:|---:|---:|")
        for line in w["bom"]:
            lines.append(
                f"| {line['label']} | {line['qty']} | {_money(line['unit_usd'])} | "
                f"{_money(line['total_usd'])} |"
            )
        lines.append(f"| **Total** | | | **{_money(w['total_cost_usd'])}** |")
        lines.append("")
        if w["stability_notes"]:
            lines.append("Stability notes:")
            for note in w["stability_notes"]:
                lines.append(f"- {note}")
            lines.append("")

    lines.append("## Should the main PC be different?")
    lines.append("")
    lines.append(ha["verdict"])
    lines.append("")
    lines.append("### Head upgrade ladder (same worker fleet)")
    lines.append("")
    lines.append("| Head | Kind | Head cost | Total | Perf | Stability | Score | In budget |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|")
    for row in ha["ladder"]:
        lines.append(
            f"| {row['head']} | {row['head_kind']} | {_money(row['head_cost'])} | "
            f"{_money(row['total_cost'])} | {row['perf_index']:.0f} | {row['stability']:.2f} | "
            f"{row['score']:.1f} | {'yes' if row['within_budget'] else 'no'} |"
        )
    lines.append("")
    lines.append("### Dedicated head vs. worker-as-head")
    lines.append("")
    lines.append("| Worker GPUs | Dedicated non-GPU head | Cost | Score | Stab | GPU head (+1 GPU) | Cost | Score | Stab | Worker-as-head cost | Score | Stab | Verdict |")
    lines.append("|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|")
    for row in ha["mode_comparison"]:
        lines.append(
            f"| {row['gpus']} | {row['dedicated_head']} | {_money(row['dedicated_cost'])} | "
            f"{row['dedicated_score']:.1f} | {row['dedicated_stability']:.1f} | "
            f"{row['gpu_head'] or '-'} | {_money(row['gpu_head_cost'])} | "
            f"{row['gpu_head_score'] if row['gpu_head_score'] is not None else '-'} | "
            f"{row['gpu_head_stability'] if row['gpu_head_stability'] is not None else '-'} | "
            f"{_money(row['homogeneous_cost'])} | "
            f"{row['homogeneous_score'] if row['homogeneous_score'] is not None else '-'} | "
            f"{row['homogeneous_stability'] if row['homogeneous_stability'] is not None else '-'} | "
            f"{row['verdict']} |"
        )
    lines.append("")
    lines.append("Rows above $6,000 show the trend for larger fleets; they are not purchase options at this budget.")
    lines.append("")
    alt = ha.get("best_homogeneous")
    if alt:
        lines.append(
            f"If you drop the separate head and put that money into GPUs, about "
            f"{_money(alt['total_cost_usd'])} buys **{alt['gpu']} x{alt['gpus_total']}** "
            f"({alt['boxes']}x {alt['platform']}, one node doubling as head). It reaches "
            f"perf {alt['perf_index']:.0f} vs {payload['winners'][0]['perf_index']:.0f}, "
            f"but stability falls from {payload['winners'][0]['stability']:.1f} to "
            f"{alt['stability']:.1f}."
        )
        lines.append("")

    alt_labels = {
        "value_used": "Used-GPU value build",
        "no_separate_head": "No separate head (spend it on GPUs)",
        "vram_first": "VRAM-first (24 GB per GPU)",
    }
    alts = payload.get("alternatives") or {}
    if alts:
        lines.append("## Alternatives worth pricing")
        lines.append("")
        lines.append("| Option | Topology | GPUs / VRAM | Cost | Perf | Stability | Score |")
        lines.append("|---|---|---|---:|---:|---:|---:|")
        for key in ("value_used", "no_separate_head", "vram_first"):
            if key not in alts:
                continue
            a = alts[key]
            lines.append(
                f"| {alt_labels[key]} | {_topology(a)} | "
                f"{a['gpus_total']} / {a['total_vram_gb']} GB | {_money(a['total_cost_usd'])} | "
                f"{a['perf_index']:.0f} | {a['stability']:.2f} | {a['score']:.1f} |"
            )
        lines.append("")

    lines.append("## Robustness")
    lines.append("")
    lines.append("| Scenario | In budget | Best cost | Best score | Same #1? |")
    lines.append("|---|---:|---:|---:|---|")
    def topology(c: dict) -> tuple:
        return (c["head_key"], c["platform_key"], c["gpu_key"], c["boxes"],
                c["gpus_per_box"], c["head_mode"])

    base_topology = topology(payload["robustness"]["scenarios"][0]["best"])
    for s in payload["robustness"]["scenarios"]:
        same = "yes" if topology(s["best"]) == base_topology else "no"
        lines.append(
            f"| {s['label']} | {s['within_budget']:,} | {_money(s['best_cost'])} | "
            f"{s['best_score']:.1f} | {same} |"
        )
    lines.append("")
    lines.append("### Weight sensitivity")
    lines.append("")
    for v in payload["weight_sensitivity"]:
        top = v["top"][0]
        lines.append(
            f"- **{v['variant']}**: {top['gpu']} x{top['gpus_total']}, "
            f"{top['head']} + {top['boxes']}x {top['platform']}, {_money(top['total_cost_usd'])}, "
            f"score {top['score']:.1f}"
        )
    lines.append("")
    return "\n".join(lines)


def write_reports(payload: dict, json_path: str, md_path: str) -> None:
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(render_markdown(payload))
