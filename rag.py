import os
import chromadb
from fastembed import TextEmbedding
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found — check your .env file")

client = genai.Client(api_key=api_key)
model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")


def build_collection(chunks, collection_name="pdf_chunks", persist_dir="./chroma_db"):
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass
    collection = chroma_client.create_collection(collection_name)
    embeddings = [e.tolist() for e in model.embed(chunks)]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks)
    return collection


def answer_question(collection, question, top_k=3):
    query_embedding = [e.tolist() for e in model.embed([question])]
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    retrieved_chunks = results["documents"][0]
    context = "\n\n".join(retrieved_chunks)
    return context


def build_prompt(context, question):
    prompt = f"""Answer the question using ONLY the context below.
Do not use any outside knowledge.
If the answer is not found in the context, say "I couldn't find this in the document."

Context:
{context}

Question:
{question}

Answer:"""
    return prompt


def generate_answer(prompt):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )
    return response.text