# Mini-Tetra build guide — a stable multi-Forge cluster for $6,000

This is the human-readable companion to [`best3.md`](best3.md). It covers what to
buy, how to assemble it, how to run Forge as a queued multi-node service, and how
to prove it is stable before you trust it.

**Assumptions**

- Workload: Stable Diffusion WebUI Forge, SDXL 1024² and Flux dev/FP8, a mix of
  interactive use and a batch queue. One Forge instance per GPU.
- Location: a room with 120 V / 15 A circuits and ≤25 °C ambient.
- Prices: USD street estimates, Nov 2026, tax and shipping excluded. The study
  adds a 7% contingency to every bill of materials.
- The podium only considers new hardware with warranty, at least 16 GB of VRAM
  per GPU, a UPS, and a dedicated non-GPU head; the resilient pick also requires
  three or more worker nodes.

## The three builds

| | Best overall | Most resilient | Best pure mini-PC |
|---|---|---|---|
| GPUs | 4x RTX 5060 Ti 16 GB | 3x RTX 5060 Ti 16 GB | 3x RTX 5060 Ti 16 GB |
| Workers | 2x dual-GPU mATX cubes | 3x 8–12 L ITX nodes | 3x GMKtec K8 Plus + OCuLink |
| Head | Minisforum MS-01 | Minisforum MS-01 | Minisforum MS-01 |
| VRAM | 64 GB | 48 GB | 48 GB |
| Network | 2.5 GbE | 2.5 GbE | 2.5 GbE |
| Storage | 4 TB NVMe share | 4 TB NVMe share | 4 TB NVMe share |
| Peak / idle | 1,104 W / 146 W | 1,017 W / 138 W | 906 W / ~120 W |
| UPS | 2000 VA / 1600 W | 2000 VA / 1600 W | 1500 VA / 1200 W |
| Stability score | 8.27 / 10 | 8.69 / 10 | 8.12 / 10 |
| Cost | **$5,921** | **$5,673** | **$5,384** |

All three share the same GPU, driver stack, model cache and head. Pick by what you
optimise for:

- **Best overall** is the most throughput per dollar. It uses two 4-slot mATX
  cubes, each with two GPUs. A single node failure removes half the fleet, so pair
  it with the retry/drain rules below.
- **Most resilient** spends about $250 less and gives each GPU its own chassis and
  PSU. One failure removes one third of the fleet, service is trivial (unplug one
  box), and it has the highest stability score of the three.
- **Best pure mini-PC** is the smallest and cheapest. Three 1 L-class hosts with OCuLink
  docks and one head fit on a single shelf. The eGPU link costs ~3% throughput and
  adds a cable/connector failure mode, hence the lower stability score.

### Build A — best overall ($5,921)

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Minisforum MS-01 (i9-13900H, 32 GB, 2 TB) | 1 | $840 | $840 |
| Dual-GPU mATX node allowance: Ryzen 5 7600, B650M, 32 GB DDR5-6000, 2 TB NVMe, 1000 W ATX 3.1, mATX case, cooler, fans, assembly/test | 2 | $980 | $1,960 |
| RTX 5060 Ti 16 GB | 4 | $500 | $2,000 |
| 2.5 GbE 8-port switch | 1 | $120 | $120 |
| Cat6 patch cables | 3 | $8 | $24 |
| 4 TB NVMe model cache in head | 1 | $260 | $260 |
| UPS 2000 VA / 1600 W | 1 | $330 | $330 |
| Contingency 7% | 1 | $387 | $387 |
| **Total** | | | **$5,921** |

Node notes:

- Use the CPU's x16 slot for GPU 0 and the chipset x4 slot for GPU 1. PCIe 4.0 x4
  is fine for inference (model load ~10% slower, sampling unaffected).
- Pick a board with at least two slots of spacing between the x16 and x4 slots,
  and a case with four expansion slots. Two axial 2-slot cards need the gap.
- 1000 W leaves headroom over the ~500 W measured node peak and the ~760 W
  transient allowance the model uses; it keeps the fan slow. 850 W would work but
  leaves less headroom.
