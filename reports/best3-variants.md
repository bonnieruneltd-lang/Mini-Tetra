# Best 3 mini-Forge clusters — variant study

Budget **$6,000** · 1817 additional models · 1,942,272 build combinations enumerated · 1,041,264 valid after physics/compatibility checks · 326,089 inside budget · 109,248 eligible after baseline filters (new hardware, UPS, ≥16 GB per GPU).

Scoring: throughput 32%, GPU capability (VRAM) 18%, stability 22%, efficiency 8%, value 12%, expandability 8%. Prices: USD street/retail estimates, Nov 2026, qty 1, tax/shipping excluded; assume +/-15% and re-run with --gpu-price-shock to test the ranking.

| Pick | Topology | Workers / total VRAM | Cost | Peak | Perf | Stability | Score |
|---|---|---|---:|---:|---:|---:|---:|
| Best overall | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1600 W, 4 GPU | 3 / 48 GB | $5,763 | 1073 W | 856 | 7.16/10 | 73.4 |
| Best raw power | Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB) + 1x Custom OPEN8 PC — Ryzen 5 5600, 32 GB, 1 TB, 1600 W, 8 GPU | 3 / 48 GB | $5,952 | 1102 W | 998 | 6.05/10 | 71.9 |
| Most resilient | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 3x Custom MATX2 PC — Ryzen 5 5600, 16 GB, 1 TB, 650 W, 1 GPU | 3 / 48 GB | $5,727 | 945 W | 499 | 8.88/10 | 68.2 |

## Best power

| Metric | Build | Workers / total VRAM | Cost | Perf | Perf/W | Stability |
|---|---|---|---:|---:|---:|---:|
| Best raw power | Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB) + 1x Custom OPEN8 PC — Ryzen 5 5600, 32 GB, 1 TB, 1600 W, 8 GPU | 3 / 48 GB | $5,952 | 998 | 0.91 | 6.05 |
| Best efficiency | Workstation head: ITX + RTX 5080 16 GB + 1x Custom MATX2 PC — Ryzen 5 5600, 32 GB, 1 TB, 650 W, 2 GPU | 2 / 48 GB | $5,991 | 1007 | 1.06 | 4.41 |
| Best power at stability ≥ 8.5 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 3x Minisforum NUCXi9 (i9-13900H + RTX 3080 Mobile 16 GB) | 3 / 48 GB | $5,887 | 570 | 0.60 | 8.55 |

## Best overall: GeForce RTX 5070 Ti 16 GB x3 — $5,763

Highest weighted score after the full variant search.

- Head: **Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+)**
- Workers: **1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1600 W, 4 GPU**, 3 GPU per chassis
- Network: 2.5 GbE (8-port 2.5G switch) · Storage: 4 TB NVMe model cache in head, exported over NFS/SMB · UPS: yes · HA head: no
- Peak draw: 1073 W · idle: 120 W
- VRAM: 48 GB total, 0.81 capability index

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Head node: Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | 1 | $840 | $840 |
| Worker chassis/CPU/RAM/SSD: Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1600 W, 4 GPU | 1 | $1,240 | $1,240 |
| GPU: GeForce RTX 5070 Ti 16 GB | 3 | $860 | $2,580 |
| Network: 2.5 GbE (8-port 2.5G switch) - switch(es) | 1 | $120 | $120 |
| Network: cables/DACs | 2 | $8 | $16 |
| Storage: 4 TB NVMe model cache in head, exported over NFS/SMB | 1 | $260 | $260 |
| UPS, 2000 VA / 1600 W line-interactive | 1 | $330 | $330 |
| Contingency 7% (tax/shipping/price drift) | 1 | $377 | $377 |
| **Total** | | | **$5,763** |

Stability notes:
- head has 10G + 3x M.2: queue, NFS and cache do not fight for I/O
- multiple GPUs share one PSU per chassis
- large fault domain: one node failure removes 3/3 of the GPUs
- PSU above 90% of rating at peak: shutdown risk
- UPS: prevents checkpoint/queue corruption on brownouts

## Best raw power: GeForce RTX 4080 SUPER 16 GB — Palit GamingPro x3 — $5,952

Highest aggregate GPU index with stability >= 6.0; this is the build to pick when throughput matters more than uptime.

