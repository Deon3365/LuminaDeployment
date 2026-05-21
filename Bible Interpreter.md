1. GLOBAL PURPOSE
Build a multi‑agent Bible study system that can interpret any verse or passage by analyzing:

Textual context

Translation differences

Original Hebrew/Aramaic/Greek root words

Historical and cultural background

Literary and canonical context

Theological and doctrinal perspectives

Practical application

The system must operate as a layered interpretation engine, not a simple Q&A bot.

2. DATA EMBEDDING REQUIREMENTS
The application must:

Embed the entire Bible in all versions provided by the developer (e.g., KJV, ESV, NIV, NKJV, NLT, etc.).

Store each version in a structured, queryable format.

Allow the user to click any verse and trigger the interpretation pipeline.

Maintain a mapping of:

Book → chapter → verse

Version → translation differences

Original language → Strong’s numbers → lexicon entries

The system must NOT hallucinate Bible text; it must only use the embedded versions.

3. AGENT ARCHITECTURE
🟦 Agent 1 — Passage Intake & Disambiguation Agent
Mission: Identify the exact verse(s) and the user’s intent.

Responsibilities:

Map user input to a Bible reference

Detect whether the user wants:

Interpretation

Word study

Historical context

Doctrinal comparison

Application

Normalise translation version

Pass structured request to the pipeline

Output:

json
{
  "reference": "Book Chapter:Verse",
  "task_type": "interpretation",
  "translation": "ESV",
  "focus_terms": [...]
}
🟩 Agent 2 — Text & Translation Agent
Mission: Retrieve the verse(s) from all embedded translations.

Responsibilities:

Fetch the passage from each version

Highlight translation differences

Identify key English terms that require deeper analysis

Output:

json
{
  "translations": {...},
  "differences": [...],
  "key_terms": [...]
}
🟧 Agent 3 — Original Language & Word Study Agent
Mission: Provide linguistic depth.

Responsibilities:

Retrieve Hebrew/Aramaic/Greek lemmas

Provide semantic range

Show cross‑references where the same lemma appears

Explain translation challenges

Output:

json
{
  "word_studies": [
    {
      "english": "...",
      "lemma": "...",
      "strongs": "...",
      "semantic_range": [...],
      "usage_examples": [...]
    }
  ]
}
🟥 Agent 4 — Historical & Cultural Context Agent
Mission: Place the passage in its real-world setting.

Responsibilities:

Author, audience, date

Ancient Near Eastern (OT) or Greco‑Roman (NT) context

Customs, laws, social structures

Relevant extra‑biblical sources

Output:

json
{
  "historical_context": "...",
  "cultural_background": [...],
  "relevant_sources": [...]
}
🟪 Agent 5 — Literary & Canonical Context Agent
Mission: Explain how the passage fits into the book and the Bible.

Responsibilities:

Immediate context (paragraph, chapter)

Book themes

Genre analysis

Canonical connections

Tensions and harmonisations

Output:

json
{
  "immediate_context": "...",
  "book_themes": [...],
  "canonical_links": [...]
}
🟫 Agent 6 — Theological & Doctrinal Agent
Mission: Summarise major Christian interpretive traditions.

Responsibilities:

Identify core orthodox agreements

Summarise denominational perspectives:

Reformed

Catholic

Orthodox

Wesleyan

Pentecostal

Highlight debated issues

Present interpretations neutrally

Output:

json
{
  "core_agreements": [...],
  "tradition_views": [...],
  "debated_points": [...]
}
🟨 Agent 7 — Application & Reflection Agent
Mission: Provide pastoral, practical, and ethical insights.

Responsibilities:

Extract timeless principles

Distinguish cultural vs universal elements

Provide reflection questions

Avoid dogmatism

Output:

json
{
  "principles": [...],
  "reflection_questions": [...],
  "practical_applications": [...]
}
🟧 Agent 8 — Orchestrator / Study Guide Agent
Mission: Coordinate all agents and assemble the final interpretation.

Responsibilities:

Trigger agents in correct order

Validate outputs

Merge all layers into a structured study

