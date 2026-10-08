import hashlib
from fastapi import APIRouter

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
    return {"status": "done"}
