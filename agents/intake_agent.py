from .base_agent import BaseAgent

SYSTEM = """You are the Passage Intake & Disambiguation Agent in a multi-agent Bible interpretation system.
Parse the user's input into a structured Bible reference and detect their intent.

Rules:
- Map the query to a precise Bible reference (book, chapter, verse range)
- Detect task_type: one of "interpretation", "word_study", "historical", "doctrinal", "application", "mixed"
- Normalise translation to one of: kjv, web, asv, bbe (default: kjv if unspecified)
- Extract focus_terms (specific words/phrases the user cares about)
- Do NOT interpret the passage — only parse and structure

Output ONLY this JSON:
{
  "reference": "Book Chapter:Verse",
  "task_type": "interpretation",
  "translation": "kjv",
  "focus_terms": []
}"""


class IntakeAgent(BaseAgent):
    async def process(self, raw_query: str, default_translation: str = "kjv") -> dict:
        user_prompt = (
            f'Query: "{raw_query}"\n'
            f"Default translation if not specified: {default_translation}"
        )
        result = await self.call_gemini(SYSTEM, user_prompt)
        # Provide sensible defaults if parsing fails
        if "error" in result:
            # Propagate critical service errors (Gemini or OpenRouter)
            err_code = str(result.get("error", ""))
            if err_code in ["GEMINI_API_KEY_MISSING", "OPENROUTER_API_KEY_MISSING", "RATE_LIMIT", "UNKNOWN_ERROR"] or err_code.startswith(("GEMINI_API_ERROR_", "OPENROUTER_ERROR_")):
                return result
            return {
                "reference": raw_query,
                "task_type": "interpretation",
                "translation": default_translation,
                "focus_terms": []
            }
        return result

