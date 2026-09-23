"""
Gemini LLM Client.

Handles communication with Google's Gemini API.
"""

import time

from google import genai

from config.logging_config import logger
from config.settings import settings


class LLMClient:
    """
    Wrapper around the Gemini API.
    """

    def __init__(self):
        """
        Initialize the Gemini client.
        """

        logger.info("Initializing Gemini client...")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Gemini model
        self.model = "gemini-3.5-flash-lite"

        logger.success("Gemini client initialized.")

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate text using Gemini.

        Retries temporary server failures
        before returning a graceful fallback.
        """

        # ------------------------------------------
        # Validate prompt
        # ------------------------------------------

        if not prompt or not prompt.strip():

            logger.warning("Empty prompt received.")

            return "I don't know based on the " "provided knowledge."

        prompt = prompt.strip()

        logger.info("Sending prompt to Gemini...")

        # ------------------------------------------
        # Retry configuration
        # ------------------------------------------

        max_retries = 3

        for attempt in range(
            1,
            max_retries + 1,
        ):

            try:

                # ----------------------------------
                # Call Gemini
                # ----------------------------------

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                # ----------------------------------
                # Validate response
                # ----------------------------------

                if not response:

                    logger.warning("Gemini returned an empty response.")

                    return "I don't know based on the " "provided knowledge."

                answer = getattr(
                    response,
                    "text",
                    None,
                )

                if not answer:

                    logger.warning("Gemini response contained " "no text.")

                    return "I don't know based on the " "provided knowledge."

                # ----------------------------------
                # Success
                # ----------------------------------

                logger.success("Response received from Gemini.")

                return answer.strip()

            except Exception as exc:

                error_message = str(exc)

                # ----------------------------------
                # Temporary Gemini 503 error
                # ----------------------------------

                is_temporary_error = (
                    "503" in error_message
                    or "UNAVAILABLE" in error_message
                    or "high demand" in error_message.lower()
                )

                if is_temporary_error:

                    logger.warning(
                        f"Gemini temporarily unavailable "
                        f"(attempt {attempt}/{max_retries})."
                    )

                    # Retry if attempts remain
                    if attempt < max_retries:

                        wait_time = 2**attempt

                        logger.info(f"Retrying in " f"{wait_time} second(s)...")

                        time.sleep(wait_time)

                        continue

                    # All retries exhausted
                    logger.error(
                        "Gemini remained unavailable " "after all retry attempts."
                    )

                    return (
                        "The AI model is temporarily " "unavailable. Please try again."
                    )

                # ----------------------------------
                # Other errors
                # ----------------------------------

                logger.exception(f"Gemini generation failed: {exc}")

                return "I was unable to generate " "an answer at this time."

        # ------------------------------------------
        # Safety fallback
        # ------------------------------------------

        return "I was unable to generate " "an answer at this time."