- The second GPU raises the node to ~550 W; the pair plus head is 1,104 W, which is
  61% of a 15 A breaker and 77% of the 80% comfort limit. Give it a dedicated
  circuit if you can.

### Build B — most resilient ($5,673)

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Minisforum MS-01 head | 1 | $840 | $840 |
| ITX node allowance: Ryzen 5 7600, B650I, 32 GB DDR5-6000, 1 TB NVMe, 650 W SFX, 8–12 L case, low-profile cooler | 3 | $740 | $2,220 |
| RTX 5060 Ti 16 GB | 3 | $500 | $1,500 |
| 2.5 GbE switch | 1 | $120 | $120 |
| Cat6 cables | 4 | $8 | $32 |
| 4 TB NVMe model cache | 1 | $260 | $260 |
| UPS 2000 VA / 1600 W | 1 | $330 | $330 |
| Contingency 7% | 1 | $371 | $371 |
| **Total** | | | **$5,673** |

Each node is ~300 W at the wall and can be lifted with one hand. Keep 10 cm of
clearance around each case; stacked ITX cubes recycle hot air.

### Build C — best pure mini-PC ($5,384)

| Item | Qty | Unit | Total |
|---|---:|---:|---:|
| Minisforum MS-01 head | 1 | $840 | $840 |
| GMKtec K8 Plus barebone (Ryzen 7 8845HS) + 32 GB DDR5 + 1 TB NVMe | 3 | $520 | $1,560 |
| OCuLink dock + 500 W SFX PSU | 3 | $160 | $480 |
| RTX 5060 Ti 16 GB | 3 | $500 | $1,500 |
| 2.5 GbE switch | 1 | $120 | $120 |
| Cat6 cables | 4 | $8 | $32 |
| 4 TB NVMe model cache | 1 | $260 | $260 |
| UPS 1500 VA / 1200 W | 1 | $240 | $240 |
| Contingency 7% | 1 | $352 | $352 |
| **Total** | | | **$5,384** |

The OCuLink dock is open-air, so the GPU fans are always audible. Put the docks on
a shelf, use 0.5 m OCuLink cables, strain-relieve them, and never hot-plug. Set
PCIe to Gen4 and enable above-4G decoding in BIOS. The 8845HS host idles at ~15 W.


## Should the main PC be different?

Yes. The study varies the head independently from the workers and compares three
placements at an equal GPU count:

| Worker GPUs | Dedicated non-GPU head | Worker also acts as head | Difference |
|---:|---|---|---|
| 2 | $4,167 · score 62.1 · stab 8.42 | $3,259 · score 57.5 · stab 6.12 | +$908, +2.3 stab |
| 3 | $5,673 · score 67.4 · stab 8.69 | $4,669 · score 62.5 · stab 6.39 | +$1,004, +2.3 stab |
| 4 | $7,137 · score 71.1 · stab 8.82 | $6,101 · score 66.1 · stab 6.52 | +$1,036, +2.3 stab |

The dedicated head wins at every fleet size the budget allows, even though it
costs about $900 more, because the score gain from stability is larger than the
score loss from spending that money on the head instead of another GPU. The head
also absorbs NFS, the queue, TLS and monitoring; those services compete with a
Forge process for CPU, RAM and the same GPU driver reset domain when merged.

The four-GPU row is over budget on purpose: it shows the trend, not a purchase
option. Six single-GPU nodes never appear because 6 × ~295 W plus the head
exceeds a 15 A circuit.

**What about a head with a GPU?** A workstation head reuses the chassis that is
already paid for, so the marginal GPU costs ~$400–500 instead of ~$1,200, and it
adds an interactive seat. It is not the stable choice: at three GPUs it costs
$6,497 (over budget), scores 70.2, and drops stability from 8.69 to 7.39. A driver
reset or an OOM now takes down the queue and NFS with the GPU. Buy a GPU head only
if you personally need a local UI seat; otherwise buy a fourth worker, which is
outside the head's failure domain.

