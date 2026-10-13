"""Minimal OpenAI-compatible chat completion adapter; no tool execution."""
import httpx
from .config import model_settings

class ProviderNotConfigured(Exception):
    pass

class ProviderFailed(Exception):
    pass

async def request_completion(instructions: str, prompt: str, memories: list[str]) -> str:
    settings = model_settings()
    if settings is None:
        raise ProviderNotConfigured("Set OPENAI_API_KEY and AGENTOS_MODEL in the backend environment.")

    context = "\n".join(f"- {m}" for m in memories)
    system = instructions + ("\nRelevant approved project notes:\n" + context if context else "")
    payload = {
        "model": settings["model"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f'{settings["base_url"]}/chat/completions',
                headers={"Authorization": f'Bearer {settings["api_key"]}'},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
            result = body["choices"][0]["message"]["content"]
            if not isinstance(result, str) or not result.strip():
                raise ValueError("Empty model response")
            return result
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError) as exc:
        # Error details may contain provider-generated sensitive content.
        raise ProviderFailed("Model request failed. Check provider configuration and logs.") from exc
