import os
import shutil
from src.krisp_client import run_session
from src.compare import score_transcription
from src.file_utils import read_text_file, write_text_file

def test_case_3_acapella_transcription():
    """Test case for transcribing an acapella audio sample."""
    out_dir = "results/case_3_acapella"
    os.makedirs(out_dir, exist_ok=True)

    # Run transcription session for the acapella sample.
    # Translation is not needed here.
    result = run_session(
        wav_path="data/audio_samples/case_3_acapella.wav",
        input_lang="en-US",
        output_lang="en-US",
    )

    ### Check that the session was successful.
    assert result is not None, "Session failed — check logs"

    # Write the transcription result to a file.
    write_text_file(f"{out_dir}/transcript.txt", result["source"])

    # Copy baseline to results directory for easy side-by-side comparison.
    baseline_path = "baselines/case_3_acapella/transcript.txt"
    shutil.copy(baseline_path, f"{out_dir}/baseline.txt")
    baseline_text = read_text_file(f"{out_dir}/baseline.txt")

    # Score the transcription against the baseline and write the score to a file.
    score, reason = score_transcription(candidate=result["source"], baseline=baseline_text)
    write_text_file(f"{out_dir}/score.txt", f"Score: {score}\nReason: {reason}\n")

    ### Check that the score meets the expected threshold otherwise fail.
    assert score >= 4, f"Transcription scored {score}, expected >=4. Reason: {reason}"