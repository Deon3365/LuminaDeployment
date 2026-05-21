from .base_agent import BaseAgent

SYSTEM = """You are the Historical & Cultural Context Agent in a multi-agent Bible interpretation system.
Your job is to place the passage in its real-world ancient setting with academic rigour.

Responsibilities:
- Identify the author, original audience, date of writing, and location/setting
- Explain the cultural, social, political, and religious factors relevant to this passage
  (Jewish/OT: Ancient Near Eastern; NT: Second Temple Judaism + Greco-Roman world)
- Reference known historical sources when relevant (Josephus, Mishnah, Dead Sea Scrolls, Tacitus, etc.)
- Clearly distinguish: well-attested historical fact vs. scholarly consensus vs. hypothesis
- Do NOT make up historical sources; only reference real, known works

Output ONLY this JSON:
{
  "author": "string",
  "audience": "string",
  "date_range": "string",
  "setting": "string",
  "historical_context": "paragraph explaining the broader historical situation",
  "cultural_background": [
    "Key cultural factor 1",
    "Key cultural factor 2"
  ],
  "source_notes": [
    "Reference to historical source or scholarly consensus",
    "Note on scholarly debate if applicable"
  ],
  "certainty_note": "Brief note distinguishing fact vs. hypothesis"
}"""


class HistoricalAgent(BaseAgent):
    def __init__(self, book_metadata: dict):
        super().__init__()
        self.book_metadata = book_metadata

    def _get_book_meta(self, book_name: str) -> dict:
        for b in self.book_metadata.get("books", []):
            if b["name"].lower() in book_name.lower() or book_name.lower() in b["name"].lower():
                return b
        return {}

    async def process(self, reference: str, rag_context: list = None) -> dict:
        book_name = reference.split()[0] if reference else ""
        meta = self._get_book_meta(book_name)

        meta_str = (
            f"Book: {meta.get('name', book_name)}\n"
            f"Author: {meta.get('author', 'Unknown')}\n"
            f"Audience: {meta.get('audience', 'Unknown')}\n"
            f"Date: {meta.get('date', 'Unknown')}\n"
            f"Genre: {meta.get('genre', 'Unknown')}\n"
            f"Themes: {', '.join(meta.get('themes', []))}"
        ) if meta else f"Book: {book_name}"

        rag_str = ""
        if rag_context:
            rag_str = "\n\nRelevant Cultural/Historical Context from Database:\n" + "\n---\n".join(rag_context)

        user_prompt = (
            f"Reference: {reference}\n\n"
            f"Known book metadata:\n{meta_str}"
            f"{rag_str}\n\n"
            "Provide a thorough historical and cultural context for this passage based on the known metadata and provided context."
        )
        return await self.call_gemini(SYSTEM, user_prompt)
