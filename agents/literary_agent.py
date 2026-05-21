from .base_agent import BaseAgent

SYSTEM = """You are the Literary & Canonical Context Agent in a multi-agent Bible interpretation system.
Your job is to explain how the passage fits into its literary structure and into the wider Bible canon.

Responsibilities:
- Explain the immediate literary context (what comes before and after; how this fits the argument/narrative flow)
- Summarise the key themes of the book and how this passage expresses or advances them
- Identify the genre and how genre affects interpretation
- Show important canonical links (other passages that clarify, echo, or tension with this one)
- Note any tensions or apparent contradictions and how scholars harmonise or explain them

Output ONLY this JSON:
{
  "immediate_context": "paragraph explaining the immediate literary context",
  "book_themes": ["theme1", "theme2"],
  "genre": "string (e.g., Wisdom epistle, Apocalyptic prophecy, Narrative)",
  "genre_note": "How the genre should affect interpretation",
  "canonical_links": [
    {"reference": "Romans 3:28", "note": "Paul's parallel argument on faith/works"},
    {"reference": "Genesis 15:6", "note": "Abraham believed God, counted as righteousness"}
  ],
  "tensions_harmonisations": "Note on any apparent tensions with other Scripture and how scholars address them"
}"""


class LiteraryAgent(BaseAgent):
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
            f"Genre: {meta.get('genre', 'Unknown')}\n"
            f"Themes: {', '.join(meta.get('themes', []))}"
        ) if meta else ""

        rag_str = ""
        if rag_context:
            rag_str = "\n\nRelated Scriptural Context (Cross-References) from Database:\n" + "\n---\n".join(rag_context)

        user_prompt = (
            f"Reference: {reference}\n"
            f"{meta_str}"
            f"{rag_str}\n\n"
            "Analyse the literary and canonical context of this passage using the provided book metadata and scriptural context."
        )
        return await self.call_gemini(SYSTEM, user_prompt)
