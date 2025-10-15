"""Core board mechanics for Tetris."""
from __future__ import annotations

from dataclasses import dataclass, replace
from random import Random
from typing import Iterable, List, Optional, Sequence, Tuple

from .shapes import Grid, Tetromino, TETROMINOES, iter_cells

WIDTH = 10
HEIGHT = 20


@dataclass(frozen=True)
class FallingPiece:
    """Represents a tetromino on the board."""

    tetromino: Tetromino
    rotation: int
    x: int
    y: int

    def cells(self) -> Iterable[Tuple[int, int]]:
        """Yield coordinates occupied by the piece."""
        for dx, dy in iter_cells(self.tetromino.rotated(self.rotation)):
            yield self.x + dx, self.y + dy

    def rotated(self, delta: int) -> "FallingPiece":
        return replace(self, rotation=(self.rotation + delta) % len(self.tetromino.rotations))

    def moved(self, dx: int, dy: int) -> "FallingPiece":
        return replace(self, x=self.x + dx, y=self.y + dy)


@dataclass
class Board:
    width: int = WIDTH
    height: int = HEIGHT
    random: Random = Random()

    def __post_init__(self) -> None:
        self.grid: List[List[int]] = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current: Optional[FallingPiece] = None
        self.next_piece: Tetromino = self.random.choice(TETROMINOES)
        self.score: int = 0
        self.level: int = 1
        self.lines_cleared: int = 0

    # -- Piece management -------------------------------------------------
    def spawn_piece(self) -> bool:
        """Spawn the next piece and choose a new one.

        Returns True if the piece fits on the board, False otherwise (game over).
        """

        tetromino = self.next_piece
        self.next_piece = self.random.choice(TETROMINOES)
        piece = FallingPiece(
            tetromino,
            rotation=0,
            x=self.width // 2 - len(tetromino.rotated(0)[0]) // 2,
            y=0,
        )
        if self.is_valid_position(piece):
            self.current = piece
            return True
        return False

    def is_valid_position(self, piece: FallingPiece) -> bool:
        for x, y in piece.cells():
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                return False
            if self.grid[y][x]:
                return False
        return True

    def lock_piece(self) -> None:
        if not self.current:
            return
        for x, y in self.current.cells():
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = 1
        self.current = None
        cleared = self.clear_lines()
        if cleared:
            self.lines_cleared += cleared
            self.score += self.calculate_score(cleared)
            self.level = self.lines_cleared // 10 + 1

    def calculate_score(self, lines: int) -> int:
        return {1: 100, 2: 300, 3: 500, 4: 800}.get(lines, 0) * self.level

    # -- Movement ---------------------------------------------------------
    def move(self, dx: int, dy: int) -> bool:
        if not self.current:
            return False
        moved = self.current.moved(dx, dy)
        if self.is_valid_position(moved):
            self.current = moved
            return True
        if dy > 0:
            self.lock_piece()
        return False

    def rotate(self, delta: int = 1) -> bool:
        if not self.current:
            return False
        rotated = self.current.rotated(delta)
        if self.is_valid_position(rotated):
            self.current = rotated
            return True
        return False

    def hard_drop(self) -> None:
        if not self.current:
            return
        while self.move(0, 1):
            pass

    # -- Line clearing ----------------------------------------------------
    def clear_lines(self) -> int:
        new_grid = [row for row in self.grid if not all(row)]
        cleared = self.height - len(new_grid)
        while len(new_grid) < self.height:
            new_grid.insert(0, [0 for _ in range(self.width)])
        self.grid = new_grid
        return cleared

    # -- Representation ---------------------------------------------------
    def ghost_piece(self) -> Optional[FallingPiece]:
        if not self.current:
            return None
        ghost = self.current
        while self.is_valid_position(ghost.moved(0, 1)):
            ghost = ghost.moved(0, 1)
        return ghost

    def as_rows(self) -> Sequence[Sequence[int]]:
        grid_copy = [row[:] for row in self.grid]
        if self.current:
            for x, y in self.current.cells():
                if 0 <= y < self.height and 0 <= x < self.width:
                    grid_copy[y][x] = 2
        ghost = self.ghost_piece()
        if ghost:
            for x, y in ghost.cells():
                if 0 <= y < self.height and 0 <= x < self.width and grid_copy[y][x] == 0:
                    grid_copy[y][x] = 3
        return grid_copy
