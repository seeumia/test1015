"""Unit tests for the Tetris board mechanics."""
from __future__ import annotations

from random import Random

from tetris.board import Board, HEIGHT, WIDTH


class DeterministicRandom(Random):
    """Predictable RNG that cycles through tetrominoes in order."""

    def __init__(self) -> None:
        super().__init__(0)
        self.index = 0

    def choice(self, seq):  # type: ignore[override]
        value = seq[self.index % len(seq)]
        self.index += 1
        return value


def new_board() -> Board:
    return Board(random=DeterministicRandom())


def test_spawn_piece_valid() -> None:
    board = new_board()
    assert board.spawn_piece()
    assert board.current is not None
    for x, y in board.current.cells():
        assert 0 <= x < WIDTH
        assert 0 <= y < HEIGHT


def test_move_piece_and_lock() -> None:
    board = new_board()
    assert board.spawn_piece()
    # Move piece to the floor by repeatedly soft dropping
    steps = 0
    while board.move(0, 1):
        steps += 1
        assert steps < HEIGHT * 2
    assert board.current is None
    # After locking, a new piece should spawn when requested
    assert board.spawn_piece()


def test_line_clearing_and_scoring() -> None:
    board = new_board()
    # Fill bottom row manually
    for x in range(board.width):
        board.grid[-1][x] = 1
    board.spawn_piece()
    board.lock_piece()
    assert all(cell == 0 for cell in board.grid[-1])
    assert board.lines_cleared == 1
    assert board.score == 100


def test_ghost_piece_is_below() -> None:
    board = new_board()
    board.spawn_piece()
    ghost = board.ghost_piece()
    assert ghost is not None
    assert ghost.y >= board.current.y  # type: ignore[union-attr]
