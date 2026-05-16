"""Runnable demo: WFRCluster over a toy "games" feature matrix (PI §65-67).

The features here are deliberately schematic — board / cards / ball / table /
digital — to recreate the §66 thought experiment. Run as::

    python examples/wfr_demo.py

Each row is one "game"; no game shares every feature with every other,
which is exactly the picture Wittgenstein draws in §66.
"""

from __future__ import annotations

import numpy as np

from family_resemblance import WFRCluster, describe


# Feature columns (categorical, 0/1):
#   0: uses a board
#   1: uses cards
#   2: uses a ball
#   3: played at a table
#   4: digital
FEATURES = ["board", "cards", "ball", "table", "digital"]

GAMES = [
    ("chess", [1, 0, 0, 1, 0]),
    ("checkers", [1, 0, 0, 1, 0]),
    ("monopoly", [1, 1, 0, 1, 0]),  # board + cards
    ("poker", [0, 1, 0, 1, 0]),
    ("solitaire", [0, 1, 0, 1, 1]),  # cards, often digital
    ("football", [0, 0, 1, 0, 0]),
    ("tennis", [0, 0, 1, 0, 0]),
    ("ping pong", [0, 0, 1, 1, 0]),
    ("tetris", [0, 0, 0, 0, 1]),
    ("pacman", [0, 0, 0, 0, 1]),
]


def main() -> None:
    names = [g[0] for g in GAMES]
    X = np.array([g[1] for g in GAMES], dtype=float)

    # eps=0.3 separates the three obvious "families" (board/cards, ball,
    # digital) while leaving monopoly and solitaire as boundary points —
    # exactly the picture §66 paints.
    wfr = WFRCluster(eps=0.3, min_samples=2, kernel="match").fit(X)
    conf = wfr.family_membership()

    print(f"{'game':10s}  family  conf   note")
    print("-" * 60)
    for name, label, c in zip(names, wfr.labels_, conf):
        r = describe(int(label), float(c))
        flag = "boundary" if r.boundary else "inside"
        print(f"{name:10s}  {r.label:>6}  {r.confidence:.2f}   {flag}")

    print(
        "\nNo single 'essence of game' was needed — families form by "
        "overlapping similarities (PI §65-67)."
    )


if __name__ == "__main__":
    main()
