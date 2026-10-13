import asyncio
import os
import time

import psutil
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/health",
    tags=["health"],
)

# cgroup v2 files: what the container is limited to, not the whole Docker VM (which psutil reports)
CGROUP_DIR = "/sys/fs/cgroup"
CPU_SAMPLE_SECONDS = 0.1


def _read_cgroup(name: str) -> str | None:
    try:
        with open(os.path.join(CGROUP_DIR, name)) as f:
            return f.read().strip()
    except OSError:
        return None  # not running in a cgroup v2 container (e.g. uvicorn on the host)


def _cpu_limit_cores() -> float:
    # cpu.max = "<quota> <period>", e.g. "100000 100000" -> 1 core, "max 100000" -> no limit
    cpu_max = _read_cgroup("cpu.max")
    if cpu_max:
        quota, period = cpu_max.split()
        if quota != "max":
            return int(quota) / int(period)
    return float(psutil.cpu_count())


def _cpu_usage_usec() -> int | None:
    cpu_stat = _read_cgroup("cpu.stat")
    if cpu_stat is None:
        return None
    for line in cpu_stat.splitlines():
        key, value = line.split()
        if key == "usage_usec":
            return int(value)
    return None


async def _cpu_percent(limit_cores: float) -> float:
    # % of the container's CPU limit: 100% = all allowed cores busy
    start_usage = _cpu_usage_usec()
    if start_usage is None:
        return psutil.cpu_percent(interval=None)
    start = time.monotonic()
    await asyncio.sleep(CPU_SAMPLE_SECONDS)
    used_usec = _cpu_usage_usec() - start_usage
    elapsed_usec = (time.monotonic() - start) * 1_000_000
    return round(used_usec / (elapsed_usec * limit_cores) * 100, 1)


def _memory() -> tuple[int, int]:
    # (used, limit) in bytes; memory.max is "max" when no limit is set
    current = _read_cgroup("memory.current")
    limit = _read_cgroup("memory.max")
    if current is None or limit is None or limit == "max":
        vm = psutil.virtual_memory()
        return vm.total - vm.available, vm.total
    return int(current), int(limit)


# Monitor resource usage
@router.get("/")
async def health_check():
    cpu_limit = _cpu_limit_cores()
    memory_used, memory_limit = _memory()
    return {
        "cpu_percent": await _cpu_percent(cpu_limit),
        "cpu_limit_cores": cpu_limit,
        "memory_percent": round(memory_used / memory_limit * 100, 1),
        "memory_used_mb": round(memory_used / 2**20, 1),
        "memory_limit_mb": round(memory_limit / 2**20, 1),
        "disk_percent": psutil.disk_usage('/').percent,  # Docker VM disk, no per-container limit
    }
