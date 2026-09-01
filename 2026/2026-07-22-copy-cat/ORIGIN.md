# Origin: Copy Cat (`copy_cat`)

- **Original Repository:** `https://github.com/admiralorbiter/copy_cat` (Archived & Private)
- **Date Created:** July 22, 2026
- **Consolidated into Sketchbook:** 2026-09-01
- **Tech Stack:** Python 3.10+, PySide6 (Qt6), Edge TTS, Ollama (Local AI), Markdown, Pytest

---

## 1. Concept & Hypothesis

Can copied or selected text be transformed into a structured, navigable **auditory document**—preserving headings, code blocks, lists, and tables with an independent semantic cursor—enabling true eyes-reduced reading rather than linear text-to-speech?

---

## 2. What Was Built

- **Document Parsing & Semantic Domain Model (`src/domain/`, `src/parser/`):**
  - Converts clipboard text into immutable `SourceSnapshot` and typed `DocumentBlock` objects (`Heading`, `Paragraph`, `CodeBlock`, `Table`, `List`).
  - `ReadingSession` maintains a semantic reading position with generation tokens to invalidate stale asynchronous TTS tasks upon seeking.
- **Speech Planning & Audio Engine (`src/speech/`, `src/audio/`):**
  - Normalizes code, markdown formatting, and lists for natural prosody.
  - Bounded asynchronous prefetch queue for Edge neural TTS.
  - In-memory Qt audio playback buffers to eliminate Windows temp-file locks.
- **Local AI Transformation Layer (`src/transformers/`):**
  - Ollama integration supporting natural reading, code explanation, table summaries, and section gists.
- **Interactive UI (`src/ui/`):**
  - PySide6 desktop interface with active block highlighting, prev/next navigation, and speed controls.

---

## 3. Why It Stopped & Lineage Value

- **Complete Focused Probe:** Built in ~1 hour 50 minutes on July 22, 2026. Proved that structured auditory document navigation is vastly superior to naive string-based text-to-speech.
- **Pedagogical & Engineering Invariant:**
  $$\text{Raw Text String} \neq \text{Auditory Document}$$
  Document structure and semantic navigation cursors must precede voice synthesis.
