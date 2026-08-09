from pypdf import PdfReader

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text

def chunk(texts, chunkSize, overlapSize):
    start = 0
    chunks = []
    while start < len(texts):
        end = start + chunkSize
        c = texts[start:end]
        chunks.append(c)
        start = start + chunkSize - overlapSize
    return chunks