"""Audio loading and preprocessing utilities.

Loads WAV files of any reasonable format (sample rate, channel count) and
converts them to the s16le PCM, 16kHz mono format required by the Krisp
Voice Translation API, resampling/downmixing as needed.
"""

import numpy as np
import logging
import soundfile as sf

# Sample rate for the Voice Translation API (16 kHz mono s16le only).
_SAMPLE_RATE_HZ = 16000

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("krisp-voice-testing")

def _resample_linear(audio: np.ndarray, src_rate: int, dst_rate: int) -> np.ndarray:
    """Lightweight linear-interpolation resampler.

    Good enough for speech going into the Krisp ASR; for highest fidelity
    pre-convert with ``ffmpeg -ar 16000 -ac 1 -sample_fmt s16``.
    """
    if src_rate == dst_rate or len(audio) == 0:
        return audio
    duration = len(audio) / float(src_rate)
    target_len = max(1, int(round(duration * dst_rate)))
    src_t = np.linspace(0.0, duration, num=len(audio), endpoint=False)
    dst_t = np.linspace(0.0, duration, num=target_len, endpoint=False)
    return np.interp(dst_t, src_t, audio).astype(np.float32, copy=False)

def load_wav_as_pcm16(path: str, target_sample_rate: int) -> bytes:
    """Load any reasonable WAV and return ``s16le`` PCM bytes (mono, target rate)."""
    audio, src_rate = sf.read(path, dtype="float32", always_2d=False)
    if audio.ndim > 1:
        log.info("Mixing %d channels down to mono", audio.shape[1])
        audio = audio.mean(axis=1).astype(np.float32, copy=False)
    if src_rate != target_sample_rate:
        log.info("Resampling %d Hz → %d Hz (linear interpolation)",
                 src_rate, target_sample_rate)
        audio = _resample_linear(audio, src_rate, target_sample_rate)
    pcm16 = np.clip(audio * 32767.0, -32768.0, 32767.0).astype(np.int16, copy=False)
    return pcm16.tobytes()