import sys, asyncio, os, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'c:\Users\gideo\OneDrive\Desktop\Agentic bible interpretator')
from dotenv import load_dotenv; load_dotenv()

async def test():
    from agents.orchestrator_agent import OrchestratorAgent
    with open('bible_data/strongs_sample.json', encoding='utf-8') as f: strongs = json.load(f)
    with open('bible_data/book_metadata.json',  encoding='utf-8') as f: meta = json.load(f)

    print("Running full 8-agent pipeline on John 3:16 via Ollama...")
    orch = OrchestratorAgent(strongs, meta)
    result = await orch.run('John 3:16')

    print("\n=== RESULTS ===")
    print(f"Reference  : {result.get('reference')}")
    print(f"Testament  : {result.get('testament')}")
    print(f"Summary    : {result.get('summary','')[:200]}")

    trans = result.get('text_and_translation', {})
    print(f"\nTranslations fetched: {list(trans.get('translations',{}).keys())}")
    print(f"Key terms  : {trans.get('key_terms',[])}")

    ws = result.get('word_study', {})
    print(f"\nWord studies: {len(ws.get('word_studies',[]))}")
    for w in ws.get('word_studies',[]):
        print(f"  {w.get('english')} → {w.get('lemma')} ({w.get('strongs')})")

    hist = result.get('historical_cultural',{})
    print(f"\nHistorical author: {hist.get('author','')}")
    print(f"Date: {hist.get('date_range','')}")

    theo = result.get('theological_doctrinal',{})
    print(f"\nCore agreements: {len(theo.get('core_agreements',[]))}")
    print(f"Tradition views: {len(theo.get('tradition_views',[]))}")
    for t in theo.get('tradition_views',[]):
        print(f"  {t.get('tradition')}: {t.get('summary','')[:80]}")

    app = result.get('application_reflection',{})
    print(f"\nPrinciples   : {len(app.get('principles',[]))}")
    print(f"Questions    : {len(app.get('reflection_questions',[]))}")
    print(f"Applications : {len(app.get('practical_applications',[]))}")

    errors = {k:v.get('error') for k,v in result.items() if isinstance(v,dict) and 'error' in v}
    if errors:
        print(f"\nErrors: {errors}")
    else:
        print("\nALL AGENTS SUCCEEDED - no errors!")

asyncio.run(test())