- Head: **Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB)**
- Workers: **1x Custom OPEN8 PC — Ryzen 5 5600, 32 GB, 1 TB, 1600 W, 8 GPU**, 3 GPU per chassis
- Network: 2.5 GbE (8-port 2.5G switch) · Storage: 4 TB NVMe model cache in head, exported over NFS/SMB · UPS: yes · HA head: no
- Peak draw: 1102 W · idle: 134 W
- VRAM: 48 GB total, 0.81 capability index

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Head node: Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB) | 1 | $400 | $400 |
| Worker chassis/CPU/RAM/SSD: Custom OPEN8 PC — Ryzen 5 5600, 32 GB, 1 TB, 1600 W, 8 GPU | 1 | $1,125 | $1,125 |
| GPU: GeForce RTX 4080 SUPER 16 GB — Palit GamingPro | 3 | $1,104 | $3,312 |
| Network: 2.5 GbE (8-port 2.5G switch) - switch(es) | 1 | $120 | $120 |
| Network: cables/DACs | 2 | $8 | $16 |
| Storage: 4 TB NVMe model cache in head, exported over NFS/SMB | 1 | $260 | $260 |
| UPS, 2000 VA / 1600 W line-interactive | 1 | $330 | $330 |
| Contingency 7% (tax/shipping/price drift) | 1 | $389 | $389 |
| **Total** | | | **$5,952** |

Stability notes:
- multiple GPUs share one PSU per chassis
- large fault domain: one node failure removes 3/3 of the GPUs
- PSU above 90% of rating at peak: shutdown risk
- UPS: prevents checkpoint/queue corruption on brownouts

## Most resilient: GeForce RTX 5060 Ti 16 GB x3 — $5,727

Best score among one-GPU-per-chassis builds with at least three nodes and stability >= 8.5.

- Head: **Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+)**
- Workers: **3x Custom MATX2 PC — Ryzen 5 5600, 16 GB, 1 TB, 650 W, 1 GPU**, 1 GPU per chassis
- Network: 2.5 GbE (8-port 2.5G switch) · Storage: 2x 4 TB NVMe RAID 0 cache · UPS: yes · HA head: no
- Peak draw: 945 W · idle: 156 W
- VRAM: 48 GB total, 0.81 capability index

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Head node: Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | 1 | $840 | $840 |
| Worker chassis/CPU/RAM/SSD: Custom MATX2 PC — Ryzen 5 5600, 16 GB, 1 TB, 650 W, 1 GPU | 3 | $700 | $2,100 |
| GPU: GeForce RTX 5060 Ti 16 GB | 3 | $500 | $1,500 |
| Network: 2.5 GbE (8-port 2.5G switch) - switch(es) | 1 | $120 | $120 |
| Network: cables/DACs | 4 | $8 | $32 |
| Storage: 2x 4 TB NVMe RAID 0 cache | 1 | $520 | $520 |
| UPS, 1500 VA / 1200 W line-interactive | 1 | $240 | $240 |
| Contingency 7% (tax/shipping/price drift) | 1 | $375 | $375 |
| **Total** | | | **$5,727** |

Stability notes:
- head has 10G + 3x M.2: queue, NFS and cache do not fight for I/O
- UPS: prevents checkpoint/queue corruption on brownouts

## Variant search

1817 additional models were generated: 324 GPUs, 1463 worker platforms, 30 heads. Dominance pruning kept 90 GPUs, 60 platforms and 7 heads; the rest were worse on every axis (price, throughput, power, VRAM, slots or I/O).

The variant search evaluated 2.5G, 5G, 10G and 25G networking with shared NVMe, local NVMe and NVMe RAID storage; 1G, NAS and HA-head options were already eliminated by the base study at this scale. It evaluated every remaining GPU, slot count and fleet size.

## Should the main PC be different?

Yes, but differentiate it by role, not by GPU. At an equal GPU count a dedicated non-GPU head costs about $908 more and adds about 2.4 stability points; it wins on score at every fleet size tested because a head that also renders shares its CPU, RAM and driver stack with the queue. A GPU in the head looks cheaper per GPU, but it puts the scheduler inside a GPU failure domain; it is worth it only if you want an interactive seat on the same box.

### Head upgrade ladder (same worker fleet)

