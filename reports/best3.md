# Best 3 mini-Forge clusters

Budget **$6,000** · 220,248 build combinations enumerated · 181,044 valid after physics/compatibility checks · 73,449 inside budget · 14,400 eligible after baseline filters (new hardware, UPS, ≥16 GB per GPU).

Scoring: throughput 32%, GPU capability (VRAM) 18%, stability 22%, efficiency 8%, value 12%, expandability 8%. Prices: USD street/retail estimates, Nov 2026, qty 1, tax/shipping excluded; assume +/-15% and re-run with --gpu-price-shock to test the ranking.

| Pick | Topology | GPUs / VRAM | Cost | Peak | Perf | Stability | Score |
|---|---|---|---:|---:|---:|---:|---:|
| Best overall | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX) | 4 / 64 GB | $5,921 | 1104 W | 648 | 8.27/10 | 71.5 |
| Most resilient | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 3x Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU) | 3 / 48 GB | $5,673 | 1017 W | 499 | 8.69/10 | 67.4 |
| Best pure mini-PC | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 3x GMKtec K8 Plus (Ryzen 7 8845HS, 32 GB, 1 TB) + OCuLink dock | 3 / 48 GB | $5,384 | 906 W | 484 | 8.12/10 | 64.2 |

## Best overall: GeForce RTX 5060 Ti 16 GB x4 — $5,921

Highest weighted score: the most aggregate 16 GB+ throughput and VRAM that fits the budget, circuit and compatibility limits.

- Head: **Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+)**
- Workers: **2x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX)**, 2 GPU each
- Network: 2.5 GbE (8-port 2.5G switch) · Storage: 4 TB NVMe model cache in head, exported over NFS/SMB · UPS: yes · HA head: no
- Peak draw: 1104 W · idle: 146 W
- VRAM: 64 GB total, 0.84 capability index

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Head node: Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | 1 | $840 | $840 |
| Worker chassis/CPU/RAM/SSD: Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX) | 2 | $980 | $1,960 |
| GPU: GeForce RTX 5060 Ti 16 GB | 4 | $500 | $2,000 |
| Network: 2.5 GbE (8-port 2.5G switch) - switch(es) | 1 | $120 | $120 |
| Network: cables/DACs | 3 | $8 | $24 |
| Storage: 4 TB NVMe model cache in head, exported over NFS/SMB | 1 | $260 | $260 |
| UPS, 2000 VA / 1600 W line-interactive | 1 | $330 | $330 |
| Contingency 7% (tax/shipping/price drift) | 1 | $387 | $387 |
| **Total** | | | **$5,921** |

Stability notes:
- head has 10G + 3x M.2: queue, NFS and cache do not fight for I/O
- two GPUs share one PSU per chassis
- large fault domain: one node failure removes 2/4 of the GPUs
- UPS: prevents checkpoint/queue corruption on brownouts

## Most resilient: GeForce RTX 5060 Ti 16 GB x3 — $5,673

Best score among builds with one GPU per chassis, at least three nodes and stability >= 8.5, so no single failure removes more than a third of the fleet.

- Head: **Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+)**
- Workers: **3x Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU)**, 1 GPU each
- Network: 2.5 GbE (8-port 2.5G switch) · Storage: 4 TB NVMe model cache in head, exported over NFS/SMB · UPS: yes · HA head: no
- Peak draw: 1017 W · idle: 138 W
- VRAM: 48 GB total, 0.81 capability index

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Head node: Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | 1 | $840 | $840 |
| Worker chassis/CPU/RAM/SSD: Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU) | 3 | $740 | $2,220 |
| GPU: GeForce RTX 5060 Ti 16 GB | 3 | $500 | $1,500 |
| Network: 2.5 GbE (8-port 2.5G switch) - switch(es) | 1 | $120 | $120 |
| Network: cables/DACs | 4 | $8 | $32 |
| Storage: 4 TB NVMe model cache in head, exported over NFS/SMB | 1 | $260 | $260 |
| UPS, 2000 VA / 1600 W line-interactive | 1 | $330 | $330 |
| Contingency 7% (tax/shipping/price drift) | 1 | $371 | $371 |
| **Total** | | | **$5,673** |

Stability notes:
- head has 10G + 3x M.2: queue, NFS and cache do not fight for I/O
- UPS: prevents checkpoint/queue corruption on brownouts

## Best pure mini-PC: GeForce RTX 5060 Ti 16 GB x3 — $5,384

Highest score among builds where every box is a NUC-class mini PC, there are at least three worker nodes and all hardware is new.

- Head: **Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+)**
- Workers: **3x GMKtec K8 Plus (Ryzen 7 8845HS, 32 GB, 1 TB) + OCuLink dock**, 1 GPU each
- Network: 2.5 GbE (8-port 2.5G switch) · Storage: 4 TB NVMe model cache in head, exported over NFS/SMB · UPS: yes · HA head: no
- Peak draw: 906 W · idle: 102 W
- VRAM: 48 GB total, 0.81 capability index

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Head node: Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | 1 | $840 | $840 |
| Worker chassis/CPU/RAM/SSD: GMKtec K8 Plus (Ryzen 7 8845HS, 32 GB, 1 TB) + OCuLink dock | 3 | $520 | $1,560 |
| GPU: GeForce RTX 5060 Ti 16 GB | 3 | $500 | $1,500 |
| eGPU dock + PSU | 3 | $160 | $480 |
| Network: 2.5 GbE (8-port 2.5G switch) - switch(es) | 1 | $120 | $120 |
| Network: cables/DACs | 4 | $8 | $32 |
| Storage: 4 TB NVMe model cache in head, exported over NFS/SMB | 1 | $260 | $260 |
| UPS, 1500 VA / 1200 W line-interactive | 1 | $240 | $240 |
| Contingency 7% (tax/shipping/price drift) | 1 | $352 | $352 |
| **Total** | | | **$5,384** |