**Budget-equivalent alternative.** Drop the head and spend the ~$900 on GPUs:
$5,889 buys three RTX 4070 Ti SUPER 16 GB in a no-head topology. It reaches perf
798 vs 648 (+23%), but stability falls from 8.27 to 5.69 and score from 71.5 to
67.7. If your priority is images per hour and you can tolerate a restart taking
the whole service down, that is a valid choice. It is not the stable-server
choice.

## Reference architecture

```
                        ┌──────────────────────────────────┐
                        │ Head: Minisforum MS-01 (no GPU)  │
                        │ SwarmUI queue · NFSv4 models     │
                        │ Caddy TLS/auth · Prometheus      │
                        │ NUT (UPS) · restic backups       │
                        └───────┬──────────────────┬───────┘
                      2.5 GbE   │                  │   2.5 GbE
                 ┌──────────────┴───┐          ┌───┴──────────────┐
                 │ Worker 1          │          │ Worker N          │
                 │ Forge :7860       │   ...    │ Forge :7860       │
                 │ 1-2x RTX 5060 Ti  │          │ 1x RTX 5060 Ti    │
                 │ /models ro, /out rw│         │ /models ro, /out rw│
                 └──────────────────┘          └──────────────────┘
```

- The head is the only box with a writable model cache and the queue database.
- Workers mount `/models` read-only and write only to their own `/outputs/<node>`.
- The switch is an 8-port 2.5 GbE unit. The MS-01's 10G ports stay unused at this
  scale; 10 GbE added ~$600 and ~2% throughput in the study, so it lost to a GPU.
- Put the head and switch on the UPS; workers can be on the same UPS if runtime
  allows, otherwise let NUT shut them down first.

## Software stack

**Base OS (all nodes).** Ubuntu Server 24.04 LTS, `nvidia-driver-580-open` (pin the
exact version), Docker Engine + NVIDIA Container Toolkit, `nvidia-persistenced`,
`chrony`, `smartd`. Disable sleep/hibernate; set BIOS to restore power on AC loss.

**Forge workers.** One container per GPU, image pinned by digest. Run the Forge
API without the Gradio UI on the workers:

```
--api --nowebui --listen 0.0.0.0 --port 7860
--ckpt-dir /models/checkpoints --lora-dir /models/loras
--vae-dir /models/vae --embeddings-dir /models/embeddings
--outputs-dir /outputs
```

Set `CUDA_VISIBLE_DEVICES` per container (or `device_ids` in Compose) so each
instance sees exactly one GPU. Keep the OS SSD for the image and the model share
for weights; do not put the HuggingFace cache on the OS disk.

**Queue and UI.** Run SwarmUI on the head. It is built for multiple backends and
speaks the Forge/A1111 API, so each worker registers as `http://worker-N:7860`.
SwarmUI owns the queue, retries and backend selection. If you prefer a smaller
stack, a FastAPI dispatcher plus Redis and a Postgres job table gives the same
properties; do not expose raw Forge ports to users.

**Model share.** Export `/srv/models` from the head's 4 TB NVMe with NFSv4.2,
read-only to workers:

```
/srv/models 10.20.0.0/24(ro,async,no_subtree_check,root_squash)
```

Mount with `vers=4.2,rsize=1M,wsize=1M,hard,timeo=600,retrans=2`. Keep a
`sha256sum` manifest and verify it on boot; a truncated checkpoint is the most
common cause of "Forge works on one node only".

**Ingress.** Caddy on the head terminates TLS for SwarmUI, enforces auth (basic
auth or OIDC), and sets upload limits. Reach it over Tailscale/WireGuard; do not
port-forward Forge or the queue.

**Monitoring.** `node_exporter` on every node, `dcgm-exporter` on workers,
Prometheus + Grafana + Alertmanager on the head. Alert on: GPU temp > 80 °C for
5 min, any Xid in `dmesg`, ECC errors on A5000/A4000, queue depth > 20, disk > 85%,
UPS on battery, NFS latency > 50 ms.

