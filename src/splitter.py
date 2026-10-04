def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    chunks = []

    for document in documents:
        text = document["text"]
        page = document["page"]

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end]

            chunks.append({
                "page": page,
                "text": chunk_text
            })

            start = end - chunk_overlap

    return chunks