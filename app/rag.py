
import os
from pathlib import Path

import chromadb
import httpx


# Ruta donde guardamos los embeddings.
ROOT_DIR = Path(__file__).resolve().parents[1]
DB_DIR = ROOT_DIR / "chroma_db"

# Configuración de Ollama.
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text",
)


def generate_embedding(text: str) -> list[float]:
    """Convierte una pregunta en un vector numérico."""

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


def search_knowledge(
    question: str,
    top_k: int = 3,
) -> list[dict]:
    """Busca documentos relevantes en ChromaDB."""

    client = chromadb.PersistentClient(
        path=str(DB_DIR)
    )

    collection = client.get_collection(
        name="getnet_knowledge"
    )

    if collection.count() == 0:
        return []

    # Convertimos la pregunta en un embedding.
    question_embedding = generate_embedding(question)

    # Buscamos los fragmentos más cercanos.
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        where={"country": "MX"},
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )


    # Obtenemos los resultados de ChromaDB.
    documents_result = results["documents"]
    metadatas_result = results["metadatas"]
    distances_result = results["distances"]

    # Verificamos que los campos contengan datos.
    if (
        documents_result is None
        or metadatas_result is None
        or distances_result is None
    ):
        return []

    # Extraemos los resultados de la primera consulta.
    documents = documents_result[0]
    metadatas = metadatas_result[0]
    distances = distances_result[0]


    matches = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances,
    ):
        matches.append({
            "text": document,
            "source": metadata["source"],
            "country": metadata["country"],
            "distance": distance,
        })

    return matches
