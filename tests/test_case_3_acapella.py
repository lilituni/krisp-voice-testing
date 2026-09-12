from unittest import result

from src.krisp_client import run_session
import os
from src.compare import score_transcription
import shutil
def read_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_case_3_acapella_transcription():
    out_dir = "results/case_3_acapella"
    os.makedirs(out_dir, exist_ok=True)

    """
    result = run_session(
        wav_path="data/audio_samples/en_acapella_sample.wav",
        input_lang="en-US",
        output_lang="en-US",
    )
    assert result is not None, "Session failed — check logs"

    with open(f"{out_dir}/transcript.txt", "w", encoding="utf-8") as f:
        f.write(result["source"])
    """
    baseline_path = "baselines/case_3_acapella/en_transcript.txt"
    shutil.copy(baseline_path, f"{out_dir}/baseline.txt")   # for easy side-by-side comparison
    
    baseline_text = read_text_file(f"{out_dir}/baseline.txt")
    source_text = read_text_file(f"{out_dir}/transcript.txt")
    #score, reason = score_transcription(candidate=result["source"], baseline=baseline_text)
    score, reason = score_transcription(candidate=source_text, baseline=baseline_text)
    with open(f"{out_dir}/score.txt", "w", encoding="utf-8") as f:
        f.write(f"Score: {score}\nReason: {reason}\n")

    assert score >= 4, f"Transcription scored {score}, expected >=4. Reason: {reason}"