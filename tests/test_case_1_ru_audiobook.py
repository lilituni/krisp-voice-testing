"""Case 1: Russian audiobook narration — transcription, translation, and
background noise removal (BVC). See docs/test-plan.md, Case 1.
"""
import os
import shutil
import pytest
from src.krisp_client import run_session
from src.compare import score_transcription
from src.file_utils import read_text_file, write_text_file

OUT_DIR = "results/case_1_ru_audiobook"
WAV_PATH = "data/audio_samples/case_1_ru_audiobook.wav"


@pytest.fixture(scope="module")
def result_raw()-> dict:
    """Run once, bvc=False. Shared by every test in this file."""
    os.makedirs(OUT_DIR, exist_ok=True)
    # Run the session without background noise removal (BVC) to get the raw transcription and translation.
    result = run_session(wav_path=WAV_PATH, input_lang="ru-RU", output_lang="en-US", bvc=False)
    ### Check that the session was successful.
    assert result is not None, "Session failed (bvc=False) — check logs"
    return result


@pytest.fixture(scope="module")
def result_clean()-> dict:
    """Run once, bvc=True. Shared by every test in this file."""
    os.makedirs(OUT_DIR, exist_ok=True)
    # Run the session with background noise removal (BVC) to get the cleaned transcription and translation.
    result = run_session(wav_path=WAV_PATH, input_lang="ru-RU", output_lang="en-US", bvc=True)
    ### Check that the session was successful.
    assert result is not None, "Session failed (bvc=True) — check logs"
    return result


def test_case_1_transcription_quality(result_raw: dict) -> None:
    """Check the Russian transcription quality against the baseline."""
    # Write the raw transcription to a file.
    write_text_file(f"{OUT_DIR}/ru_transcript.txt", result_raw["source"])
    # Copy baseline to results directory for easy side-by-side comparison.
    baseline_path = "baselines/case_1_ru_audiobook/ru_transcript.txt"
    shutil.copy(baseline_path, f"{OUT_DIR}/ru_baseline.txt")
    baseline_text = read_text_file(f"{OUT_DIR}/ru_baseline.txt")
    # Score the transcription against the baseline and write the score to a file.
    score, reason = score_transcription(candidate=result_raw["source"], baseline=baseline_text)
    write_text_file(f"{OUT_DIR}/ru_score.txt", f"Score: {score}\nReason: {reason}\n")
    ### Check that the score meets the expected threshold otherwise fail.
    assert score >= 4, f"Transcription scored {score}, expected >=4. Reason: {reason}"


def test_case_1_translation_quality(result_raw: dict) -> None:
    """Check the English translation quality against the baseline."""
    # Write the raw translation to a file.
    write_text_file(f"{OUT_DIR}/en_transcript.txt", result_raw["target"])
    # Copy baseline to results directory for easy side-by-side comparison.
    baseline_path = "baselines/case_1_ru_audiobook/en_transcript.txt"
    shutil.copy(baseline_path, f"{OUT_DIR}/en_baseline.txt")
    baseline_text = read_text_file(f"{OUT_DIR}/en_baseline.txt")
    # Score the translation against the baseline and write the score to a file.
    score, reason = score_transcription(candidate=result_raw["target"], baseline=baseline_text)
    write_text_file(f"{OUT_DIR}/en_score.txt", f"Score: {score}\nReason: {reason}\n")
    ### Check that the score meets the expected threshold otherwise fail.
    assert score >= 4, f"Translation scored {score}, expected >=4. Reason: {reason}"


def test_case_1_noise_removal_effect(result_raw: dict, result_clean: dict) -> None:
    """Check that BVC improves transcription quality (or at least doesn't make it worse)."""
    # Save both transcripts for inspection/debugging.
    write_text_file(f"{OUT_DIR}/ru_transcript_raw.txt", result_raw["source"])
    write_text_file(f"{OUT_DIR}/ru_transcript_clean.txt", result_clean["source"])

    # Compare the raw and cleaned transcriptions against the baseline and write the scores to a file.
    baseline_text = read_text_file("baselines/case_1_ru_audiobook/ru_transcript.txt")
    score_raw, _ = score_transcription(candidate=result_raw["source"], baseline=baseline_text)
    score_clean, _ = score_transcription(candidate=result_clean["source"], baseline=baseline_text)

    if score_clean == score_raw:
        verdict = f"Inconclusive — no measurable difference ({score_raw} vs {score_clean})"
        write_text_file(f"{OUT_DIR}/noise_comparison.txt", verdict)
        print(verdict)
    else:
        verdict = f"Without BVC: {score_raw}\nWith BVC: {score_clean}"
        write_text_file(f"{OUT_DIR}/noise_comparison.txt", verdict)
        assert score_clean > score_raw, f"BVC made things worse: {score_raw} → {score_clean}. {verdict}"