"""Captura automatica de informacion del entorno de ejecucion (D8)."""

import json
import platform
import sys
from pathlib import Path
from typing import Any

import cpuinfo
import numba
import numpy as np
import psutil


def get_env_info() -> dict[str, Any]:
    """Obtiene especificaciones del hardware, sistema operativo y versiones de software."""
    cpu = cpuinfo.get_cpu_info()
    mem = psutil.virtual_memory()
    return {
        "cpu_brand": cpu.get("brand_raw", platform.processor()),
        "cpu_arch": cpu.get("arch", platform.machine()),
        "cpu_physical_cores": psutil.cpu_count(logical=False),
        "cpu_logical_cores": psutil.cpu_count(logical=True),
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "os_system": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "numba_version": numba.__version__,
    }


def save_env_info(output_dir: Path | str = "results/raw") -> Path:
    """Guarda la informacion del entorno en env.json dentro de output_dir."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / "env.json"
    info = get_env_info()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    return file_path


if __name__ == "__main__":
    path = save_env_info()
    print(f"Informacion del entorno guardada en: {path}")
