#!/usr/bin/env python3
"""The Most Boring Object, Reviewed in One Line -- make.fun entry.

Writes one original line (at most 200 characters) reviewing a wall clock
to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output).

The joke is the clock's own dullness. 86,400 is the exact number of
seconds in a day, so the line is funny because it is true: the most
reliable object in the house ticks once a second for a decade, never
takes a day off, and is never once thanked. The punchline lands on the
last words, "nobody has ever once said well done."

Deterministic by construction: the line is a constant, there is no
input, no network, no randomness and no clock. Every run writes
byte-identical output. Before writing, the program gates the line
itself (exactly one line, 1-200 characters, not blank) and reports
every failed gate with its exact count instead of stopping at the
first one. After writing, it reads the file back and checks both the
bytes and the SHA-256 digest against the expected values, so a
truncated or altered write can never be reported as a success.
"""

import hashlib
import os
import sys
from pathlib import Path

LINE = (
    "The wall clock has ticked 86,400 times a day for a decade without "
    "a single day off, and nobody has ever once said well done."
)

MAX_CHARS = 200

# SHA-256 of entry.txt: the line above plus one trailing newline,
# UTF-8 encoded. Kept here so the post-write check can prove the
# file on disk is exactly the gated line, byte for byte.
EXPECTED_SHA256 = "3da35bec36e400f5de857eeee279ee06385bd5b4b90a12fd09719da68c565e40"


def check_line(text):
    """Return a list of gate failures for *text*, each with its exact count.

    An empty list means the line passes every gate. All gates are
    evaluated, so the caller learns about every problem at once
    instead of only the first one found.
    """
    failures = []
    if not text.strip():
        failures.append("gate failed: line is blank (0 non-space characters)")
    newline_count = text.count("\n") + text.count("\r")
    if newline_count:
        failures.append(
            "gate failed: line must be a single line "
            "(found %d newline character(s))" % newline_count
        )
    length = len(text)
    if length < 1 or length > MAX_CHARS:
        failures.append(
            "gate failed: %d characters, must be 1-%d"
            % (length, MAX_CHARS)
        )
    return failures


def expected_bytes(text):
    """The exact bytes entry.txt must contain for *text*."""
    return (text + "\n").encode("utf-8")


def write_entry(path, payload):
    """Write *payload* to *path*, creating the parent directory first."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def verify_entry(path, payload):
    """Return a list of verification failures for the file at *path*.

    Compares the bytes read back from disk with *payload* and the
    SHA-256 digest with EXPECTED_SHA256, reporting the exact lengths
    and digests on any mismatch.
    """
    failures = []
    try:
        written = path.read_bytes()
    except OSError as exc:
        failures.append("gate failed: cannot read back %s (%s)" % (path, exc))
        return failures
    if written != payload:
        failures.append(
            "gate failed: written file is %d bytes, expected %d bytes"
            % (len(written), len(payload))
        )
    actual_digest = hashlib.sha256(written).hexdigest()
    if actual_digest != EXPECTED_SHA256:
        failures.append(
            "gate failed: written file sha256 %s, expected %s"
            % (actual_digest, EXPECTED_SHA256)
        )
    return failures


def fail(failures):
    """Print each failure to stderr and return the failure exit code."""
    for failure in failures:
        print(failure, file=sys.stderr)
    return 1


def main():
    failures = check_line(LINE)
    if failures:
        return fail(failures)
    payload = expected_bytes(LINE)
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    path = out_dir / "entry.txt"
    try:
        write_entry(path, payload)
    except OSError as exc:
        return fail(["gate failed: cannot write %s (%s)" % (path, exc)])
    failures = verify_entry(path, payload)
    if failures:
        return fail(failures)
    print(
        "wrote %s: %d characters, sha256 %s"
        % (path, len(LINE), EXPECTED_SHA256)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
