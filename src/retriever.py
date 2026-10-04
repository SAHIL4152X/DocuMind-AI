def search_documents(
    collection,
    query_embedding,
    document_id,
    top_k=3
):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "document_id": document_id
        }
    )

    return results