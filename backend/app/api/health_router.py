import psutil
from fastapi import APIRouter

router = APIRouter(
    prefix="/v1/health",
    tags=["health"],
)


# Monitor resource usage
@router.get("/")
async def health_check():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
