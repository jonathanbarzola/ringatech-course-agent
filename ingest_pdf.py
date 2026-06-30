import os
import sys
from pypdf import PdfReader
from gemini_embedder import GeminiEmbedder
from dotenv import load_dotenv

from supabase_doc_store import SupabaseDocStore

def extract_pdf_text(path:str):
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": i, "text": text})

    return pages

def chunk_text(text:str, size:int=500, overlap:int=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks

def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "sample.pdf"
    if not os.path.exists(pdf_path):
        print("Favor de indicar el archivo PDF a utilizar")
        sys.exit(1)

    pages = extract_pdf_text(pdf_path)

    load_dotenv()
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    embedder = GeminiEmbedder(api_key=GEMINI_API_KEY)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    store = SupabaseDocStore(DATABASE_URL)


    #print(pages)
    for page in pages:
        chunks = chunk_text(page["text"])
        print(chunks)

        for chunk in chunks:
            vectors = embedder.embed_document(chunk)
            #print(vectors)
            store.insert_chunk(chunk, {"page": page["page"]}, vectors)

if __name__ == "__main__":
    main()