**Update policy.** One image tag, one driver branch, one Forge commit for the whole
fleet. Update one worker, run the smoke test, then roll. Never auto-update a
working inference stack mid-week.

## Power, cooling and network

**Power.** The three builds peak at 1,104 W, 1,017 W and 906 W. A 15 A / 120 V
branch is 1,800 W; the 80% continuous limit is 1,440 W. Build A sits at 61% of the
breaker and 77% of the comfort limit, Build B at 57%/71%, Build C at 50%/63%. Do
not put two builds on one circuit and do not share it with a heater, laser printer
or air conditioner. If you have a 20 A circuit, use it for Build A.

The UPS is sized at 1.25× peak: 2000 VA / 1600 W for A and B, 1500 VA / 1200 W for
C. Connect it over USB and run NUT on the head: on-battery → shut down workers
first, then the head. A 1,100 W load on a 1,600 W UPS gives roughly 5–8 minutes,
enough for a clean shutdown, not enough to finish a batch. Configure Forge/SwarmUI
to checkpoint or drop the queue, not to "finish current job".

Idle draw is 120–146 W for the whole cluster. At $0.14/kWh that is about $15/month
idling 24/7. Put workers to sleep or shut them down when unused if noise and power
matter; the queue will simply have fewer backends.

**Cooling.** Each 5060 Ti is 180 W and dual-slot. In the dual-GPU cube, leave at
least one empty slot between the cards and use three 120 mm intake fans; two axial
cards stacked with no gap will run at 83 °C and throttle. In the ITX and K8 Plus
builds the card is the largest heat source; keep 10 cm of clearance on the fan side.
Target: GPU < 80 °C sustained, CPU < 85 °C, ambient ≤ 25 °C. If the room runs warm,
cap the GPUs at 160 W with `nvidia-smi -pl 160`; you lose ~4% throughput and ~15 W
per card.

**Network.** A single 8-port 2.5 GbE switch is enough for 3–4 workers plus the head.
Use static leases, put the cluster on its own VLAN, and keep NFS on TCP. Jumbo
frames are optional and usually not worth the debugging. Do not buy 10 GbE for this
fleet: it added ~$600 and ~2–3% throughput in the study, which is worse than spending
the money on a GPU. 10 GbE only starts to pay when you keep checkpoints on a remote
NAS or run 8+ workers that cold-load models simultaneously.

## Assembly and BIOS checklist

1. Update the BIOS on every board before installing the OS. Enable above-4G
   decoding / Resizable BAR, set PCIe to Gen4 (or Auto), enable "restore on AC
   power loss", disable CSM, and set the fan curve to a fixed 40% minimum.
2. Install the OS with a static IP or DHCP reservation. Set the hostname to
   `forge-head`, `forge-w1` … so the queue config is readable.
3. Install the pinned NVIDIA driver and Docker first, then the NVIDIA container
   toolkit, then run `nvidia-smi` and a CUDA container smoke test before adding
   Forge. A node that cannot run `nvidia-smi -q` reliably is not ready.
4. Mount `/models` read-only from the head and `/outputs` read-write. Run the
   checksum manifest; do not copy models by hand to each node.
5. Start one Forge container, hit `/sdapi/v1/options`, generate one 512×512 image,
   then register the backend in SwarmUI. Repeat per GPU, not per node.
6. Label every cable at both ends, photograph the inside of each node, and record
   the PSU/GPU serial numbers. In six months you will not remember which OCuLink
   cable goes where.


## Prove it is stable

Run this before exposing the service:

- **48-hour soak.** 100 mixed jobs: SDXL 1024² batch 4, Flux dev FP8 batch 1,
  one LoRA-heavy job. Log images/hour, p50/p95 latency, VRAM, GPU temp, clocks and
  wall power. Acceptance: no Xid, no OOM, no throttle, p95 latency within 2× p50.
- **Thermal soak.** One hour at 100% on every GPU simultaneously. Acceptance:
  < 83 °C, no clock drop below 90% of sustained boost, no fan at 100%.
