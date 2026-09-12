import google.genai as genai
import os
from dotenv import load_dotenv
load_dotenv()
import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
import re

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def score_transcription(candidate, baseline):
    prompt = f"""Compare this transcription against the baseline. Score 1-5:
5 — Meaning fully preserved, no notable errors
4 — Meaning preserved, minor wording differences
3 — Meaning mostly preserved, one notable omission/error
2 — Meaning partially lost or distorted
1 — Meaning lost / unusable output

Baseline: {baseline}
Candidate: {candidate}

Respond with just the number and a one-line reason."""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    text = response.text.strip()

    match = re.match(r"\s*([1-5])", text)
    if not match:
        raise ValueError(f"Could not parse a score from LLM response: {text!r}")

    score = int(match.group(1))
    return score, text