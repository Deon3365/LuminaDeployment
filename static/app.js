// ══════════════════════════════════════════════
//  Lumina Bible Interpreter — app.js
// ══════════════════════════════════════════════

// If running on GitHub Pages (github.io), we point to the external backend API URL.
// Replace the URL below with your actual deployed Hugging Face Space or Render backend URL.
const API = (window.location.hostname.endsWith('github.io')) 
  ? 'https://your-username-lumina-bible-interpreter.hf.space' 
  : '';

// ── State ──
const state = {
  books: [],
  currentTestament: 'NT',
  currentBook: 'John',
  currentChapter: 3,
  currentVersion: 'kjv',
  selectedVerses: [],
  lastResult: null,
  studies: JSON.parse(localStorage.getItem('lumina_studies') || '[]'),
};

// ── Init ──
async function init() {
  await loadBooks();
  await checkHealth();
  // Default to NT / John / ch.3
  state.currentTestament = 'NT';
  state.currentBook = 'John';
  state.currentChapter = 3;
  document.getElementById('nav-testament').value = 'NT';
  populateBookSelect();
  document.getElementById('nav-book').value = 'John';
  const johnMeta = state.books.find(b => b.name === 'John');
  if (johnMeta) populateChapterSelect(johnMeta.chapters);
  document.getElementById('nav-chapter').value = 3;
  setupEventListeners();
  await loadChapter('John', 3, 'kjv');
  renderStudiesList();
}

async function checkHealth() {
  try {
    const r = await fetch(`${API}/api/health`);
    const data = await r.json();
    const badge = document.getElementById('rag-status-badge');
    if (!badge) return;
    if (data.kb_status === 'ready') {
      badge.innerHTML = `<span class="status-dot" style="width:6px;height:6px;background:#4CAF50;border-radius:50%"></span> KB: Ready`;
      badge.style.color = '#4CAF50';
    } else if (data.kb_status === 'indexing_required') {
      badge.innerHTML = `<span class="status-dot" style="width:6px;height:6px;background:var(--gold);border-radius:50%"></span> KB: Indexing...`;
    }
  } catch { /* offline */ }
}

// ── Load books from API ──
async function loadBooks() {
  try {
    const r = await fetch(`${API}/api/books`);
    const data = await r.json();
    state.books = data.books || [];
  } catch {
    state.books = [];
  }
}

// ── Populate book <select> ──
function populateBookSelect() {
  const testament = state.currentTestament;
  const bookSel = document.getElementById('nav-book');
  const filtered = state.books.filter(b => b.testament === testament);
  bookSel.innerHTML = filtered.map(b =>
    `<option value="${b.name}">${b.name}</option>`
  ).join('');
  if (filtered.length) {
    const first = filtered[0];
    state.currentBook = first.name;
    state.currentChapter = 1;
    populateChapterSelect(first.chapters);
  }
}

function populateChapterSelect(numChapters) {
  const sel = document.getElementById('nav-chapter');
  sel.innerHTML = Array.from({length: numChapters}, (_, i) =>
    `<option value="${i+1}">${i+1}</option>`
  ).join('');
  sel.value = state.currentChapter;
}

// ── Load & render a chapter ──
async function loadChapter(book, chapter, version) {
  state.currentBook = book;
  state.currentChapter = chapter;
  state.currentVersion = version;
  state.selectedVerses = [];
  hideFloatBtn();

  const container = document.getElementById('verses-container');
  const heading   = document.getElementById('chapter-heading');
  heading.textContent = `${book} ${chapter}`;

  // Show skeletons
  container.innerHTML = Array.from({length: 12}, () =>
    `<div class="skeleton skeleton-verse"></div>`
  ).join('');

  try {
    const r = await fetch(`${API}/api/chapter?book=${encodeURIComponent(book)}&chapter=${chapter}&version=${version}`);
    if (!r.ok) throw new Error('fetch failed');
    const data = await r.json();
    const verses = data.verses || [];
    if (!verses.length) {
      container.innerHTML = `<p style="color:var(--text-muted);padding:20px">No text returned for ${book} ${chapter}.</p>`;
      return;
    }
    container.innerHTML = verses.map(v =>
      `<div class="verse-row" id="v${v.verse}" data-verse="${v.verse}" onclick="toggleVerse(${v.verse})">
        <span class="verse-num">${v.verse}</span>
        <span class="verse-text">${v.text.trim()}</span>
      </div>`
    ).join('');
  } catch {
    container.innerHTML = `<p style="color:var(--text-muted);padding:20px 0">Could not load chapter. Check your internet connection.</p>`;
  }
}