Stability notes:
- head has 10G + 3x M.2: queue, NFS and cache do not fight for I/O
- eGPU link (OCuLink/USB4) adds a hot-plug failure mode
- UPS: prevents checkpoint/queue corruption on brownouts

## Should the main PC be different?

Yes, but differentiate it by role, not by GPU. At an equal GPU count a dedicated non-GPU head costs about $983 more and adds about 2.3 stability points; it wins on score at every fleet size tested because a head that also renders shares its CPU, RAM and driver stack with the queue. A GPU in the head looks cheaper per GPU, but it puts the scheduler inside a GPU failure domain; it is worth it only if you want an interactive seat on the same box.

### Head upgrade ladder (same worker fleet)

| Head | Kind | Head cost | Total | Perf | Stability | Score | In budget |
|---|---|---:|---:|---:|---:|---:|---|
| Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | mini | $840 | $5,921 | 648 | 8.27 | 71.5 | yes |
| Minisforum UM890 Pro (Ryzen 9 8945HS, 32 GB, 1 TB) | mini | $640 | $5,707 | 648 | 7.57 | 69.3 | yes |
| Beelink SER8 (Ryzen 7 8845HS, 32 GB, 1 TB) | mini | $500 | $5,558 | 648 | 7.37 | 69.0 | yes |
| Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB) | mini | $400 | $5,451 | 648 | 7.27 | 69.0 | yes |
| Used HP EliteDesk 800 G6 (i7-10700, 32 GB, 1 TB) | used | $450 | $5,531 | 648 | 7.17 | 68.6 | yes |
| Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX) (first node is also head) | homogeneous | $0 | $5,014 | 648 | 5.87 | 67.3 | yes |
| Beelink EQ12 (N100, 16 GB, 500 GB) | mini | $260 | $5,301 | 603 | 6.67 | 65.7 | yes |
| Workstation head: ITX base + RTX 4070 Ti SUPER 16 GB | workstation | $1,610 | $6,745 | 884 | 6.97 | 73.1 | no |
| Workstation head: ITX base + RTX 4060 Ti 16 GB | workstation | $1,240 | $6,349 | 772 | 7.07 | 71.2 | no |
| ASUS NUC 13 Extreme (i9-13900K, 32 GB, 2 TB) | sff_modular | $1,310 | $6,424 | 648 | 7.67 | 68.9 | no |

### Dedicated head vs. worker-as-head

| Worker GPUs | Dedicated non-GPU head | Cost | Score | Stab | GPU head (+1 GPU) | Cost | Score | Stab | Worker-as-head cost | Score | Stab | Verdict |
|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 2 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $4,167 | 62.1 | 8.4 | Workstation head: ITX base + RTX 4070 Ti SUPER 16 GB | $5,065 | 67.0 | 7.12 | $3,259 | 57.53 | 6.12 | keep head separate (reliability wins) |
| 3 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $5,673 | 67.4 | 8.7 | Workstation head: ITX base + RTX 4070 Ti SUPER 16 GB | $6,497 | 70.19 | 7.39 | $4,669 | 62.53 | 6.39 | keep head separate (reliability wins) |
| 4 | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) | $7,137 | 71.1 | 8.8 | Workstation head: ITX base + RTX 4060 Ti 16 GB | $7,565 | 70.77 | 7.62 | $6,101 | 66.08 | 6.52 | keep head separate (reliability wins) |

Rows above $6,000 show the trend for larger fleets; they are not purchase options at this budget.

If you drop the separate head and put that money into GPUs, about $5,889 buys **GeForce RTX 4070 Ti SUPER 16 GB x3** (3x Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU), one node doubling as head). It reaches perf 798 vs 648, but stability falls from 8.3 to 5.7.

## Alternatives worth pricing

| Option | Topology | GPUs / VRAM | Cost | Perf | Stability | Score |
|---|---|---|---:|---:|---:|---:|
| Used-GPU value build | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX) | 4 / 64 GB | $5,911 | 630 | 8.05 | 70.7 |
| No separate head (spend it on GPUs) | 3x Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU) (one node doubles as head) | 3 / 48 GB | $5,889 | 798 | 5.69 | 67.7 |
| VRAM-first (24 GB per GPU) | Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU) | 2 / 48 GB | $5,632 | 585 | 7.86 | 69.2 |

## Robustness

| Scenario | In budget | Best cost | Best score | Same #1? |
|---|---:|---:|---:|---|
| base | 73,449 | $5,921 | 71.5 | yes |
| gpu +15% | 68,738 | $5,964 | 69.6 | yes |
| gpu -15% | 78,937 | $5,600 | 71.8 | yes |

### Weight sensitivity

- **default**: GeForce RTX 5060 Ti 16 GB x4, Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX), $5,921, score 71.5
- **throughput-first**: GeForce RTX 5070 Ti 16 GB x2, Workstation head: ITX base + RTX 4070 Ti SUPER 16 GB + 1x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX), $5,581, score 68.7
- **stability-first**: GeForce RTX 5060 Ti 16 GB x4, Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX), $5,921, score 71.5
- **value-first**: GeForce RTX 5060 Ti 16 GB x4, Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+) + 2x Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX), $5,921, score 71.5
