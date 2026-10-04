from google import genai
from google.genai import errors
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List


load_dotenv()

client = genai.Client()


# =========================================================
# CUSTOM ERROR
# =========================================================

class MCQGenerationError(Exception):
    pass


# =========================================================
# MCQ MODELS
# =========================================================

class MCQ(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str


class MCQResponse(BaseModel):
    questions: List[MCQ]


# =========================================================
# MCQ PROMPT
# =========================================================

def create_mcq_prompt(context):

    return f"""
You are DocuMind AI, a PDF study assistant.

Create exactly 10 multiple-choice questions using ONLY the information
provided in the PDF context below.

Rules:
- Create exactly 10 questions.
- Each question must have exactly 4 options.
- There must be only one correct answer.
- Do not use information outside the PDF context.
- Do not make up facts.
- Keep the questions suitable for a college student.
- Mix conceptual and factual questions.
- The correct answer must be exactly one of: A, B, C, or D.

PDF Context:
{context}
"""


# =========================================================
# GENERATE MCQs
# =========================================================

def generate_mcqs(context):

    try:

        prompt = create_mcq_prompt(context)

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": MCQResponse,
            }
        )

        if not response.text:

            raise MCQGenerationError(
                "Gemini returned an empty response."
            )

        return MCQResponse.model_validate_json(
            response.text
        )

    except errors.APIError as e:

        if e.code == 503:

            raise MCQGenerationError(
                "Gemini is temporarily busy. "
                "Please wait a moment and try again."
            )

        if e.code == 429:

            raise MCQGenerationError(
                "Gemini API quota or rate limit has been reached. "
                "Please try again later."
            )

        if e.code in (401, 403):

            raise MCQGenerationError(
                "There is a problem with the Gemini API key. "
                "Please check your API configuration."
            )

        if e.code == 400:

            raise MCQGenerationError(
                "The MCQ request could not be processed. "
                "Please try again."
            )

        raise MCQGenerationError(
            "Gemini could not generate MCQs right now. "
            "Please try again later."
        )

    except MCQGenerationError:

        raise

    except Exception:

        raise MCQGenerationError(
            "Something went wrong while generating MCQs. "
            "Please try again."
        )


# =========================================================
# CHECK ANSWERS
# =========================================================

def check_answers(mcqs, user_answers):

    score = 0
    results = []

    for index, mcq in enumerate(
        mcqs.questions
    ):

        user_answer = user_answers[index].upper()
        correct_answer = mcq.correct_answer.upper()

        if user_answer == correct_answer:

            score += 1
            is_correct = True

        else:

            is_correct = False

        results.append(
            {
                "question": mcq.question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            }
        )

    return score, results