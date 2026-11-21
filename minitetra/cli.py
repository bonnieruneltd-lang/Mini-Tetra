"""Command line entry point: python -m minitetra.cli evaluate"""

from __future__ import annotations

import argparse
import os

from .enumerate import explore, select_winners
from .report import build_payload, write_reports


def cmd_evaluate(args: argparse.Namespace) -> None:
    os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.markdown) or ".", exist_ok=True)

    if args.fast:
        ex = explore(args.budget, gpu_price_scale=args.gpu_price_shock,
                     keep=args.keep)
        winners = select_winners(ex, args.top)
        print(f"considered={ex.considered:,} valid={ex.valid:,} "
              f"within_budget={ex.within_budget:,}")
        for rank, (c, label, why) in enumerate(winners, 1):
            print(f"\n#{rank} [{label}] score={c.score:.2f} cost=${c.total_cost:,} "
                  f"perf={c.perf_index:.0f} stability={c.stability:.2f}")
            print(f"    {c.gpu.name} x{c.gpus_total} | {c.boxes}x {c.platform.name}")
            print(f"    head: {c.head.name if c.head else 'worker-as-head'}")
            print(f"    {why}")
        return

    payload = build_payload(args.budget, args.gpu_price_shock, args.top,
                            args.csv, args.bom_csv)
    write_reports(payload, args.json, args.markdown)
    ex = payload["exploration"]
    print(f"considered={ex['considered']:,} valid={ex['valid']:,} "
          f"within_budget={ex['within_budget']:,}")
    for w in payload["winners"]:
        print(f"#{w['rank']} score={w['score']:.2f} cost=${w['total_cost_usd']:,} "
              f"{w['gpu']} x{w['gpus_total']} | {w['boxes']}x {w['platform']}")
    print(f"\nwrote {args.json}, {args.markdown}, {args.csv} and {args.bom_csv}")


def cmd_head(args: argparse.Namespace) -> None:
    from .enumerate import head_mode_comparison

    rows = head_mode_comparison(args.platform, args.gpu, args.fabric, args.storage)
    for row in rows:
        print(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="minitetra")
    sub = parser.add_subparsers(dest="command", required=True)

    ev = sub.add_parser("evaluate", help="enumerate the build space and write reports")
    ev.add_argument("--budget", type=int, default=6000)
    ev.add_argument("--json", default="out/report.json")
    ev.add_argument("--markdown", default="reports/best3.md")
    ev.add_argument("--csv", default="out/candidates.csv")
    ev.add_argument("--bom-csv", default="reports/bom.csv")
    ev.add_argument("--top", type=int, default=3)
    ev.add_argument("--keep", type=int, default=2000)
    ev.add_argument("--gpu-price-shock", type=float, default=1.0)
    ev.add_argument("--fast", action="store_true", help="skip reports and scenarios")
    ev.set_defaults(func=cmd_evaluate)

    hd = sub.add_parser("head-check", help="compare head options for one fleet")
    hd.add_argument("--platform", default="itx_sff")
    hd.add_argument("--gpu", default="rtx5060ti_16")
    hd.add_argument("--fabric", default="2.5gbe")
    hd.add_argument("--storage", default="shared_nvme")
    hd.set_defaults(func=cmd_head)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
