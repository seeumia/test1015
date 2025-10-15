"""Definitions for Tetris tetromino shapes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

Coordinate = Tuple[int, int]
Grid = List[List[int]]


@dataclass(frozen=True)
class Tetromino:
    """Represents a tetromino with a set of rotation states."""

    name: str
    rotations: Tuple[Grid, ...]

    def rotated(self, index: int) -> Grid:
        """Return the rotation grid at the provided index."""
        return self.rotations[index % len(self.rotations)]


# Tetromino definitions use 0/1 grids to indicate filled blocks.
TETROMINOES: Tuple[Tetromino, ...] = (
    Tetromino(
        "I",
        (
            [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
            ],
        ),
    ),
    Tetromino(
        "O",
        (
            [
                [1, 1],
                [1, 1],
            ],
        ),
    ),
    Tetromino(
        "T",
        (
            [
                [0, 1, 0],
                [1, 1, 1],
                [0, 0, 0],
            ],
            [
                [0, 1, 0],
                [0, 1, 1],
                [0, 1, 0],
            ],
            [
                [0, 0, 0],
                [1, 1, 1],
                [0, 1, 0],
            ],
            [
                [0, 1, 0],
                [1, 1, 0],
                [0, 1, 0],
            ],
        ),
    ),
    Tetromino(
        "S",
        (
            [
                [0, 1, 1],
                [1, 1, 0],
                [0, 0, 0],
            ],
            [
                [0, 1, 0],
                [0, 1, 1],
                [0, 0, 1],
            ],
        ),
    ),
    Tetromino(
        "Z",
        (
            [
                [1, 1, 0],
                [0, 1, 1],
                [0, 0, 0],
            ],
            [
                [0, 0, 1],
                [0, 1, 1],
                [0, 1, 0],
            ],
        ),
    ),
    Tetromino(
        "J",
        (
            [
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 0],
            ],
            [
                [0, 1, 1],
                [0, 1, 0],
                [0, 1, 0],
            ],
            [
                [0, 0, 0],
                [1, 1, 1],
                [0, 0, 1],
            ],
            [
                [0, 1, 0],
                [0, 1, 0],
                [1, 1, 0],
            ],
        ),
    ),
    Tetromino(
        "L",
        (
            [
                [0, 0, 1],
                [1, 1, 1],
                [0, 0, 0],
            ],
            [
                [0, 1, 0],
                [0, 1, 0],
                [0, 1, 1],
            ],
            [
                [0, 0, 0],
                [1, 1, 1],
                [1, 0, 0],
            ],
            [
                [1, 1, 0],
                [0, 1, 0],
                [0, 1, 0],
            ],
        ),
    ),
)


def iter_cells(grid: Grid) -> Iterable[Coordinate]:
    """Yield coordinates for all filled cells in the grid."""
    for y, row in enumerate(grid):
        for x, value in enumerate(row):
            if value:
                yield x, y
