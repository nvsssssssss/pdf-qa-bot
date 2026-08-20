# PDF Q&A Bot

A retrieval-augmented generation (RAG) API that lets you upload a PDF and ask natural-language questions about its content. Built as a deployed, resume-ready project — not a notebook script.

**Live demo:** https://pdf-qa-bot-ez7w.onrender.com/docs
*(Interactive Swagger UI — try the full upload → ask flow directly in the browser)*

---

## How it works

1. **Upload** a PDF — the text is extracted, split into overlapping chunks, embedded, and stored in a vector database.
2. **Ask** a question — the question is embedded, the most relevant chunks are retrieved via similarity search, and an LLM generates an answer grounded only in that retrieved context.

This is the standard RAG pattern: retrieval narrows the search space so the LLM only ever answers from the document, reducing hallucination compared to asking the LLM directly.

---

## Tech stack

| Layer | Tool |
|---|---|
| API framework | FastAPI + Uvicorn |
| PDF parsing | pypdf |
| Embeddings | fastembed (ONNX runtime, `all-MiniLM-L6-v2`) |
| Vector store | ChromaDB (persistent, local) |
| LLM | Google Gemini (`gemini-3.6-flash`) |
| Deployment | Render (free tier) |

---

## Architecture

```
main.py         → FastAPI app, routes only (/upload, /ask)
pdf_utils.py    → PDF text extraction + chunking
rag.py          → Embedding, vector storage, retrieval, prompt building, LLM call
```

**Request flow:**

```
POST /upload (PDF file)
    -> extract_text()          [pdf_utils.py]
    -> chunk()                 [pdf_utils.py]
    -> build_collection()      [rag.py]  -> embeds chunks, stores in ChromaDB
    -> returns a session_id

POST /ask (session_id, question)
    -> answer_question()       [rag.py]  -> embeds question, retrieves top-k relevant chunks
    -> build_prompt()          [rag.py]  -> wraps context + question into a grounded prompt
    -> generate_answer()       [rag.py]  -> calls Gemini, returns the answer
```

Each upload gets its own isolated ChromaDB collection, keyed by a unique `session_id` — so multiple PDFs/users can be handled concurrently without their data mixing.

---

## API Endpoints

### `POST /upload`
Uploads a PDF and builds its vector index.

**Request:** `multipart/form-data`, field `file` (PDF only)

**Response:**

    {
      "session_id": "a1b2c3d4-...",
      "chunks_stored": 12
    }

**Errors:** `400` if the file isn't a PDF.

### `POST /ask`
Asks a question about a previously uploaded PDF.

**Request:**

    {
      "session_id": "a1b2c3d4-...",
      "question": "What is this document about?"
    }

**Response:**

    {
      "answer": "..."
    }

**Errors:** `404` if `session_id` doesn't exist (e.g. server restarted, or invalid ID).

---

## Running locally

```
git clone https://github.com/nvsssssssss/pdf-qa-bot.git
cd pdf-qa-bot

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

Create a `.env` file in the project root:

    GEMINI_API_KEY=your_key_here

Run the server:

```
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` to test via Swagger UI.

---

## Known limitations (free-tier deployment)

- **Cold starts:** Render's free tier spins down the service after inactivity. The first request after idling can take 30–50+ seconds while the instance wakes up.
- **In-memory session store:** `session_id -> collection` mappings live in server RAM, not a database. A server restart or redeploy wipes all active sessions — previously uploaded PDFs must be re-uploaded to get a new `session_id`.
- **Single-instance, no persistence across deploys:** ChromaDB data is stored on local disk within the container, which is ephemeral on Render's free tier — it does not survive a redeploy.
- **Memory-constrained embedding model:** Uses `fastembed` (ONNX-based) instead of `sentence-transformers`/PyTorch specifically to fit within Render's 512MB free-tier RAM limit.

These are intentional trade-offs for a free-tier deployment, not unaddressed bugs — a production version would use a managed vector DB (e.g. hosted ChromaDB, Pinecone) and a persistent session store (e.g. Redis) instead.

---

## Demo

*(screen recording link here — added after recording)*