// ── Verse selection ──
function toggleVerse(num) {
  const idx = state.selectedVerses.indexOf(num);
  const el  = document.getElementById(`v${num}`);
  if (idx === -1) {
    state.selectedVerses.push(num);
    el?.classList.add('selected');
  } else {
    state.selectedVerses.splice(idx, 1);
    el?.classList.remove('selected');
  }
  state.selectedVerses.length ? showFloatBtn() : hideFloatBtn();
}

function getSelectedReference() {
  if (!state.selectedVerses.length) return null;
  const sorted = [...state.selectedVerses].sort((a, b) => a - b);
  const ref = sorted.length === 1
    ? `${state.currentBook} ${state.currentChapter}:${sorted[0]}`
    : `${state.currentBook} ${state.currentChapter}:${sorted[0]}-${sorted[sorted.length-1]}`;
  return ref;
}

function showFloatBtn() {
  const btn = document.getElementById('float-interpret');
  const ref = getSelectedReference();
  btn.style.display = 'flex';
  btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg> Interpret ${ref}`;
}

function hideFloatBtn() {
  document.getElementById('float-interpret').style.display = 'none';
}

// ── Run interpretation ──
async function runInterpretation(reference) {
  document.getElementById('study-welcome').style.display  = 'none';
  document.getElementById('study-loading').style.display  = 'flex';
  document.getElementById('study-results').style.display  = 'none';
  document.getElementById('study-reference').textContent  = reference;
  document.getElementById('study-status').textContent     = 'Analysing…';
  document.getElementById('btn-bookmark').style.display   = 'none';
  document.getElementById('btn-copy-study').style.display = 'none';

  // Animate steps
  const steps = ['intake','translation','word','historical','literary','theological','application'];
  let i = 0;
  const stepTimer = setInterval(() => {
    if (i > 0) document.getElementById(`step-${steps[i-1]}`)?.classList.replace('active','done');
    if (i < steps.length) document.getElementById(`step-${steps[i]}`)?.classList.add('active');
    i++;
    if (i > steps.length) clearInterval(stepTimer);
  }, 900);

  try {
    const r = await fetch(`${API}/api/interpret`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        reference,
        task_type: 'interpretation',
        translation: state.currentVersion,
        focus_terms: [],
        depth: 'full'
      })
    });
    clearInterval(stepTimer);
    steps.forEach(s => {
      document.getElementById(`step-${s}`)?.classList.remove('active');
      document.getElementById(`step-${s}`)?.classList.add('done');
    });

    if (!r.ok) throw new Error(`API error ${r.status}`);
    const data = await r.json();
    state.lastResult = data;

    // Reset step classes
    steps.forEach(s => {
      const el = document.getElementById(`step-${s}`);
      if (el) { el.className = 'loader-step'; }
    });

    // ── Handle Gemini API key missing ──
    if (data.error === 'GEMINI_API_KEY_MISSING') {
      document.getElementById('study-loading').style.display  = 'none';
      document.getElementById('study-welcome').style.display  = 'flex';
      document.getElementById('study-reference').textContent  = 'API Key Missing';
      document.getElementById('study-status').textContent     = 'Set GEMINI_API_KEY';
      showToast('🔑 Gemini API key is missing. Set GEMINI_API_KEY in your env file or hosting platform settings.', 9000);
      return;
    }

    // ── Handle Gemini rate limit ──
    if (data.error === 'RATE_LIMIT') {
      document.getElementById('study-loading').style.display = 'none';
      document.getElementById('study-welcome').style.display = 'flex';
      document.getElementById('study-reference').textContent = 'Quota limit reached';
      document.getElementById('study-status').textContent    = 'Please wait a moment';
      showToast('⏳ Gemini API rate limit reached. Please wait ~1 minute and retry.', 7000);
      return;
    }

    // ── Handle generic API errors ──
    if (data.error) {
      document.getElementById('study-loading').style.display = 'none';
      document.getElementById('study-welcome').style.display = 'flex';
      document.getElementById('study-reference').textContent = 'API Error';
      document.getElementById('study-status').textContent    = 'Interpretation failed';
      showToast('⚠ Error: ' + (data.message || 'Gemini API invocation failed.'), 8000);
      return;
    }

    renderResults(data);
    saveStudy(reference, data);

  } catch (e) {
    clearInterval(stepTimer);
    document.getElementById('study-loading').style.display = 'none';
    document.getElementById('study-welcome').style.display = 'flex';
    showToast('⚠ Interpretation failed. Check console for details.');
    console.error(e);
  }
}

// ── Render results ──
function renderResults(data) {
  document.getElementById('study-loading').style.display = 'none';
  document.getElementById('study-results').style.display = 'block';
  document.getElementById('study-status').textContent     = 'Complete';
  document.getElementById('btn-bookmark').style.display   = 'flex';
  document.getElementById('btn-copy-study').style.display = 'flex';

  document.getElementById('result-summary').textContent =
    data.summary || 'Interpretation complete.';

  renderTranslation(data.text_and_translation || {});
  renderWordStudy(data.word_study || {});
  renderHistorical(data.historical_cultural || {});
  renderLiterary(data.literary_canonical || {});
  renderTheological(data.theological_doctrinal || {});
  renderApplication(data.application_reflection || {});
  renderRAG(data.rag_context || {});

  document.getElementById('study-panel').querySelector('#study-content').scrollTop = 0;
}

function renderRAG(d) {
  const vList = document.getElementById('rag-verses');
  const cList = document.getElementById('rag-culture');
  const tList = document.getElementById('rag-commentary');

  const verses = arr(d.related_verses);
  vList.innerHTML = verses.length ? verses.map(v => `<div class="rag-item">• ${esc(v)}</div>`).join('') : '<div class="rag-empty">No direct cross-references found.</div>';

  const culture = arr(d.historical_cultural);
  cList.innerHTML = culture.length ? culture.map(c => `<div class="rag-item" style="padding-bottom:10px">${esc(c)}</div>`).join('') : '<div class="rag-empty">No specific cultural data available for this query.</div>';

  const comms = arr(d.commentary);
  tList.innerHTML = comms.length ? comms.map(c => `<div class="rag-item" style="padding-bottom:10px">${esc(c)}</div>`).join('') : '<div class="rag-empty">No historical commentary snippets found.</div>';
}

function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function arr(v) { return Array.isArray(v) ? v : []; }
function block(label, content) {
  return `<div class="content-block"><div class="content-label">${label}</div><div class="content-text">${content}</div></div>`;
}

function renderTranslation(d) {
  const el = document.getElementById('content-translation');
  const translations = d.translations || {};
  let html = '';

  if (Object.keys(translations).length) {
    html += `<button class="compare-toggle" onclick="toggleCompare(this)">⇄ Show Version Comparison</button>
    <div class="translation-grid" id="trans-grid">`;
    for (const [ver, text] of Object.entries(translations)) {
      html += `<div class="translation-card"><div class="translation-version">${esc(ver)}</div><div class="translation-text">${esc(text)}</div></div>`;
    }
    html += `</div>`;
  }

  const diffs = arr(d.differences);
  if (diffs.length) {
    html += `<div class="content-block" id="compare-block" style="display:none"><div class="content-label">Translation Differences</div>
    <table class="diff-table"><thead><tr><th>Term</th><th>Versions</th><th>Note</th></tr></thead><tbody>`;
    diffs.forEach(df => {
      const vers = arr(df.versions).join(', ');
      html += `<tr><td><strong>${esc(df.term||'')}</strong></td><td style="color:var(--gold-dim)">${esc(vers)}</td><td>${esc(df.note||'')}</td></tr>`;
    });
    html += `</tbody></table></div>`;
  }

  if (d.translation_notes) html += block('Translation Notes', esc(d.translation_notes));
  el.innerHTML = html || '<p style="color:var(--text-muted)">No translation data.</p>';
}

function toggleCompare(btn) {
  const block = document.getElementById('compare-block');
  if (!block) return;
  const showing = block.style.display !== 'none';
  block.style.display = showing ? 'none' : 'block';
  btn.textContent = showing ? '⇄ Show Version Comparison' : '⇄ Hide Version Comparison';
}

function renderWordStudy(d) {
  const el = document.getElementById('content-word');
  const studies = arr(d.word_studies);
  if (!studies.length) { el.innerHTML = '<p style="color:var(--text-muted)">No word study data.</p>'; return; }
  el.innerHTML = studies.map(ws => `
    <div class="word-card">
      <div class="word-card-header">
        <span class="word-english">${esc(ws.english||'')}</span>
        <span class="word-lemma">${esc(ws.lemma||'')}</span>
        <span class="word-translit">${esc(ws.transliteration||'')}</span>
        <span class="word-strongs">${esc(ws.strongs||'')}</span>
      </div>
      <div class="semantic-tags">${arr(ws.semantic_range).map(t=>`<span class="semantic-tag">${esc(t)}</span>`).join('')}</div>
      ${ws.contextual_note ? block('Contextual Meaning', esc(ws.contextual_note)) : ''}
      ${ws.translation_note ? block('Translation Note', esc(ws.translation_note)) : ''}
      ${arr(ws.usage_examples).length ? `<div class="content-block"><div class="content-label">Usage Examples</div>
        ${arr(ws.usage_examples).map(ex=>`<div style="padding:4px 0;font-size:0.84rem"><span style="color:var(--gold)">${esc(ex.reference||'')}</span> — ${esc(ex.note||'')}</div>`).join('')}
      </div>` : ''}
    </div>`).join('');
}

function renderHistorical(d) {
  const el = document.getElementById('content-historical');
  let html = '';
  if (d.author)           html += block('Author', esc(d.author));
  if (d.audience)         html += block('Audience', esc(d.audience));
  if (d.date_range)       html += block('Date', esc(d.date_range));
  if (d.setting)          html += block('Setting', esc(d.setting));
  if (d.historical_context) html += block('Historical Context', esc(d.historical_context));
  if (arr(d.cultural_background).length)
    html += `<div class="content-block"><div class="content-label">Cultural Background</div><ul style="padding-left:16px;display:flex;flex-direction:column;gap:5px">${arr(d.cultural_background).map(c=>`<li style="font-size:0.87rem;color:var(--text)">${esc(c)}</li>`).join('')}</ul></div>`;
  if (arr(d.source_notes).length)
    html += `<div class="content-block"><div class="content-label">Source Notes</div>${arr(d.source_notes).map(s=>`<div style="font-size:0.82rem;color:var(--text-muted);padding:3px 0">• ${esc(s)}</div>`).join('')}</div>`;
  if (d.certainty_note)   html += block('Certainty Note', `<em style="color:var(--text-muted)">${esc(d.certainty_note)}</em>`);
  el.innerHTML = html || '<p style="color:var(--text-muted)">No historical data.</p>';
}

function renderLiterary(d) {
  const el = document.getElementById('content-literary');
  let html = '';
  if (d.immediate_context) html += block('Immediate Context', esc(d.immediate_context));
  if (arr(d.book_themes).length)
    html += `<div class="content-block"><div class="content-label">Book Themes</div><div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">${arr(d.book_themes).map(t=>`<span class="semantic-tag">${esc(t)}</span>`).join('')}</div></div>`;
  if (d.genre)      html += block('Genre', esc(d.genre));
  if (d.genre_note) html += block('Genre Impact on Interpretation', esc(d.genre_note));
  if (arr(d.canonical_links).length)
    html += `<div class="content-block"><div class="content-label">Canonical Links</div>${arr(d.canonical_links).map(l=>`<div style="padding:6px 0;border-bottom:1px solid var(--border)"><span style="color:var(--gold);font-weight:700">${esc(l.reference||'')}</span> — <span style="font-size:0.85rem;color:var(--text)">${esc(l.note||'')}</span></div>`).join('')}</div>`;
  if (d.tensions_harmonisations) html += block('Tensions & Harmonisation', esc(d.tensions_harmonisations));
  el.innerHTML = html || '<p style="color:var(--text-muted)">No literary data.</p>';
}