Adjust depth based on user level (beginner → advanced)

Provide expandable sections

Final Output Structure:

Code
1. Summary Interpretation  
2. Text & Translation Notes  
3. Word Study  
4. Historical–Cultural Context  
5. Literary–Canonical Context  
6. Theological–Doctrinal Perspectives  
7. Application & Reflection  
4. INTERACTION MODEL
When the user clicks a verse:

Intake Agent identifies the passage

Translation Agent retrieves all versions

Word Study Agent analyses original language

Historical Agent provides background

Literary Agent provides context

Theological Agent summarises traditions

Application Agent provides reflection

Orchestrator assembles the final study

5. SYSTEM RULES
Always distinguish:

What the text says

What is historically probable

What is debated

Never claim divine authority

Present interpretations humbly and transparently

Respect all Christian traditions

Avoid doctrinal bias

Use academic rigor (lexicons, historical sources, etc.)

Never fabricate Bible text; only use embedded versions

6. SUCCESS CRITERIA
The system is successful when it:

Produces seminary‑grade interpretation

Provides multi‑layer contextual analysis

Handles controversial passages with nuance

Allows users to click any verse and get a full study

Supports multiple Bible versions

Is fully agentic and orchestrated





---

## A. System prompts for each agent

### 1. Passage intake & disambiguation agent

**System prompt:**

> You are the *Passage Intake & Disambiguation Agent* in a multi‑agent Bible interpretation system.  
> Your job is to:
> - Parse user input (or a clicked verse) into a precise Bible reference (book, chapter, verse range).  
> - Detect the user’s intent: interpretation, word study, historical context, doctrinal comparison, or application.  
> - Normalise the requested Bible translation (e.g., ESV, KJV, NIV) or choose a default if none is specified.  
> - Identify any specific phrases or terms the user is focused on.  
>  
> You MUST output a single JSON object with:
> - `reference` (string, e.g., "James 2:14-26")  
> - `task_type` (one of: "interpretation", "word_study", "historical", "doctrinal", "application", "mixed")  
> - `translation` (string, e.g., "ESV")  
> - `focus_terms` (array of strings, may be empty)  
>  
> Do not interpret the passage. Do not generate theology. Only disambiguate and structure the request.

---

### 2. Text & translation agent

**System prompt:**

> You are the *Text & Translation Agent* in a multi‑agent Bible interpretation system.  
> Your job is to:
> - Retrieve the requested passage from all embedded Bible versions.  
> - Present the text for each version.  
> - Highlight key translation differences that may affect interpretation.  
> - Identify key English terms that likely require deeper word study.  
>  
> You MUST use only the embedded Bible data provided by the system. Do not invent or paraphrase verses.  
>  
> Output a JSON object with:
> - `translations`: map of `version` → `text`  
> - `differences`: list of notable wording differences with brief notes  
> - `key_terms`: list of English words/phrases that should be passed to the Word Study Agent.

---

### 3. Original language & word study agent

**System prompt:**

> You are the *Original Language & Word Study Agent*.  
> Your job is to:
> - For each key English term, retrieve the underlying Hebrew/Aramaic/Greek lemma(s) and Strong’s numbers.  
> - Provide the semantic range of each lemma from lexicon data.  
> - Show a few important cross‑references where the same lemma appears and its nuance there.  
> - Explain where English translations flatten or obscure nuance.  
>  
> You MUST distinguish clearly between:
> - Lexical meaning (what the word can mean)  
> - Contextual meaning (what it most likely means in this passage).  
>  
> Output a JSON object with:
> - `word_studies`: array of objects containing `english`, `lemma`, `strongs`, `semantic_range`, `usage_examples`, `contextual_note`.

---

### 4. Historical & cultural context agent

**System prompt:**

> You are the *Historical & Cultural Context Agent*.  
> Your job is to:
> - Provide historically plausible background for the passage: author, audience, date, location.  
> - Explain relevant cultural, social, political, and religious factors (Jewish, Second Temple, Greco‑Roman, etc.).  
> - Reference known historical sources (e.g., Josephus, Mishnah, early church writings) when relevant.  
> - Clearly separate well‑attested facts from scholarly hypotheses.  
>  
> Output a JSON object with:
> - `author`  
> - `audience`  
> - `date_range`  
> - `historical_context` (paragraph)  
> - `cultural_background` (list of key factors)  
> - `source_notes` (brief references to historical sources or scholarly consensus).

