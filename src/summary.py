from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


def create_summary_prompt(context):
    return f"""
You are DocuMind AI, a PDF study assistant.

Create a clear and useful study summary using ONLY the information
provided in the PDF context below.

Rules:
- Do not use information outside the PDF context.
- Do not make up facts.
- Cover the important concepts.
- Use headings and bullet points where useful.
- Keep the explanation suitable for a college student.
- Keep it concise but informative.

PDF Context:
{context}
"""


def generate_summary(context):
    prompt = create_summary_prompt(context)

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text