"""Hardware catalog for the Mini-Tetra multi-Forge cluster study.

All prices are planning estimates in USD for single-unit purchases in
Nov 2026 (street/retail, tax and shipping excluded).  Treat them as
+/-15%; the evaluator supports a GPU price shock so the ranking can be
stress-tested.  Perf numbers are relative SDXL 1024x1024 throughput with
an RTX 3060 12 GB normalised to 100; they are used only to compare
candidate topologies, not as benchmark claims.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

PRICE_BASIS = (
    "USD street/retail estimates, Nov 2026, qty 1, tax/shipping excluded; "
    "assume +/-15% and re-run with --gpu-price-shock to test the ranking"
)


@dataclass(frozen=True)
class Gpu:
    key: str
    name: str
    vram_gb: int
    perf: float
    tdp_w: int
    price_usd: int
    vendor: str = "nvidia"
    form: str = "desktop"
    note: str = ""
    used: bool = False

    @property
    def idle_w(self) -> int:
        if self.tdp_w <= 100:
            return 8
        if self.tdp_w <= 200:
            return 12
        if self.tdp_w <= 320:
            return 18
        return 28


GPUS: dict[str, Gpu] = {
    g.key: g
    for g in (
        Gpu("rtx3060_12", "GeForce RTX 3060 12 GB", 12, 100, 170, 280,
            note="cheapest 12 GB; mature Ampere drivers"),
        Gpu("rtx4060_8", "GeForce RTX 4060 8 GB", 8, 115, 115, 300),
        Gpu("rtx4060ti_16", "GeForce RTX 4060 Ti 16 GB", 16, 155, 165, 470,
            note="Ada, 16 GB, 165 W"),
        Gpu("rtx5060ti_16", "GeForce RTX 5060 Ti 16 GB", 16, 175, 180, 500,
            note="Blackwell, FP4/FP8, 16 GB, 180 W"),
        Gpu("rtx4070_12", "GeForce RTX 4070 12 GB", 12, 190, 200, 550),
        Gpu("rtx5070_12", "GeForce RTX 5070 12 GB", 12, 215, 250, 620),
        Gpu("rtx4070s_12", "GeForce RTX 4070 SUPER 12 GB", 12, 225, 220, 650),
        Gpu("rtx4070tis_16", "GeForce RTX 4070 Ti SUPER 16 GB", 16, 280, 285, 850),
        Gpu("rtx5070ti_16", "GeForce RTX 5070 Ti 16 GB", 16, 300, 300, 860),
        Gpu("rtx4080s_16", "GeForce RTX 4080 SUPER 16 GB", 16, 350, 320, 1150),
        Gpu("rtx5080_16", "GeForce RTX 5080 16 GB", 16, 380, 360, 1150),
        Gpu("rtx5090_32", "GeForce RTX 5090 32 GB", 32, 560, 575, 2450),
        Gpu("rtx3090_24", "GeForce RTX 3090 24 GB (used)", 24, 330, 350, 800, used=True),
        Gpu("rtxa4000_16", "RTX A4000 16 GB (used)", 16, 170, 140, 520,
            note="blower, 140 W", used=True),
        Gpu("rtxa5000_24", "RTX A5000 24 GB (used)", 24, 300, 230, 1150, used=True),
        Gpu("rtx2000ada_16", "RTX 2000 Ada 16 GB", 16, 110, 70, 680,
            note="70 W, dual slot, fits low-profile SFF"),
        Gpu("l4_24", "NVIDIA L4 24 GB", 24, 200, 72, 1900,
            note="passive, needs server airflow"),
        Gpu("rx7900xtx_24", "Radeon RX 7900 XTX 24 GB", 24, 330, 355, 950,
            vendor="amd", note="ROCm only; gfx1100"),
        Gpu("arc_a770_16", "Arc A770 16 GB", 16, 90, 225, 300,
            vendor="intel", note="IPEX/SYCL path, extra tuning"),
        # Mobile GPUs: price is baked into the fixed platform.
        Gpu("rtx3070m_8", "GeForce RTX 3070 Mobile 8 GB (NUCXi7)", 8, 165, 130, 0,
            form="mobile"),
        Gpu("rtx4090m_16", "GeForce RTX 4090 Mobile 16 GB (Titan 18 Pro)", 16, 300, 175, 0,
            form="mobile"),
        Gpu("rx6600m_8", "Radeon RX 6600M 8 GB (HX99G)", 8, 95, 100, 0,
            vendor="amd", form="mobile"),
        Gpu("rx6650m_8", "Radeon RX 6650M 8 GB (HX100G)", 8, 105, 120, 0,
            vendor="amd", form="mobile"),
    )
}

DESKTOP_GPUS: tuple[str, ...] = tuple(
    k for k, g in GPUS.items() if g.form == "desktop"
)


@dataclass(frozen=True)
class Platform:
    """A worker node without its GPU (or with a fixed mobile GPU included)."""

    key: str
    name: str
    base_price: int
    idle_w: int
    cpu_load_w: int
    gpu_slots: int
    max_gpu_tdp: int
    gpu_choices: tuple[str, ...]
    fixed_gpu: str | None
    egpu: bool
    egpu_factor: float
    lan_gbps: float
    m2_slots: int
    psu_included_w: int
    stability_mod: float
    kind: str
    per_gpu_dock_cost: int = 0
    scheduler: float = 5.0
    note: str = ""
    used: bool = False

    @property
    def pure_mini(self) -> bool:
        return self.kind in ("mini", "mini_egpu")


def _desktop_up_to(tdp: int) -> tuple[str, ...]:
    return tuple(k for k in DESKTOP_GPUS if GPUS[k].tdp_w <= tdp)


PLATFORMS: dict[str, Platform] = {
    p.key: p
    for p in (
        Platform(
            "itx_sff",
            "Custom 8.5 L ITX node (Ryzen 5 7600, 32 GB, 1 TB, SFX PSU)",
            740, 28, 95, 1, 320, _desktop_up_to(320), None,
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=2,
            psu_included_w=650, stability_mod=0.4, kind="sff", scheduler=5,
            note="desktop GPU, serviceable, quiet at 200-300 W",
        ),
        Platform(
            "itx_dual",
            "Dual-GPU mATX cube (Ryzen 5, 32 GB, 2 TB, 1000 W ATX)",
            980, 40, 110, 2, 300, _desktop_up_to(300), None,
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=3,
            psu_included_w=1000, stability_mod=0.5, kind="sff_dual", scheduler=6,
            note="2 GPUs per chassis; best $/GPU but a shared PSU is a shared fault",
        ),
        Platform(
            "ms01",
            "Minisforum MS-01 (i9-13900H, 32 GB, 1 TB, 2x10G SFP+) + USB4 eGPU dock",
            840, 18, 90, 1, 250, _desktop_up_to(250), None,
            egpu=True, egpu_factor=0.88, lan_gbps=10, m2_slots=3,
            psu_included_w=9999, stability_mod=-0.3, kind="mini_egpu",
            per_gpu_dock_cost=240, scheduler=8,
            note="10G onboard, 3x M.2, but USB4 eGPU costs ~12% GPU throughput",
        ),
        Platform(
            "um890",
            "Minisforum UM890 Pro (Ryzen 9 8945HS, 32 GB, 1 TB) + OCuLink dock",
            640, 15, 65, 1, 250, _desktop_up_to(250), None,
            egpu=True, egpu_factor=0.97, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=-0.2, kind="mini_egpu",
            per_gpu_dock_cost=170, scheduler=6,
            note="OCuLink x4 keeps ~97% of GPU throughput; 2.5 GbE onboard",
        ),
        Platform(
            "ser8",
            "Beelink SER8 (Ryzen 7 8845HS, 32 GB, 1 TB) + USB4 eGPU dock",
            500, 14, 65, 1, 250, _desktop_up_to(250), None,
            egpu=True, egpu_factor=0.85, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=-0.5, kind="mini_egpu",
            per_gpu_dock_cost=220, scheduler=5,
            note="cheapest mini host, but USB4 eGPU is the least reliable link",
        ),
        Platform(
            "k8p",
            "GMKtec K8 Plus (Ryzen 7 8845HS, 32 GB, 1 TB) + OCuLink dock",
            520, 16, 70, 1, 250, _desktop_up_to(250), None,
            egpu=True, egpu_factor=0.97, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=-0.3, kind="mini_egpu",
            per_gpu_dock_cost=160, scheduler=5,
            note="budget OCuLink host; fewer QC hours than Minisforum",
        ),
        Platform(
            "nucxi7",
            "Minisforum NUCXi7 (i7-11800H + RTX 3070 Mobile 8 GB, 32 GB, 1 TB)",
            1050, 22, 85, 1, 200, (), "rtx3070m_8",
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=0.1, kind="mini", scheduler=5,
            note="all-in-one 8 GB CUDA node; laptop-grade cooling",
        ),
        Platform(
            "hx99g",
            "Minisforum HX99G (Ryzen 9 6900HX + RX 6600M 8 GB, 32 GB, 1 TB)",
            900, 20, 95, 1, 200, (), "rx6600m_8",
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=-1.0, kind="mini", scheduler=5,
            note="ROCm on gfx1032 needs HSA_OVERRIDE; 8 GB is the practical limit",
        ),
        Platform(
            "hx100g",
            "Minisforum HX100G (Ryzen 7 8845HS + RX 6650M 8 GB, 32 GB, 1 TB)",
            1000, 20, 95, 1, 200, (), "rx6650m_8",
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=-1.0, kind="mini", scheduler=5,
            note="same ROCm caveats as HX99G, slightly faster GPU",
        ),
        Platform(
            "titan18",
            "Minisforum Titan 18 Pro (i9-14900HX + RTX 4090 Mobile 16 GB, 32 GB, 1 TB)",
            2600, 35, 140, 1, 250, (), "rtx4090m_16",
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=2,
            psu_included_w=9999, stability_mod=-0.2, kind="mini", scheduler=7,
            note="fastest single mini, but one box eats 43% of the budget",
        ),
        Platform(
            "nuc13ext",
            "ASUS NUC 13 Extreme kit (i9-13900K, 32 GB, 1 TB, 750 W)",
            1310, 30, 125, 1, 350, _desktop_up_to(350), None,
            egpu=False, egpu_factor=1.0, lan_gbps=2.5, m2_slots=2,
            psu_included_w=750, stability_mod=0.3, kind="sff_modular", scheduler=8,
            note="desktop GPU in a 14 L chassis; strong CPU, one 2.5 GbE port",
        ),
        Platform(
            "office_sff",
            "Used HP EliteDesk 800 G6 SFF (i7-10700, 32 GB, 1 TB)",
            380, 25, 90, 1, 200, ("rtx2000ada_16",), None,
            egpu=False, egpu_factor=1.0, lan_gbps=1.0, m2_slots=1,
            psu_included_w=400, stability_mod=-0.2, kind="used_sff", scheduler=5,
            note="cheap 16 GB 70 W node; single M.2 and 1 GbE hold it back",
            used=True,
        ),
    )
}


@dataclass(frozen=True)
class HeadNode:
    key: str
    name: str
    price: int
    idle_w: int
    load_w: int
    m2_slots: int
    lan_gbps: float
    sfp10: bool
    scheduler: float
    has_gpu: str | None
    stability_mod: float
    kind: str
    note: str = ""


HEADS: dict[str, HeadNode] = {
    h.key: h
    for h in (
        HeadNode("n100", "Beelink EQ12 (N100, 16 GB, 500 GB)", 260, 8, 30,
                 1, 2.5, False, 2.0, None, 0.0, "mini",
                 "cheap and silent, but one M.2, 16 GB RAM and a weak scheduler"),
        HeadNode("n305", "Beelink EQ12 Pro (i3-N305, 16 GB, 500 GB)", 400, 10, 40,
                 2, 2.5, False, 3.5, None, 0.1, "mini",
                 "2x M.2 and 2x 2.5 GbE; the cheapest credible head"),
        HeadNode("used_sff", "Used HP EliteDesk 800 G6 (i7-10700, 32 GB, 1 TB)", 450, 22, 90,
                 2, 1.0, False, 5.0, None, 0.0, "used",
                 "plenty of CPU/RAM for NFS and a queue, but only 1 GbE"),
        HeadNode("ser8_head", "Beelink SER8 (Ryzen 7 8845HS, 32 GB, 1 TB)", 500, 14, 65,
                 2, 2.5, False, 5.0, None, 0.2, "mini"),
        HeadNode("um890_head", "Minisforum UM890 Pro (Ryzen 9 8945HS, 32 GB, 1 TB)", 640, 15, 65,
                 2, 2.5, False, 6.0, None, 0.4, "mini",
                 "the value sweet spot: 2x M.2, 2.5 GbE, 15 W idle"),
        HeadNode("ms01_head", "Minisforum MS-01 (i9-13900H, 32 GB, 2 TB, 2x10G SFP+)", 840, 18, 90,
                 3, 10.0, True, 8.0, None, 0.6, "mini",
                 "10G + 3x M.2 + remote management; the stable default"),
        HeadNode("nuc13_head", "ASUS NUC 13 Extreme (i9-13900K, 32 GB, 2 TB)", 1310, 30, 125,
                 2, 2.5, False, 8.0, None, 0.5, "sff_modular",
                 "desktop-class CPU, PCIe slot for a 10G NIC, but 30 W idle"),
        HeadNode("ws_4060ti", "Workstation head: ITX base + RTX 4060 Ti 16 GB", 1240, 40, 190,
                 2, 2.5, False, 7.0, "rtx4060ti_16", 0.5, "workstation",
                 "adds one 16 GB worker and an interactive seat; shares fate with the queue"),
        HeadNode("ws_4070tis", "Workstation head: ITX base + RTX 4070 Ti SUPER 16 GB", 1610, 48, 260,
                 2, 2.5, False, 7.0, "rtx4070tis_16", 0.4, "workstation",
                 "fastest head option; costs more than two dedicated nodes"),
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
    slope: float
    floor: float
    stability: float

    def factor(self, gpus: int) -> float:
        return max(self.floor, 1.0 - self.slope * max(0, gpus - 1))


FABRICS: dict[str, Fabric] = {
    f.key: f
    for f in (
        Fabric("1gbe", "1 GbE (existing/cheap switch)", 45, 6, 0, 1.0, 0.050, 0.75, -0.1),
        Fabric("2.5gbe", "2.5 GbE (8-port 2.5G switch)", 120, 8, 25, 2.5, 0.015, 0.92, 0.0),
        Fabric("10gbe", "10 GbE SFP+ (CRS310 + DACs)", 380, 22, 95, 10.0, 0.004, 0.97, 0.0),
    )
}


@dataclass(frozen=True)
class Storage:
    key: str
    name: str
    cost: int
    stability: float
    throughput: float
    note: str = ""


STORAGE: dict[str, Storage] = {
    s.key: s
    for s in (
        Storage("local", "Per-node NVMe, models duplicated", 0, -0.25, 0.97,
                "no shared cache; 4x 60 GB of checkpoints to keep in sync"),
        Storage("shared_nvme", "4 TB NVMe model cache in head, exported over NFS/SMB", 260, 0.35, 1.0,
                "single source of truth for checkpoints, LoRAs and outputs"),
        Storage("nas", "8 TB mirrored NAS (2x8 TB HDD) + 2.5 GbE", 470, 0.45, 0.99,
                "archive-grade, but cold model loads are slower than NVMe"),
    )
}

CONTINGENCY = 0.07


@dataclass(frozen=True)
class Catalog:
    """An immutable view of the hardware that a search may use."""

    gpus: Mapping[str, Gpu]
    platforms: Mapping[str, Platform]
    heads: Mapping[str, HeadNode]
    fabrics: Mapping[str, Fabric]
    storage: Mapping[str, Storage]


BASE_CATALOG = Catalog(GPUS, PLATFORMS, HEADS, FABRICS, STORAGE)
