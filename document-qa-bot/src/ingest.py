import os
import sys

# Ensure the root directory is in the Python path so absolute imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import glob
# pyrefly: ignore [missing-import]
from pypdf import PdfReader
# pyrefly: ignore [missing-import]
from docx import Document
# pyrefly: ignore [missing-import]
import chromadb
from src.embedding import CustomGoogleGenerativeAiEmbeddingFunction as GoogleGenerativeAiEmbeddingFunction
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from tqdm import tqdm

from src.config import (
    DATA_DIR, DB_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, COLLECTION_NAME
)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def extract_pdf_pages(file_path: str) -> list[dict]:
    """Extracts text page-by-page from a PDF."""
    extracted_data = []
    file_name = os.path.basename(file_path)

    try:
        reader = PdfReader(file_path)
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                clean_text = " ".join(text.split())
                extracted_data.append({
                    "text": clean_text,
                    "metadata": {
                        "source": file_name,
                        "page": index + 1
                    }
                })
    except Exception as e:
        print(f"Error reading PDF {file_name}: {e}")

    return extracted_data

def extract_docx_pages(file_path: str) -> list[dict]:
    """Extracts text from a Word document (treated as one page for simplicity)."""
    extracted_data = []
    file_name = os.path.basename(file_path)

    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if text.strip():
            clean_text = " ".join(text.split())
            extracted_data.append({
                "text": clean_text,
                "metadata": {
                    "source": file_name,
                    "page": 1
                }
            })
    except Exception as e:
        print(f"Error reading DOCX {file_name}: {e}")

    return extracted_data

def extract_text_pages(file_path: str) -> list[dict]:
    """Extracts text from a plain text or markdown file."""
    extracted_data = []
    file_name = os.path.basename(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            if text.strip():
                clean_text = " ".join(text.split())
                extracted_data.append({
                    "text": clean_text,
                    "metadata": {
                        "source": file_name,
                        "page": 1
                    }
                })
    except Exception as e:
        print(f"Error reading text file {file_name}: {e}")

    return extracted_data

def chunk_extracted_pages(pages: list[dict], chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[dict]:
    """Splits page-level documents into smaller, overlapping chunks."""
    chunks = []

    for page in pages:
        text = page["text"]
        metadata = page["metadata"]

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_range": f"{start}-{end}"
                }
            })
            start += (chunk_size - chunk_overlap)

    return chunks

def process_documents(data_dir: str = DATA_DIR) -> list[dict]:
    """Scans directory for PDFs, DOCXs, TXTs, and MDs and extracts text."""
    all_pages = []
    files = glob.glob(os.path.join(data_dir, "*.[pP][dD][fF]")) + \
            glob.glob(os.path.join(data_dir, "*.[dD][oO][cC][xX]")) + \
            glob.glob(os.path.join(data_dir, "*.[tT][xX][tT]")) + \
            glob.glob(os.path.join(data_dir, "*.[mM][dD]"))
    
    for file_path in tqdm(files, desc="Extracting documents"):
        if file_path.lower().endswith(".pdf"):
            pages = extract_pdf_pages(file_path)
        elif file_path.lower().endswith(".docx"):
            pages = extract_docx_pages(file_path)
        elif file_path.lower().endswith(".txt") or file_path.lower().endswith(".md"):
            pages = extract_text_pages(file_path)
        all_pages.extend(pages)
        
    return all_pages

def save_to_vector_db(chunks: list[dict], db_path: str = DB_DIR):
    """Embeds text chunks and saves them into ChromaDB."""
    if not chunks:
        print("No chunks to insert.")
        return

    client = chromadb.PersistentClient(path=db_path)

    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError("GEMINI_API_KEY is not set or is using the default template. Please set it in the .env file.")

    embedding_fn = GoogleGenerativeAiEmbeddingFunction(
        api_key=api_key,
        model_name=EMBEDDING_MODEL
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    # Batch upload to ChromaDB in chunks to avoid overwhelming the API
    BATCH_SIZE = 100
    for i in tqdm(range(0, len(chunks), BATCH_SIZE), desc="Uploading to ChromaDB"):
        batch = chunks[i:i + BATCH_SIZE]
        ids = [f"{chunk['metadata']['source']}_p{chunk['metadata']['page']}_{chunk['metadata']['chunk_range']}" for chunk in batch]
        documents = [chunk["text"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
    print(f"Successfully indexed {len(chunks)} chunks in the vector database.")

def main():
    print(f"Scanning directory: {DATA_DIR}")
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)

    pages = process_documents()
    print(f"Extracted {len(pages)} pages/documents.")

    chunks = chunk_extracted_pages(pages)
    print(f"Generated {len(chunks)} text chunks.")

    save_to_vector_db(chunks)

if __name__ == "__main__":
    main()
