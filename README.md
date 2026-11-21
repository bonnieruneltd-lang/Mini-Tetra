# Mini-Tetra — a $6k multi-Forge mini-PC cluster

A reproducible design study for a small cluster that serves **Stable Diffusion WebUI
Forge** from several GPUs behind one queue. The repo contains the hardware catalog,
an exhaustive configurator, the scoring model, tests, and the generated report.

The configurator does not hand-pick a build. It enumerates every valid combination
of head node, worker chassis, GPU, node count, network fabric, storage strategy,
UPS and head redundancy, throws out anything that violates budget, power, chassis
or software constraints, scores what remains, and then selects three builds with
different design goals.

## TL;DR (Nov 2026 street prices)

| Pick | Build | GPUs / VRAM | Cost | Peak | Stability | Score |
|---|---|---|---:|---:|---:|---:|
| **Best overall** | 2x dual-GPU mATX nodes + MS-01 head | 4x RTX 5060 Ti 16 GB / 64 GB | **$5,921** | 1,104 W | 8.27/10 | 71.5 |
| **Most resilient** | 3x single-GPU ITX nodes + MS-01 head | 3x RTX 5060 Ti 16 GB / 48 GB | **$5,673** | 1,017 W | 8.69/10 | 67.4 |
| **Best pure mini-PC** | 3x GMKtec K8 Plus + OCuLink docks + MS-01 head | 3x RTX 5060 Ti 16 GB / 48 GB | **$5,384** | 906 W | 8.12/10 | 64.2 |

All three use the same GPU, 2.5 GbE, a shared 4 TB NVMe model cache, a correctly
sized UPS, and a dedicated non-GPU head. They trade density, blast radius and
physical size against each other.

**Should the main PC be different?** Yes — different by *role*, not by GPU. At an
equal GPU count, a dedicated non-GPU head costs about $900 more and adds about
2.3 stability points; it wins on score at every fleet size the budget allows.
A GPU in the head is cheaper per GPU (it reuses the chassis) but drops stability
by ~1.5 points and puts the scheduler inside a GPU failure domain. Buy it only if
you want an interactive seat on the same box.

## Quick start

```bash
make evaluate   # out/report.json, reports/best3.md, out/candidates.csv, reports/bom.csv
make test       # 19 invariants
make fast       # console summary only (~3 s)
```

Other useful invocations:

```bash
python3 -m minitetra.cli evaluate --budget 5000
python3 -m minitetra.cli evaluate --gpu-price-shock 1.15
python3 -m minitetra.cli evaluate --budget 6000 --top 3
python3 -m minitetra.cli head-check --platform itx_sff --gpu rtx5060ti_16
```

## What was considered

| Dimension | Options |
|---|---|
| Head node | 9: N100 / N305 / used SFF / SER8 / UM890 / MS-01 / NUC 13 Extreme / 2 workstation heads |
| Worker chassis | 12: ITX SFF, dual-GPU mATX, MS-01+USB4, UM890+OCuLink, SER8+USB4, K8 Plus+OCuLink, NUCXi7, HX99G, HX100G, Titan 18 Pro, NUC 13 Extreme, used EliteDesk |
| GPU | 23: RTX 3060 through 5090, A4000/A5000/L4/2000 Ada, RX 7900 XTX, Arc A770, mobile 3070/4090/6600M/6650M |
| Fleet | 1–6 chassis, 1–8 GPUs, 1–2 GPUs per chassis |
| Fabric | 1 GbE, 2.5 GbE, 10 GbE SFP+ |
| Storage | per-node copies, 4 TB NVMe share, 8 TB mirrored NAS |
| Resilience | single or HA head, UPS sized to 1.25x peak |

Full run: **220,248 combinations considered**, 181,044 valid after physics and
compatibility checks, 73,449 inside $6,000, 14,400 eligible for the podium
(new hardware, UPS, ≥16 GB per GPU).

## Scoring model

| Component | Weight | What it captures |
|---|---:|---|
| Throughput | 32% | aggregate GPU index × fabric/scheduler/orchestration factors |
| Capability | 18% | per-GPU VRAM for Flux/SDXL + total cluster VRAM |
| Stability | 22% | CUDA path, head separation, eGPU links, thermals, PSU headroom, fault domain, UPS, shared storage, scheduler capacity |
| Efficiency | 8% | perf per watt at peak |
| Value | 12% | perf per dollar |
| Expandability | 8% | M.2/PCIe slots and chassis serviceability |

Hard constraints: ≤$6,000 including 7% contingency; ≤1,800 W peak (15 A circuit);
GPU TDP within chassis/PSU limits; only GPUs the chassis can physically host;
≥16 GB per GPU for the podium; new hardware for the podium.

Run `--gpu-price-shock 1.15` to see the ranking under a 15% GPU price rise, and
read the weight-sensitivity section of the report to see how the podium moves
under throughput-first, stability-first and value-first weights.

## Repository layout

```
minitetra/
  catalog.py     hardware catalog and price basis
  model.py       cost, power, throughput, stability and score
  enumerate.py   exhaustive search, podium selection, head analysis
  report.py      JSON + Markdown + CSV report
  cli.py         command line entry point
tests/           invariants (stdlib unittest, no dependencies)
deploy/
  compose.worker.yml  one Forge API per GPU, NFS mounts, healthcheck
  Caddyfile           TLS/auth reverse proxy for SwarmUI
  README.md           host prep, NFS, NUT and smoke-test steps
reports/
  best3.md       generated podium with BOMs and head analysis
  bom.csv        BOM for the three picks, one row per line item
  cluster-design.md  build guide, software stack and ops runbook
out/
  report.json    full machine-readable result
  candidates.csv top 200 scored candidates for spreadsheet review
```

## Deploy

`deploy/` contains the templates the build guide refers to: a worker Compose file
(one Forge API per GPU, read-only NFS models, healthcheck), a Caddyfile for
SwarmUI with auth/TLS, and a step-by-step host/NUT guide. Pin your Forge image by
digest before production; the template only assumes the image honours `PORT` and
`COMMANDLINE_ARGS`.

## Caveats

Prices are planning estimates, not live quotes. GPU street prices in particular
move with memory supply; the 7% contingency and the price-shock run exist for
that reason. The throughput index is a comparison tool, not a benchmark. Verify
clearances, power connectors (the 5060 Ti may be 1x or 2x 8-pin depending on the
board partner), and BIOS support before ordering.
