"""Case 2: Conversation in Russian between a man and a woman — transcription
and translation. Accent conversion is out of scope: the Accent Conversion SDK
was not surfaced in this account's self-serve SDK downloads, and it only
supports specific English accents converted to North American English —
not applicable to Russian audio regardless of access. See docs/test-plan.md,
Case 2.
"""

import os
import shutil
import pytest
from src.krisp_client import run_session
from src.compare import score_transcription
from src.file_utils import read_text_file, write_text_file

OUT_DIR = "results/case_2_conversation"
WAV_PATH = "data/audio_samples/case_2_conversation.wav"


@pytest.fixture(scope="module")
def result()-> dict:
    """Run once. Shared by both tests in this file."""
    os.makedirs(OUT_DIR, exist_ok=True)
    result = run_session(wav_path=WAV_PATH, input_lang="ru-RU", output_lang="en-US")
    ### Check that the session was successful.
    assert result is not None, "Session failed — check logs"
    return result


def test_case_2_transcription_quality(result: dict) -> None:
    """Check the Russian transcription quality against the baseline."""
    # Write the transcription to a file.
    write_text_file(f"{OUT_DIR}/ru_transcript.txt", result["source"])
    # Copy baseline to results directory for easy side-by-side comparison.
    baseline_path = "baselines/case_2_conversation/ru_transcript.txt"
    shutil.copy(baseline_path, f"{OUT_DIR}/ru_baseline.txt")
    baseline_text = read_text_file(f"{OUT_DIR}/ru_baseline.txt")
    # Score the transcription against the baseline and write the score to a file.
    score, reason = score_transcription(candidate=result["source"], baseline=baseline_text)
    write_text_file(f"{OUT_DIR}/ru_score.txt", f"Score: {score}\nReason: {reason}\n")
    ### Check that the score meets the expected threshold otherwise fail.
    assert score >= 4, f"Transcription scored {score}, expected >=4. Reason: {reason}"


def test_case_2_translation_quality(result: dict) -> None:
    """Check the English translation quality against the baseline."""
    # Write the raw translation to a file.
    write_text_file(f"{OUT_DIR}/en_transcript.txt", result["target"])
    # Copy baseline to results directory for easy side-by-side comparison.
    baseline_path = "baselines/case_2_conversation/en_transcript.txt"
    shutil.copy(baseline_path, f"{OUT_DIR}/en_baseline.txt")
    baseline_text = read_text_file(f"{OUT_DIR}/en_baseline.txt")
    # Score the translation against the baseline and write the score to a file.
    score, reason = score_transcription(candidate=result["target"], baseline=baseline_text)
    write_text_file(f"{OUT_DIR}/en_score.txt", f"Score: {score}\nReason: {reason}\n")
    ### Check that the score meets the expected threshold otherwise fail.
    assert score >= 4, f"Translation scored {score}, expected >=4. Reason: {reason}"
