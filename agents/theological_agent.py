from .base_agent import BaseAgent

SYSTEM = """You are the Theological & Doctrinal Agent in a multi-agent Bible interpretation system.
Your job is to summarise how major Christian traditions have interpreted this passage.

Responsibilities:
- Identify what most major Christian traditions agree on (core orthodox consensus)
- Summarise how each major tradition interprets this passage:
  Reformed/Calvinist, Roman Catholic, Eastern Orthodox, Wesleyan/Arminian, Pentecostal/Charismatic,
  Anglican, Lutheran (include those most relevant to this passage)
- Identify the key theological debates and the strongest arguments on each side
- Present ALL views respectfully and neutrally — do NOT take sides
- Distinguish: widely shared Christian beliefs vs. intra-Christian disagreements

Output ONLY this JSON:
{
  "core_agreements": [
    "Widely shared belief 1",
    "Widely shared belief 2"
  ],
  "tradition_views": [
    {
      "tradition": "Reformed",
      "summary": "Concise summary of Reformed interpretation",
      "key_texts": ["supporting references"]
    }
  ],
  "debated_points": [
    {
      "issue": "The relationship between faith and works",
      "perspectives": [
        {"view": "Works as evidence of genuine faith", "proponents": ["Reformed", "Lutheran"]},
        {"view": "Works as cooperation with grace in justification", "proponents": ["Catholic"]}
      ]
    }
  ],
  "historical_interpretation_note": "Brief note on how interpretation of this passage has developed historically"
}"""


class TheologicalAgent(BaseAgent):
    async def process(self, reference: str, rag_context: list = None) -> dict:
        rag_str = ""
        if rag_context:
            rag_str = "\n\nRelevant Theological Commentary from Database:\n" + "\n---\n".join(rag_context)

        user_prompt = (
            f"Reference: {reference}\n\n"
            f"{rag_str}\n\n"
            "Provide a balanced, multi-tradition theological analysis of this passage using the provided context."
        )
        return await self.call_gemini(SYSTEM, user_prompt)
