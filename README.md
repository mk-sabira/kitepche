# Kitepche

**Kitepche** is a reading platform for Kyrgyz-language children's books, built around an original NLP component: a readability analyzer that scores how difficult a Kyrgyz text is to read, so books can eventually be matched to a child's reading level automatically.

Kyrgyz is a low-resource language with very little existing NLP tooling. This project's core technical contribution is building that tooling — text analysis and readability scoring — from scratch, then wrapping it in a real product. On top of the analyzer sits an **AI reading assistant**: an LLM that answers questions about a text by calling the analyzer as a tool, so its answer rests on measured numbers, not on the model's impression alone.

**Status:** MVP (minimum viable product) in active development. Working end-to-end: the readability engine and Analyze page, a database-backed book library, and the AI reading assistant (`/assistant`). Book content / reading flow, authentication, and an admin panel are the next phase (see Roadmap). This is a local development project — it is not deployed.

Repository: [github.com/mk-sabira/kitepche](https://github.com/mk-sabira/kitepche)

---

## Project architecture

The project is split into two services plus a database:

1. **Backend (`/backend`)** — a FastAPI service exposing the Kyrgyz text readability analyzer, the book catalog, and the AI reading assistant as an API. Books are stored in PostgreSQL via SQLAlchemy. The assistant calls Google's Gemini API.
2. **Frontend (`/frontend`)** — a React web app for browsing the book library (loaded from the backend), analyzing Kyrgyz text readability, and asking the AI assistant about a text. Login UI is in place but not yet wired to authentication (see Roadmap).
3. **Database** — PostgreSQL 16, run locally with Docker Compose (`docker-compose.yml` at the repo root).

```
Browser (React, :5173)
   │  fetch http://localhost:8000/...
   ▼
FastAPI (:8000) ──► analyzer.py (tokenizer, syllables, ARI, Ateşman-style score)
   │          └──► assistant.py ──► Gemini API (tool calling)
   ▼
PostgreSQL 16 (Docker, localhost:5433)
```

The frontend calls the backend directly at `http://localhost:8000`; the backend's CORS middleware allows the Vite dev server origin (`http://localhost:5173` / `http://127.0.0.1:5173`).

---

## What's built (MVP)

### Backend
- FastAPI app with five endpoints:
  - `GET /` — simple "API is alive" message
  - `GET /health` — health check
  - `POST /analyze` — accepts raw Kyrgyz text, returns readability metrics (returns a `400` with a readable message for empty text or text with no valid words/sentences)
  - `GET /books` — returns the book catalog from the database
  - `POST /assistant` — answers a question about a text using an LLM that calls the analyzer as a tool (see [AI reading assistant](#ai-reading-assistant))
- CORS middleware configured for the local Vite dev server
- PostgreSQL database via SQLAlchemy, with a `books` table (`id`, `title`, `age_group`, `cover_url`). Tables are created on backend startup (`Base.metadata.create_all`)
- Config via `pydantic-settings`, read from `backend/.env` (`DATABASE_URL`, `GEMINI_API_KEY`). Both are required — the backend fails at startup if they're missing, rather than falling back to a hidden default
- Idempotent seed script (`app/seed.py`) that inserts the 6 sample books, skipping any title that already exists
- Original Kyrgyz-aware tokenizer (word/sentence segmentation handling Cyrillic script plus the Kyrgyz-specific letters ң, ө, ү)
- Original vowel-based syllable counter for Kyrgyz words
- Two readability scoring models implemented:
  - **ARI** (Automated Readability Index)
  - A **Flesch-style formula (Ateşman constants)**, adapted from Turkish as a first-pass approximation in the absence of a native Kyrgyz readability formula — not yet validated for Kyrgyz (see [Limitations](#limitations))
- Returns word, sentence, character, and syllable counts alongside both readability scores
- A `find_difficult_words` function that ranks a text's unique words by syllable count, then length, and returns the top 5 (used by the assistant)
- pytest unit tests for the tokenizer (including a regression test for a bug where words containing `ң` were split in two) and for `find_difficult_words`

### Frontend
- React 19 + Vite 8 + Tailwind CSS v4, with React Router for client-side routing
- shadcn/ui components (button, card, input, textarea, select, badge, alert) for the assistant page, with an `@/` import alias
- Three routes: `/` (home), `/analyze`, and `/assistant` ("Ask AI" in the header)
- Landing page with header, hero banner, and a book library fetched from the backend's `GET /books`, with loading and error states. The age-group filter (6-7, 8-9, 10-11, 12+) is built from whatever age groups the returned books have
- Analyze page (`/analyze`): submits text to the backend's `POST /analyze` and displays word/sentence/syllable counts alongside ARI and Kyrgyz readability scores
- Assistant page (`/assistant`): a form with the text, a question, and an answer language (English / Russian / Kyrgyz); shows the answer, a badge for each tool the model used, and an error alert when something fails
- Small API layer in `src/api/` (`books.js`, `analyze.js`, `assistant.js`) so components don't call `fetch` directly
- Book cards fall back to showing the title when a cover image fails to load
- Login button present in the header UI as a placeholder — not yet wired to any logic (auth doesn't exist yet, see Roadmap)
- Book cover images are still static files in `frontend/public/books/`; the database stores their paths

---

## AI reading assistant

A parent or teacher pastes a Kyrgyz text and asks a question in plain language — *"Is this suitable for a 7-year-old?"*, *"Which words might be hard?"* — and picks the answer language (Kyrgyz, Russian, or English).

Instead of letting the model judge the text on its own, the backend gives it two **tools** backed by the project's own analyzer code, and the model decides which to call:

| Tool | What it does |
|------|--------------|
| `analyze_readability` | Runs the existing analyzer: word, sentence, and syllable counts, ARI score, and the Ateşman-style readability score |
| `find_difficult_words` | Ranks the text's unique words by syllable count, then length, and returns the top 5 |

The model can call one tool, both, or neither (for an off-topic question it is instructed to decline briefly). The backend runs a tool-calling loop with a cap on the number of rounds, then returns the final answer together with the list of tools that were called — the frontend shows those as badges, so it's visible which analyzer tools the model consulted.

```
Browser  ──POST /assistant {text, question, language}──►  FastAPI
                                                            │
                                                            ▼
                                              Gemini (Interactions API)
                                                 │ decides: call a tool?
                                  ┌──────────────┼──────────────────┐
                                  ▼              ▼                  ▼
                       analyze_readability  find_difficult_words   no tool
                                  │              │                  │
                                  └──── results sent back ──────────┘
                                                 │  (loop, max 5 rounds)
                                                 ▼
Browser  ◄────────── {answer, tools_used} ─────  FastAPI
```

The system prompt tells the model that the scores come from formulas not yet validated for Kyrgyz, so it should present its conclusion as an estimate and say so.

<!-- TODO: add screenshot of the assistant answering, with the tool badge visible -->

---

## Scope of the MVP

This is a functioning proof of concept, not yet a production product. Deliberately out of scope for this phase:
- Book content — the database stores book metadata only (title, age group, cover); there is no book text or reading view yet
- Database migrations — tables are created on startup with `create_all`, which creates missing tables but does not alter existing ones; there is no migration tool (e.g. Alembic) yet
- User accounts and authentication
- CI/CD and deployment infrastructure (tests exist for the analyzer, but nothing runs them automatically yet)
- ML-based scoring (current scoring is formula-based; see Roadmap)

---

## Limitations

Being explicit about what this does *not* do yet:
- **The readability formulas are not validated for Kyrgyz.** ARI is language-agnostic, and the second score uses Ateşman's constants from Turkish. Both are first-pass approximations until they can be checked against age-labelled Kyrgyz texts.
- **Assistant answers in Kyrgyz are uneven** with the small model used for development; English and Russian answers are more reliable.
- **`/assistant` has no authentication or rate limiting.** Every request spends Gemini API quota, so it must not be exposed publicly as is.
- The assistant's answer is shown as plain text, so Markdown formatting from the model appears as raw `**` markers.
- If the backend can't be reached, the frontend shows the browser's generic "Failed to fetch" message rather than a friendly one.
- `GET /books` has no explicit ordering, so book order can change after updates.
- No auth, no book text/reading view, no database migrations, no CI yet (see Roadmap).

---

## Tech stack

| Layer    | Tech |
|----------|------|
| Backend  | Python, FastAPI, Pydantic v2, pydantic-settings, Uvicorn, SQLAlchemy 2, psycopg2 |
| AI       | Google Gemini API (`google-genai` SDK, Interactions API with function calling) |
| Database | PostgreSQL 16 (Docker Compose for local dev) |
| Frontend | React 19, React Router 7, Vite 8, Tailwind CSS v4, shadcn/ui, ESLint |
| Testing  | pytest |

---

## Running locally

Prerequisites: Python 3, Node.js + npm, Docker (with Compose), and a Gemini API key.

**1. Database**

From the repo root:
```bash
docker compose up -d --wait
```
This starts PostgreSQL 16 in a container (`kitepche-postgres`) on `localhost:5433`, bound to `127.0.0.1` only, with data kept in a named volume (`kitepche_pgdata`). `--wait` returns once the healthcheck passes.

**2. Backend config**

```bash
cd backend
cp .env.example .env
```
Then edit `backend/.env` and replace `your_key_here` with your Gemini API key. The `DATABASE_URL` already matches the Docker Compose database.

`.env` is gitignored. The backend will not start without both values.

**3. Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

Tables are created when the backend starts, so start it at least once **before** seeding. Then, in another terminal (venv active):
```bash
cd backend
python -m app.seed          # inserts the 6 sample books; safe to run again (skips existing titles)
```

**4. Tests**
```bash
cd backend
python -m pytest tests
```

**5. Frontend**
```bash
cd frontend
npm install
npm run dev
```
App at `http://localhost:5173`.

---

## API reference

**`POST /analyze`**
```json
// Request
{ "text": "Kыргыз тилиндеги текст..." }

// Response
{
  "words_count": 0,
  "sentences_count": 0,
  "characters_count": 0,
  "total_syllables": 0,
  "avg_syllables_per_word": 0.0,
  "avg_words_per_sentence": 0.0,
  "avg_characters_per_word": 0.0,
  "ari_score": 0.0,
  "readability_score": 0.0
}
```

Errors: `400` with `{ "detail": "Text is required" }` for empty text, or `{ "detail": "Text has no valid words or sentences" }` when nothing analyzable is found.

**`POST /assistant`**
```json
// Request — language is one of "ky", "ru", "en" (defaults to "en")
{
  "text": "Таңкы мектепке барам. Мен китеп окуймун.",
  "question": "Is this text suitable for a 7-year-old?",
  "language": "en"
}

// Response — tools_used lists every tool call the model made (may be empty)
{
  "answer": "…",
  "tools_used": ["analyze_readability"]
}
```

Errors:
- `422` — invalid input caught by FastAPI validation (missing or empty `text`/`question`, or a `language` other than `ky`/`ru`/`en`)
- `400` — `{ "detail": "Text and question must not be empty" }` when `text` or `question` is whitespace only
- `502` — `{ "detail": "The assistant is unavailable, please try again" }` when the model call fails. The real error is logged server-side and not returned to the client

**`GET /books`**
```json
[
  { "id": 1, "title": "Манас баатыры", "age_group": "10-11", "cover_url": "/books/book-1.jpg" }
]
```

**`GET /health`** → `{ "status": "health ok" }`

---

## Roadmap

**Phase 2 — Product foundation**
- *(Done)* Analyze page wired to `POST /analyze`; books stored in PostgreSQL and served by `GET /books`
- *(Done)* Reproducible local setup: Docker Compose database, `.env`-based config, tables created on startup, idempotent seed, working `requirements.txt`
- *(Done)* AI reading assistant (`POST /assistant` + `/assistant` page) with two analyzer-backed tools
- Protect `/assistant` before it is reachable by anyone else: rate limiting at minimum, and auth once it exists, so the Gemini quota can't be drained
- Small fixes: explicit ordering for `GET /books`, render the assistant's Markdown properly, a friendly message when the backend is unreachable, and remove the unused Vite `/api` proxy (or switch to it)
- Book content: extend the `books` table with the book's text (and later, its stored readability score)
- Reading flow: when a user opens a book, the frontend fetches its content from the backend (new endpoint, e.g. `GET /books/{id}`) and shows a reading page — with an **"Ask about this book"** entry point into the assistant, so the two halves of the project meet
- User registration and login: build real auth behind the existing "Login" button in the header
- Admin panel: a restricted view for adding/editing/removing books in the catalog, gated behind auth once it exists

**Phase 3 — ML & NLP depth** *(not required for the current MVP — see note below)*
- Validate the readability formulas against age-labelled Kyrgyz texts, and build a proper Kyrgyz readability formula (replacing the borrowed Turkish constants) from that data
- Build a small evaluation set for the assistant: questions paired with the tool(s) the model *should* call, to measure tool-routing accuracy and catch regressions when the prompt or model changes
- Move from formula-based scoring toward a trained/fine-tuned model for Kyrgyz text difficulty classification
- Explore additional NLP features (e.g. vocabulary-level tagging) to support recommendations

> **On ML:** the current MVP's readability scoring is fully functional using classical formulas (ARI + an adapted Ateşman formula) — no ML is required for it to work end-to-end. ML becomes worthwhile once a labeled Kyrgyz corpus (text tagged by reading level) exists to train and validate against; until then it's tracked as a future enhancement, not a blocker.

**Phase 4 — Production readiness**
- Database migrations (Alembic) instead of `create_all` on startup
- CI that runs the test suite (and linting) on every push; more tests (API endpoints, frontend components)
- Containerize the backend and frontend (only the database runs in Docker today) and deploy

---