function renderTheological(d) {
  const el = document.getElementById('content-theological');
  let html = '';
  if (arr(d.core_agreements).length)
    html += `<div class="content-block"><div class="content-label">Core Orthodox Agreements</div><ul class="principle-list">${arr(d.core_agreements).map(a=>`<li>${esc(a)}</li>`).join('')}</ul></div>`;
  if (arr(d.tradition_views).length)
    html += `<div class="content-block"><div class="content-label">Tradition Views</div>${arr(d.tradition_views).map(t=>`<div class="tradition-card"><div class="tradition-name">${esc(t.tradition||'')}</div><div class="tradition-summary">${esc(t.summary||'')}</div>${arr(t.key_texts).length?`<div style="margin-top:6px;font-size:0.75rem;color:var(--gold-dim)">${arr(t.key_texts).join(' · ')}</div>`:''}</div>`).join('')}</div>`;
  if (arr(d.debated_points).length)
    html += `<div class="content-block"><div class="content-label">Debated Points</div>${arr(d.debated_points).map(dp=>`<div style="margin-bottom:10px"><div class="debate-issue">${esc(dp.issue||'')}</div><div class="debate-perspectives">${arr(dp.perspectives).map(p=>`<div class="debate-view">${typeof p==='string'?esc(p):`<strong>${esc(p.view||'')}</strong>${p.proponents?` <span style="color:var(--text-dim)">(${arr(p.proponents).join(', ')})</span>`:''}`}</div>`).join('')}</div></div>`).join('')}</div>`;
  if (d.historical_interpretation_note) html += block('Historical Interpretation', esc(d.historical_interpretation_note));
  el.innerHTML = html || '<p style="color:var(--text-muted)">No theological data.</p>';
}

