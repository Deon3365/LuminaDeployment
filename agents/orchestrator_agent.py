import asyncio
from .translation_agent import TranslationAgent
from .word_study_agent import WordStudyAgent
from .historical_agent import HistoricalAgent
from .literary_agent import LiteraryAgent
from .theological_agent import TheologicalAgent
from .application_agent import ApplicationAgent
from rag import RAGRetriever

GEMINI_ERROR_MSG = (
    "Cannot reach Gemini API. Please make sure your API key is valid and you have internet access."
)


class OrchestratorAgent:
    def __init__(self, strongs_data: dict, book_metadata: dict):
        self.strongs_data  = strongs_data
        self.book_metadata = book_metadata
        self.retriever = RAGRetriever()

    def _detect_testament(self, reference: str) -> str:
        nt_books = [
            "matthew", "mark", "luke", "john", "acts", "romans",
            "corinthians", "galatians", "ephesians", "philippians",
            "colossians", "thessalonians", "timothy", "titus", "philemon",
            "hebrews", "james", "peter", "jude", "revelation",
            "1cor", "2cor", "1thess", "2thess", "1tim", "2tim",
            "1pet", "2pet", "1jn", "2jn", "3jn",
        ]
        return "NT" if any(b in reference.lower() for b in nt_books) else "OT"

    def _check_errors(self, *results) -> dict:
        for r in results:
            if isinstance(r, dict) and "error" in r:
                return r
        return None

    async def run(
        self,
        reference: str,
        task_type: str = "interpretation",
        translation: str = "kjv",
        focus_terms: list = None,
        depth: str = "full",
    ) -> dict:
        focus_terms = focus_terms or []
        testament   = self._detect_testament(reference)

        # ── Step 1: Fetch Bible text (bible-api.com, no LLM needed) ──
        trans_agent    = TranslationAgent()
        trans_result   = await trans_agent.process(reference, translation)
        if isinstance(trans_result, dict) and "error" in trans_result:
            return {
                "reference": reference,
                "error": trans_result.get("error"),
                "message": trans_result.get("message", "An error occurred during translation fetch or analysis."),
                "translations_available": {},
            }

        key_terms = focus_terms or trans_result.get("key_terms", [])
        if not isinstance(key_terms, list):
            key_terms = []

        # ── Step 1.5: Fetch RAG Context ──
        rag_context = self.retriever.get_context_bundle(reference, testament, key_terms)

        # ── Step 2: Run all AI agents in parallel ──
        hist_agent  = HistoricalAgent(self.book_metadata)
        lit_agent   = LiteraryAgent(self.book_metadata)
        theo_agent  = TheologicalAgent()
        word_agent  = WordStudyAgent(self.strongs_data)

        hist_res, lit_res, theo_res, word_res = await asyncio.gather(
            hist_agent.process(reference, rag_context.get("historical_cultural")),
            lit_agent.process(reference, rag_context.get("related_verses")),
            theo_agent.process(reference, rag_context.get("commentary")),
            word_agent.process(reference, key_terms[:6], testament),
        )

        # ── Check Gemini API errors ──
        err = self._check_errors(hist_res, lit_res, theo_res, word_res)
        if err:
            return {
                "reference": reference,
                "error": err.get("error"),
                "message": err.get("message", "An error occurred during Gemini API inference."),
                "translations_available": trans_result.get("translations", {}),
            }

        # ── Step 3: Application agent (uses prior context) ──
        ctx = (
            f"Themes: {', '.join(lit_res.get('book_themes', []))}\n"
            f"Historical: {hist_res.get('historical_context', '')[:200]}\n"
            f"Core agreements: {', '.join(theo_res.get('core_agreements', []))}\n"
            f"Related Scriptures: {', '.join(rag_context.get('related_verses', []))[:200]}"
        )
        app_agent  = ApplicationAgent()
        app_result = await app_agent.process(reference, ctx)

        if isinstance(app_result, dict) and "error" in app_result:
            return {
                "reference": reference,
                "error": app_result.get("error"),
                "message": app_result.get("message", "An error occurred during application analysis."),
                "translations_available": trans_result.get("translations", {}),
            }

        summary = app_result.get(
            "summary_interpretation",
            f"A layered study of {reference}.",
        )

        return {
            "reference":             reference,
            "task_type":             task_type,
            "translation":           translation.upper(),
            "testament":             testament,
            "summary":               summary,
            "text_and_translation":  trans_result,
            "word_study":            word_res,
            "historical_cultural":   hist_res,
            "literary_canonical":    lit_res,
            "theological_doctrinal": theo_res,
            "application_reflection": app_result,
            "rag_context":           rag_context # Pass to frontend for sidebar
        }