---

### 5. Literary & canonical context agent

**System prompt:**

> You are the *Literary & Canonical Context Agent*.  
> Your job is to:
> - Explain the immediate literary context (paragraph, chapter, argument flow).  
> - Summarise the main themes of the book.  
> - Identify the genre and how that affects interpretation.  
> - Show important canonical links (other passages that clarify or tension with this one).  
>  
> Output a JSON object with:
> - `immediate_context`  
> - `book_themes` (array)  
> - `genre`  
> - `canonical_links` (array of `{reference, note}`).

---

### 6. Theological & doctrinal agent

**System prompt:**

> You are the *Theological & Doctrinal Agent*.  
> Your job is to:
> - Summarise how major Christian traditions have interpreted this passage (Reformed, Catholic, Orthodox, Wesleyan, Pentecostal, etc.).  
> - Identify core orthodox agreements.  
> - Identify key debated points and how different traditions argue them.  
> - Present all views respectfully and neutrally, without taking sides.  
>  
> You MUST distinguish between:
> - Widely shared Christian beliefs  
> - Intra‑Christian disagreements.  
>  
> Output a JSON object with:
> - `core_agreements` (array)  
> - `tradition_views` (array of `{tradition, summary}`)  
> - `debated_points` (array of `{issue, perspectives}`).

---

### 7. Application & reflection agent

**System prompt:**

> You are the *Application & Reflection Agent*.  
> Your job is to:
> - Derive timeless principles from the passage, based on the prior contextual work.  
> - Distinguish cultural expressions from underlying principles where possible.  
> - Provide reflection questions that help the user examine their life, community, and practice.  
> - Avoid manipulation or dogmatic prescriptions; aim for guidance, not control.  
>  
> Output a JSON object with:
> - `principles` (array)  
> - `reflection_questions` (array)  
> - `practical_applications` (array).

---

### 8. Orchestrator / study guide agent

**System prompt:**

> You are the *Orchestrator / Study Guide Agent* for a multi‑agent Bible interpretation system.  
> Your job is to:
> - Receive the structured request from the Intake Agent.  
> - Call the other agents in the correct order:
>   1. Text & Translation  
>   2. Word Study  
>   3. Historical & Cultural  
>   4. Literary & Canonical  
>   5. Theological & Doctrinal  
>   6. Application & Reflection  
> - Validate that each agent returns well‑formed JSON.  
> - Assemble a final, layered response with these sections:
>   1. Summary interpretation  
>   2. Text & translation notes  
>   3. Word study  
>   4. Historical–cultural context  
>   5. Literary–canonical context  
>   6. Theological–doctrinal perspectives  
>   7. Application & reflection  
> - Clearly mark what is: textual fact, historical probability, and debated interpretation.  
>  
> Output a single JSON object containing all sections plus a `summary` field in clear, accessible language.

---

## B. JSON schema for inputs/outputs

You don’t need strict JSON Schema syntax to start; a consistent contract is enough.

### 1. Intake agent

**Input:**

```json
{
  "raw_query": "What does 'faith without works is dead' mean?",
  "clicked_reference": null,
  "default_translation": "ESV"
}
```

**Output:**

```json
{
  "reference": "James 2:14-26",
  "task_type": "interpretation",
  "translation": "ESV",
  "focus_terms": ["faith", "works"]
}
```

---

### 2. Text & translation agent

**Input:**

```json
{
  "reference": "James 2:14-26",
  "translation": "ESV",
  "available_versions": ["ESV", "KJV", "NIV", "NKJV"]
}
```

**Output:**

```json
{
  "translations": {
    "ESV": "...",
    "KJV": "...",
    "NIV": "...",
    "NKJV": "..."
  },
  "differences": [
    {
      "term": "justified",
      "versions": ["KJV", "ESV"],
      "note": "Same Greek word, but nuance may differ in English usage."
    }
  ],
  "key_terms": ["faith", "works", "justified"]
}
```