function renderApplication(d) {
  const el = document.getElementById('content-application');
  let html = '';
  if (arr(d.principles).length)
    html += `<div class="content-block"><div class="content-label">Timeless Principles</div><ul class="principle-list">${arr(d.principles).map(p=>`<li>${esc(p)}</li>`).join('')}</ul></div>`;
  if (d.cultural_vs_universal) html += block('Cultural vs. Universal', esc(d.cultural_vs_universal));
  if (arr(d.reflection_questions).length)
    html += `<div class="content-block"><div class="content-label">Reflection Questions</div><ul class="question-list">${arr(d.reflection_questions).map(q=>`<li>${esc(q)}</li>`).join('')}</ul></div>`;
  if (arr(d.practical_applications).length)
    html += `<div class="content-block"><div class="content-label">Practical Applications</div><ul class="app-list">${arr(d.practical_applications).map(a=>`<li>${esc(a)}</li>`).join('')}</ul></div>`;
  el.innerHTML = html || '<p style="color:var(--text-muted)">No application data.</p>';
}

// ── Accordion ──
function toggleAccordion(id) {
  document.getElementById(id)?.classList.toggle('open');
}

// ── Studies (localStorage) ──
function saveStudy(reference, data) {
  const study = {
    reference,
    date: new Date().toISOString(),
    summary: data.summary || '',
    data,
  };
  state.studies = [study, ...state.studies.filter(s => s.reference !== reference)].slice(0, 50);
  localStorage.setItem('lumina_studies', JSON.stringify(state.studies));
  renderStudiesList();
}

