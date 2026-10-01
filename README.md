# Kitepche

**Kitepche** is a reading platform for Kyrgyz-language children's books, built around an original NLP component: a readability analyzer that scores how difficult a Kyrgyz text is to read, so books can eventually be matched to a child's reading level automatically.

Kyrgyz is a low-resource language with very little existing NLP tooling. This project's core technical contribution is building that tooling — text analysis and readability scoring — from scratch, then wrapping it in a real product.

**Status:** MVP (minimum viable product) — core readability engine, the Analyze page, and a database-backed book library are functional and in active development. Book content / reading flow, authentication, and an admin panel are the next phase (see Roadmap).

---

## Project architecture

The project is split into two services:

1. **Backend (`/backend`)** — a FastAPI service exposing the Kyrgyz text readability analyzer and the book catalog as an API. Books are stored in PostgreSQL via SQLAlchemy.
2. **Frontend (`/frontend`)** — a React web app for browsing the book library (loaded from the backend) and analyzing Kyrgyz text readability. Login UI is in place but not yet wired to authentication (see Roadmap).

The frontend calls the backend directly at `http://localhost:8000`; the backend's CORS middleware allows the Vite dev server origin (`http://localhost:5173` / `http://127.0.0.1:5173`).

---

## What's built (MVP)

### Backend
- FastAPI app with four endpoints:
  - `GET /` — simple "API is alive" message
  - `GET /health` — health check
  - `POST /analyze` — accepts raw Kyrgyz text, returns readability metrics (returns a `400` with a readable message for empty text or text with no valid words/sentences)
  - `GET /books` — returns the book catalog from the database
- CORS middleware configured for the local Vite dev server
- PostgreSQL database via SQLAlchemy, with a `books` table (`id`, `title`, `age_group`, `cover_url`)
- Config via `pydantic-settings` (`DATABASE_URL` env var, with a local-dev default)
- Seed script (`app/seed.py`) that inserts the 6 sample books
- Original Kyrgyz-aware tokenizer (word/sentence segmentation handling Cyrillic script plus Kyrgyz-specific letters ө, ү)
- Original vowel-based syllable counter for Kyrgyz words
- Two readability scoring models implemented:
  - **ARI** (Automated Readability Index)
  - A **Flesch-style formula (Ateşman constants)**, adapted from Turkish as a first-pass approximation in the absence of a native Kyrgyz readability formula — a known limitation being tracked for future validation/retraining
- Returns word, sentence, character, and syllable counts alongside both readability scores

### Frontend
- React 19 + Vite 8 + Tailwind CSS v4, with React Router for client-side routing
- Two routes: `/` (home) and `/analyze`
- Landing page with header, hero banner, and a book library fetched from the backend's `GET /books`, with loading and error states. The age-group filter (6-7, 8-9, 10-11, 12+) is built from whatever age groups the returned books have
- Analyze page (`/analyze`): submits text to the backend's `POST /analyze` and displays word/sentence/syllable counts alongside ARI and Kyrgyz readability scores — implemented and working end-to-end
- Small API layer in `src/api/` (`books.js`, `analyze.js`) so components don't call `fetch` directly
- Login button present in the header UI as a placeholder — not yet wired to any logic (auth doesn't exist yet, see Roadmap)
- Book cover images are still static files in `frontend/public/books/`; the database stores their paths

---

## Scope of the MVP

This is a functioning proof of concept, not yet a production product. Deliberately out of scope for this phase:
- Book content — the database stores book metadata only (title, age group, cover); there is no book text or reading view yet
- Database migrations — the `books` table was created manually; there is no migration tool (e.g. Alembic) yet
- User accounts and authentication
- Automated tests, CI/CD, and deployment infrastructure
- ML-based scoring (current scoring is formula-based; see Roadmap)

---

## Tech stack

| Layer    | Tech |
|----------|------|
| Backend  | Python, FastAPI, Pydantic, pydantic-settings, Uvicorn, SQLAlchemy 2, psycopg2 |
| Database | PostgreSQL |
| Frontend | React 19, React Router 7, Vite 8, Tailwind CSS v4, ESLint |

---

## Running locally

**Database**

You need a running PostgreSQL server. The default connection string (in `backend/app/core/config.py`) is:
```
postgresql://kitepche:devpassword@localhost:5432/kitepche_db
```
Create that user and database, or set a `DATABASE_URL` environment variable to point somewhere else. The `books` table must exist before seeding (there is no migration/create-table step in the code yet).

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed          # one-time: inserts the 6 sample books (running it again duplicates them)
uvicorn app.main:app --reload
```
API at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

> **Known issue:** `requirements.txt` is currently out of date — it is missing `fastapi`, `uvicorn`, `pydantic`, and `pydantic-settings`, and contains unrelated packages. Until it's regenerated from the backend venv, install those four manually.

**Frontend**
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
- Book content: extend the `books` table with the book's text (and later, its stored readability score)
- Reading flow: when a user opens a book to read, the frontend fetches the book's content from the backend (new endpoint, e.g. `GET /books/{id}`) instead of using static data
- User registration and login: build real auth behind the existing "Login" button in the header
- Admin panel: a restricted view for adding/editing/removing books in the catalog, gated behind auth once it exists

**Phase 3 — ML & NLP depth** *(not required for the current MVP — see note below)*
- Move from formula-based scoring toward a trained/fine-tuned model for Kyrgyz text difficulty classification
- Build and validate a proper Kyrgyz readability formula (replacing the borrowed Turkish constants) against real reading-level data
- Explore additional NLP features (e.g. vocabulary-level tagging) to support recommendations

> **On ML:** the current MVP's readability scoring is fully functional using classical formulas (ARI + an adapted Ateşman formula) — no ML is required for it to work end-to-end. ML becomes worthwhile once a labeled Kyrgyz corpus (text tagged by reading level) exists to train and validate against; until then it's tracked as a future enhancement, not a blocker.

**Phase 4 — Production readiness**
- Automated tests, CI/CD
- Database migrations (e.g. Alembic) instead of manually created tables
- Containerization and deployment

---