- **Model-load test.** Cold-load the largest checkpoint on all workers at once over
  NFS. On 2.5 GbE this is the worst-case network moment; it must not time out.
- **Failure drills.** Stop one worker container (queue must retry and finish),
  power off the head (workers may finish current jobs; queue must recover from
  backup), pull the UPS input (graceful shutdown within runtime), unplug one
  network cable (no corrupted outputs).
- **Restart test.** Reboot every node twice. The cluster must come back without
  manual steps: NFS mounted, containers up, backends registered, queue intact.

Only after those pass should you point users at Caddy.

## Runbook

- **Node unhealthy:** `nvidia-smi -q` for Xid/ECC, `dmesg -T | grep -i xid`,
  container logs. Drain the backend in SwarmUI, reboot, run the smoke test, then
  re-enable. Three failures in 10 minutes should page you, not loop forever.
- **Head unhealthy:** workers keep serving direct API requests, but the queue and
  NFS are down. Restore from the restic snapshot, remount, re-register backends.
  Keep a documented rebuild USB and a copy of the Compose files in git.
- **Disk full:** outputs fill the share first. Alert at 85%, prune outputs older
  than 30 days, and keep models on a separate NVMe from the OS.
- **Power event:** NUT shuts down workers, then the head; on restore, BIOS powers
  the nodes, `systemd` starts containers, and SwarmUI reconnects. Test this, do not
  assume it.
- **Driver/Forge update:** one node, one image tag, smoke test, then roll. Keep the
  previous image tagged `rollback`.

## What not to buy, and why

- **One RTX 5090.** It is the fastest single GPU and has 32 GB, but at ~$2,450 it
  consumes 41% of the budget and 100% of your redundancy. One card failure or one
  driver reset takes the whole service down. A 4-GPU 16 GB fleet wins on
  concurrency, resilience and $/throughput at this budget.
- **8 GB cards.** SDXL works with offload, Flux is painful, and the capability
  score drops sharply. 12 GB is the practical floor, 16 GB is the sweet spot for
  this generation.
- **AMD mini PCs (HX99G/HX100G).** ROCm works, but you pin kernels, `HSA_OVERRIDE`
  and PyTorch versions; the study scores them well below CUDA for stability. Fine
  as a hobby, not as the stable default.
- **10 GbE.** See above: ~$600 for ~2–3%. Buy a fourth GPU instead.
- **HA head pair.** A second MS-01 is ~$840, which is most of a GPU, and the study
  never fits it with four GPUs. Keep a cold spare config and a tested rebuild
  instead; the queue database is small enough to back up hourly.
- **Six single-GPU nodes.** 6 × ~295 W plus the head exceeds a 15 A circuit, and
  the budget cannot hold six 16 GB GPUs with a head.
- **A GPU in the head.** It looks cheap because the chassis is already there, but
  it puts the queue, NFS and the driver reset domain in the same box as a renderer.
  It is an interactive-seat feature, not a server-stability feature.

## Shopping list (Build A)

- 1× Minisforum MS-01 (i9-13900H) barebone, 32 GB DDR5 SODIMM kit, 2 TB NVMe (OS),
  4 TB NVMe (models)
- 2× AMD Ryzen 5 7600, 2× B650M mATX board with x16 + x4 slots, 2× 32 GB DDR5-6000,
  2× 2 TB NVMe, 2× 1000 W ATX 3.1 Gold, 2× mATX case with four slots, 2× tower
  cooler, 6× 120 mm fans
- 4× GeForce RTX 5060 Ti 16 GB (check 1× vs 2× 8-pin per board partner)
- 1× 8-port 2.5 GbE switch, 3× Cat6 patch cables
- 1× 2000 VA / 1600 W line-interactive UPS with USB
- 1× 1500 VA surge protector for the switch/monitor (optional)

Build B swaps the two dual-GPU nodes for three ITX nodes (one GPU each). Build C
swaps them for three K8 Plus hosts plus three OCuLink docks and 500 W SFX PSUs.
The head, switch, model NVMe and UPS are the same across all three.



