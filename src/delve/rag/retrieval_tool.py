from delve.rag.ingest import _model, get_chroma_collection


def search_historical_incidents(query: str, top_k: int = 3) -> list[dict]:
    """Search historical incident postmortems for content relevant to a
    given incident description.

    Args:
        query: The current incident's title/description to search against.
        top_k: How many of the most relevant historical postmortems to return.

    Returns:
        A list of matching postmortems, each with filename, relevance 
        distance (lower is more relevant), and full document text.
    """
    collection = get_chroma_collection()
    query_embedding = _model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    matches = []
    for i in range(len(results["ids"][0])):
        matches.append({
            "filename": results["metadatas"][0][i]["filename"],
            "distance": results["distances"][0][i],
            "content": results["documents"][0][i],
        })
    return matches
