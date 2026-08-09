from ingest import extract_text, chunk
from vector_store import build_collection, answer_question, build_prompt
from llm import generate_answer

if __name__ == "__main__":
    print("running")
    pdf_path = "sample.pdf"
    pdf_text = extract_text(pdf_path)
    chunks = chunk(pdf_text, 500, 50)
    collection = build_collection(chunks)
    print(f"Stored {collection.count()} chunks in Chroma")

    print("\nAsk a question about the PDF (type 'exit' to quit)")

    while True:
        question = input("\nYour question: ")

        if question.strip().lower() == "exit":
            print("Goodbye!")
            break

        context = answer_question(collection, question)
        prompt = build_prompt(context, question)
        answer = generate_answer(prompt)
        print("Answer:", answer)