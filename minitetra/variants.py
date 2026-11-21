"""~500 additional hardware models and custom-PC variants.

The base catalog covers one representative card per GPU class and one chassis
per form factor. This module adds board-partner cards, used/workstation GPUs,
mobile minis, and a large matrix of custom 1-4 GPU PCs built from CPU/RAM/PSU/
case combinations. Dominance pruning keeps the exhaustive search tractable.
"""

from __future__ import annotations

from .catalog import (
    BASE_CATALOG,
    FABRICS,
    GPUS,
    HEADS,
    PLATFORMS,
    STORAGE,
    Catalog,
    Fabric,
    Gpu,
    HeadNode,
    Platform,
    Storage,
)

ASSEMBLY = 50

FABRICS_EXTRA = {
    "5gbe": Fabric("5gbe", "5 GbE (8-port 5G switch)", 250, 10, 45, 5.0, 0.008, 0.96, -0.1),
    "25gbe": Fabric("25gbe", "25 GbE SFP28 (CRS326 + DACs)", 700, 35, 180, 25.0, 0.002, 0.98, 0.0),
}

STORAGE_EXTRA = {
    "nvme_raid": Storage("nvme_raid", "2x 4 TB NVMe RAID 0 cache", 520, 0.45, 1.0,
                         "faster cold loads, but a RAID 0 failure loses the cache"),
    "san": Storage("san", "8 TB iSCSI SAN over 10/25G", 900, 0.50, 0.99,
                   "centralised and snapshot-capable; higher latency than local NVMe"),
}
DESKTOP_KEYS = tuple(k for k, g in GPUS.items() if g.form == "desktop")

AIB = (
    ("asus", "ASUS TUF", 1.06, 1.005, 5),
    ("msi", "MSI Gaming X", 1.10, 1.01, 10),
    ("gigabyte", "Gigabyte Windforce", 0.98, 1.0, 0),
    ("zotac", "Zotac Twin Edge", 0.95, 0.995, -5),
    ("pny", "PNY Verto", 1.00, 0.995, 0),
    ("palit", "Palit GamingPro", 0.96, 1.0, 0),
    ("asus_dual", "ASUS Dual", 1.03, 1.0, 0),
    ("oc", "OC Edition", 1.05, 1.02, 10),
    ("silent", "Silent Edition", 0.99, 0.99, -10),
    ("compact", "Compact Edition", 1.0, 0.98, -15),
)

AIB_BASES = (
    "rtx3060_12", "rtx4060_8", "rtx4060ti_16", "rtx5060ti_16", "rtx4070_12",
    "rtx5070_12", "rtx4070s_12", "rtx4070tis_16", "rtx5070ti_16",
    "rtx4080s_16", "rtx5080_16", "rtx5090_32", "rtx3090_24",
    "rtxa4000_16", "rtxa5000_24", "rtx2000ada_16", "l4_24",
    "rx7900xtx_24", "arc_a770_16",
)


def _aib_gpus() -> dict[str, Gpu]:
    out: dict[str, Gpu] = {}
    for base_key in AIB_BASES:
        base = GPUS[base_key]
        for suffix, brand, price_mul, perf_mul, tdp_delta in AIB:
            key = f"{base_key}_{suffix}"
            if key in out or key in GPUS:
                continue
            out[key] = Gpu(
                key=key,
                name=f"{base.name} — {brand}",
                vram_gb=base.vram_gb,
                perf=round(base.perf * perf_mul, 1),
                tdp_w=max(50, base.tdp_w + tdp_delta),
                price_usd=round(base.price_usd * price_mul),
                vendor=base.vendor,
                form="desktop",
                note=f"AIB variant of {base_key}",
                used=base.used,
            )
    return out
