from google import genai
from app.core.config import settings

gemini_client: genai.Client | None = None

async def init_gemini_client() -> None:
    global gemini_client
    gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)



async def close_gemini_client() -> None:
    global gemini_client
    if gemini_client:
        await gemini_client.aio.aclose()
        gemini_client = None


def get_gemini_client() -> genai.Client:
    if gemini_client is None:
        raise RuntimeError('Gemini client is not initialized')
    return gemini_client
