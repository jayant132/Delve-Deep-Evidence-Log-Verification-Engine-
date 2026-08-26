import pathlib

import chromadb
from sentence_transformers import SentenceTransformer

POSTMORTEMS_DIR = pathlib.Path(__file__).parent.parent / "data" / "postmortems"
CHROMA_PATH = pathlib.Path(__file__).parent / "chroma_store"

_model = SentenceTransformer("all-MiniLM-L6-v2")


def get_chroma_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(name="postmortems")


def ingest_postmortems():
    collection = get_chroma_collection()
    files = sorted(POSTMORTEMS_DIR.glob("*.md"))

    docs, ids, metadatas = [], [], []
    for f in files:
        text = f.read_text()
        docs.append(text)
        ids.append(f.stem)
        metadatas.append({"filename": f.name})

    embeddings = _model.encode(docs).tolist()

    collection.upsert(
        ids=ids,
        documents=docs,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(docs)
