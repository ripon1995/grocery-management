from google import genai
from app.clients.fake_gemini_client import FakeGeminiClient
from app.clients.redis_client import get_redis
from app.core.config import settings

gemini_client: genai.Client | FakeGeminiClient | None = None


async def init_gemini_client() -> None:
    global gemini_client
    if settings.GEMINI_PROVIDER == 'fake':
        gemini_client = FakeGeminiClient(get_redis())  # needs init_redis() to have run first
    else:
        gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)


async def close_gemini_client() -> None:
    global gemini_client
    if gemini_client:
        await gemini_client.aio.aclose()
        gemini_client = None


def get_gemini_client() -> genai.Client | FakeGeminiClient:
    if gemini_client is None:
        raise RuntimeError('Gemini client is not initialized')
    return gemini_client