function renderStudiesList() {
  const list = document.getElementById('studies-list');
  if (!state.studies.length) {
    list.innerHTML = '<p class="no-studies">No studies yet. Interpret a passage to begin.</p>';
    return;
  }
  list.innerHTML = state.studies.map((s, i) => `
    <div class="study-history-item" onclick="reloadStudy(${i})">
      <div class="study-history-ref">${esc(s.reference)}</div>
      <div class="study-history-date">${new Date(s.date).toLocaleDateString()}</div>
      <div class="study-history-preview">${esc((s.summary||'').slice(0,100))}</div>
    </div>`).join('');
}

function reloadStudy(i) {
  const s = state.studies[i];
  if (!s) return;
  document.getElementById('study-reference').textContent = s.reference;
  state.lastResult = s.data;
  renderResults(s.data);
  toggleStudiesSidebar();
}

function toggleStudiesSidebar() {
  document.getElementById('studies-sidebar').classList.toggle('open');
}

// ── Bookmark ──
function bookmarkCurrent() {
  if (!state.lastResult) return;
  showToast('✓ Study bookmarked');
}

// ── Copy study text ──
function copyStudy() {
  if (!state.lastResult) return;
  const d = state.lastResult;
  const text = [
    `LUMINA BIBLE STUDY — ${d.reference}`,
    `\nSUMMARY\n${d.summary}`,
    `\nWORD STUDY\n${(d.word_study?.word_studies||[]).map(w=>`${w.english} (${w.lemma} ${w.strongs}): ${(w.semantic_range||[]).join(', ')}`).join('\n')}`,
    `\nHISTORICAL CONTEXT\n${d.historical_cultural?.historical_context||''}`,
    `\nAPPLICATION\n${(d.application_reflection?.practical_applications||[]).join('\n')}`,
  ].join('\n');
  navigator.clipboard.writeText(text).then(() => showToast('✓ Study copied to clipboard'));
}

