import asyncio
import hashlib
import os
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/v1/stress",
    tags=["Stress Testing"],
    include_in_schema=False,
)


# 1. Triggers Memory Exhaustion (OOM)
# Hold memory in a module-level global list so Python Garbage Collection CANNOT free it
STRESS_MEMORY_STORE = []
@router.get("/memory")
async def stress_memory():
    # Force physical memory allocation beyond 256MB
    # 40 chunks of 10MB = 400MB total (well above 256MB)
    for _ in range(40):
        # bytearray ensures real physical RAM allocation across memory pages
        STRESS_MEMORY_STORE.append(bytearray(10 * 1024 * 1024))

    return {"allocated_mb": len(STRESS_MEMORY_STORE) * 10}


# 2. Triggers CPU Throttling
@router.get("/cpu")
def stress_cpu():
    # Heavy synchronous hashing to peg CPU
    target = b"stress_test"
    for _ in range(500_000):
        target = hashlib.sha256(target).digest()
    return {"status": "done", "worker_pid": os.getpid()}  # uvicorn worker process that served this request


# ================================ 3. Sequential vs ThreadPool vs ProcessPool ================================
# Each endpoint runs the SAME CPU work `tasks` times (default 4), only the execution model differs.
# Compare `elapsed_seconds` between them, then change the "server size" and compare again.
# How to run each one: docs/project-staff/phase-5-vertical-scaling-simulations.md

STRESS_TASK_HASHES = 500_000  # same work as /stress/cpu, ~0.2s of one core
POOL_SIZE = 4  # max tasks a pool runs at once (tasks above this wait for a free slot)


def _cpu_task(_: int) -> tuple[int, int]:
    """Pure Python CPU work. Hashing an 11-32 byte input never releases the GIL.

    Must be a top-level function: ProcessPoolExecutor pickles it to send it to a child process.
    Returns (process id, thread id) so the response shows where the task actually ran.
    """
    target = b"stress_test"
    for _ in range(STRESS_TASK_HASHES):
        target = hashlib.sha256(target).digest()
    return os.getpid(), threading.get_ident()


def _report(mode: str, start: float, results: list[tuple[int, int]]) -> dict:
    return {
        "mode": mode,
        "tasks": len(results),
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "worker_pid": os.getpid(),  # uvicorn worker process that served this request
        "task_processes": len({pid for pid, _ in results}),  # distinct processes the tasks ran in
        "task_threads": len(set(results)),  # distinct (process, thread) pairs the tasks ran in
    }


# 3.1 Sequential: tasks run one after another on the event loop thread
@router.get("/cpu/sequential")
async def stress_cpu_sequential(tasks: int = Query(4, ge=1, le=16)):
    # Deliberately `async def` with NO await: this BLOCKS the event loop for the whole run.
    # Without workers: every other request (even /health) waits until this one finishes.
    # With 2+ workers: another worker process keeps serving requests meanwhile.
    start = time.perf_counter()
    results = [_cpu_task(i) for i in range(tasks)]
    return _report("sequential", start, results)


# 3.2 ThreadPool: tasks run in several threads of the SAME process
@router.get("/cpu/thread-pool")
async def stress_cpu_thread_pool(tasks: int = Query(4, ge=1, le=16)):
    # The event loop stays free (it only awaits), so other requests are still served.
    # But all threads share this process' one GIL: only one runs Python code at a time,
    # so elapsed time is ~ the same as sequential, whatever the number of cores.
    # A new pool per request: starting threads is cheap, so this adds almost nothing to elapsed time.
    start = time.perf_counter()
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=POOL_SIZE, thread_name_prefix="stress") as thread_pool:
        results = await asyncio.gather(*(loop.run_in_executor(thread_pool, _cpu_task, i) for i in range(tasks)))
    return _report("thread-pool", start, results)


# 3.3 ProcessPool: tasks run in separate child processes, each with its own GIL
@router.get("/cpu/process-pool")
async def stress_cpu_process_pool(tasks: int = Query(4, ge=1, le=16)):
    # True parallelism, but ONLY if the container has more than 1 core:
    #   cpus: '1.00' -> processes take turns on one core, ~ sequential (plus process overhead)
    #   cpus: '4.00' -> 4 tasks run at the same time, ~4x faster
    # The child processes count against the container's memory limit too.
    # A new pool per request: every call pays for starting (forking) the child processes,
    # and they exit when the `with` block ends, so their memory is returned after each request.
    start = time.perf_counter()
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=POOL_SIZE) as process_pool:
        results = await asyncio.gather(*(loop.run_in_executor(process_pool, _cpu_task, i) for i in range(tasks)))
    return _report("process-pool", start, results)
