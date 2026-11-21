"""CLI: python -m mcforge.cli evaluate"""

from __future__ import annotations

import argparse
import os

from .report import build_payload, write_reports
from .search import explore, select_winners


def cmd_evaluate(args: argparse.Namespace) -> None:
    os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.markdown) or ".", exist_ok=True)
    if args.fast:
        ex = explore(args.budget)
        print(f"considered={ex.considered:,} valid={ex.valid:,} "
              f"within_budget={ex.within_budget:,} max_instances={ex.stats['max_instances']}")
        for c, label, _ in select_winners(ex):
            print(f"[{label}] {c.cpu.name} x{c.nodes} | {c.total_instances} instances | "
                  f"{c.total_ram_gb} GB | ${c.total_cost:,} | tick {c.tick_index:.0f}")
        return
    payload = build_payload(args.budget)
    write_reports(payload, args.json, args.markdown)
    ex = payload["exploration"]
    print(f"considered={ex['considered']:,} valid={ex['valid']:,} "
          f"within_budget={ex['within_budget']:,} GPUs=0")
    for w in payload["winners"]:
        print(f"#{w['rank']} [{w['label']}] {w['cpu']} x{w['nodes']} | "
              f"{w['total_instances']} instances | ${w['total_cost_usd']:,}")
    print(f"wrote {args.json} and {args.markdown}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcforge")
    sub = parser.add_subparsers(dest="command", required=True)
    ev = sub.add_parser("evaluate", help="search Minecraft Forge cluster builds")
    ev.add_argument("--budget", type=int, default=6000)
    ev.add_argument("--json", default="out/mcforge.json")
    ev.add_argument("--markdown", default="reports/minecraft-forge.md")
    ev.add_argument("--fast", action="store_true")
    ev.set_defaults(func=cmd_evaluate)
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
