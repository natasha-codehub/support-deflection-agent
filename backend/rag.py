import os
import glob
import chromadb
import google.generativeai as genai
from config import GEMINI_API_KEY, CHROMA_PATH, KB_PATH, EMBEDDING_MODEL, RAG_TOP_K

genai.configure(api_key=GEMINI_API_KEY)

_client: chromadb.Client = None
_collection: chromadb.Collection = None


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i: i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def _embed(texts: list[str]) -> list[list[float]]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=texts,
        task_type="retrieval_document",
    )
    return result["embedding"] if isinstance(texts, str) else result["embedding"]


def _embed_query(text: str) -> list[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text,
        task_type="retrieval_query",
    )
    return result["embedding"]


def init_rag():
    global _client, _collection

    _client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        _client.delete_collection("kb")
    except Exception:
        pass

    _collection = _client.create_collection(
        name="kb",
        metadata={"hnsw:space": "cosine"},
    )

    md_files = glob.glob(os.path.join(KB_PATH, "*.md"))
    ids, embeddings, documents, metadatas = [], [], [], []

    for md_path in md_files:
        filename = os.path.basename(md_path)
        with open(md_path, encoding="utf-8") as f:
            content = f.read()

        chunks = _chunk_text(content)
        for idx, chunk in enumerate(chunks):
            doc_id = f"{filename}__chunk_{idx}"
            ids.append(doc_id)
            documents.append(chunk)
            metadatas.append({"source_file": filename, "chunk_index": idx})

    if ids:
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_texts = documents[i: i + batch_size]
            batch_embeds = _embed(batch_texts)
            _collection.add(
                ids=ids[i: i + batch_size],
                embeddings=batch_embeds,
                documents=batch_texts,
                metadatas=metadatas[i: i + batch_size],
            )

    print(f"[RAG] Indexed {len(ids)} chunks from {len(md_files)} KB documents")


def get_relevant_chunks(query: str, k: int = RAG_TOP_K) -> list[dict]:
    if _collection is None:
        raise RuntimeError("RAG not initialised — call init_rag() first")

    query_embedding = _embed_query(query)
    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=min(k, _collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        # ChromaDB cosine distance: score = 1 - distance
        score = round(1.0 - dist, 4)
        chunks.append({"text": doc, "score": score, "metadata": meta})

    return chunks


def get_collection_size() -> int:
    if _collection is None:
        return 0
    return _collection.count()
