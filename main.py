from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, uuid, os

from pdf_utils import extract_text, chunk
from rag import build_collection, answer_question, build_prompt, generate_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}  # session_id -> collection


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    session_id = str(uuid.uuid4())
    os.makedirs("temp", exist_ok=True)
    temp_path = f"temp/{session_id}.pdf"

    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    pdf_text = extract_text(temp_path)
    chunks = chunk(pdf_text, 500, 50)
    collection = build_collection(chunks, collection_name=session_id)

    sessions[session_id] = collection

    return {"session_id": session_id, "chunks_stored": len(chunks)}


class AskRequest(BaseModel):
    session_id: str
    question: str


@app.post("/ask")
async def ask_question(req: AskRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Invalid session_id — upload a PDF first")

    collection = sessions[req.session_id]

    context = answer_question(collection, req.question)
    prompt = build_prompt(context, req.question)
    answer = generate_answer(prompt)

    return {"answer": answer}