EXTRA_GPUS = (
    ("rtx2080ti_11", "GeForce RTX 2080 Ti 11 GB (used)", 11, 200, 250, 260, "nvidia", True),
    ("rtx3080_10", "GeForce RTX 3080 10 GB (used)", 10, 260, 320, 340, "nvidia", True),
    ("rtx3080_12", "GeForce RTX 3080 12 GB (used)", 12, 270, 350, 390, "nvidia", True),
    ("rtx3080ti_12", "GeForce RTX 3080 Ti 12 GB (used)", 12, 290, 350, 450, "nvidia", True),
    ("rtxa2000_12", "RTX A2000 12 GB (used)", 12, 110, 70, 350, "nvidia", True),
    ("rtxa6000_48", "RTX A6000 48 GB (used)", 48, 380, 300, 2300, "nvidia", True),
    ("quadro_rtx5000_16", "Quadro RTX 5000 16 GB (used)", 16, 150, 265, 450, "nvidia", True),
    ("quadro_rtx6000_24", "Quadro RTX 6000 24 GB (used)", 24, 220, 295, 900, "nvidia", True),
    ("tesla_p40_24", "Tesla P40 24 GB (used)", 24, 60, 250, 250, "nvidia", True),
    ("tesla_p100_16", "Tesla P100 16 GB (used)", 16, 70, 250, 200, "nvidia", True),
    ("tesla_v100_16", "Tesla V100 16 GB (used)", 16, 120, 250, 300, "nvidia", True),
    ("tesla_v100_32", "Tesla V100 32 GB (used)", 32, 140, 300, 600, "nvidia", True),
    ("l40s_48", "NVIDIA L40S 48 GB", 48, 420, 350, 4500, "nvidia", False),
    ("a10_24", "NVIDIA A10 24 GB (used)", 24, 230, 150, 1200, "nvidia", True),
    ("a40_48", "NVIDIA A40 48 GB (used)", 48, 320, 300, 2500, "nvidia", True),
    ("rtx4000ada_20", "RTX 4000 Ada 20 GB", 20, 160, 130, 900, "nvidia", False),
    ("rtx5000ada_32", "RTX 5000 Ada 32 GB", 32, 320, 250, 1800, "nvidia", False),
    ("rtx6000ada_48", "RTX 6000 Ada 48 GB", 48, 450, 300, 4000, "nvidia", False),
    ("rtx4000sff_20", "RTX 4000 SFF Ada 20 GB", 20, 150, 70, 1100, "nvidia", False),
    ("rx6800xt_16", "Radeon RX 6800 XT 16 GB (used)", 16, 300, 300, 350, "amd", True),
    ("rx6900xt_16", "Radeon RX 6900 XT 16 GB (used)", 16, 320, 300, 400, "amd", True),
    ("rx6950xt_16", "Radeon RX 6950 XT 16 GB (used)", 16, 330, 335, 450, "amd", True),
    ("mi50_32", "Radeon Instinct MI50 32 GB (used)", 32, 180, 300, 300, "amd", True),
    ("mi100_32", "Radeon Instinct MI100 32 GB (used)", 32, 250, 300, 600, "amd", True),
    ("arc_a750_8", "Arc A750 8 GB", 8, 85, 225, 180, "intel", False),
    ("arc_a580_8", "Arc A580 8 GB", 8, 75, 185, 150, "intel", False),
    ("arc_b580_12", "Arc B580 12 GB", 12, 110, 190, 250, "intel", False),
    ("rtx5060_8", "GeForce RTX 5060 8 GB", 8, 100, 145, 330, "nvidia", False),
    ("rtx5060ti_8", "GeForce RTX 5060 Ti 8 GB", 8, 165, 180, 430, "nvidia", False),
    ("rx9060xt_16", "Radeon RX 9060 XT 16 GB", 16, 165, 160, 350, "amd", False),
    ("rx9070_16", "Radeon RX 9070 16 GB", 16, 260, 220, 600, "amd", False),
    ("rx9070xt_16", "Radeon RX 9070 XT 16 GB", 16, 290, 300, 700, "amd", False),
    ("rtx2080s_8", "GeForce RTX 2080 SUPER 8 GB (used)", 8, 180, 250, 220, "nvidia", True),
    ("rtx2080_8", "GeForce RTX 2080 8 GB (used)", 8, 165, 215, 190, "nvidia", True),
    ("rtx2070s_8", "GeForce RTX 2070 SUPER 8 GB (used)", 8, 150, 215, 170, "nvidia", True),
    ("rtx2060s_8", "GeForce RTX 2060 SUPER 8 GB (used)", 8, 130, 175, 150, "nvidia", True),
    ("rtx2060_6", "GeForce RTX 2060 6 GB (used)", 6, 110, 160, 120, "nvidia", True),
    ("gtx1080ti_11", "GeForce GTX 1080 Ti 11 GB (used)", 11, 130, 250, 180, "nvidia", True),
    ("gtx1080_8", "GeForce GTX 1080 8 GB (used)", 8, 100, 180, 120, "nvidia", True),
    ("rtx3070_8", "GeForce RTX 3070 8 GB (used)", 8, 200, 220, 300, "nvidia", True),
    ("rtx3070ti_8", "GeForce RTX 3070 Ti 8 GB (used)", 8, 215, 290, 340, "nvidia", True),
    ("rtx3060ti_8", "GeForce RTX 3060 Ti 8 GB (used)", 8, 160, 200, 240, "nvidia", True),
    ("rtx4060ti_8", "GeForce RTX 4060 Ti 8 GB", 8, 150, 160, 400, "nvidia", False),
    ("rtx4070ti_12", "GeForce RTX 4070 Ti 12 GB (used)", 12, 250, 285, 550, "nvidia", True),
    ("rtx4080_16", "GeForce RTX 4080 16 GB (used)", 16, 330, 320, 800, "nvidia", True),
    ("rx6700xt_12", "Radeon RX 6700 XT 12 GB (used)", 12, 220, 230, 240, "amd", True),
    ("rx6750xt_12", "Radeon RX 6750 XT 12 GB (used)", 12, 230, 250, 270, "amd", True),
    ("rx6800_16", "Radeon RX 6800 16 GB (used)", 16, 280, 250, 300, "amd", True),
    ("rx7700xt_12", "Radeon RX 7700 XT 12 GB", 12, 230, 245, 380, "amd", False),
    ("rx7800xt_16", "Radeon RX 7800 XT 16 GB", 16, 270, 263, 480, "amd", False),
    ("rx7900gre_16", "Radeon RX 7900 GRE 16 GB", 16, 300, 260, 520, "amd", False),
    ("rx7900xt_20", "Radeon RX 7900 XT 20 GB", 20, 320, 315, 700, "amd", False),
    ("arc_b570_10", "Arc B570 10 GB", 10, 95, 150, 210, "intel", False),
    ("rtxa4500_20", "RTX A4500 20 GB (used)", 20, 220, 200, 900, "nvidia", True),
    ("rtxa5500_24", "RTX A5500 24 GB (used)", 24, 300, 230, 1300, "nvidia", True),
    ("rtxa30_24", "NVIDIA A30 24 GB (used)", 24, 260, 165, 1100, "nvidia", True),
    ("a100_40", "NVIDIA A100 40 GB (used)", 40, 500, 250, 4500, "nvidia", True),
    ("a100_80", "NVIDIA A100 80 GB (used)", 80, 560, 300, 9000, "nvidia", True),
    ("l40_48", "NVIDIA L40 48 GB", 48, 400, 300, 3500, "nvidia", False),
    ("tesla_t4_16", "Tesla T4 16 GB (used)", 16, 90, 70, 400, "nvidia", True),
    ("tesla_p4_8", "Tesla P4 8 GB (used)", 8, 40, 75, 120, "nvidia", True),
)

