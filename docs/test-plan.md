# Test plan for Krisp AI SDK

## Objective
Test Krisp's transcription/translation/noise-removal accuracy meanwhile showcasing my ability to design a test methodology around voice AI.

## Input Data preparation
To meet Krisp API requirements the following steps are done:
1. Input audio file conversion to PCM: `input.m4a -ar 16000 -ac 1 -f s16le output.pcm`
2. Chunking it into frames (the docs show 16kHz mono s16le = 640 bytes per 20ms chunk)
3. Streaming those chunks with a sleep(0.020) pace between them, matching real-time playback speed

## Collection of results
The output result is derived by:
1. Collecting the incremental transcript/translation events as they arrive
2. Assembling the final result

## Case 1: Russian audiobook translation into English
**1. Objective**

Monologue/narration speech. Adjacent to Krisp's core use case. Realistic spoken-language input, but not conversational; tests robustness on a related-but-different pattern

**2. Scope**

The input is self recorded russian audiobook with no accent with background noise. 
The input data need to be cleaned from back noise, transcribed and translated to English.

**3. Baseline**

Russian transcription is given, English translation is also present. It's a well known poem

**4. Evaluation method**

Noise removal is evaluated indirectly: comparing transcription accuracy with vs. without Krisp's noise removal applied, rather than a separate audio-quality metric.

LLM-as-judge
- 5 — Meaning fully preserved, no notable errors
- 4 — Meaning preserved, minor wording differences
- 3 — Meaning mostly preserved, one notable omission/error
- 2 — Meaning partially lost or distorted
- 1 — Meaning lost / unusable output

**5. Success criteria**

- Noise removal: transcription accuracy must improve when Krisp's noise removal is applied vs. not applied
- Translation quality: average LLM-judge score ≥4 across test utterances

**6. Known limitations**

Small sample size, subjective judgment calls

## Case 2: Conversation between man and woman (with accent)
**1. Objective**

Conversational speech. This is direct fit to Krisp's core use case. 

**2. Scope**

The input is self recorded conversation in Russian with 1 speaker with Armenian accent, another no a little background noise. 
The input data need to be cleaned from back noise, man's speech needs to be polished to sound more Russian, both transcribed and translated to English.

**3. Baseline**

Russian transcription is given, English translation is also present. It's written by me, translated by llm.

**4. Evaluation method**

LLM-as-judge
- 5 — Meaning fully preserved, no notable errors
- 4 — Meaning preserved, minor wording differences
- 3 — Meaning mostly preserved, one notable omission/error
- 2 — Meaning partially lost or distorted
- 1 — Meaning lost / unusable output
How to assess accent removal?

**5. Success criteria**

- Accent conversion: transcription accuracy improved on the accented speaker's segments after accent conversion is applied.
- Translation quality: average LLM-judge score ≥4 across test utterances

**6. Known limitations**

Small sample size, subjective judgment calls

## Case 3: Acappela in English
**1. Objective**

This is an edge Krisp use case to test acapella transcription.

**2. Scope**

Non-speech (singing). Deliberate edge case — outside the product's intended domain entirely.

**3. Baseline**

English transcription is given by me. Known song. 

**4. Evaluation method**

LLM-as-judge
- 5 — Meaning fully preserved, no notable errors
- 4 — Meaning preserved, minor wording differences
- 3 — Meaning mostly preserved, one notable omission/error
- 2 — Meaning partially lost or distorted
- 1 — Meaning lost / unusable output


**5. Success criteria**

- Translation quality: average LLM-judge score ≥4 across test utterances

**6. Known limitations**

Small sample size, subjective judgment calls

