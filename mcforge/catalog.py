"""Hardware catalog for a multi-Forge Minecraft server cluster.

Minecraft Forge is a Java game server: the tick loop is single-thread bound,
each modpack needs 6-12 GB of RAM, and world/chunk I/O wants NVMe. GPUs are not
part of the server path. Prices are Nov 2026 planning estimates in USD.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class Cpu:
    key: str
    name: str
    st: float          # single-thread index, i5-14600K = 100
    mt: float          # multi-thread index
    cores: int
    threads: int
    tdp_w: int
    price: int
    socket: str
    igpu: bool = True
    note: str = ""


CPUS: dict[str, Cpu] = {
    c.key: c
    for c in (
        Cpu("r5_5600", "Ryzen 5 5600", 80, 50, 6, 12, 65, 110, "am4"),
        Cpu("r7_5700x3d", "Ryzen 7 5700X3D", 85, 60, 8, 16, 105, 180, "am4",
            note="3D V-Cache helps modded tick time"),
        Cpu("r9_5950x", "Ryzen 9 5950X", 90, 100, 16, 32, 105, 300, "am4"),
        Cpu("r5_7600", "Ryzen 5 7600", 88, 60, 6, 12, 65, 170, "am5"),
        Cpu("r5_9600x", "Ryzen 5 9600X", 95, 65, 6, 12, 65, 200, "am5"),
        Cpu("r7_7700", "Ryzen 7 7700", 92, 80, 8, 16, 65, 280, "am5"),
        Cpu("r7_9700x", "Ryzen 7 9700X", 100, 85, 8, 16, 65, 330, "am5"),
        Cpu("r7_7800x3d", "Ryzen 7 7800X3D", 95, 75, 8, 16, 120, 350, "am5",
            note="best tick-per-watt for one or two modpacks"),
        Cpu("r9_7900x", "Ryzen 9 7900X", 97, 120, 12, 24, 170, 400, "am5"),
        Cpu("r9_9900x", "Ryzen 9 9900X", 105, 130, 12, 24, 120, 450, "am5"),
        Cpu("r9_9950x", "Ryzen 9 9950X", 110, 170, 16, 32, 170, 600, "am5"),
        Cpu("epyc_4344p", "EPYC 4344P", 100, 90, 8, 16, 65, 350, "am5",
            note="ECC memory support"),
        Cpu("i5_12400f", "Core i5-12400F", 85, 55, 6, 12, 65, 120, "lga1700", igpu=False),
        Cpu("i5_13400", "Core i5-13400", 90, 65, 10, 16, 65, 160, "lga1700"),
        Cpu("i5_14600k", "Core i5-14600K", 100, 90, 14, 20, 150, 250, "lga1700"),
        Cpu("i7_13700k", "Core i7-13700K", 105, 110, 16, 24, 125, 300, "lga1700"),
        Cpu("i7_14700k", "Core i7-14700K", 108, 125, 20, 28, 200, 380, "lga1700"),
        Cpu("i9_14900k", "Core i9-14900K", 115, 160, 24, 32, 250, 550, "lga1700"),
        Cpu("ultra7_265k", "Core Ultra 7 265K", 110, 140, 20, 20, 200, 400, "lga1851"),
        Cpu("ultra9_285k", "Core Ultra 9 285K", 115, 170, 24, 24, 250, 600, "lga1851"),
    )
}

RAM_OPTIONS = {
    32: 85,
    64: 160,
    96: 240,
    128: 300,
    192: 450,
    256: 600,
}

STORAGE_OPTIONS = {
    "1tb": (1, 70),
    "2tb": (2, 120),
    "4tb": (4, 220),
    "8tb": (8, 420),
}


@dataclass(frozen=True)
class Chassis:
    key: str
    name: str
    sockets: tuple[str, ...]
    base_price: int
    ram_slots: int
    max_ram_gb: int
    m2_slots: int
    sata_bays: int
    lan_gbps: float
    psu_w: int
    idle_w: int
    kind: str
    stability: float
    note: str = ""


CHASSIS: dict[str, Chassis] = {
    c.key: c
    for c in (
        Chassis("itx_am5", "Custom 8 L ITX (AM5, 2x DDR5, 2x M.2, 2.5G)",
                ("am5",), 300, 2, 96, 2, 2, 2.5, 650, 24, "sff", 0.4),
        Chassis("matx_am5", "Custom 25 L mATX (AM5, 4x DDR5, 3x M.2, 2.5G)",
                ("am5",), 320, 4, 192, 3, 4, 2.5, 850, 32, "matx", 0.45),
        Chassis("atx_am5", "Custom 45 L ATX (AM5, 4x DDR5, 4x M.2, 2.5G)",
                ("am5",), 420, 4, 192, 4, 6, 2.5, 1000, 40, "atx", 0.4),
        Chassis("itx_lga1700", "Custom 8 L ITX (LGA1700, 2x DDR5, 2x M.2, 2.5G)",
                ("lga1700",), 300, 2, 96, 2, 2, 2.5, 650, 24, "sff", 0.4),
        Chassis("matx_lga1700", "Custom 25 L mATX (LGA1700, 4x DDR5, 3x M.2, 2.5G)",
                ("lga1700",), 320, 4, 192, 3, 4, 2.5, 850, 32, "matx", 0.45),
        Chassis("atx_lga1851", "Custom 45 L ATX (LGA1851, 4x DDR5, 4x M.2, 2.5G)",
                ("lga1851",), 500, 4, 256, 4, 6, 2.5, 1000, 40, "atx", 0.4),
        Chassis("rack4u", "4U rack (AM5/LGA1700, 8x DDR5, 8x M.2, 10G)",
                ("am5", "lga1700"), 650, 8, 512, 8, 8, 10.0, 1000, 60, "rack", 0.35),
    )
}

RAM_SETS = {
    "2x16": (32, 2),
    "2x32": (64, 2),
    "2x48": (96, 2),
    "4x32": (128, 4),
    "4x48": (192, 4),
    "8x32": (256, 8),
}


@dataclass(frozen=True)
class Head:
    key: str
    name: str
    price: int
    idle_w: int
    load_w: int
    lan_gbps: float
    scheduler: float
    stability: float
    kind: str


HEADS: dict[str, Head] = {
    h.key: h
    for h in (
        Head("n100", "Beelink EQ12 (N100, 16 GB)", 260, 8, 30, 2.5, 2.0, 0.0, "mini"),
        Head("n305", "Beelink EQ12 Pro (N305, 16 GB)", 400, 10, 40, 2.5, 4.0, 0.2, "mini"),
        Head("um890", "Minisforum UM890 (Ryzen 9, 32 GB)", 640, 15, 65, 2.5, 6.0, 0.4, "mini"),
        Head("ms01", "Minisforum MS-01 (i9, 32 GB, 2x10G)", 840, 18, 90, 10.0, 8.0, 0.6, "mini"),
        Head("used_sff", "Used HP EliteDesk (i7, 32 GB)", 450, 22, 90, 1.0, 5.0, 0.0, "used"),
    )
}


@dataclass(frozen=True)
class Fabric:
    key: str
    name: str
    switch_price: int
    cable_cost: int
    adapter_cost: int
    bandwidth_gbps: float
    stability: float


FABRICS: dict[str, Fabric] = {
    f.key: f
    for f in (
        Fabric("1gbe", "1 GbE", 45, 6, 0, 1.0, -0.1),
        Fabric("2.5gbe", "2.5 GbE", 120, 8, 0, 2.5, 0.0),
        Fabric("10gbe", "10 GbE SFP+", 380, 22, 95, 10.0, 0.1),
    )
}

UPS_TIERS = ((700, 150, "900 VA"), (1100, 220, "1500 VA"), (1600, 320, "2000 VA"))


def ups_for(peak_w: float) -> tuple[int, str]:
    need = peak_w * 1.25
    for watts, price, label in UPS_TIERS:
        if need <= watts:
            return price, label
    return 420, "2200 VA"


CONTINGENCY = 0.07


@dataclass(frozen=True)
class Catalog:
    cpus: Mapping[str, Cpu]
    chassis: Mapping[str, Chassis]
    heads: Mapping[str, Head]
    fabrics: Mapping[str, Fabric]


BASE_CATALOG = Catalog(CPUS, CHASSIS, HEADS, FABRICS)
