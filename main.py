#!/usr/bin/env python3
"""The Most Boring Object, Reviewed in One Line -- make.fun entry.

Writes one original line (at most 200 characters) reviewing a wall clock
to $MAKEFUN_OUTPUT_DIR/entry.txt (default /output).

Angle: the clock's own dullness is the joke. 86,400 is the true number of
seconds in a day, so the line is funny because it is true: the most
reliable thing in the house ticks once a second for a decade, never takes
a day off, and is never once thanked. The turn lands on the last words.

Deterministic: no input, no network, no randomness, no clock. Every run
writes byte-identical output. The program checks the gate itself before
writing: exactly one line, 1-200 characters, not blank.
"""

import os
import sys

LINE = (
    "The wall clock has ticked 86,400 times a day for a decade without "
    "a single day off, and nobody has ever once said well done."
)


def main():
    text = LINE
    if not text or not text.strip():
        print("gate failed: line is blank", file=sys.stderr)
        return 1
    if "\n" in text or "\r" in text:
        print("gate failed: line must be a single line", file=sys.stderr)
        return 1
    if len(text) < 1 or len(text) > 200:
        print(
            "gate failed: %d characters, must be 1-200" % len(text),
            file=sys.stderr,
        )
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    # Read the file back and verify what was written is exactly the gated
    # line plus one trailing newline; refuse to report success otherwise.
    with open(path, "r", encoding="utf-8", newline="") as f:
        written = f.read()
    if written != text + "\n":
        print("gate failed: written file does not match the gated line",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
