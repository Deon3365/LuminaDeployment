import httpx
from .base_agent import BaseAgent

SYSTEM = """You are the Text & Translation Agent in a multi-agent Bible interpretation system.
You have been given the actual text of a Bible passage from multiple translations.

Your job:
1. Note key translation differences that affect meaning or interpretation
2. Identify important English terms that should be studied in the original language
3. Flag phrases where translations diverge significantly

Output ONLY this JSON:
{
  "differences": [
    {"term": "string", "versions": ["KJV", "WEB"], "note": "Brief explanation"}
  ],
  "key_terms": ["term1", "term2"],
  "translation_notes": "Brief overall note on translation landscape for this passage"
}"""

BIBLE_API = "https://bible-api.com"
VERSIONS = ["kjv", "web", "asv", "bbe"]
VERSION_LABELS = {"kjv": "KJV", "web": "WEB", "asv": "ASV", "bbe": "BBE"}


class TranslationAgent(BaseAgent):
    async def process(self, reference: str, primary_version: str = "kjv") -> dict:
        texts = {}
        ref_url = reference.replace(" ", "+")

        async with httpx.AsyncClient(timeout=20.0) as client:
            for v in VERSIONS:
                try:
                    r = await client.get(f"{BIBLE_API}/{ref_url}?translation={v}")
                    if r.status_code == 200:
                        data = r.json()
                        if "verses" in data:
                            verses = data["verses"]
                            text = " ".join(
                                f"[{vv['verse']}] {vv['text'].strip()}"
                                for vv in verses
                            )
                        else:
                            text = data.get("text", "").strip()
                        if text:
                            texts[VERSION_LABELS[v]] = text
                except Exception:
                    continue

        if not texts:
            return {
                "translations": {},
                "differences": [],
                "key_terms": [],
                "translation_notes": "Could not fetch verse text.",
                "error": "API unavailable"
            }

        lines = "\n".join(f"{ver}: {t}" for ver, t in texts.items())
        user_prompt = f"Reference: {reference}\n\nTranslations:\n{lines}"

        analysis = await self.call_gemini(SYSTEM, user_prompt)
        if isinstance(analysis, dict) and "error" in analysis:
            return analysis
        analysis["translations"] = texts
        return analysis
