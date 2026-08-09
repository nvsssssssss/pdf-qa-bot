PDF Q&A Bot

A command-line RAG (Retrieval-Augmented Generation) pipeline that lets you ask natural language questions about any PDF document and get accurate, context-grounded answers.

How It Works
Ingestion — Extracts raw text from a PDF using pypdf.
Chunking — Splits the text into overlapping chunks using a custom sliding-window algorithm, sized to fit within the embedding model's token limit.
Embedding — Converts each chunk into a vector using sentence-transformers (all-MiniLM-L6-v2).
Storage & Retrieval — Stores embeddings in a local ChromaDB vector store (PersistentClient) and retrieves the most relevant chunks for a given query via similarity search.
Generation — Passes the retrieved context + user question to Google Gemini (gemini-3.5-flash-lite) via the google-genai SDK to generate a grounded answer.
Tech Stack
Component	Tool
PDF Parsing	pypdf
Chunking	Custom sliding-window logic
Embeddings	sentence-transformers (all-MiniLM-L6-v2)
Vector Store	ChromaDB (PersistentClient)
LLM	Google Gemini (gemini-3.5-flash-lite) via google-genai
Project Structure
my_project/
├── ingest.py         # PDF text extraction + chunking
├── vector_store.py   # Embedding generation + ChromaDB storage/retrieval
├── llm.py            # Gemini API integration
├── main.py           # CLI entry point — ties the pipeline together
├── requirements.txt  # Python dependencies
└── sample.pdf         # Example PDF for testing
Setup
Clone the repo:
bash
   git clone https://github.com/nvsssssssss/pdf-qa-bot.git
   cd pdf-qa-bot
Create and activate a virtual environment:
bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
Install dependencies:
bash
   pip install -r requirements.txt
Create a .env file in the project root with your Gemini API key:
   GEMINI_API_KEY=your_key_here
Run the bot:
bash
   python main.py
Usage
Provide a PDF file when prompted (or place it in the project directory).
The bot ingests, chunks, and embeds the document into the vector store.
Ask questions about the PDF in natural language — the bot retrieves relevant context and generates an answer using Gemini.
Roadmap / Next Steps
 Wrap the pipeline in a FastAPI service with /upload and /ask endpoints
 Deploy to Render
 Add support for multi-document Q&A
Author

Built by Navas as a hands-on project to learn RAG pipelines end-to-end.