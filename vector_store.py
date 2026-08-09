import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def build_collection(chunks, collection_name="pdf_chunks", persist_dir="./chroma_db"):
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.create_collection(collection_name)
    embeddings = model.encode(chunks).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks)
    return collection


def answer_question(collection, question, top_k=3):
    query_embedding = model.encode([question]).tolist()
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