// ── Toast ──
function showToast(msg, duration = 3000) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), duration);
}

// ── Quick load shortcuts ──
function quickLoad(reference) {
  document.getElementById('study-welcome').style.display = 'none';
  runInterpretation(reference);
}

// ── Search ──
async function handleSearch(q) {
  if (!q.trim()) {
    document.getElementById('search-results-overlay').style.display = 'none';
    return;
  }
  // Try to parse as a Bible reference first
  try {
    const r = await fetch(`${API}/api/parse-query`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({raw_query: q, default_translation: state.currentVersion})
    });
    const data = await r.json();
    if (data.reference && !data.error) {
      showSearchResult([{reference: data.reference, text: `Navigate to ${data.reference}`}], q);
    }
  } catch { /* silent */ }
}

function showSearchResult(items, q) {
  const overlay = document.getElementById('search-results-overlay');
  overlay.style.display = 'block';
  overlay.innerHTML = items.map(item => `
    <div class="search-result-item" onclick="navigateToRef('${esc(item.reference)}')">
      <div class="search-result-ref">${esc(item.reference)}</div>
      <div class="search-result-text">${esc(item.text)}</div>
    </div>`).join('');
}

async function navigateToRef(reference) {
  document.getElementById('search-results-overlay').style.display = 'none';
  document.getElementById('search-input').value = '';
  // Parse reference and navigate
  const r = await fetch(`${API}/api/parse-query`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({raw_query: reference})
  });
  const data = await r.json();
  runInterpretation(data.reference || reference);
}

