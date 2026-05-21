import asyncio
import json
import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class BaseAgent:
    def __init__(self, model_name: str = None):
        self.model = model_name or GEMINI_MODEL
        self.api_key = GEMINI_API_KEY

    async def call_gemini(self, system_prompt: str, user_prompt: str) -> dict:
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
                
                # Check for rate limit (429)
                if r.status_code == 429:
                    return {
                        "error": "RATE_LIMIT",
                        "message": "Gemini API rate limit reached. Please wait a moment."
                    }
                
                r.raise_for_status()
                data = r.json()

            # Extract generated content
            candidates = data.get("candidates", [])
            if not candidates:
                return {"error": "NO_CANDIDATES", "message": "Gemini API returned no candidates."}
                
            raw = candidates[0].get("content", {}).get("parts", [])[0].get("text", "").strip()

            # Parse JSON
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
        except json.JSONDecodeError as e:
            # Fallback regex search for JSON if it had extra text (unlikely with responseMimeType but good safety)
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

