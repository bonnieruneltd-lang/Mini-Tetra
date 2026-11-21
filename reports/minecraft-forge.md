# Minecraft Forge cluster — no GPU required

Budget **$6,000** · 457,920 configurations enumerated · 246,842 inside budget · **0 GPUs**.

This study is for multiple **Minecraft Forge** servers. The tick loop is single-thread CPU work; each modpack needs ~8 GB RAM; world and chunk I/O wants NVMe. A discrete GPU does nothing for a dedicated server.

| Pick | CPU × nodes | RAM/node | Instances | Tick | Stability | Cost |
|---|---|---:|---:|---:|---:|---:|
| Best overall | Core i7-14700K × 4 | 64 GB | 32 | 82 | 7.72 | $5,949 |
| Most resilient | Ryzen 5 9600X × 5 | 64 GB | 30 | 78 | 8.10 | $5,929 |
| Most instances | Core i5-14600K × 5 | 96 GB | 50 | 68 | 6.10 | $5,308 |

## Why no GPU?

Minecraft's server tick runs on one thread per dimension; Forge mods add CPU work, not shader work. A GPU helps the *client* render frames, not the server simulate ticks. The integrated GPU on every CPU here is enough for console access, and spending $500-2,000 on a card would take RAM, NVMe or a whole second node away from the cluster.

## Best overall: Core i7-14700K × 4 — $5,949

Highest weighted score: instance capacity, tick performance and stability.

- Nodes: **4× Custom 8 L ITX (LGA1700, 2x DDR5, 2x M.2, 2.5G)**
- Head: **Minisforum MS-01 (i9, 32 GB, 2x10G)**
- Memory: 64 GB/node (256 GB total) · storage 16 TB NVMe
- Forge instances: 8/node → **32 total**
- Network: 2.5 GbE · RAID 1: no · UPS: yes
- Peak draw: 1146 W · idle: 134 W

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Node: Custom 8 L ITX (LGA1700, 2x DDR5, 2x M.2, 2.5G) + Core i7-14700K | 4 | $680 | $2,720 |
| DDR5 kit, 64 GB | 4 | $160 | $640 |
| NVMe, 4 TB | 4 | $220 | $880 |
| Head: Minisforum MS-01 (i9, 32 GB, 2x10G) | 1 | $840 | $840 |
| Switch: 2.5 GbE | 1 | $120 | $120 |
| Cables | 5 | $8 | $40 |
| UPS, 2000 VA | 1 | $320 | $320 |
| Contingency 7% | 1 | $389 | $389 |
| **Total** | | | **$5,949** |

Notes:
- 8+ modpacks per node: tick spikes and GC pauses are harder to isolate

## Most resilient: Ryzen 5 9600X × 5 — $5,929

Best score among 3+ node builds with a dedicated head and stability >= 8.

- Nodes: **5× Custom 8 L ITX (AM5, 2x DDR5, 2x M.2, 2.5G)**
- Head: **Minisforum MS-01 (i9, 32 GB, 2x10G)**
- Memory: 64 GB/node (320 GB total) · storage 20 TB NVMe
- Forge instances: 6/node → **30 total**
- Network: 1 GbE · RAID 1: no · UPS: yes
- Peak draw: 668 W · idle: 163 W

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Node: Custom 8 L ITX (AM5, 2x DDR5, 2x M.2, 2.5G) + Ryzen 5 9600X | 5 | $500 | $2,500 |
| DDR5 kit, 64 GB | 5 | $160 | $800 |
| NVMe, 4 TB | 5 | $220 | $1,100 |
| Head: Minisforum MS-01 (i9, 32 GB, 2x10G) | 1 | $840 | $840 |
| Switch: 1 GbE | 1 | $45 | $45 |
| Cables | 6 | $6 | $36 |
| UPS, 1500 VA | 1 | $220 | $220 |
| Contingency 7% | 1 | $388 | $388 |
| **Total** | | | **$5,929** |

## Most instances: Core i5-14600K × 5 — $5,308

Maximum Forge instances while keeping estimated tick index >= 65.

- Nodes: **5× Custom 8 L ITX (LGA1700, 2x DDR5, 2x M.2, 2.5G)**
- Head: **Beelink EQ12 (N100, 16 GB)**
- Memory: 96 GB/node (480 GB total) · storage 5 TB NVMe
- Forge instances: 10/node → **50 total**
- Network: 1 GbE · RAID 1: no · UPS: yes
- Peak draw: 1100 W · idle: 153 W

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Node: Custom 8 L ITX (LGA1700, 2x DDR5, 2x M.2, 2.5G) + Core i5-14600K | 5 | $550 | $2,750 |
| DDR5 kit, 96 GB | 5 | $240 | $1,200 |
| NVMe, 1 TB | 5 | $70 | $350 |
| Head: Beelink EQ12 (N100, 16 GB) | 1 | $260 | $260 |
| Switch: 1 GbE | 1 | $45 | $45 |
| Cables | 6 | $6 | $36 |
| UPS, 2000 VA | 1 | $320 | $320 |
| Contingency 7% | 1 | $347 | $347 |
| **Total** | | | **$5,308** |

Notes:
- panel/backup host is undersized for this many instances
- 8+ modpacks per node: tick spikes and GC pauses are harder to isolate
- estimated tick headroom is marginal at this instance density

## Software stack

- **Panel:** Pterodactyl (panel + Wings per node) or Crafty Controller. One allocation per Forge instance, 8 GB RAM and 2 threads each.
- **Java:** Eclipse Temurin 21 for Minecraft 1.20.5+; keep the exact Forge and modpack versions pinned per instance.
- **Storage:** world + mods + backups on NVMe. Run `restic` or the panel's backup job to the head/NAS; test a restore.
- **Tuning:** Spark for tick profiling, Chunky for chunk pre-generation, `view-distance=8`, `simulation-distance=6`, and a modest player cap per pack.
- **Network:** 2.5 GbE is plenty for players; the extra bandwidth is for backups and panel traffic. A Velocity proxy is optional if the packs share one player identity.

## Alternatives

| Option | Build | Instances | Tick | Cost |
|---|---|---:|---:|---:|
| Best instances per dollar | Core i5-14600K × 4, 96 GB | 40 | 68 | $5,430 |
| Best tick headroom | Core i7-14700K × 4, 64 GB | 32 | 82 | $5,949 |

## Notes

Scoring: capacity 30%, tick 30%, memory 10%, storage 10%, stability 15%, value 5%. Prices are Nov 2026 planning estimates with a 7% contingency.
