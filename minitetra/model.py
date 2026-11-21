"""Evaluation model: cost, throughput, capability, stability, score."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .catalog import (
    CONTINGENCY,
    FABRICS,
    GPUS,
    HEADS,
    PLATFORMS,
    STORAGE,
)

MAX_GPUS = 8
MAX_BOXES = 6
CIRCUIT_LIMIT_W = 1800  # a 15 A / 120 V branch, 80% derating
COMFORT_W = 1440
CONTINGENCY_RATE = CONTINGENCY

WEIGHTS = {
    "throughput": 0.32,
    "capability": 0.18,
    "stability": 0.22,
    "efficiency": 0.08,
    "value": 0.12,
    "expandability": 0.08,
}

VRAM_CAP = {8: 0.55, 12: 0.80, 16: 0.95, 24: 1.00, 32: 1.05}

PSU_TIERS = ((650, 0), (850, 60), (1000, 110), (1300, 180))


def ups_spec(peak_w: float) -> tuple[int, str]:
    """Size the UPS at 1.25x peak draw and return (price, label)."""
    need = peak_w * 1.25
    if need <= 900:
        return 170, "1500 VA / 900 W"
    if need <= 1200:
        return 240, "1500 VA / 1200 W"
    if need <= 1600:
        return 330, "2000 VA / 1600 W"
    return 450, "2200 VA / 1980 W"


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def vram_cap(vram_gb: int) -> float:
    return VRAM_CAP[vram_gb]


def psu_upgrade_cost(included_w: int, need_w: float) -> int | None:
    if need_w <= included_w:
        return 0
    for watts, cost in PSU_TIERS:
        if need_w <= watts:
            return cost
    return None


@dataclass(frozen=True)
class BomLine:
    label: str
    qty: int
    unit_usd: int

    @property
    def total_usd(self) -> int:
        return self.qty * self.unit_usd


@dataclass
class Candidate:
    signature: str
    head_mode: str  # dedicated | homogeneous
    head_key: str | None
    platform_key: str
    gpu_key: str
    boxes: int
    gpus_per_box: int
    fabric_key: str
    storage_key: str
    ha: bool
    ups: bool

    gpus_total: int
    total_vram_gb: int
    head_cost: int
    node_cost: int
    fabric_cost: int
    storage_cost: int
    switch_count: int
    adapter_count: int
    psu_cost: int
    gpu_price_eff: int

    subtotal: int
    total_cost: int
    peak_w: float
    idle_w: float
    ups_cost: int
    ups_label: str
    perf_index: float
    capability: float
    stability: float
    stability_notes: tuple[str, ...]
    components: dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    bom: tuple[BomLine, ...] = ()

    @property
    def head(self):
        return HEADS[self.head_key] if self.head_key else None

    @property
    def platform(self):
        return PLATFORMS[self.platform_key]

    @property
    def gpu(self):
        return GPUS[self.gpu_key]

    @property
    def pure_mini(self) -> bool:
        head = self.head
        head_ok = head is None or head.kind in ("mini", "used")
        return self.platform.pure_mini and head_ok

    def summary(self) -> dict:
        head = self.head
        return {
            "signature": self.signature,
            "head_mode": self.head_mode,
            "head": head.name if head else f"{self.platform.name} (first node doubles as head)",
            "head_key": self.head_key,
            "platform": self.platform.name,
            "platform_key": self.platform_key,
            "gpu": self.gpu.name,
            "gpu_key": self.gpu_key,
            "boxes": self.boxes,
            "gpus_per_box": self.gpus_per_box,
            "gpus_total": self.gpus_total,
            "total_vram_gb": self.total_vram_gb,
            "fabric": FABRICS[self.fabric_key].name,
            "storage": STORAGE[self.storage_key].name,
            "ha": self.ha,
            "ups": self.ups,
            "total_cost_usd": self.total_cost,
            "peak_w": round(self.peak_w, 1),
            "idle_w": round(self.idle_w, 1),
            "ups_rating": self.ups_label if self.ups else "none",
            "perf_index": round(self.perf_index, 1),
            "capability": round(self.capability, 4),
            "stability": round(self.stability, 2),
            "stability_notes": list(self.stability_notes),
            "components": {k: round(v, 1) for k, v in self.components.items()},
            "score": round(self.score, 2),
            "bom": [
                {"label": line.label, "qty": line.qty, "unit_usd": line.unit_usd,
                 "total_usd": line.total_usd}
                for line in self.bom
            ],
        }


def _stability(c: Candidate, head, platform, gpu, fabric, storage) -> tuple[float, tuple[str, ...]]:
    notes: list[str] = []
    score = 6.0

    if gpu.vendor == "nvidia":
        score += 1.0
    elif gpu.vendor == "intel":
        score -= 1.5
        notes.append("Intel Arc: IPEX/SYCL stack, not the default Forge path")
    else:
        score -= 0.8
        notes.append("AMD ROCm: works, but needs driver/version pinning")

    if gpu.used:
        score -= 0.35
        notes.append("used GPU: no warranty and unknown fan hours; buy from a seller with returns")
    if platform.used:
        score -= 0.25
        notes.append("used chassis: one PSU and one fan set with unknown service life")

    if c.head_mode == "dedicated":
        score += head.stability_mod
        if head.sfp10 and head.m2_slots >= 3:
            score += 0.5
            notes.append("head has 10G + 3x M.2: queue, NFS and cache do not fight for I/O")
        if head.has_gpu:
            score -= 0.6
            notes.append("head has a GPU: a driver reset or OOM also kills the queue")
    else:
        score -= 0.8 + platform.stability_mod
        notes.append("homogeneous head: Forge load shares CPU/RAM with the scheduler")

    if platform.egpu:
        score -= 0.7
        notes.append("eGPU link (OCuLink/USB4) adds a hot-plug failure mode")
    if platform.kind == "mini" and gpu.tdp_w > 140:
        score -= 0.3
        notes.append(">140 W GPU in a small chassis: sustained clocks depend on fan curves")

    score += storage.stability
    score += fabric.stability

    if c.gpus_per_box >= 2:
        score -= 0.15
        notes.append("two GPUs share one PSU per chassis")
    fault_share = c.gpus_per_box / c.gpus_total
    score -= 1.6 * fault_share
    if fault_share > 0.34:
        notes.append(
            f"large fault domain: one node failure removes {c.gpus_per_box}/{c.gpus_total} of the GPUs"
        )

    thermal_ratio = gpu.tdp_w / platform.max_gpu_tdp
    score += 0.4 * clamp((0.95 - thermal_ratio) / 0.15, -1.0, 1.0)
    if thermal_ratio >= 0.95:
        notes.append("GPU runs at the chassis power limit (no transient headroom)")

    need = 150 + platform.cpu_load_w + c.gpus_per_box * gpu.tdp_w * 1.4
    psu_ratio = need / max(platform.psu_included_w, 1)
    score += 0.3 * clamp((0.85 - psu_ratio) / 0.15, -1.0, 1.0)
    if psu_ratio >= 0.9:
        notes.append("PSU above 90% of rating at peak: shutdown risk")

    scheduler = head.scheduler if head else platform.scheduler
    if c.gpus_total > scheduler * 2.5:
        score -= 1.0
        notes.append("scheduler is undersized for this many Forge backends")
    elif c.gpus_total > scheduler * 1.5:
        score -= 0.5
        notes.append("scheduler queue adds latency under bursty load")

    if c.ha:
        score += 0.4
        notes.append("HA head pair: queue and NFS survive a head failure")
    if c.ups:
        score += 0.2
        notes.append("UPS: prevents checkpoint/queue corruption on brownouts")
    if c.peak_w > COMFORT_W:
        score -= 1.0
        notes.append(f"peak {c.peak_w:.0f} W exceeds 80% of a 15 A circuit")

    return clamp(score, 0.0, 10.0), tuple(notes)


def score_components(c: Candidate) -> dict[str, float]:
    throughput = 100 * min(1.0, math.log10(1 + c.perf_index / 100) / math.log10(13))
    capability = 100 * min(1.0, c.capability / 1.05)
    stability = c.stability * 10
    efficiency = 100 * min(1.0, (c.perf_index / c.peak_w) / 3.0)
    value = 100 * min(1.0, (c.perf_index / c.total_cost) / 0.25)
    platform = c.platform
    head = c.head
    expand = 0.30 + 0.10 * (head.m2_slots if head else platform.m2_slots) + 0.05 * platform.m2_slots
    if platform.kind in ("sff", "sff_modular", "sff_dual"):
        expand += 0.12
    if platform.egpu:
        expand -= 0.10
    if platform.kind == "mini":
        expand -= 0.08
    expandability = 100 * clamp(expand, 0.0, 1.0)
    return {
        "throughput": throughput,
        "capability": capability,
        "stability": stability,
        "efficiency": efficiency,
        "value": value,
        "expandability": expandability,
    }


def make_bom(c: Candidate) -> tuple[BomLine, ...]:
    platform = c.platform
    gpu = c.gpu
    fabric = FABRICS[c.fabric_key]
    storage = STORAGE[c.storage_key]
    lines: list[BomLine] = []
    if c.head is not None:
        lines.append(BomLine(f"Head node: {c.head.name}", 1, c.head.price))
        if c.ha:
            lines.append(BomLine("Second head (HA pair)", 1, c.head.price))
    if platform.fixed_gpu:
        lines.append(BomLine(f"Worker node, GPU included: {platform.name}", c.boxes, platform.base_price))
    else:
        lines.append(BomLine(f"Worker chassis/CPU/RAM/SSD: {platform.name}", c.boxes, platform.base_price))
        lines.append(BomLine(f"GPU: {gpu.name}", c.boxes * c.gpus_per_box, c.gpu_price_eff))
        if platform.per_gpu_dock_cost:
            lines.append(BomLine("eGPU dock + PSU", c.boxes * c.gpus_per_box, platform.per_gpu_dock_cost))
        if c.psu_cost:
            lines.append(BomLine("PSU upgrade", c.boxes, c.psu_cost))
    lines.append(BomLine(f"Network: {fabric.name} - switch(es)", c.switch_count, fabric.switch_price))
    lines.append(BomLine(f"Network: cables/DACs", c.boxes + (1 if c.head else 0), fabric.cable_cost))
    if c.adapter_count:
        lines.append(BomLine("Network: 2.5G/10G adapters", c.adapter_count, fabric.adapter_cost))
    lines.append(BomLine(f"Storage: {storage.name}", 1, c.storage_cost))
    if c.ups:
        lines.append(BomLine(f"UPS, {c.ups_label} line-interactive", 1, c.ups_cost))
    lines.append(BomLine(f"Contingency {CONTINGENCY_RATE:.0%} (tax/shipping/price drift)",
                         1, c.total_cost - c.subtotal))
    return tuple(lines)


def evaluate(
    head_key: str | None,
    head_mode: str,
    platform_key: str,
    gpu_key: str,
    boxes: int,
    gpus_per_box: int,
    fabric_key: str,
    storage_key: str,
    ha: bool = False,
    ups: bool = True,
    gpu_price_scale: float = 1.0,
    detailed: bool = True,
) -> Candidate | None:
    head = HEADS[head_key] if head_key else None
    platform = PLATFORMS[platform_key]
    gpu = GPUS[gpu_key]
    fabric = FABRICS[fabric_key]
    storage = STORAGE[storage_key]

    if boxes < 1 or boxes > MAX_BOXES:
        return None
    gpus_total = boxes * gpus_per_box
    if gpus_total < 1 or gpus_total > MAX_GPUS:
        return None
    if gpus_per_box > platform.gpu_slots:
        return None
    if platform.fixed_gpu:
        if gpu_key != platform.fixed_gpu or gpus_per_box != 1:
            return None
    elif gpu_key not in platform.gpu_choices:
        return None
    if gpu.tdp_w > platform.max_gpu_tdp:
        return None
    if head_mode == "homogeneous":
        if ha or head is not None or boxes < 2:
            return None
    elif head_mode == "dedicated":
        if head is None:
            return None
    else:
        return None

    gpu_price_eff = 0 if platform.fixed_gpu else round(gpu.price_usd * gpu_price_scale)
    psu_need = 150 + platform.cpu_load_w + gpus_per_box * gpu.tdp_w * 1.4
    psu_cost = psu_upgrade_cost(platform.psu_included_w, psu_need)
    if psu_cost is None:
        return None
    dock_cost = platform.per_gpu_dock_cost
    node_cost = platform.base_price + psu_cost + gpus_per_box * (gpu_price_eff + dock_cost)

    head_cost = head.price * (2 if ha else 1) if head is not None else 0

    nodes = boxes + (1 if head is not None else 0)
    switch_count = math.ceil(nodes / 8)
    missing_adapters = boxes if platform.lan_gbps < fabric.bandwidth_gbps else 0
    if head is not None and head.lan_gbps < fabric.bandwidth_gbps:
        missing_adapters += 1
    fabric_cost = (
        switch_count * fabric.switch_price
        + nodes * fabric.cable_cost
        + missing_adapters * fabric.adapter_cost
    )
    storage_cost = storage.cost
    peak_box = platform.idle_w + platform.cpu_load_w + gpus_per_box * gpu.tdp_w * 0.95 + 15
    peak_w = boxes * peak_box + (head.load_w if head else 0)
    if peak_w > CIRCUIT_LIMIT_W:
        return None
    idle_w = boxes * (platform.idle_w + gpus_per_box * gpu.idle_w) + (head.idle_w if head else 0)
    ups_cost, ups_label = ups_spec(peak_w) if ups else (0, "none")
    subtotal = (
        node_cost * boxes
        + head_cost
        + fabric_cost
        + storage_cost
        + ups_cost
    )
    total_cost = round(subtotal * (1 + CONTINGENCY_RATE))

    total_gpus = gpus_total + (1 if head is not None and head.has_gpu else 0)
    sched = head.scheduler if head is not None else platform.scheduler
    if total_gpus > sched * 2.5:
        sched_penalty = 0.86
    elif total_gpus > sched * 1.5:
        sched_penalty = 0.93
    else:
        sched_penalty = 1.0
    orchestration = max(0.94, 1.0 - 0.01 * (total_gpus - 1))
    throughput_factor = (
        fabric.factor(total_gpus) * storage.throughput * sched_penalty * orchestration
    )
    egpu_factor = platform.egpu_factor if platform.egpu else 1.0
    head_perf = GPUS[head.has_gpu].perf if head is not None and head.has_gpu else 0.0
    perf_index = (gpus_total * gpu.perf * egpu_factor + head_perf) * throughput_factor

    caps = [vram_cap(gpu.vram_gb)] * gpus_total
    total_vram = gpus_total * gpu.vram_gb
    if head is not None and head.has_gpu:
        hg = GPUS[head.has_gpu]
        caps.append(vram_cap(hg.vram_gb))
        total_vram += hg.vram_gb
    capability = 0.75 * min(caps) + 0.25 * min(1.0, total_vram / 128.0)

    signature = "|".join(
        (
            head_key or "HOM",
            platform_key,
            gpu_key,
            f"{boxes}x{gpus_per_box}",
            fabric_key,
            storage_key,
            "ha" if ha else "single",
            "ups" if ups else "noups",
        )
    )
    c = Candidate(
        signature=signature,
        head_mode=head_mode,
        head_key=head_key,
        platform_key=platform_key,
        gpu_key=gpu_key,
        boxes=boxes,
        gpus_per_box=gpus_per_box,
        fabric_key=fabric_key,
        storage_key=storage_key,
        ha=ha,
        ups=ups,
        gpus_total=gpus_total,
        total_vram_gb=total_vram,
        head_cost=head_cost,
        node_cost=node_cost,
        fabric_cost=fabric_cost,
        storage_cost=storage_cost,
        switch_count=switch_count,
        adapter_count=missing_adapters,
        psu_cost=psu_cost,
        gpu_price_eff=gpu_price_eff,
        subtotal=subtotal,
        total_cost=total_cost,
        peak_w=peak_w,
        idle_w=idle_w,
        ups_cost=ups_cost,
        ups_label=ups_label,
        perf_index=perf_index,
        capability=capability,
        stability=0.0,
        stability_notes=(),
    )
    c.stability, c.stability_notes = _stability(c, head, platform, gpu, fabric, storage)
    if detailed:
        c.bom = make_bom(c)
    c.components = score_components(c)
    c.score = round(sum(WEIGHTS[k] * v for k, v in c.components.items()), 4)
    return c
