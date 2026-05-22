import asyncio
import json
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Default free model on OpenRouter (Google Gemma 3 27B is free and high quality)
OPENROUTER_DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")


class BaseAgent:
    def __init__(self, model_name: str = None, use_openrouter: bool = None):
        self.model = model_name or GEMINI_MODEL
        self.api_key = GEMINI_API_KEY
        self.openrouter_api_key = OPENROUTER_API_KEY
        self.openrouter_model = OPENROUTER_DEFAULT_MODEL

        # Auto-detect: use OpenRouter if its key exists and no Gemini key,
        # or if explicitly requested
        if use_openrouter is not None:
            self.use_openrouter = use_openrouter
        else:
            self.use_openrouter = bool(OPENROUTER_API_KEY) and not bool(GEMINI_API_KEY)

    async def call_gemini(self, system_prompt: str, user_prompt: str) -> dict:
        """
        Main LLM dispatch — transparently routes to OpenRouter when enabled.
        All child agents call this method, so they benefit automatically.
        """
        if self.use_openrouter:
            return await self._call_openrouter(system_prompt, user_prompt)
        return await self._call_gemini_native(system_prompt, user_prompt)

    # ── Native Gemini call ───────────────────────────────────────
    async def _call_gemini_native(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.api_key:
            return {
                "error": "GEMINI_API_KEY_MISSING",
                "message": "Gemini API key is missing. Please set the GEMINI_API_KEY environment variable."
            }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": user_prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_prompt}
                ]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(url, json=payload)

                if r.status_code == 429:
                    return {
                        "error": "RATE_LIMIT",
                        "message": "Gemini API rate limit reached. Please wait a moment."
                    }

                r.raise_for_status()
                data = r.json()

            candidates = data.get("candidates", [])
            if not candidates:
                return {"error": "NO_CANDIDATES", "message": "Gemini API returned no candidates."}

            raw = candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()
            return json.loads(raw)

        except httpx.HTTPStatusError as e:
            try:
                err_detail = e.response.json().get("error", {}).get("message", e.response.text)
            except Exception:
                err_detail = e.response.text
            return {
                "error": f"GEMINI_API_ERROR_{e.response.status_code}",
                "message": f"Gemini API returned status code {e.response.status_code}: {err_detail}"
            }
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            return {
                "error": "JSON_PARSE_FAILED",
                "message": "Failed to parse Gemini response as JSON.",
                "raw": raw[:500] if 'raw' in locals() else ""
            }
        except Exception as e:
            return {"error": "UNKNOWN_ERROR", "message": str(e)}

    # ── OpenRouter call (OpenAI-compatible) ──────────────────────
    async def _call_openrouter(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.openrouter_api_key:
            return {
                "error": "OPENROUTER_API_KEY_MISSING",
                "message": "OpenRouter API key is missing. Set OPENROUTER_API_KEY in .env."
            }

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://lumina-bible.app",
            "X-Title": "Lumina Bible Interpreter",
        }

        # Ask for JSON output in the system prompt itself
        json_instruction = (
            "\n\nIMPORTANT: You MUST respond with ONLY valid JSON. "
            "No markdown, no code fences, no extra text."
        )

        payload = {
            "model": self.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt + json_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(url, json=payload, headers=headers)

                if r.status_code == 429:
                    return {
                        "error": "RATE_LIMIT",
                        "message": "OpenRouter rate limit reached. Please wait a moment."
                    }

                r.raise_for_status()
                data = r.json()

            # OpenAI-compatible response format
            choices = data.get("choices", [])
            if not choices:
                return {"error": "NO_CHOICES", "message": "OpenRouter returned no choices."}

            raw = choices[0].get("message", {}).get("content", "").strip()

            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = re.sub(r'^```(?:json)?\s*', '', raw)
                raw = re.sub(r'\s*```$', '', raw)

            return json.loads(raw)

        except httpx.HTTPStatusError as e:
            try:
                err_detail = e.response.json().get("error", {}).get("message", e.response.text)
            except Exception:
                err_detail = e.response.text
            return {
                "error": f"OPENROUTER_ERROR_{e.response.status_code}",
                "message": f"OpenRouter returned status {e.response.status_code}: {err_detail}"
            }
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from mixed text
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            return {
                "error": "JSON_PARSE_FAILED",
                "message": "Failed to parse OpenRouter response as JSON.",
                "raw": raw[:500] if 'raw' in locals() else ""
            }
        except Exception as e:
            return {"error": "UNKNOWN_ERROR", "message": str(e)}

    # ── List free models available on OpenRouter ─────────────────
    @staticmethod
    async def list_free_models() -> dict:
        """Fetch all free models from OpenRouter's model directory."""
        api_key = OPENROUTER_API_KEY
        if not api_key:
            return {"error": "OPENROUTER_API_KEY_MISSING"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                r.raise_for_status()
                data = r.json()

            free_models = []
            for m in data.get("data", []):
                pricing = m.get("pricing", {})
                prompt_cost = pricing.get("prompt", "1")
                completion_cost = pricing.get("completion", "1")
                # Free models have "0" cost (API returns strings)
                if str(prompt_cost) == "0" and str(completion_cost) == "0":
                    free_models.append({
                        "id": m.get("id"),
                        "name": m.get("name", m.get("id")),
                        "context_length": m.get("context_length"),
                        "description": m.get("description", "")[:120],
                    })

            return {"count": len(free_models), "models": free_models}

        except Exception as e:
            return {"error": "FETCH_FAILED", "message": str(e)}
