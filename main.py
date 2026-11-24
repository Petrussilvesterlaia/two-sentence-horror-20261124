#!/usr/bin/env python3
"""Two-Sentence Horror — make.fun entry program.

Writes exactly one horror story of exactly two sentences to
/output/entry.txt (falling back to output/entry.txt next to this file
when /output is not writable, e.g. during local testing).

The story is fixed and deterministic: the same bytes are written on
every run. Before writing, the program validates the story itself:
exactly two sentences, at most 400 characters, valid UTF-8, and
ending in sentence-final punctuation.
"""

import os
import re
import sys

STORY = (
    "The pediatrician said my daughter's imaginary friend would fade "
    "by the time she turned six. "
    "She turned six yesterday, and this morning the friend introduced "
    "itself to me \u2014 in her voice, with her full name, from inside "
    "her bedroom, while she stood beside me in the kitchen."
)

MAX_CHARS = 400
SENTENCE_END = re.compile(r"[.!?]")


def split_sentences(text):
    """Split text into sentences on terminal punctuation.

    A sentence ends at a '.', '!' or '?' that is followed by a space or
    by the end of the text. Returns the list of sentence strings.
    """
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part for part in parts if part]


def validate(text):
    """Check the story against the competition's gate rules.

    Returns a list of problems; an empty list means the story is valid.
    """
    problems = []
    if not text or not text.strip():
        problems.append("story is empty or whitespace only")
        return problems
    if len(text) > MAX_CHARS:
        problems.append(
            "story is %d characters, over the %d limit" % (len(text), MAX_CHARS)
        )
    if text != text.strip():
        problems.append("story has leading or trailing whitespace")
    if any(ord(ch) < 0x20 and ch not in "\n\r\t" for ch in text):
        problems.append("story contains a control character")
    if "\n" in text or "\r" in text or "\t" in text:
        problems.append("story contains a line break or tab")
    sentences = split_sentences(text)
    if len(sentences) != 2:
        problems.append(
            "story has %d sentences, expected exactly 2" % len(sentences)
        )
    for index, sentence in enumerate(sentences, start=1):
        if not SENTENCE_END.search(sentence[-1:]):
            problems.append(
                "sentence %d does not end with sentence-final punctuation"
                % index
            )
        if not sentence.strip():
            problems.append("sentence %d is empty" % index)
    if not SENTENCE_END.search(text[-1:]):
        problems.append("story does not end with sentence-final punctuation")
    return problems


def output_path():
    """Resolve where to write entry.txt.

    The grader sandbox provides /output; locally, use output/ next to
    this file so the program can be run and checked without root.
    """
    preferred = "/output/entry.txt"
    try:
        os.makedirs("/output", exist_ok=True)
        with open(preferred, "a", encoding="utf-8"):
            pass
        return preferred
    except OSError:
        here = os.path.dirname(os.path.abspath(__file__))
        local_dir = os.path.join(here, "output")
        os.makedirs(local_dir, exist_ok=True)
        return os.path.join(local_dir, "entry.txt")


def main():
    problems = validate(STORY)
    if problems:
        for problem in problems:
            print("validation error: %s" % problem, file=sys.stderr)
        return 1
    path = output_path()
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(STORY)
    # Verify the write round-trips byte for byte: read the file back as
    # raw bytes, decode it strictly as UTF-8, and compare with the story.
    with open(path, "rb") as handle:
        written = handle.read()
    try:
        decoded = written.decode("utf-8")
    except UnicodeDecodeError as error:
        print("validation error: output is not valid UTF-8: %s" % error,
              file=sys.stderr)
        return 1
    if decoded != STORY:
        print("validation error: output bytes differ from the story",
              file=sys.stderr)
        return 1
    sentences = split_sentences(STORY)
    print("wrote %d characters (%d sentences) to %s"
          % (len(STORY), len(sentences), path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
