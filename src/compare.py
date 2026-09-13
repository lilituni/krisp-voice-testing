"""LLM-as-judge scoring for transcription/translation quality.

Compares a candidate transcript against a baseline using Gemini, scored
1-5 per the rubric defined in test-plan.md (meaning preservation).
Used by all three test cases to evaluate their output against ground truth.
"""

import google.genai as genai
import os
from dotenv import load_dotenv
load_dotenv()
import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
import re

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def score_transcription(candidate: str, baseline: str) -> tuple[int, str]:
    """
    Compare a candidate transcription against a baseline.
    This is done by prompting a language model to evaluate the quality of the transcription.
    Return a score and reason.
    Score is an integer from 1 to 5, from bad to good, with 5 being the best.
    """

    prompt = f"""Compare this transcription against the baseline. Score 1-5:
5 — Meaning fully preserved, no notable errors
4 — Meaning preserved, minor wording differences
3 — Meaning mostly preserved, one notable omission/error
2 — Meaning partially lost or distorted
1 — Meaning lost / unusable output

Baseline: {baseline}
Candidate: {candidate}

Respond with just the number and a one-line reason."""

    # Send the prompt to the language model and get the response.
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    # Extract the text from the response.
    text = response.text.strip()

    # Parse the score.
    match = re.match(r"\s*([1-5])", text)
    if not match:
        raise ValueError(f"Could not parse a score from LLM response: {text!r}")
    score = int(match.group(1))

    return score, text