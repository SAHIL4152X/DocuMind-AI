from google import genai
from google.genai import errors
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List


load_dotenv()

client = genai.Client()


class ImportantQuestionsGenerationError(Exception):
    pass


class ImportantQuestionsResponse(BaseModel):
    questions: List[str]


def create_important_questions_prompt(context):

    return f"""
You are DocuMind AI, a PDF study assistant.

Create exactly 10 important exam questions using ONLY the information
provided in the PDF context below.

Rules:
- Create exactly 10 questions.
- Questions should be useful for college exam preparation.
- Mix conceptual, descriptive, and analytical questions.
- Do not provide answers.
- Do not use information outside the PDF context.
- Do not make up facts.
- Keep the questions clear and exam-oriented.

PDF Context:
{context}
"""


def generate_important_questions(context):

    try:

        prompt = create_important_questions_prompt(
            context
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ImportantQuestionsResponse,
            }
        )

        if not response.text:

            raise ImportantQuestionsGenerationError(
                "Gemini returned an empty response."
            )

        return ImportantQuestionsResponse.model_validate_json(
            response.text
        )

    except errors.APIError as e:

        if e.code == 503:

            raise ImportantQuestionsGenerationError(
                "Gemini is temporarily busy. "
                "Please wait a moment and try again."
            )

        if e.code == 429:

            raise ImportantQuestionsGenerationError(
                "Gemini API quota or rate limit has been reached. "
                "Please try again later."
            )

        if e.code in (401, 403):

            raise ImportantQuestionsGenerationError(
                "There is a problem with the Gemini API key. "
                "Please check your API configuration."
            )

        if e.code == 400:

            raise ImportantQuestionsGenerationError(
                "The request could not be processed. "
                "Please try again."
            )

        raise ImportantQuestionsGenerationError(
            "Gemini could not generate important questions "
            "right now. Please try again later."
        )

    except ImportantQuestionsGenerationError:

        raise

    except Exception:

        raise ImportantQuestionsGenerationError(
            "Something went wrong while generating important "
            "questions. Please try again."
        )