// ── Event listeners ──
function setupEventListeners() {
  // Testament change
  document.getElementById('nav-testament').addEventListener('change', e => {
    state.currentTestament = e.target.value;
    populateBookSelect();
  });

  // Book change
  document.getElementById('nav-book').addEventListener('change', e => {
    state.currentBook = e.target.value;
    state.currentChapter = 1;
    const book = state.books.find(b => b.name === state.currentBook);
    if (book) populateChapterSelect(book.chapters);
    loadChapter(state.currentBook, 1, state.currentVersion);
  });

  // Chapter select
  document.getElementById('nav-chapter').addEventListener('change', e => {
    state.currentChapter = parseInt(e.target.value);
    loadChapter(state.currentBook, state.currentChapter, state.currentVersion);
  });

  // Chapter nav arrows
  document.getElementById('nav-chapter-prev').addEventListener('click', () => {
    if (state.currentChapter > 1) {
      state.currentChapter--;
      document.getElementById('nav-chapter').value = state.currentChapter;
      loadChapter(state.currentBook, state.currentChapter, state.currentVersion);
    }
  });
  document.getElementById('nav-chapter-next').addEventListener('click', () => {
    const book = state.books.find(b => b.name === state.currentBook);
    if (book && state.currentChapter < book.chapters) {
      state.currentChapter++;
      document.getElementById('nav-chapter').value = state.currentChapter;
      loadChapter(state.currentBook, state.currentChapter, state.currentVersion);
    }
  });

  // Version selectors
  document.getElementById('version-select-reader').addEventListener('change', e => {
    state.currentVersion = e.target.value;
    loadChapter(state.currentBook, state.currentChapter, state.currentVersion);
  });
  document.getElementById('version-select-global').addEventListener('change', e => {
    state.currentVersion = e.target.value;
    document.getElementById('version-select-reader').value = e.target.value;
    loadChapter(state.currentBook, state.currentChapter, state.currentVersion);
  });

  // Interpret button
  document.getElementById('float-interpret').addEventListener('click', () => {
    const ref = getSelectedReference();
    if (ref) runInterpretation(ref);
  });

  // Studies sidebar
  document.getElementById('btn-studies').addEventListener('click', toggleStudiesSidebar);

  // Bookmark
  document.getElementById('btn-bookmark').addEventListener('click', bookmarkCurrent);

  // Copy
  document.getElementById('btn-copy-study').addEventListener('click', copyStudy);

  // Search
  let searchTimer;
  document.getElementById('search-input').addEventListener('input', e => {
    const val = e.target.value;
    document.getElementById('search-clear').style.display = val ? 'block' : 'none';
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => handleSearch(val), 500);
  });
  document.getElementById('search-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      clearTimeout(searchTimer);
      navigateToRef(e.target.value);
    }
    if (e.key === 'Escape') {
      document.getElementById('search-results-overlay').style.display = 'none';
      e.target.value = '';
      document.getElementById('search-clear').style.display = 'none';
    }
  });
  document.getElementById('search-clear').addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    document.getElementById('search-clear').style.display = 'none';
    document.getElementById('search-results-overlay').style.display = 'none';
  });

  // Close overlays on outside click
  document.addEventListener('click', e => {
    if (!e.target.closest('#search-box') && !e.target.closest('#search-results-overlay')) {
      document.getElementById('search-results-overlay').style.display = 'none';
    }
    if (!e.target.closest('#studies-sidebar') && !e.target.closest('#btn-studies')) {
      document.getElementById('studies-sidebar').classList.remove('open');
    }
  });

  // Keyboard shortcut: / to focus search
  document.addEventListener('keydown', e => {
    if (e.key === '/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      document.getElementById('search-input').focus();
    }
  });
}

// ── Bootstrap ──
document.addEventListener('DOMContentLoaded', init);