MOBILE_GPUS = (
    ("rtx4060m_8", "GeForce RTX 4060 Mobile 8 GB", 8, 110, 115, 0, "nvidia"),
    ("rtx4070m_8", "GeForce RTX 4070 Mobile 8 GB", 8, 140, 115, 0, "nvidia"),
    ("rtx4080m_12", "GeForce RTX 4080 Mobile 12 GB", 12, 190, 150, 0, "nvidia"),
    ("rtx5080m_16", "GeForce RTX 5080 Mobile 16 GB", 16, 260, 175, 0, "nvidia"),
    ("rtx5090m_24", "GeForce RTX 5090 Mobile 24 GB", 24, 340, 200, 0, "nvidia"),
    ("rtx3080m_16", "GeForce RTX 3080 Mobile 16 GB", 16, 200, 165, 0, "nvidia"),
    ("rx7600mxt_8", "Radeon RX 7600M XT 8 GB", 8, 130, 120, 0, "amd"),
    ("rx7700s_8", "Radeon RX 7700S 8 GB", 8, 120, 100, 0, "amd"),
    ("rx7900m_16", "Radeon RX 7900M 16 GB", 16, 260, 180, 0, "amd"),
    ("arc_a730m_12", "Arc A730M 12 GB", 12, 70, 120, 0, "intel"),
    ("m4_24", "Apple M4 24 GB unified", 24, 60, 40, 0, "apple"),
    ("rtx4050m_6", "GeForce RTX 4050 Mobile 6 GB", 6, 80, 90, 0, "nvidia"),
    ("rtx5070m_8", "GeForce RTX 5070 Mobile 8 GB", 8, 180, 115, 0, "nvidia"),
    ("rx7600s_8", "Radeon RX 7600S 8 GB", 8, 115, 90, 0, "amd"),
    ("rx7800m_12", "Radeon RX 7800M 12 GB", 12, 200, 180, 0, "amd"),
    ("arc_a570m_8", "Arc A570M 8 GB", 8, 60, 95, 0, "intel"),
)


def _extra_gpus() -> dict[str, Gpu]:
    out: dict[str, Gpu] = {}
    for key, name, vram, perf, tdp, price, vendor, used in EXTRA_GPUS:
        out[key] = Gpu(
            key=key, name=name, vram_gb=vram, perf=perf, tdp_w=tdp,
            price_usd=price, vendor=vendor, form="desktop", used=used,
        )
    for key, name, vram, perf, tdp, price, vendor in MOBILE_GPUS:
        out[key] = Gpu(
            key=key, name=name, vram_gb=vram, perf=perf, tdp_w=tdp,
            price_usd=price, vendor=vendor, form="mobile",
        )
    return out

CPUS = (
    ("r5_7600", "Ryzen 5 7600", 170, 95, 5),
    ("r5_9600x", "Ryzen 5 9600X", 200, 95, 5),
    ("r7_7700x", "Ryzen 7 7700X", 280, 120, 6),
    ("r7_9700x", "Ryzen 7 9700X", 330, 120, 6),
    ("r7_7800x3d", "Ryzen 7 7800X3D", 350, 120, 6),
    ("r9_7900x", "Ryzen 9 7900X", 400, 170, 7),
    ("r9_9900x", "Ryzen 9 9900X", 450, 170, 7),
    ("i5_14400", "Core i5-14400", 180, 110, 5),
    ("i5_14600k", "Core i5-14600K", 250, 150, 6),
    ("i7_14700k", "Core i7-14700K", 380, 200, 7),
    ("i9_14900k", "Core i9-14900K", 550, 250, 8),
    ("ultra7_265k", "Core Ultra 7 265K", 400, 200, 7),
)

RAM = ((32, 85), (64, 160))
SSD = ((1, 70), (2, 120))
PSU = ((650, 100), (850, 140), (1000, 180), (1300, 250), (1600, 400))

FORMS = {
    "itx": dict(mobo=200, m2=2, case=100, idle=25, cooler=35, fans=25,
                lan=2.5, slots=(1,), psus=(650, 850), stability=0.4,
                kind="sff", max_tdp=300),
    "matx": dict(mobo=150, m2=3, case=90, idle=35, cooler=35, fans=30,
                 lan=2.5, slots=(1, 2), psus=(650, 850, 1000), stability=0.45,
                 kind="sff_dual", max_tdp=320),
    "atx": dict(mobo=250, m2=4, case=120, idle=50, cooler=45, fans=40,
                lan=2.5, slots=(2, 4), psus=(1000, 1300, 1600), stability=0.35,
                kind="tower", max_tdp=400),
    "rack": dict(mobo=450, m2=4, case=250, idle=70, cooler=80, fans=60,
                 lan=10, slots=(2, 4), psus=(1300, 1600), stability=0.3,
                 kind="rack", max_tdp=400),
}

CPU_SETS = {
    "itx": CPUS[:4],
    "matx": (CPUS[0], CPUS[2], CPUS[7], CPUS[8]),
    "atx": (CPUS[1], CPUS[3], CPUS[4], CPUS[5], CPUS[8], CPUS[10]),
    "rack": (CPUS[5], CPUS[6], CPUS[11]),
}


def _custom_platforms(gpus: dict[str, Gpu]) -> dict[str, Platform]:
    out: dict[str, Platform] = {}
    for form, spec in FORMS.items():
        choices = tuple(
            k for k, g in gpus.items()
            if g.form == "desktop" and g.tdp_w <= spec["max_tdp"]
        )
        for cpu_key, cpu_name, cpu_price, cpu_w, sched in CPU_SETS[form]:
            for ram_gb, ram_price in RAM:
                for ssd_tb, ssd_price in SSD:
                    if form == "itx" and ssd_tb == 4:
                        continue
                    for psu_w, psu_price in PSU:
                        if psu_w not in spec["psus"]:
                            continue
                        for slots in spec["slots"]:
                            if slots > 2 and psu_w < 1600:
                                continue
                            if slots > 1 and ram_gb < 32:
                                continue
                            base = (
                                cpu_price + spec["mobo"] + ram_price + ssd_price
                                + psu_price + spec["case"] + spec["cooler"]
                                + spec["fans"] + ASSEMBLY
                            )
                            stability = spec["stability"] - (0.1 if slots > 2 else 0.0)
                            key = (
                                f"{form}_{cpu_key}_{ram_gb}g_{ssd_tb}t_"
                                f"{psu_w}w_{slots}g"
                            )
                            out[key] = Platform(
                                key=key,
                                name=(f"Custom {form.upper()} PC — {cpu_name}, "
                                      f"{ram_gb} GB, {ssd_tb} TB, {psu_w} W, "
                                      f"{slots} GPU"),
                                base_price=base,
                                idle_w=spec["idle"],
                                cpu_load_w=cpu_w,
                                gpu_slots=slots,
                                max_gpu_tdp=spec["max_tdp"],
                                gpu_choices=choices,
                                fixed_gpu=None,
                                egpu=False,
                                egpu_factor=1.0,
                                lan_gbps=spec["lan"],
                                m2_slots=spec["m2"],
                                psu_included_w=psu_w,
                                stability_mod=stability,
                                kind=spec["kind"],
                                scheduler=float(sched),
                                note=f"custom {form} build; {slots} GPU slot(s)",
                            )
    return out

