import re
import sys
from pathlib import Path

import chromadb
import httpx
import requests
from bs4 import BeautifulSoup


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "chroma_db"

OLLAMA_URL = "http://127.0.0.1:11434"
EMBEDDING_MODEL = "nomic-embed-text"

SOURCES = [
    {
        "url": "https://www.getnet.net/mx/nuestras-soluciones/pagos-en-persona/terminal-de-pago-con-impresora",
        "country": "MX",
    },
    {
        "url": "https://www.getnet.net/mx/nuestras-soluciones/portal-de-ventas/getnet-portal",
        "country": "MX",
    },
]


def extract_page(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(
        ["script", "style", "nav", "footer", "header"]
    ):
        tag.decompose()

    main = soup.find("main") or soup.body or soup

    text = main.get_text(separator=" ", strip=True)

    return re.sub(r"\s+", " ", text)


def split_text(text: str, chunk_size: int = 700) -> list[str]:
    """Divide el texto en fragmentos con solapamiento."""
    chunks = []
    overlap = 100
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def generate_embedding(text: str) -> list[float]:
    """Genera un embedding mediante Ollama."""
    response = httpx.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": EMBEDDING_MODEL,
            "input": text,
        },
        timeout=60.0,
    )

    response.raise_for_status()

    return response.json()["embeddings"][0]


def main():
    client = chromadb.PersistentClient(path=str(DB_DIR))

    collection = client.get_or_create_collection(
        name="getnet_knowledge"
    )

    total_chunks = 0

    for source_index, source in enumerate(SOURCES):
        url = source["url"]

        print(f"\nProcesando: {url}")

        try:
            text = extract_page(url)

            if len(text) < 200:
                print("Contenido insuficiente. Se omite.")
                continue

            chunks = split_text(text)

            for chunk_index, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)

                document_id = (
                    f"source_{source_index}_chunk_{chunk_index}"
                )

                collection.upsert(
                    ids=[document_id],
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[{
                        "source": url,
                        "country": source["country"],
                    }],
                )

                total_chunks += 1

            print(f"Fragmentos almacenados: {len(chunks)}")

        except (requests.RequestException, httpx.HTTPError) as error:
            print(f"Error procesando fuente: {error}")

    print(f"\nFragmentos procesados: {total_chunks}")
    print(f"Total en ChromaDB: {collection.count()}")


if __name__ == "__main__":
    main()
