from .base_agent import BaseAgent

SYSTEM = """You are the Original Language & Word Study Agent in a multi-agent Bible interpretation system.
For each key English term provided, perform a rigorous linguistic analysis.

You have access to Strong's lexicon data provided in the prompt.
Your job:
- Identify the Hebrew/Aramaic (OT) or Greek (NT) lemma(s) for each English term
- Provide the Strong's number (H#### or G####)
- Give the semantic range (what the word CAN mean)
- Provide 2-3 important usage examples from elsewhere in Scripture
- Explain the contextual meaning (what it MOST LIKELY means in this specific passage)
- Note where English translations flatten or obscure nuance

Output ONLY this JSON:
{
  "word_studies": [
    {
      "english": "faith",
      "lemma": "πίστις",
      "transliteration": "pistis",
      "strongs": "G4102",
      "language": "Greek",
      "semantic_range": ["trust", "faithfulness", "loyalty"],
      "usage_examples": [
        {"reference": "Hebrews 11:1", "note": "faith as trust in unseen realities"},
        {"reference": "Romans 3:3", "note": "faithfulness / loyalty nuance"}
      ],
      "contextual_note": "In this passage, 'faith' is contrasted with empty verbal profession.",
      "translation_note": "KJV and ESV both render pistis as 'faith'; the word carries loyalty/commitment nuance often lost in English."
    }
  ]
}"""


class WordStudyAgent(BaseAgent):
    def __init__(self, strongs_data: dict):
        super().__init__()
        self.strongs_data = strongs_data

    async def process(self, reference: str, key_terms: list, testament: str = "NT") -> dict:
        if not key_terms:
            return {"word_studies": []}

        # Build relevant Strong's context
        lang = "greek" if testament == "NT" else "hebrew"
        lexicon_context = []
        for entry in self.strongs_data.get(lang, {}).values():
            if any(t.lower() in [kw.lower() for kw in key_terms]
                   for t in entry.get("semantic_range", [])):
                lexicon_context.append(entry)

        lexicon_str = "\n".join(
            f"- {e['lemma']} ({e['translit']}): {e['definition']} | Range: {', '.join(e['semantic_range'])}"
            for e in lexicon_context[:15]
        )

        user_prompt = (
            f"Reference: {reference}\n"
            f"Testament: {testament}\n"
            f"Key terms to study: {', '.join(key_terms)}\n\n"
            f"Relevant lexicon entries:\n{lexicon_str or 'Use your training knowledge.'}"
        )
        return await self.call_gemini(SYSTEM, user_prompt)