EXTRA_CPUS = (
    ("r5_5600", "Ryzen 5 5600", 110, 65, 5),
    ("r7_5700x3d", "Ryzen 7 5700X3D", 180, 105, 6),
    ("r9_5950x", "Ryzen 9 5950X", 300, 105, 7),
    ("i3_14100", "Core i3-14100", 120, 60, 4),
    ("i5_13400", "Core i5-13400", 160, 65, 5),
    ("i7_13700k", "Core i7-13700K", 300, 125, 6),
    ("i9_13900k", "Core i9-13900K", 450, 125, 7),
    ("ultra5_245k", "Core Ultra 5 245K", 300, 125, 6),
    ("ultra9_285k", "Core Ultra 9 285K", 600, 250, 8),
    ("xeon_4310", "Xeon Silver 4310", 300, 120, 7),
    ("xeon_6248", "Xeon Gold 6248", 500, 150, 8),
    ("tr_7960x", "Threadripper 7960X", 1200, 350, 8),
)

EXTRA_FORMS = {
    "itx2": dict(mobo=210, m2=2, case=110, idle=24, cooler=35, fans=25,
                 lan=2.5, slots=(1,), psus=(450, 650, 850), stability=0.4,
                 kind="sff", max_tdp=300),
    "matx2": dict(mobo=160, m2=3, case=95, idle=34, cooler=35, fans=30,
                  lan=2.5, slots=(1, 2), psus=(650, 850, 1000), stability=0.45,
                  kind="sff_dual", max_tdp=320),
    "atx2": dict(mobo=260, m2=4, case=130, idle=48, cooler=45, fans=40,
                 lan=2.5, slots=(1, 2, 4), psus=(850, 1000, 1300, 1600, 2000),
                 stability=0.35, kind="tower", max_tdp=400),
    "rack4u2": dict(mobo=460, m2=4, case=260, idle=68, cooler=80, fans=60,
                    lan=10.0, slots=(2, 4), psus=(1300, 1600, 2000),
                    stability=0.3, kind="rack", max_tdp=400),
    "rack2u2": dict(mobo=420, m2=2, case=220, idle=58, cooler=70, fans=50,
                    lan=10.0, slots=(2, 4), psus=(1000, 1300, 1600),
                    stability=0.25, kind="rack", max_tdp=350),
    "open2": dict(mobo=180, m2=1, case=60, idle=60, cooler=45, fans=50,
                  lan=2.5, slots=(2, 4, 6, 8), psus=(1000, 1600, 2000),
                  stability=0.1, kind="open", max_tdp=400),
}

EXTRA_CPU_SETS = {
    "itx2": EXTRA_CPUS[:6],
    "matx2": (EXTRA_CPUS[0], EXTRA_CPUS[1], EXTRA_CPUS[4], EXTRA_CPUS[5],
              EXTRA_CPUS[7], EXTRA_CPUS[8]),
    "atx2": (EXTRA_CPUS[1], EXTRA_CPUS[2], EXTRA_CPUS[4], EXTRA_CPUS[5],
             EXTRA_CPUS[6], EXTRA_CPUS[8], EXTRA_CPUS[9], EXTRA_CPUS[11]),
    "rack4u2": (EXTRA_CPUS[2], EXTRA_CPUS[9], EXTRA_CPUS[10], EXTRA_CPUS[11]),
    "rack2u2": (EXTRA_CPUS[1], EXTRA_CPUS[5], EXTRA_CPUS[9], EXTRA_CPUS[11]),
    "open2": (EXTRA_CPUS[2], EXTRA_CPUS[6], EXTRA_CPUS[9], EXTRA_CPUS[11]),
}

EXTRA_RAM = ((16, 50), (32, 85), (64, 160))
EXTRA_SSD = ((1, 70), (2, 120))


def _more_custom_platforms(gpus: dict[str, Gpu]) -> dict[str, Platform]:
    """A second, wider matrix of custom PCs (more CPUs, slots and chassis)."""
    out: dict[str, Platform] = {}
    for form, spec in EXTRA_FORMS.items():
        choices = tuple(
            k for k, g in gpus.items()
            if g.form == "desktop" and g.tdp_w <= spec["max_tdp"]
        )
        for cpu_key, cpu_name, cpu_price, cpu_w, sched in EXTRA_CPU_SETS[form]:
            for ram_gb, ram_price in EXTRA_RAM:
                for ssd_tb, ssd_price in EXTRA_SSD:
                    for psu_w, psu_price in PSU:
                        if psu_w not in spec["psus"]:
                            continue
                        for slots in spec["slots"]:
                            if slots > 2 and psu_w < 1000:
                                continue
                            if slots >= 6 and psu_w < 1600:
                                continue
                            if slots > 1 and ram_gb < 32:
                                continue
                            base = (
                                cpu_price + spec["mobo"] + ram_price + ssd_price
                                + psu_price + spec["case"] + spec["cooler"]
                                + spec["fans"] + ASSEMBLY
                            )
                            stability = spec["stability"] - (0.1 if slots > 2 else 0.0)
                            key = (
                                f"x{form}_{cpu_key}_{ram_gb}g_{ssd_tb}t_"
                                f"{psu_w}w_{slots}g"
                            )
                            out[key] = Platform(
                                key=key,
                                name=(f"Custom {form.upper()} PC — {cpu_name}, "
                                      f"{ram_gb} GB, {ssd_tb} TB, {psu_w} W, "
                                      f"{slots} GPU"),
                                base_price=base,
                                idle_w=spec["idle"],
                                cpu_load_w=cpu_w,
                                gpu_slots=slots,
                                max_gpu_tdp=spec["max_tdp"],
                                gpu_choices=choices,
                                fixed_gpu=None,
                                egpu=False,
                                egpu_factor=1.0,
                                lan_gbps=spec["lan"],
                                m2_slots=spec["m2"],
                                psu_included_w=psu_w,
                                stability_mod=stability,
                                kind=spec["kind"],
                                scheduler=float(sched),
                                note=f"wide custom {form} build; {slots} GPU slot(s)",
                            )
    return out