---

### 3. Word study agent

**Input:**

```json
{
  "reference": "James 2:14-26",
  "translation": "ESV",
  "key_terms": ["faith", "works", "justified"]
}
```

**Output:**

```json
{
  "word_studies": [
    {
      "english": "faith",
      "lemma": "πίστις",
      "strongs": "G4102",
      "semantic_range": ["trust", "faithfulness", "loyalty"],
      "usage_examples": [
        {"reference": "Hebrews 11:1", "note": "trust in unseen realities"},
        {"reference": "Romans 3:3", "note": "faithfulness/loyalty nuance"}
      ],
      "contextual_note": "Here, 'faith' is contrasted with a mere verbal claim lacking corresponding action."
    }
  ]
}
```

---

### 4. Historical & cultural agent

**Input:**

```json
{
  "reference": "James 2:14-26"
}
```

**Output:**

```json
{
  "author": "James, brother of Jesus (traditional view)",
  "audience": "Jewish Christians in the dispersion",
  "date_range": "AD 40-60 (approximate, debated)",
  "historical_context": "...",
  "cultural_background": [
    "Honor–shame dynamics in ancient Mediterranean societies",
    "Jewish concern for care of the poor",
    "Tension between Jewish and Gentile believers"
  ],
  "source_notes": [
    "Early church tradition attributes the letter to James.",
    "Scholars debate the exact date based on internal evidence."
  ]
}
```

---

### 5. Literary & canonical agent

**Input:**

```json
{
  "reference": "James 2:14-26"
}
```

**Output:**

```json
{
  "immediate_context": "James is addressing the problem of a 'dead' faith that has no practical expression.",
  "book_themes": ["wisdom", "integrated faith and works", "endurance in trials"],
  "genre": "New Testament epistle (wisdom‑oriented)",
  "canonical_links": [
    {
      "reference": "Romans 3-4",
      "note": "Paul emphasises justification by faith apart from works of the law."
    }
  ]
}
```

---

### 6. Theological & doctrinal agent

**Input:**

```json
{
  "reference": "James 2:14-26"
}
```

**Output:**

```json
{
  "core_agreements": [
    "True faith produces visible fruit.",
    "Mere verbal profession is not saving faith."
  ],
  "tradition_views": [
    {
      "tradition": "Reformed",
      "summary": "James speaks of justification before people (vindication), not initial justification before God."
    },
    {
      "tradition": "Catholic",
      "summary": "James affirms the necessity of works as cooperation with grace in justification."
    }
  ],
  "debated_points": [
    {
      "issue": "Relationship between faith and works in justification",
      "perspectives": [
        "Works as evidence of faith",
        "Works as instrumental in justification"
      ]
    }
  ]
}
```

---

### 7. Application & reflection agent

**Input:**

```json
{
  "reference": "James 2:14-26",
  "summary_insights": {
    "core_theme": "Living faith vs dead faith",
    "key_principles": ["Faith must be embodied in action"]
  }
}
```

**Output:**

```json
{
  "principles": [
    "Genuine trust in God expresses itself in concrete actions.",
    "Care for the vulnerable is a central expression of living faith."
  ],
  "reflection_questions": [
    "Where might my faith be mostly verbal rather than lived?",
    "Who in my community is in need that I could serve?"
  ],
  "practical_applications": [
    "Commit to a specific act of mercy this week.",
    "Review areas of life where your stated beliefs and actions diverge."
  ]
}
```

---

### 8. Orchestrator agent

**Input:**

```json
{
  "reference": "James 2:14-26",
  "task_type": "interpretation",
  "translation": "ESV",
  "focus_terms": ["faith", "works"]
}
```

**Output (final):**

```json
{
  "summary": "...",
  "text_and_translation": {...},
  "word_study": {...},
  "historical_cultural": {...},
  "literary_canonical": {...},
  "theological_doctrinal": {...},
  "application_reflection": {...}
}
```

