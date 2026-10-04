from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()


def generate_answer(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        if not response.text:
            return (
                "I could not generate an answer right now. "
                "Please try again."
            )

        return response.text

    except errors.APIError as e:

        if e.code == 503:

            return (
                "Gemini is temporarily busy. "
                "Please wait a moment and try again."
            )

        if e.code == 429:

            return (
                "Gemini API quota or rate limit has been reached. "
                "Please try again later."
            )

        if e.code in (401, 403):

            return (
                "There is a problem with the Gemini API key. "
                "Please check your API configuration."
            )

        if e.code == 400:

            return (
                "The request could not be processed. "
                "Please try a different question."
            )

        return (
            "Gemini could not process the request right now. "
            "Please try again later."
        )

    except Exception:

        return (
            "Something went wrong while generating the answer. "
            "Please try again."
        )