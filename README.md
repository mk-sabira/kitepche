# Kitepche

[![CI](https://github.com/mk-sabira/kitepche/actions/workflows/ci.yml/badge.svg)](https://github.com/mk-sabira/kitepche/actions/workflows/ci.yml)

**Kitepche** is a reading platform for Kyrgyz-language children's books, built around an original NLP component: a readability analyzer that scores how difficult a Kyrgyz text is to read, so books can eventually be matched to a child's reading level automatically.

Kyrgyz is a low-resource language with very little existing NLP tooling. This project's core technical contribution is building that tooling — text analysis and readability scoring — from scratch, then wrapping it in a real product. On top of the analyzer sits an **AI reading assistant**: an LLM that answers questions about a text by calling the analyzer as a tool, so its answer rests on measured numbers, not on the model's impression alone.

**Status:** MVP (minimum viable product) in active development. Working end-to-end: the readability engine and Analyze page, a database-backed book library with a reading page for each book, user accounts (register, log in and log out, with the login kept in an httpOnly cookie), and the AI reading assistant (`/assistant`), which requires a login and can be opened from a book with its text filled in. The book texts are short placeholders for now. Reading history, user profiles, and an admin panel are the next phase (see Roadmap). This is a local development project — it is not deployed.

Repository: [github.com/mk-sabira/kitepche](https://github.com/mk-sabira/kitepche)

---

## Project architecture

The project is split into two services plus a database:

1. **Backend (`/backend`)** — a FastAPI service exposing the Kyrgyz text readability analyzer, the book catalog, user accounts (register, log in), and the AI reading assistant as an API. Data is stored in PostgreSQL via SQLAlchemy. The assistant calls Google's Gemini API.
2. **Frontend (`/frontend`)** — a React web app for browsing the book library, analyzing Kyrgyz text readability, creating an account and logging in, and asking the AI assistant about a text (logged-in users only).
3. **Database** — PostgreSQL 16, run locally with Docker Compose (`docker-compose.yml` at the repo root).

```
Browser (React, :5173)
   │  fetch http://localhost:8000/...   (login cookie sent with credentials: 'include')
   ▼
FastAPI (:8000) ──► auth (bcrypt password hashes, JWT in an httpOnly cookie, Origin check)
   │          ├──► analyzer.py (tokenizer, syllables, ARI, Ateşman-style score)
   │          └──► assistant.py ──► Gemini API (tool calling)
   ▼
PostgreSQL 16 (Docker, localhost:5433)
```

The frontend calls the backend directly at the address in `VITE_API_URL` (default `http://localhost:8000`). The backend's CORS middleware allows the origins listed in `CORS_ORIGINS` (default: the Vite dev server, `http://localhost:5173` and `http://127.0.0.1:5173`) and allows credentials, so the browser can send the login cookie.

---

## What's built (MVP)

### Backend
- FastAPI app with ten endpoints:
  - `GET /` — simple "API is alive" message
  - `GET /health` — health check
  - `POST /analyze` — accepts raw Kyrgyz text, returns readability metrics (returns a `400` with a readable message for empty text or text with no valid words/sentences)
  - `GET /books` — returns the published books from the database, ordered by id (without their text)
  - `GET /books/{id}` — returns one published book with its text and source (`404` for a missing or unpublished book)
  - `POST /auth/register` — creates an account (email and password); the password is hashed and never returned
  - `POST /auth/login` — checks the credentials, sets a signed access token (JWT, valid for 24 hours) in an httpOnly cookie, and returns the user
  - `POST /auth/logout` — clears the login cookie
  - `GET /auth/me` — returns the logged-in user (read from the cookie); this is the check other endpoints use to require a login
  - `POST /assistant` — answers a question about a text using an LLM that calls the analyzer as a tool (see [AI reading assistant](#ai-reading-assistant)); it requires a login and is limited to 10 questions per user per hour
- CORS middleware for the origins in `CORS_ORIGINS` (default: the local Vite dev server), with credentials allowed for the login cookie; it also exposes the `Retry-After` header, so the browser can read how long to wait after a rate-limit response
- An Origin check (`app/core/origin.py`): a `POST`/`PUT`/`PATCH`/`DELETE` request whose `Origin` header is not in `CORS_ORIGINS` gets `403`, as a defense against cross-site request forgery (see [Authentication](#authentication))
- PostgreSQL database via SQLAlchemy, with a `books` table (`id`, `title`, `age_group`, `cover_url`, `text` and `source` (both optional), and `status` (`draft`/`published`, default `published`)) and a `users` table (`id`, `email`, `hashed_password`, `role`, `created_at`). Schema is managed with Alembic migrations (`backend/alembic/`); the app does not create tables itself
- Config via `pydantic-settings`, read from `backend/.env` (`DATABASE_URL`, `GEMINI_API_KEY`, `SECRET_KEY`). All three are required — the backend fails at startup if one is missing, rather than falling back to a hidden default. Two optional settings have defaults for local development: `CORS_ORIGINS` (comma-separated frontend addresses) and `COOKIE_SECURE` (default `false`)
- Seed script (`app/seed.py`) that loads the books from `backend/data/books.json` (6 books with short placeholder texts, `source: "placeholder"`). It matches books by title: new titles are inserted, existing ones are updated from the file, so the JSON file is the source of truth and the script is safe to run again
- Original Kyrgyz-aware tokenizer (word/sentence segmentation handling Cyrillic script plus the Kyrgyz-specific letters ң, ө, ү)
- Original vowel-based syllable counter for Kyrgyz words
- Two readability scoring models implemented:
  - **ARI** (Automated Readability Index)
  - A **Flesch-style formula (Ateşman constants)**, adapted from Turkish as a first-pass approximation in the absence of a native Kyrgyz readability formula — not yet validated for Kyrgyz (see [Limitations](#limitations))
- Returns word, sentence, character, and syllable counts alongside both readability scores
- A `find_difficult_words` function that ranks a text's unique words by syllable count, then length, and returns the top 5 (used by the assistant)
- A small in-memory rate limiter (sliding window per user) in front of the model call
- pytest tests for the tokenizer (including a regression test for a bug where words containing `ң` were split in two), `find_difficult_words`, password hashing and tokens, the rate limiter, the `CORS_ORIGINS` setting, the Origin check, and the register, login, logout, `/auth/me`, `/assistant`, `/books` and `/books/{id}` endpoints (60 tests). The endpoint tests use an in-memory SQLite database and a fake model, so they need neither PostgreSQL nor the Gemini API

### Frontend
- React 19 + Vite 8 + Tailwind CSS v4, with React Router for client-side routing
- shadcn/ui components (button, card, input, textarea, select, badge, alert) for the assistant, login and register pages, with an `@/` import alias
- Six routes: `/` (home), `/analyze`, `/assistant` ("Ask AI" in the header), `/login`, `/register` and `/books/:id`
- Landing page with header, hero banner, and a book library fetched from the backend's `GET /books`, with loading and error states. The age-group filter (6-7, 8-9, 10-11, 12+) is built from whatever age groups the returned books have
- Book page (`/books/:id`): each book card links to it. It fetches the book from `GET /books/{id}` and shows the title, age group and text, with loading and error ("Book not found.") states, "Text coming soon." for a book without text, and a link back to the library. An **"Ask AI about this book"** button opens `/assistant` with the book's text already filled in (passed through React Router navigation state)
- Analyze page (`/analyze`): submits text to the backend's `POST /analyze` and displays word/sentence/syllable counts alongside ARI and Kyrgyz readability scores
- Assistant page (`/assistant`): a form with the text, a question, and an answer language (English / Russian / Kyrgyz); shows the answer, a badge for each tool the model used, and an error alert when something fails. Logged-out visitors see a login card instead of the form; an expired login signs the user out, and the hourly limit shows a clear message
- Login and register pages. The login state lives in a React context; the page never sees the token (it is in an httpOnly cookie), so on load the context asks `GET /auth/me` who is logged in, and "Log out" calls `POST /auth/logout`. The header shows "Log in" and "Sign up", or the user's email and "Log out"
- Small API layer in `src/api/` (`books.js`, `analyze.js`, `assistant.js`, `auth.js`) so components don't call `fetch` directly. The API address comes from `VITE_API_URL` (read in `src/api/config.js`, default `http://localhost:8000`), and every call that needs the login sends `credentials: 'include'`
- Book cards fall back to showing the title when a cover image fails to load
- Book cover images are still static files in `frontend/public/books/`; the database stores their paths

---

## AI reading assistant

A logged-in parent or teacher pastes a Kyrgyz text and asks a question in plain language — *"Is this suitable for a 7-year-old?"*, *"Which words might be hard?"* — and picks the answer language (Kyrgyz, Russian, or English).

Instead of letting the model judge the text on its own, the backend gives it two **tools** backed by the project's own analyzer code, and the model decides which to call:

| Tool | What it does |
|------|--------------|
| `analyze_readability` | Runs the existing analyzer: word, sentence, and syllable counts, ARI score, and the Ateşman-style readability score |
| `find_difficult_words` | Ranks the text's unique words by syllable count, then length, and returns the top 5 |

The model can call one tool, both, or neither (for an off-topic question it is instructed to decline briefly). The backend runs a tool-calling loop with a cap on the number of rounds, then returns the final answer together with the list of tools that were called — the frontend shows those as badges, so it's visible which analyzer tools the model consulted.

```
Browser  ──POST /assistant {text, question, language} + login cookie─►  FastAPI
                                                            │  checks the login, then the hourly limit
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

## Authentication

Users register with an email and a password and log in; the backend then keeps them logged in with an access token in an httpOnly cookie. The assistant endpoint requires a login.

- **Passwords** are hashed with bcrypt (through `pwdlib`) and never stored or returned in plain text. They are Unicode-normalized (NFKC) before hashing, so the same Kyrgyz or Russian password typed on two devices gives the same result. bcrypt reads only the first 72 bytes and a Cyrillic letter takes 2 bytes, so passwords over 72 bytes (about 36 Cyrillic letters) are rejected with a clear message instead of being silently cut off. The minimum is 8 characters.
- **Emails** are trimmed and lowercased, so `Dati@x.com` and `dati@x.com` are one account.
- **Login** uses the standard OAuth2 password form (the email goes in the `username` field). On success it creates a signed JWT (HS256) that carries the user's id and expires after 24 hours, puts it in a cookie named `access_token`, and returns the user (id, email, role) — the token itself is never in the response body. A wrong email and a wrong password get the same `401` message, and an unknown email still runs a dummy password check, so response time doesn't reveal which emails have accounts.
- **The cookie** is `HttpOnly` (page scripts can't read it, so an injected script can't steal the token), `SameSite=Lax`, `Path=/`, `Max-Age` 24 hours, and `Secure` when the `COOKIE_SECURE` setting is `true` (it should be in production, where the site runs on https). `POST /auth/logout` clears it.
- **Protected endpoints** use a `get_current_user` dependency: it reads the token from the cookie, verifies its signature and expiry (a token without an expiry is refused), then loads the user from the database on every request. The role is read from the database, not from the token. An `Authorization: Bearer` header is not accepted, so the "Authorize" button in `/docs` no longer logs you in.
- **Cross-site request forgery (CSRF):** a cookie is sent automatically by the browser, so two defenses stop another website from acting as a logged-in user. `SameSite=Lax` keeps the browser from sending the cookie on cross-site `POST` requests, and an Origin check refuses any `POST`/`PUT`/`PATCH`/`DELETE` whose `Origin` header is not in `CORS_ORIGINS` (`403` `"Origin not allowed"`). Requests without an `Origin` header (curl, scripts, tests) pass, since the risk comes from browsers.
- **Rate limit:** `/assistant` allows 10 questions per user per hour (`429` with a `Retry-After` header after that). Empty requests don't count.
- **Roles:** every user has a `role` (`reader` by default). Nothing enforces `admin` yet.

---

## Scope of the MVP

This is a functioning proof of concept, not yet a production product. Deliberately out of scope for this phase:
- Real book content — the 6 books have short placeholder texts; they will be replaced with the author's own writing
- User profiles and reading history
- An admin panel (books are added by editing `backend/data/books.json` and re-running the seed)
- Password reset and email verification
- Deployment — there is no hosting and no automatic deployment (CD) yet. CI does exist (see [Continuous integration](#continuous-integration)), but there are no frontend tests yet
- ML-based scoring (current scoring is formula-based; see Roadmap)

---

## Limitations

Being explicit about what this does *not* do yet:
- **The readability formulas are not validated for Kyrgyz.** ARI is language-agnostic, and the second score uses Ateşman's constants from Turkish. Both are first-pass approximations until they can be checked against age-labelled Kyrgyz texts.
- **Assistant answers in Kyrgyz are uneven** with the small model used for development; English and Russian answers are more reliable.
- **The rate limiter keeps its counts in memory**, so they reset when the backend restarts and are not shared between server processes.
- **Tokens can't be revoked before they expire** (24 hours): logging out clears the cookie in the browser, but the token itself stays valid until then. There is no password reset or email verification.
- **The `role` column exists, but nothing uses it yet** (there is no admin panel).
- The assistant's answer is shown as plain text, so Markdown formatting from the model appears as raw `**` markers.
- If the backend can't be reached, the frontend shows the browser's generic "Failed to fetch" message rather than a friendly one.
- **The book texts are short placeholders**, not real children's books yet.
- **The assistant prefill is lost across login:** if a logged-out visitor clicks "Ask AI about this book" and then logs in, the text is not carried over and has to be pasted again.
- No deployment yet (see Roadmap).
- There are no frontend tests yet, and no tests for `/analyze`.

---

## Tech stack

| Layer    | Tech |
|----------|------|
| Backend  | Python, FastAPI, Pydantic v2, pydantic-settings, Uvicorn, SQLAlchemy 2, psycopg2, PyJWT, pwdlib (bcrypt), email-validator |
| AI       | Google Gemini API (`google-genai` SDK, Interactions API with function calling) |
| Database | PostgreSQL 16 (Docker Compose for local dev) |
| Frontend | React 19, React Router 7, Vite 8, Tailwind CSS v4, shadcn/ui, ESLint |
| Testing  | pytest (FastAPI TestClient; in-memory SQLite for the auth, books and assistant tests) |
| CI       | GitHub Actions |

---

## Running locally

Prerequisites: Python 3.13, Node.js + npm, Docker (with Compose), and a Gemini API key.

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
Then edit `backend/.env`: replace `your_key_here` with your Gemini API key, and replace the `SECRET_KEY` placeholder with a long random value, for example the output of `openssl rand -hex 32`. The `DATABASE_URL` already matches the Docker Compose database.

`.env` is gitignored. The backend will not start without all three values.

Two optional settings (commented out in `.env.example`) can stay unset for local development:
- `CORS_ORIGINS` — comma-separated frontend addresses (default `http://localhost:5173,http://127.0.0.1:5173`). It is also the list the Origin check allows, so in production it must contain the frontend's address.
- `COOKIE_SECURE` — default `false`; set it to `true` in production, so the login cookie is only sent over https.

**3. Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`. Start `uvicorn` from the `backend/` folder.

Create the tables with Alembic, then seed (venv active, from backend/):
```bash
cd backend
alembic upgrade head       # creates the tables (run once per new database)
python -m app.seed          # loads the books from data/books.json; safe to run again (updates existing titles)
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
App at `http://localhost:5173`. Open it as `localhost`, not `127.0.0.1`: the API runs on `localhost:8000`, and the browser treats `127.0.0.1` and `localhost` as different sites, so with `127.0.0.1` the `SameSite=Lax` login cookie is not kept and you end up logged out. To use the AI assistant, create an account with "Sign up" in the header; the assistant requires a login.

The API address is read at build time from `VITE_API_URL` (default `http://localhost:8000`; see `frontend/.env.example`). It doesn't need to be set for local development.

**6. Before pushing**
```bash
cd frontend
npm run lint
npm run build
```
CI runs the same commands, plus the backend tests.

---

## Continuous integration

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main` and on every pull request, with two jobs on `ubuntu-latest`:

- **backend** — Python 3.13: `pip install -r requirements.txt`, then `python -m pytest tests`. `DATABASE_URL`, `GEMINI_API_KEY` and `SECRET_KEY` are set to dummy values so the config loads; no real secrets are used. The tests don't touch PostgreSQL or the Gemini API (the auth and assistant tests use an in-memory SQLite database and a fake model).
- **frontend** — Node 22: `npm ci`, `npm run lint`, `npm run build`.

ESLint (`frontend/eslint.config.js`) relaxes two rules for the shadcn-generated files in `src/components/ui/` only: `no-unused-vars` ignores a variable named `React`, and `react-refresh/only-export-components` is off. The project's own code keeps all rules.

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

**`POST /auth/register`**
```json
// Request
{ "email": "reader@example.com", "password": "at least 8 characters" }

// Response (201) — the password hash is never returned
{ "id": 1, "email": "reader@example.com", "role": "reader" }
```

Errors: `409` `{ "detail": "Email already registered" }`; `422` for an invalid email, a password under 8 characters, or a password over 72 bytes.

**`POST /auth/login`** — form-encoded (`application/x-www-form-urlencoded`); the email goes in the `username` field.
```json
// Response — the token is not in the body; it is set in the access_token cookie
// (Set-Cookie: access_token=…; HttpOnly; SameSite=Lax; Path=/; Max-Age=86400, plus Secure when COOKIE_SECURE=true)
{ "id": 1, "email": "reader@example.com", "role": "reader" }
```

Error: `401` `{ "detail": "Incorrect email or password" }` (the same for a wrong password and an unknown email); no cookie is set.

**`POST /auth/logout`** — clears the login cookie. Returns `204` with no body, also when nobody is logged in.

**`GET /auth/me`** — requires the login cookie.
```json
// Response
{ "id": 1, "email": "reader@example.com", "role": "reader" }
```

Error: `401` `{ "detail": "Could not validate credentials" }` when the cookie is missing, the token is invalid or expired, or the user no longer exists. An `Authorization: Bearer` header is ignored.

**`POST /assistant`** — requires the login cookie.
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
- `401` — missing cookie, or an invalid or expired token
- `422` — invalid input caught by FastAPI validation (missing or empty `text`/`question`, or a `language` other than `ky`/`ru`/`en`)
- `400` — `{ "detail": "Text and question must not be empty" }` when `text` or `question` is whitespace only
- `429` — more than 10 questions per user per hour; the `Retry-After` header gives the seconds to wait
- `502` — `{ "detail": "The assistant is unavailable, please try again" }` when the model call fails. The real error is logged server-side and not returned to the client

**`GET /books`** — published books only, ordered by id; the list does not include the text.
```json
[
  { "id": 1, "title": "Манас баатыры", "age_group": "10-11", "cover_url": "/books/book-1.jpg" }
]
```

**`GET /books/{id}`**
```json
{
  "id": 1,
  "title": "Манас баатыры",
  "age_group": "10-11",
  "cover_url": "/books/book-1.jpg",
  "text": "Илгери-илгери …",
  "source": "placeholder"
}
```

`text` and `source` may be `null`. Errors: `404` `{ "detail": "Book not found" }` for a missing or unpublished book; `422` for a non-numeric id.

**`GET /health`** → `{ "status": "health ok" }`

Any `POST`/`PUT`/`PATCH`/`DELETE` sent with an `Origin` header that is not in `CORS_ORIGINS` gets `403` `{ "detail": "Origin not allowed" }`.

---

## Roadmap

**Phase 2 — Product foundation**
- *(Done)* Analyze page wired to `POST /analyze`; books stored in PostgreSQL and served by `GET /books` (ordered by id)
- *(Done)* Reproducible local setup: Docker Compose database, `.env`-based config, Alembic migrations, idempotent seed, working `requirements.txt`
- *(Done)* AI reading assistant (`POST /assistant` + `/assistant` page) with two analyzer-backed tools
- *(Done)* User registration and login (bcrypt, JWT), with login and register pages and an auth-aware header
- *(Done)* `/assistant` requires a login and is rate-limited per user (10 per hour), so anonymous requests can't drain the Gemini quota
- *(Done)* Book text: `text`, `source` and `status` columns (Alembic migration), `GET /books/{id}`, seed data in `backend/data/books.json`
- *(Done)* Reading page (`/books/:id`) with an **"Ask AI about this book"** button that opens the assistant with the text filled in, so the two halves of the project meet
- Next: "mark as read" and a profile page with reading history
- Then: replace the placeholder texts with the author's own writing (and later, store each book's readability score)
- Admin panel: a restricted view for adding/editing/removing books in the catalog, gated behind the admin role (the `role` column already exists)

**Phase 3 — ML & NLP depth** *(not required for the current MVP — see note below)*
- Validate the readability formulas against age-labelled Kyrgyz texts, and build a proper Kyrgyz readability formula (replacing the borrowed Turkish constants) from that data
- Build a small evaluation set for the assistant: questions paired with the tool(s) the model *should* call, to measure tool-routing accuracy and catch regressions when the prompt or model changes
- Move from formula-based scoring toward a trained/fine-tuned model for Kyrgyz text difficulty classification
- Explore additional NLP features (e.g. vocabulary-level tagging) to support recommendations

> **On ML:** the current MVP's readability scoring is fully functional using classical formulas (ARI + an adapted Ateşman formula) — no ML is required for it to work end-to-end. ML becomes worthwhile once a labeled Kyrgyz corpus (text tagged by reading level) exists to train and validate against; until then it's tracked as a future enhancement, not a blocker.

**Phase 4 — Production readiness**
- *(Done)* CI on GitHub Actions: backend tests, frontend lint and build, on every push to `main` and on pull requests
- *(Done)* Login token in an httpOnly cookie (`SameSite=Lax`, plus an Origin check against CSRF), a logout endpoint, and configurable addresses (`VITE_API_URL` for the frontend, `CORS_ORIGINS` and `COOKIE_SECURE` for the backend)
- More tests: `/analyze` and the frontend components
- Before public hosting: serve the frontend and the API as one site — the frontend host forwards `/api/...` to the backend, with `VITE_API_URL=/api`, `COOKIE_SECURE=true` and `CORS_ORIGINS` set to the frontend's address — because cookies sent between two different hosting domains are unreliable (Safari and Chrome restrict them); move the rate-limit counter out of memory if more than one server process runs; use a hosted database; and add a privacy note and terms
- Containerize the backend and frontend (only the database runs in Docker today) and deploy
- Automatic deployment (CD) from GitHub Actions

---