MINIS = (
    ("um760", "Minisforum UM760 (Ryzen 5 7640HS) + OCuLink", 420, 14, 65, 250, 2.5, 2, None, True, 160, 0.97, -0.2, "mini_egpu"),
    ("um870", "Minisforum UM870 (Ryzen 7 8745H) + OCuLink", 560, 14, 65, 250, 2.5, 2, None, True, 170, 0.97, -0.2, "mini_egpu"),
    ("um880", "Minisforum UM880 (Ryzen 7 8845HS) + OCuLink", 620, 14, 65, 250, 2.5, 2, None, True, 170, 0.97, -0.2, "mini_egpu"),
    ("um890v2", "Minisforum UM890 Pro (Ryzen 9 8945HS) + OCuLink", 660, 15, 65, 250, 2.5, 2, None, True, 170, 0.97, -0.2, "mini_egpu"),
    ("ms01v2", "Minisforum MS-01 (i9-13900H) + USB4 dock", 860, 18, 90, 250, 10.0, 3, None, True, 240, 0.88, -0.3, "mini_egpu"),
    ("ms_a2", "Minisforum MS-A2 (Ryzen 9 9955HX) + OCuLink", 780, 20, 90, 250, 10.0, 3, None, True, 200, 0.97, -0.2, "mini_egpu"),
    ("ser6", "Beelink SER6 (Ryzen 7 7735HS) + USB4", 420, 14, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("ser7", "Beelink SER7 (Ryzen 7 7840HS) + USB4", 500, 14, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("ser8v2", "Beelink SER8 (Ryzen 7 8845HS) + USB4", 520, 14, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("ser9", "Beelink SER9 (Ryzen AI 9 HX 370) + USB4", 620, 14, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("gtr7", "Beelink GTR7 (Ryzen 7 7840HS) + USB4", 600, 16, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("gtr9", "Beelink GTR9 (Ryzen AI 9 HX 370) + USB4", 750, 16, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("k6", "GMKtec K6 (Ryzen 5 7640HS) + OCuLink", 350, 15, 70, 250, 2.5, 2, None, True, 160, 0.97, -0.3, "mini_egpu"),
    ("k8pv2", "GMKtec K8 Plus (Ryzen 7 8845HS) + OCuLink", 540, 16, 70, 250, 2.5, 2, None, True, 160, 0.97, -0.3, "mini_egpu"),
    ("k10", "GMKtec K10 (Ryzen 7 8845HS) + OCuLink", 650, 16, 70, 250, 2.5, 2, None, True, 160, 0.97, -0.3, "mini_egpu"),
    ("m7", "GMKtec M7 (Ryzen 7 6800H) + OCuLink", 450, 15, 70, 250, 2.5, 2, None, True, 160, 0.97, -0.3, "mini_egpu"),
    ("a7", "Geekom A7 (Ryzen 7 7840HS) + USB4", 550, 14, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("a8", "Geekom A8 (Ryzen 7 8845HS) + USB4", 650, 14, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("gt13", "Geekom GT13 (i9-13900H) + USB4", 700, 18, 90, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("nuc14pro", "ASUS NUC 14 Pro (Core Ultra 7) + USB4", 650, 15, 65, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("nuc14proplus", "ASUS NUC 14 Pro+ (Core Ultra 9) + USB4", 800, 18, 90, 250, 2.5, 2, None, True, 220, 0.85, -0.5, "mini_egpu"),
    ("f3a", "AceMagic F3A (Ryzen 7 8845HS) + OCuLink", 450, 16, 70, 250, 2.5, 2, None, True, 160, 0.97, -0.3, "mini_egpu"),
    ("s1", "AceMagic S1 (i9-13900H) + OCuLink", 520, 18, 90, 250, 2.5, 2, None, True, 160, 0.97, -0.3, "mini_egpu"),
    ("nucxi9", "Minisforum NUCXi9 (i9-13900H + RTX 3080 Mobile 16 GB)", 1250, 24, 90, 200, 2.5, 2, "rtx3080m_16", False, 0, 1.0, 0.1, "mini"),
    ("g7pt", "Minisforum G7 Pt (Ryzen 9 7945HX + RX 7600M XT)", 1150, 22, 90, 200, 2.5, 2, "rx7600mxt_8", False, 0, 1.0, -0.8, "mini"),
    ("titan18v2", "Minisforum Titan 18 Pro (RTX 5090 Mobile 24 GB)", 2800, 35, 140, 250, 2.5, 2, "rtx5090m_24", False, 0, 1.0, -0.2, "mini"),
    ("z2mini", "HP Z2 Mini G9 (i7-14700 + RTX A2000 12 GB)", 1100, 30, 125, 200, 2.5, 2, "rtxa2000_12", False, 0, 1.0, 0.1, "mini"),
    ("precision3260", "Dell Precision 3260 (i7-13700 + RTX A2000 12 GB)", 950, 28, 125, 200, 2.5, 2, "rtxa2000_12", False, 0, 1.0, 0.1, "mini"),
    ("p360tiny", "Lenovo P360 Tiny (i7-12700 + RTX A2000 12 GB)", 900, 28, 125, 200, 2.5, 2, "rtxa2000_12", False, 0, 1.0, 0.1, "mini"),
    ("macmini_m4", "Apple Mac mini M4 24 GB", 800, 10, 40, 100, 1.0, 1, "m4_24", False, 0, 1.0, -2.0, "mini"),
    ("minisforum_790m", "Minisforum 790M (Ryzen 9 7945HX + RX 7900M)", 1600, 28, 90, 250, 2.5, 2, "rx7900m_16", False, 0, 1.0, -0.8, "mini"),
)


def _mini_platforms(gpus: dict[str, Gpu]) -> dict[str, Platform]:
    out: dict[str, Platform] = {}
    for (key, name, price, idle, cpu_w, max_tdp, lan, m2, fixed,
         egpu, dock, factor, stability, kind) in MINIS:
        choices = () if fixed else tuple(
            k for k, g in gpus.items()
            if g.form == "desktop" and g.tdp_w <= max_tdp
        )
        out[key] = Platform(
            key=key, name=name, base_price=price, idle_w=idle, cpu_load_w=cpu_w,
            gpu_slots=1, max_gpu_tdp=max_tdp, gpu_choices=choices,
            fixed_gpu=fixed, egpu=egpu, egpu_factor=factor, lan_gbps=lan,
            m2_slots=m2, psu_included_w=9999, stability_mod=stability,
            kind=kind, per_gpu_dock_cost=dock, scheduler=6.0,
            note="mini PC variant",
        )
    return out

USED_PLATFORMS = (
    ("dell_7920", "Used Dell Precision 7920 (2x Xeon Silver, 4U)", 1100, 90, 220, 4, 400, 2.5, 4, 1300, -0.2, "used_tower"),
    ("hp_z8g4", "Used HP Z8 G4 (2x Xeon Silver, 4U)", 1000, 85, 200, 4, 400, 2.5, 4, 1300, -0.2, "used_tower"),
    ("dell_3640", "Used Dell Precision 3640 (i7-10700)", 650, 50, 120, 2, 350, 2.5, 3, 1000, -0.1, "used_tower"),
    ("hp_z2g9", "Used HP Z2 G9 (i7-12700)", 800, 55, 125, 2, 350, 2.5, 3, 1000, -0.1, "used_tower"),
    ("lenovo_p360", "Used Lenovo P360 (i7-12700)", 600, 50, 120, 2, 350, 2.5, 3, 1000, -0.1, "used_tower"),
    ("dell_r730", "Used Dell PowerEdge R730 (2x Xeon, 4U)", 900, 120, 220, 4, 400, 10.0, 4, 1300, -0.3, "rack"),
    ("hp_dl380", "Used HP DL380 G9 (2x Xeon, 2U)", 950, 130, 240, 4, 400, 10.0, 4, 1300, -0.3, "rack"),
    ("supermicro_4u", "Used Supermicro 4U GPU server", 1200, 140, 250, 4, 450, 10.0, 4, 1600, -0.2, "rack"),
)


def _used_platforms(gpus: dict[str, Gpu]) -> dict[str, Platform]:
    out: dict[str, Platform] = {}
    for (key, name, price, idle, cpu_w, slots, max_tdp, lan, m2, psu,
         stability, kind) in USED_PLATFORMS:
        choices = tuple(
            k for k, g in gpus.items()
            if g.form == "desktop" and g.tdp_w <= max_tdp
        )
        for ram, ssd in ((32, 1), (128, 2)):
            out[f"{key}_{ram}g"] = Platform(
                key=f"{key}_{ram}g",
                name=f"{name}, {ram} GB, {ssd} TB",
                base_price=price + (160 if ram == 128 else 0) + (120 if ssd == 2 else 0),
                idle_w=idle, cpu_load_w=cpu_w, gpu_slots=slots,
                max_gpu_tdp=max_tdp, gpu_choices=choices, fixed_gpu=None,
                egpu=False, egpu_factor=1.0, lan_gbps=lan, m2_slots=m2,
                psu_included_w=psu, stability_mod=stability, kind=kind,
                scheduler=7.0, note="used workstation/server", used=True,
            )
    return out


HEADS_EXTRA = (
    ("n150", "Beelink EQ14 (N150, 16 GB, 500 GB)", 280, 8, 30, 1, 2.5, False, 2.0, None, 0.0, "mini"),
    ("n355", "Beelink EQ14 Pro (N355, 16 GB, 500 GB)", 380, 10, 45, 2, 2.5, False, 3.5, None, 0.1, "mini"),
    ("r5_6600h", "Minisforum UM560 (Ryzen 5 6600H, 32 GB, 1 TB)", 400, 12, 55, 2, 2.5, False, 4.5, None, 0.2, "mini"),
    ("r7_7735hs", "Minisforum UM773 (Ryzen 7 7735HS, 32 GB, 1 TB)", 450, 12, 55, 2, 2.5, False, 5.0, None, 0.3, "mini"),
    ("r7_8845hs", "Minisforum UM880 (Ryzen 7 8845HS, 32 GB, 1 TB)", 500, 14, 65, 2, 2.5, False, 5.0, None, 0.3, "mini"),
    ("r9_8945hs", "Minisforum UM890 (Ryzen 9 8945HS, 32 GB, 1 TB)", 640, 15, 65, 2, 2.5, False, 6.0, None, 0.4, "mini"),
    ("ms_a2h", "Minisforum MS-A2 (Ryzen 9 9955HX, 32 GB, 2 TB)", 780, 20, 90, 3, 10.0, True, 8.0, None, 0.6, "mini"),
    ("ser9h", "Beelink SER9 (Ryzen AI 9, 32 GB, 1 TB)", 620, 14, 65, 2, 2.5, False, 5.0, None, 0.3, "mini"),
    ("gtr9h", "Beelink GTR9 (Ryzen AI 9, 32 GB, 1 TB)", 750, 16, 65, 2, 2.5, False, 5.0, None, 0.3, "mini"),
    ("k8ph", "GMKtec K8 Plus (Ryzen 7 8845HS, 32 GB, 1 TB)", 540, 16, 70, 2, 2.5, False, 5.0, None, 0.3, "mini"),
    ("k10h", "GMKtec K10 (Ryzen 7 8845HS, 32 GB, 2 TB)", 650, 16, 70, 2, 2.5, False, 5.0, None, 0.3, "mini"),
    ("nuc14h", "ASUS NUC 14 Pro (Ultra 7, 32 GB, 1 TB)", 650, 15, 65, 2, 2.5, False, 5.0, None, 0.4, "mini"),
    ("nuc14pph", "ASUS NUC 14 Pro+ (Ultra 9, 32 GB, 2 TB)", 800, 18, 90, 2, 2.5, False, 6.0, None, 0.5, "mini"),
    ("used_sffh", "Used HP EliteDesk 800 G6 (i7-10700, 32 GB, 1 TB)", 450, 22, 90, 2, 1.0, False, 5.0, None, 0.0, "used"),
    ("nas_n305", "NAS head (i3-N305, 16 GB, 4x 8 TB)", 650, 15, 45, 4, 2.5, False, 4.0, None, 0.2, "mini"),
    ("nas_n100", "NAS head (N100, 16 GB, 4x 8 TB)", 500, 12, 30, 4, 2.5, False, 3.0, None, 0.1, "mini"),
    ("ws_5060ti", "Workstation head: ITX + RTX 5060 Ti 16 GB", 1260, 40, 190, 2, 2.5, False, 7.0, "rtx5060ti_16", 0.4, "workstation"),
    ("ws_5070", "Workstation head: ITX + RTX 5070 12 GB", 1360, 42, 200, 2, 2.5, False, 7.0, "rtx5070_12", 0.4, "workstation"),
    ("ws_4070s", "Workstation head: ITX + RTX 4070 SUPER 12 GB", 1280, 42, 200, 2, 2.5, False, 7.0, "rtx4070s_12", 0.4, "workstation"),
    ("ws_3090", "Workstation head: ITX + RTX 3090 24 GB", 1560, 55, 240, 2, 2.5, False, 7.0, "rtx3090_24", 0.3, "workstation"),
    ("ws_a4000", "Workstation head: ITX + RTX A4000 16 GB", 1200, 40, 190, 2, 2.5, False, 7.0, "rtxa4000_16", 0.4, "workstation"),
    ("ws_a5000", "Workstation head: ITX + RTX A5000 24 GB", 1750, 50, 220, 2, 2.5, False, 7.0, "rtxa5000_24", 0.3, "workstation"),
    ("ws_5080", "Workstation head: ITX + RTX 5080 16 GB", 1900, 60, 240, 2, 2.5, False, 7.0, "rtx5080_16", 0.3, "workstation"),
    ("ws_5070ti", "Workstation head: ITX + RTX 5070 Ti 16 GB", 1600, 50, 220, 2, 2.5, False, 7.0, "rtx5070ti_16", 0.3, "workstation"),
    ("nuc14ext", "ASUS NUC 14 Extreme (Ultra 9, 32 GB, 2 TB)", 1500, 35, 140, 2, 2.5, False, 8.0, None, 0.5, "sff_modular"),
    ("n100_2t", "Beelink EQ12 (N100, 16 GB, 2 TB)", 330, 8, 30, 2, 2.5, False, 2.5, None, 0.1, "mini"),
    ("n305_2t", "Beelink EQ12 Pro (N305, 16 GB, 2 TB)", 450, 10, 40, 2, 2.5, False, 4.0, None, 0.2, "mini"),
    ("um890_2t", "Minisforum UM890 Pro (Ryzen 9, 32 GB, 2 TB)", 700, 15, 65, 2, 2.5, False, 6.0, None, 0.4, "mini"),
    ("ms01_4t", "Minisforum MS-01 (i9, 32 GB, 4 TB)", 980, 18, 90, 3, 10.0, True, 8.0, None, 0.6, "mini"),
    ("ser8_2t", "Beelink SER8 (Ryzen 7, 32 GB, 2 TB)", 560, 14, 65, 2, 2.5, False, 5.0, None, 0.3, "mini"),
)


def _head_nodes() -> dict[str, HeadNode]:
    out: dict[str, HeadNode] = {}
    for (key, name, price, idle, load, m2, lan, sfp10, sched, gpu,
         stability, kind) in HEADS_EXTRA:
        out[key] = HeadNode(
            key=key, name=name, price=price, idle_w=idle, load_w=load,
            m2_slots=m2, lan_gbps=lan, sfp10=sfp10, scheduler=sched,
            has_gpu=gpu, stability_mod=stability, kind=kind,
            note="variant head",
        )
    return out

def build_extended_catalog() -> tuple[Catalog, dict]:
    gpus = dict(GPUS)
    gpus.update(_aib_gpus())
    gpus.update(_extra_gpus())
    platforms = dict(PLATFORMS)
    platforms.update(_custom_platforms(gpus))
    platforms.update(_more_custom_platforms(gpus))
    platforms.update(_mini_platforms(gpus))
    platforms.update(_used_platforms(gpus))
    heads = dict(HEADS)
    heads.update(_head_nodes())
    catalog = Catalog(gpus, platforms, heads,
                      {**FABRICS, **FABRICS_EXTRA},
                      {**STORAGE, **STORAGE_EXTRA})
    stats = {
        "base_gpus": len(GPUS),
        "base_platforms": len(PLATFORMS),
        "base_heads": len(HEADS),
        "added_gpus": len(gpus) - len(GPUS),
        "added_platforms": len(platforms) - len(PLATFORMS),
        "added_heads": len(heads) - len(HEADS),
    }
    stats["total_added"] = (
        stats["added_gpus"] + stats["added_platforms"] + stats["added_heads"]
    )
    return catalog, stats


def _gpu_dominates(a: Gpu, b: Gpu) -> bool:
    return (
        a.price_usd <= b.price_usd and a.perf >= b.perf
        and a.tdp_w <= b.tdp_w and a.vram_gb >= b.vram_gb
        and (a.price_usd < b.price_usd or a.perf > b.perf
             or a.tdp_w < b.tdp_w or a.vram_gb > b.vram_gb)
    )


def _platform_dominates(a: Platform, b: Platform) -> bool:
    if a.fixed_gpu != b.fixed_gpu or a.egpu != b.egpu:
        return False
    no_worse = (
        a.base_price <= b.base_price and a.gpu_slots >= b.gpu_slots
        and a.max_gpu_tdp >= b.max_gpu_tdp and a.m2_slots >= b.m2_slots
        and a.lan_gbps >= b.lan_gbps and a.psu_included_w >= b.psu_included_w
        and a.stability_mod >= b.stability_mod and a.idle_w <= b.idle_w
        and a.cpu_load_w <= b.cpu_load_w and a.scheduler >= b.scheduler
    )
    strict = (
        a.base_price < b.base_price or a.gpu_slots > b.gpu_slots
        or a.max_gpu_tdp > b.max_gpu_tdp or a.m2_slots > b.m2_slots
        or a.lan_gbps > b.lan_gbps or a.psu_included_w > b.psu_included_w
        or a.stability_mod > b.stability_mod or a.idle_w < b.idle_w
        or a.cpu_load_w < b.cpu_load_w or a.scheduler > b.scheduler
    )
    return no_worse and strict


def _head_dominates(a: HeadNode, b: HeadNode) -> bool:
    if a.has_gpu or b.has_gpu:
        return False
    no_worse = (
        a.price <= b.price and a.scheduler >= b.scheduler
        and a.m2_slots >= b.m2_slots and a.lan_gbps >= b.lan_gbps
        and a.stability_mod >= b.stability_mod and a.idle_w <= b.idle_w
        and a.load_w <= b.load_w
    )
    strict = (
        a.price < b.price or a.scheduler > b.scheduler
        or a.m2_slots > b.m2_slots or a.lan_gbps > b.lan_gbps
        or a.stability_mod > b.stability_mod or a.idle_w < b.idle_w
        or a.load_w < b.load_w
    )
    return no_worse and strict


def pareto_gpus(catalog: Catalog) -> dict[str, Gpu]:
    desktop = [g for g in catalog.gpus.values() if g.form == "desktop"]
    fixed = [g for g in catalog.gpus.values() if g.form != "desktop"]
    base = {g.key: g for g in catalog.gpus.values()
            if g.key in GPUS and g.form == "desktop"}
    keep = {g.key: g for g in fixed}
    keep.update(base)
    for candidate in desktop:
        if not any(
            _gpu_dominates(other, candidate)
            for other in desktop if other.key != candidate.key
        ):
            keep[candidate.key] = candidate
    return keep


def pareto_platforms(catalog: Catalog) -> dict[str, Platform]:
    items = list(catalog.platforms.values())
    keep: dict[str, Platform] = {}
    for candidate in items:
        if not any(
            _platform_dominates(other, candidate)
            for other in items if other.key != candidate.key
        ):
            keep[candidate.key] = candidate
    return keep


def pareto_heads(catalog: Catalog) -> dict[str, HeadNode]:
    items = list(catalog.heads.values())
    keep: dict[str, HeadNode] = {}
    for candidate in items:
        if candidate.has_gpu:
            keep[candidate.key] = candidate
        elif not any(
            _head_dominates(other, candidate)
            for other in items if other.key != candidate.key
        ):
            keep[candidate.key] = candidate
    return keep


HEAD_SHORTLIST = (
    "n150", "n305", "used_sff", "um890_head", "ms01_head",
    "ws_4060ti", "ws_5070", "ws_3090", "ws_5080", "nuc14ext",
)


def _cap_gpus(gpus: dict[str, Gpu], limit: int = 90) -> dict[str, Gpu]:
    fixed = {k: g for k, g in gpus.items() if g.form != "desktop"}
    base = {k: g for k, g in gpus.items() if k in GPUS and g.form == "desktop"}
    desktop = [g for g in gpus.values() if g.form == "desktop"]
    picks = {**fixed, **base}
    rankings = (
        (sorted(desktop, key=lambda g: (-g.perf, g.price_usd)), limit),
        (sorted(desktop, key=lambda g: (g.price_usd / max(g.perf, 1), -g.perf)), 30),
        (sorted(desktop, key=lambda g: (-g.vram_gb, -g.perf)), 20),
    )
    for ranked, count in rankings:
        for gpu in ranked[:count]:
            picks[gpu.key] = gpu
            if len(picks) >= limit:
                return picks
    return picks


def _cap_platforms(platforms: dict[str, Platform], limit: int = 60) -> dict[str, Platform]:
    items = list(platforms.values())
    fixed = {p.key: p for p in items if p.fixed_gpu}
    custom = [p for p in items if not p.fixed_gpu]
    picks = dict(fixed)
    rankings = (
        (sorted(custom, key=lambda p: (
            -(p.gpu_slots * p.max_gpu_tdp / max(p.base_price, 1)), p.base_price)), 20),
        (sorted(custom, key=lambda p: (-p.gpu_slots, p.base_price)), 10),
        (sorted(custom, key=lambda p: (-p.max_gpu_tdp, p.base_price)), 5),
        (sorted(custom, key=lambda p: (p.base_price, -p.gpu_slots)), 10),
        (sorted(custom, key=lambda p: (-p.stability_mod, p.base_price)), 5),
    )
    for ranked, count in rankings:
        for platform in ranked[:count]:
            picks[platform.key] = platform
            if len(picks) >= limit:
                return picks
    for platform in custom:
        picks[platform.key] = platform
        if len(picks) >= limit:
            break
    return picks


def pruned_catalog(catalog: Catalog, head_shortlist=None,
                   max_gpus: int = 90,
                   max_platforms: int = 60) -> tuple[Catalog, dict]:
    gpus = pareto_gpus(catalog)
    platforms = pareto_platforms(catalog)
    heads = pareto_heads(catalog)
    if head_shortlist:
        heads = {
            k: v for k, v in heads.items()
            if k in head_shortlist and k in catalog.heads
        }
    gpus = _cap_gpus(gpus, max_gpus)
    platforms = _cap_platforms(platforms, max_platforms)
    pruned = Catalog(gpus, platforms, heads, catalog.fabrics, catalog.storage)
    stats = {
        "gpus_before": len(catalog.gpus), "gpus_after": len(gpus),
        "platforms_before": len(catalog.platforms), "platforms_after": len(platforms),
        "heads_before": len(catalog.heads), "heads_after": len(heads),
    }
    return pruned, stats

