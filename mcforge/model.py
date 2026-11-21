"""Cost, capacity, tick performance and stability for Minecraft Forge nodes."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .catalog import BASE_CATALOG, CONTINGENCY, STORAGE_OPTIONS, Catalog, ups_for

RAM_PER_INSTANCE = 8
THREADS_PER_INSTANCE = 2
MAX_INSTANCES_PER_NODE = 12
MAX_NODES = 6

RAM_OPTIONS_PRICES = {
    32: (85, 2),
    64: (160, 2),
    96: (240, 2),
    128: (300, 4),
    192: (450, 4),
    256: (600, 8),
}

WEIGHTS = {
    "capacity": 0.30,
    "tick": 0.30,
    "memory": 0.10,
    "storage": 0.10,
    "stability": 0.15,
    "value": 0.05,
}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


@dataclass(frozen=True)
class Candidate:
    signature: str
    cpu_key: str
    chassis_key: str
    ram_gb: int
    storage_key: str
    nodes: int
    head_key: str | None
    fabric_key: str
    raid: bool
    ups: bool

    instances_per_node: int
    total_instances: int
    total_ram_gb: int
    total_storage_tb: int
    tick_index: float
    peak_w: float
    idle_w: float
    subtotal: int
    total_cost: int
    adapter_count: int
    ups_cost: int
    ups_label: str

    stability: float
    stability_notes: tuple[str, ...]
    components: dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    catalog: Catalog = field(default=BASE_CATALOG, repr=False, compare=False)

    @property
    def cpu(self):
        return self.catalog.cpus[self.cpu_key]

    @property
    def chassis(self):
        return self.catalog.chassis[self.chassis_key]

    @property
    def head(self):
        return self.catalog.heads[self.head_key] if self.head_key else None

    def summary(self) -> dict:
        head = self.head
        return {
            "signature": self.signature,
            "cpu": self.cpu.name,
            "cpu_key": self.cpu_key,
            "chassis": self.chassis.name,
            "ram_gb_per_node": self.ram_gb,
            "storage_tb_per_node": STORAGE_OPTIONS[self.storage_key][0],
            "nodes": self.nodes,
            "head": head.name if head else f"{self.chassis.name} (first node doubles as head)",
            "fabric": self.catalog.fabrics[self.fabric_key].name,
            "raid": self.raid,
            "ups": self.ups,
            "instances_per_node": self.instances_per_node,
            "total_instances": self.total_instances,
            "total_ram_gb": self.total_ram_gb,
            "total_storage_tb": self.total_storage_tb,
            "tick_index": round(self.tick_index, 1),
            "peak_w": round(self.peak_w, 1),
            "idle_w": round(self.idle_w, 1),
            "total_cost_usd": self.total_cost,
            "stability": round(self.stability, 2),
            "stability_notes": list(self.stability_notes),
            "components": {k: round(v, 1) for k, v in self.components.items()},
            "score": round(self.score, 2),
            "gpus": 0,
        }


def evaluate(
    cpu_key: str,
    chassis_key: str,
    ram_gb: int,
    storage_key: str,
    nodes: int,
    head_key: str | None,
    fabric_key: str,
    raid: bool = False,
    ups: bool = True,
    catalog: Catalog | None = None,
) -> Candidate | None:
    cat = catalog or BASE_CATALOG
    cpu = cat.cpus[cpu_key]
    chassis = cat.chassis[chassis_key]
    fabric = cat.fabrics[fabric_key]
    head = cat.heads[head_key] if head_key else None

    if cpu.socket not in chassis.sockets:
        return None
    if nodes < 1 or nodes > MAX_NODES:
        return None
    if ram_gb not in RAM_OPTIONS_PRICES:
        return None
    ram_price, ram_slots = RAM_OPTIONS_PRICES[ram_gb]
    if ram_slots > chassis.ram_slots or ram_gb > chassis.max_ram_gb:
        return None
    storage_tb, storage_price = STORAGE_OPTIONS[storage_key]

    per_node = min(
        ram_gb // RAM_PER_INSTANCE,
        cpu.threads // THREADS_PER_INSTANCE,
        MAX_INSTANCES_PER_NODE,
    )
    if per_node < 1:
        return None
    total_instances = nodes * per_node

    node_cost = chassis.base_price + cpu.price + ram_price + storage_price * (2 if raid else 1)
    head_cost = head.price if head else 0
    devices = nodes + (1 if head else 0)
    switch_count = math.ceil(devices / 8)
    adapters = nodes if chassis.lan_gbps < fabric.bandwidth_gbps else 0
    if head and head.lan_gbps < fabric.bandwidth_gbps:
        adapters += 1
    network_cost = (
        switch_count * fabric.switch_price
        + devices * fabric.cable_cost
        + adapters * fabric.adapter_cost
    )

    node_peak = chassis.idle_w + cpu.tdp_w * 1.1 + 10 + (ram_gb / 32) * 5
    peak_w = nodes * node_peak + (head.load_w if head else 0)
    idle_w = nodes * (chassis.idle_w + 5) + (head.idle_w if head else 0)
    ups_price, ups_label = ups_for(peak_w) if ups else (0, "none")

    subtotal = nodes * node_cost + head_cost + network_cost + ups_price
    total_cost = round(subtotal * (1 + CONTINGENCY))

    tick = cpu.st * (1 - 0.035 * (per_node - 1))

    stability = 7.0
    notes: list[str] = []
    stability += chassis.stability
    if head:
        stability += head.stability
        if head.scheduler < 4:
            stability -= 0.5
            notes.append("panel/backup host is undersized for this many instances")
    else:
        stability -= 0.8
        notes.append("first node also runs the panel and backups")
    stability += fabric.stability
    if ups:
        stability += 0.2
    else:
        stability -= 0.4
        notes.append("no UPS: a brownout can corrupt every world at once")
    if raid:
        stability += 0.3
        notes.append("RAID 1 mirrors each node's world/backup drives")
    if nodes >= 3:
        stability += 0.3
    if per_node <= 4:
        stability += 0.3
    elif per_node >= 8:
        stability -= 0.4
        notes.append("8+ modpacks per node: tick spikes and GC pauses are harder to isolate")
    stability -= 1.5 * (per_node / total_instances)
    if tick < 70:
        stability -= 0.5
        notes.append("estimated tick headroom is marginal at this instance density")
    stability = clamp(stability, 0.0, 10.0)

    capacity = 100 * min(1.0, total_instances / 32)
    tick_score = 100 * min(1.0, tick / 110)
    memory = 100 * min(1.0, ram_gb / (per_node * RAM_PER_INSTANCE + 8))
    storage = 100 * min(1.0, storage_tb / (per_node * 0.4 + 0.5))
    stability_score = stability * 10
    value = 100 * min(1.0, (total_instances / total_cost) / 0.008)
    components = {
        "capacity": capacity,
        "tick": tick_score,
        "memory": memory,
        "storage": storage,
        "stability": stability_score,
        "value": value,
    }
    score = round(sum(WEIGHTS[k] * v for k, v in components.items()), 4)
    signature = "|".join((
        cpu_key, chassis_key, f"{ram_gb}g", storage_key, f"{nodes}n",
        head_key or "HOM", fabric_key, "raid" if raid else "single",
        "ups" if ups else "noups",
    ))
    return Candidate(
        signature=signature,
        cpu_key=cpu_key,
        chassis_key=chassis_key,
        ram_gb=ram_gb,
        storage_key=storage_key,
        nodes=nodes,
        head_key=head_key,
        fabric_key=fabric_key,
        raid=raid,
        ups=ups,
        instances_per_node=per_node,
        total_instances=total_instances,
        total_ram_gb=nodes * ram_gb,
        total_storage_tb=nodes * storage_tb,
        tick_index=tick,
        peak_w=peak_w,
        idle_w=idle_w,
        subtotal=subtotal,
        total_cost=total_cost,
        adapter_count=adapters,
        ups_cost=ups_price,
        ups_label=ups_label,
        stability=stability,
        stability_notes=tuple(notes),
        components=components,
        score=score,
        catalog=cat,
    )
