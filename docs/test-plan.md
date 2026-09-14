# Test plan for Krisp AI SDK

## Objective
Test Krisp's transcription/translation/noise-removal accuracy meanwhile showcasing my ability to design a test methodology around voice AI. 
All LLM-as-judge scoring uses gemini-3.6-flash with temperature=0 to reduce sampling randomness (though this does not fully guarantee identical output across calls — see Known Limitations).

## Test coverage overview
- Case 1 tests a related but non-conversational input: single-speaker narration.
- Case 2 tests Krisp's core use case: conversational, two-speaker speech.
- Case 3 tests a deliberate out-of-domain input: sung, non-conversational audio.

## Input Data preparation
To meet Krisp API requirements the following steps are done:
1. Input audio file conversion to PCM: `input.m4a -ar 16000 -ac 1 -f s16le output.pcm`.
2. Chunking it into frames (the docs show 16kHz mono s16le = 640 bytes per 20ms chunk).
3. Streaming those chunks with a sleep(0.020) pace between them, matching real-time playback speed.

## Collection of results
The output result is derived by:
1. Collecting the incremental transcript/translation events as they arrive.
2. Assembling the final result.

## Case 1: Russian audiobook translation into English
**1. Objective**

Monologue/narration speech. Adjacent to Krisp's core use case. Realistic spoken-language input, but not conversational; tests robustness on a related-but-different pattern.

**2. Scope**

The input is self recorded russian audiobook with no accent with background noise. 
The input data need to be cleaned from back noise, transcribed and translated to English.

**3. Baseline**

Russian transcription is given, English translation is also present. It's a well known poem.

**4. Evaluation method**

Noise removal is evaluated indirectly: comparing transcription accuracy with vs. without Krisp's noise removal applied, rather than a separate audio-quality metric.

LLM-as-judge
- 5 — Meaning fully preserved, no notable errors
- 4 — Meaning preserved, minor wording differences
- 3 — Meaning mostly preserved, one notable omission/error
- 2 — Meaning partially lost or distorted
- 1 — Meaning lost / unusable output

**5. Success criteria**

- Noise removal: transcription accuracy improves after Krisp's noise removal — pass
- No measurable difference — inconclusive (may indicate the noise level in this sample wasn't strong enough to test the feature meaningfully, not that the feature failed)
- Accuracy is worse after processing — fail
- Translation quality: average LLM-judge score ≥4 across test utterances

## Case 2: Conversation between man and woman (with accent)
**1. Objective**

Conversational speech. This is direct fit to Krisp's core use case. 

**2. Scope**

The input is a self-recorded conversation in Russian, with one speaker having 
an Armenian accent, with a little background noise. Originally scoped to also 
test accent conversion; investigation showed Krisp's Accent Conversion is a 
separate SDK (not available in this account's self-serve downloads) limited 
to specific English accents converted to North American English — it does 
not apply to Russian audio. This case therefore tests transcription and 
translation only.

**3. Baseline**

Russian transcription is given, English translation is also present. It's written by me, translated by LLM.

**4. Evaluation method**

LLM-as-judge
- 5 — Meaning fully preserved, no notable errors
- 4 — Meaning preserved, minor wording differences
- 3 — Meaning mostly preserved, one notable omission/error
- 2 — Meaning partially lost or distorted
- 1 — Meaning lost / unusable output

**5. Success criteria**

- Translation quality: average LLM-judge score ≥4 across test utterances

## Case 3: Acappela in English
**1. Objective**

This is an edge Krisp use case to test acapella transcription.

**2. Scope**

Non-speech (singing). Deliberate edge case — outside the product's intended domain entirely.

**3. Baseline**

English transcription given by me (known song, excerpt).

**4. Evaluation method**

LLM-as-judge
- 5 — Meaning fully preserved, no notable errors
- 4 — Meaning preserved, minor wording differences
- 3 — Meaning mostly preserved, one notable omission/error
- 2 — Meaning partially lost or distorted
- 1 — Meaning lost / unusable output

**5. Success criteria**

- Transcription accuracy: average LLM-judge score ≥4 across test utterances

## Results

| Case | Metric | Score | Outcome | Notes |
|------|--------|-------|---------|-------|
| **1 — Audiobook** | Transcription | 3/5 | Fail (<4) | Garbled words in final two sentences |
| **1 — Audiobook** | Translation | 4/5 | Pass | Meaning preserved, prose vs. verse style |
| **1 — Audiobook** | Noise removal | — | Inconclusive | Raw/clean scored equally in most runs; one run showed improvement — see Limitations |
| **2 — Conversation** | Transcription | 4/5 | Pass | Minor typo, digits vs. spelled-out numbers |
| **2 — Conversation** | Translation | 4/5 | Pass | Meaning preserved, minor wording/grammar differences |
| **2 — Conversation** | Accent conversion | — | Out of scope | SDK not available on this account; feature limited to specific English accents anyway (not applicable to Russian) |
| **3 — Acapella** | Transcription | 2/5 | Fail (<4) | Multiple word-level errors on out-of-domain input (expected) |

Full transcripts, translations, and per-run scores are generated locally by
the test suite (`pytest tests/`) but not committed, since they're
reproducible outputs rather than source material.

## Known limitations

- Small sample size.
- LLM-as-judge scoring showed some run-to-run variance on the same input
  (observed: the same transcript scored 3 in one call, 2 in another) — a
  known limitation of using a non-deterministic model as an evaluator, not
  a defect in the pipeline. Partially mitigated via `temperature=0`;
  possible non-determinism in Krisp's ASR output across identical inputs
  may also contribute.
- Accent strength and noise level are not independently quantified; if either is mild, transcription-accuracy differences may be too small to be a reliable signal for this feature specifically.
- Cases 1 and 3 are not Krisp's primary target use case (conversational speech); results there indicate robustness/edge-case behavior, not core-feature validation.
- Baseline transcript for Case 3 is a copyrighted song excerpt, used for personal testing purposes only — full lyrics not republished in this repo.

## Possible future extensions
Bilingual conversation. This is an interesting Krisp use case as 2 sessions will be created for 2 directional translation.

## Summary
Krisp performs strongly on its core use case (Case 2, natural conversation) and degrades gracefully on adjacent/out-of-domain input, with specific, identifiable failure modes rather than silent breakage.