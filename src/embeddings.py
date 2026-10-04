from google import genai
from dotenv import load_dotenv


load_dotenv()

client = genai.Client()


def create_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )

    return response.embeddings[0].values