| Head | Kind | Head cost | Total | Perf | Stability | Score | In budget |
|---|---|---:|---:|---:|---:|---:|---|
| Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | mini | $840 | $5,763 | 856 | 7.16 | 73.4 | yes |
| Minisforum UM890 Pro (Ryzen 9 8945HS, 32 GB, 1 TB) | mini | $640 | $5,549 | 856 | 6.46 | 71.4 | yes |
| Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB) | mini | $400 | $5,292 | 856 | 6.16 | 71.1 | yes |
| Workstation head: ITX + RTX 5080 16 GB | workstation | $1,900 | $6,897 | 1186 | 5.76 | 75.3 | no |
| Workstation head: ITX + RTX 3090 24 GB | workstation | $1,560 | $6,533 | 1139 | 5.76 | 75.2 | no |
| Workstation head: ITX base + RTX 4060 Ti 16 GB | workstation | $1,240 | $6,191 | 977 | 5.96 | 72.5 | no |
| Workstation head: ITX + RTX 5070 12 GB | workstation | $1,360 | $6,319 | 1033 | 5.86 | 71.2 | no |

### Dedicated head vs. worker-as-head

| Worker GPUs | Dedicated non-GPU head | Cost | Score | Stab | GPU head (+1 GPU) | Cost | Score | Stab | Worker-as-head cost | Score | Stab | Verdict |
|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 2 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $4,359 | 62.9 | 8.6 | Workstation head: ITX + RTX 5080 16 GB | $5,568 | 69.97 | 7.21 | $3,452 | 58.89 | 6.26 | keep head separate (reliability wins) |
| 3 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $5,727 | 68.2 | 8.9 | Workstation head: ITX + RTX 5080 16 GB | $6,957 | 72.73 | 7.48 | $4,819 | 64.01 | 6.53 | keep head separate (reliability wins) |
| 4 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $7,116 | 72.0 | 9.0 | Workstation head: ITX + RTX 5080 16 GB | $8,378 | 74.89 | 7.61 | $6,208 | 67.62 | 6.66 | keep head separate (reliability wins) |
| 6 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $9,829 | 75.2 | 8.2 | - | - | - | - | $8,922 | 70.55 | 5.8 | keep head separate (reliability wins) |

Rows above $6,000 show the trend for larger fleets; they are not purchase options at this budget.

If you drop the separate head and put that money into GPUs, about $5,977 buys **GeForce RTX 4060 Ti 16 GB x6** (2x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1000 W, 4 GPU, one node doubling as head). It reaches perf 817 vs 856, but stability falls from 7.2 to 5.8.

## Alternatives worth pricing

| Option | Topology | GPUs / VRAM | Cost | Perf | Stability | Score |
|---|---|---|---:|---:|---:|---:|
| Used-GPU build (no warranty) | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1000 W, 4 GPU | 3 / 72 GB | $5,866 | 969 | 6.35 | 75.2 |
| No separate head (spend it on GPUs) | 2x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1000 W, 4 GPU (one node doubles as head) | 6 / 96 GB | $5,977 | 817 | 5.83 | 71.5 |
| VRAM-first (24 GB per GPU) | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 1x Custom MATX2 PC — Ryzen 5 5600, 32 GB, 1 TB, 1000 W, 2 GPU | 2 / 64 GB | $5,950 | 605 | 6.57 | 68.7 |
| Best non-CUDA (AMD/Intel) | Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB) + 1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1000 W, 4 GPU | 4 / 80 GB | $5,849 | 1186 | 4.20 | 73.9 |

The used-GPU build can score higher because it buys more raw compute per dollar. It is kept off the podium because it has no warranty and the model penalizes used hardware; choose it only if you accept that risk. The non-CUDA build scores highest of all but runs ROCm/SYCL, not the default Forge path; it is included for completeness, not as the stable pick.

## Robustness

_Price-shock scenarios are skipped in the variant run; the base report covers the +15%/-15% GPU cases._

### Weight sensitivity

- **default**: GeForce RTX 5070 Ti 16 GB x3, Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1600 W, 4 GPU, $5,763, score 73.4
- **throughput-first**: GeForce RTX 5080 16 GB — Zotac Twin Edge x2, Workstation head: ITX + RTX 3090 24 GB + 1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1300 W, 4 GPU, $5,949, score 73.1
- **stability-first**: GeForce RTX 5060 Ti 16 GB x4, Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Custom MATX2 PC — Ryzen 5 5600, 32 GB, 1 TB, 1000 W, 2 GPU, $5,846, score 72.1
- **value-first**: GeForce RTX 5080 16 GB — Zotac Twin Edge x2, Workstation head: ITX + RTX 3090 24 GB + 1x Custom ATX2 PC — Core i5-13400, 32 GB, 1 TB, 1300 W, 4 GPU, $5,949, score 73.1
