"""Thin wrapper around the Krisp Voice Translation SDK — session setup,
chunked streaming, and result collection. Used by all three test cases."""

import os
import time
import logging
from dotenv import load_dotenv
from krisp_voice_translation import (
    Vt, VtSessionConfig, VtVoice, get_vt_session_key,
    KrispVtApiError, KrispVtError,
)
from .audio_utils import load_wav_as_pcm16
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("krisp-voice-testing")

load_dotenv()
API_KEY = os.getenv("KRISP_API_KEY")

# Sample rate for the Voice Translation API (16 kHz mono s16le only).
_SAMPLE_RATE_HZ = 16000
# Bytes per 20ms chunk, 16kHz mono s16le
_CHUNK_BYTES = 640          
# How long to wait between sending each chunk — 20 milliseconds, matching pace in real time — required by the API.
_CHUNK_PACE_SEC = 0.020
_DRAIN_SECONDS = 2.0

def _mask(token: str) -> str:
    if not token:
        return "<missing>"
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}…{token[-4:]}"

def run_session(wav_path, input_lang, output_lang, voice=VtVoice.FEMALE):
    """
    Stream a WAV file through Krisp and return the final transcript/translation.
    Returns: {"source": str, "target": str}
    """
    results = {"source": {}, "target": {}}

    # 1. Get a session key
    try:
        token = get_vt_session_key(API_KEY)
    except KrispVtApiError as e:
        log.error("Failed to mint session key: [%s] %s — %s",
                    e.error_type.name, e.reason, e.description)
        if e.recovery_hint:
            log.info("Hint: %s", e.recovery_hint)
        return None
    except KrispVtError as e:
        log.error("Failed to mint session key: %s", e)
        return None
    session_key = token["session_key"]
    log.info(
        "Session key acquired: %s (expires_at=%s, key_id=%s)",
        _mask(session_key), token.get("expires_at"), token.get("key_id"),
    )

    # 2. Load and prepare audio
    pcm = load_wav_as_pcm16(wav_path, target_sample_rate=_SAMPLE_RATE_HZ)
    chunks = [pcm[i:i + _CHUNK_BYTES] for i in range(0, len(pcm), _CHUNK_BYTES)]
    chunks = [c for c in chunks if len(c) == _CHUNK_BYTES]  # drop incomplete trailing chunk

    # 3. Callbacks — are invoked with SDK events as they arrive.
    def on_source_text(r):
        log.info("chunk_id=%s type=%s len=%d", r.chunk_id, r.type.name, len(r.transcript))
        # Collected in a dict keyed by chunk_id, rather than only appending on FINAL
        # like Krisp's example does — continuous singing doesn't always reach FINAL
        # before the session closes, so this keeps the latest INTERIM as a fallback.
        if r.chunk_id:
            results["source"][r.chunk_id] = r.transcript

    def on_target_text(r):
        if r.chunk_id:
            results["target"][r.chunk_id] = r.transcript

    def on_error(err):
        log.error("Voice Translation error: %s", err.name)

    def on_audio(result):
        pass  # not used — we only care about transcript text, not synthesized audio

    def on_event(event):
        pass  # not used — no live event logging needed for this test

    # 4. Open session
    config = VtSessionConfig(
        auth_token=session_key,
        input_language_code=input_lang,
        output_language_code=output_lang,
        voice=voice,
    )
    try:
        vt = Vt.create(
            config,
            original_transcript_callback=on_source_text,
            translated_transcript_callback=on_target_text,
            error_callback=on_error,
            audio_result_callback=on_audio,
            event_callback=on_event,
        )
    except KrispVtApiError as e:
        log.error("Failed to open VT session: [%s] %s — %s",
                    e.error_type.name, e.reason, e.description)
        if e.recovery_hint:
            log.info("Hint: %s", e.recovery_hint)
        return None
    except KrispVtError as e:
        log.error("Failed to open VT session: %s", e)
        return None

    # 5. Stream
    for chunk in chunks:
        vt.process(chunk)
        time.sleep(_CHUNK_PACE_SEC)
    time.sleep(_DRAIN_SECONDS)
    vt.close()

    return {
        "source": " ".join(results["source"].values()),
        "target": " ".join(results["target"].values()),
    }