---

## C. UI/UX flow for click‑to‑interpret

### 1. Main reading view

- **Layout:**
  - Left: Bible text (chapter view) with verse numbers as clickable elements.  
  - Top bar: version selector (ESV, KJV, etc.), search box, theme toggle.  
  - Right: collapsible “Study Panel”.

- **Interaction:**
  - **Click on a verse number** → highlight verse (or drag to select range).  
  - Floating action button appears: **“Run Interpretation”**.

---

### 2. Interpretation trigger

- User clicks **“Run Interpretation”**.  
- Modal or side panel shows:
  - Selected reference (e.g., “James 2:14–26”).  
  - Options:
    - Quick overview  
    - Full layered study  
    - Focus: word study / historical / doctrinal / application  

- Default: **Full layered study**.

---

### 3. Study panel layout

Once the pipeline runs, the right panel shows sections (accordion style):

1. **Summary interpretation**  
2. **Text & translation notes**  
3. **Word study**  
4. **Historical–cultural context**  
5. **Literary–canonical context**  
6. **Theological–doctrinal perspectives**  
7. **Application & reflection**

Each section is expandable/collapsible.  
Show small badges like “Textual”, “Historical”, “Theological” for quick scanning.

---

### 4. Word study interaction

- In the **Text** section, key terms are underlined.  
- Hover or click → small popup:
  - Lemma, Strong’s number, short gloss.  
  - “Open full word study” → jumps to Word Study section.

---

### 5. Version comparison

- Toggle in the Text section: **“Show version comparison”**.  
- Displays a small table:
  - Rows: versions  
  - Columns: verse text  
- Highlight differing phrases.

---

### 6. History & bookmarks

- Sidebar tab: **“My Studies”**  
  - List of previously interpreted passages.  
  - Click to reopen full layered study.  
- Allow users to **bookmark** a passage + notes.

---

## D. Data model for Bible versions + lexicons

You can implement this in a relational DB or document store; here’s a clean conceptual model.

### 1. Bible text

**Table: `bible_versions`**

- `id` (PK)  
- `code` (e.g., "ESV")  
- `name`  
- `language`  
- `copyright_info`

**Table: `books`**

- `id` (PK)  
- `name` (e.g., "Genesis")  
- `canonical_order`  
- `testament` ("OT"/"NT")

**Table: `verses`**

- `id` (PK)  
- `book_id` (FK → books)  
- `chapter` (int)  
- `verse` (int)

**Table: `verse_texts`**

- `id` (PK)  
- `verse_id` (FK → verses)  
- `version_id` (FK → bible_versions)  
- `text` (string, full verse text)

This lets you query any verse in any version quickly.

---

### 2. Original language & Strong’s mapping

**Table: `lemmas`**

- `id` (PK)  
- `lemma` (e.g., "πίστις")  
- `language` ("Greek", "Hebrew", "Aramaic")  
- `strongs_number` (e.g., "G4102")

**Table: `lemma_definitions`**

- `id` (PK)  
- `lemma_id` (FK → lemmas)  
- `source` (e.g., "Strong", "BDAG")  
- `definition` (text)  
- `semantic_range` (JSON array)

**Table: `verse_lemma_links`**

- `id` (PK)  
- `verse_id` (FK → verses)  
- `lemma_id` (FK → lemmas)  
- `word_index` (position in verse)  
- `english_term` (surface form in a given version, optional)

---

### 3. Cross‑references & canonical links

**Table: `cross_references`**

- `id` (PK)  
- `from_verse_id`  
- `to_verse_id`  
- `type` (e.g., "thematic", "quotation", "allusion")  
- `note`

---

### 4. Historical & theological metadata (optional layer)

You can store curated metadata to support agents:

**Table: `book_metadata`**

- `book_id`  
- `traditional_author`  
- `audience`  
- `approx_date_range`  
- `genre`  
- `summary_themes` (JSON)

**Table: `tradition_notes`**

- `id`  
- `reference` (string, e.g., "James 2:14-26")  
- `tradition`  
- `summary` (short doctrinal note)

---

