import chromadb


def get_vector_store():
    client = chromadb.PersistentClient(
        path="chroma_db"
    )

    collection = client.get_or_create_collection(
        name="documind"
    )

    return collection


def create_vector_store(
    chunks,
    embeddings,
    document_id
):
    collection = get_vector_store()

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        collection.add(
            ids=[
                f"{document_id}_{index}"
            ],
            embeddings=[
                embedding
            ],
            documents=[
                chunk["text"]
            ],
            metadatas=[
                {
                    "page": chunk["page"],
                    "document_id": document_id
                }
            ]
        )

    return collection