# Krisp Voice Translation — Test Suite

An independent project exploring test design for voice-AI accuracy, inspired
by Krisp's Voice Translation API. Built to demonstrate test methodology —
not requested or reviewed by Krisp.

## What this tests

Three deliberately different audio scenarios against Krisp's Voice
Translation API, chosen to cover the product's core use case and its edges:

- **Case 1 — Russian audiobook narration.** Adjacent to Krisp's core use
  case (single-speaker, not conversational). Also tests noise removal by
  comparing transcription accuracy with and without background voice
  cancellation applied.
- **Case 2 — Russian conversation, one accented speaker.** Krisp's core
  use case: natural two-speaker dialogue.
- **Case 3 — Acapella song (English).** Deliberate out-of-domain edge
  case — Krisp targets spoken conversation, not singing.

Each case scores transcription/translation against a hand-prepared baseline
using an LLM-as-judge, per a 1–5 rubric. See
[`docs/test-plan.md`](docs/test-plan.md) for full methodology, evaluation
criteria, and results.

## Results summary

Krisp performs strongly on its core use case (Case 2) and degrades
gracefully on adjacent/out-of-domain input, with specific, identifiable
failure modes rather than silent breakage. Full results and scoring
rationale in the test plan.

## Project structure

```
src/
├── krisp_client.py     # Session setup, chunked streaming, result collection
├── audio_utils.py      # WAV loading/resampling
├── compare.py          # LLM-as-judge scoring
└── file_utils.py       # Shared read/write helpers

tests/                   # One file per test case (pytest)
data/audio_samples/      # Links to audio (not committed — see data/README.md)
baselines/               # Reference transcripts/translations per case
docs/test-plan.md        # Full methodology and results
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file with:

```
KRISP_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

## Running the tests

```bash
python -m pytest tests/test_case_1_ru_audiobook.py -v -s
python -m pytest tests/test_case_2_conversation.py -v -s
python -m pytest tests/test_case_3_acapella.py -v -s
```

## Notes

- Data-loading approach (WAV resampling) adapted from Krisp's example script.
- Case 3's baseline/results are excluded from this repo due to copyright
  (song lyrics) — see [`docs/test-plan.md`](docs/test-plan.md) for details.