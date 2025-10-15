"""Terminal engine for running Tetris using curses."""
from __future__ import annotations

import argparse
import curses
import os
import sys
import time
from dataclasses import dataclass
from random import Random
from typing import Optional, Sequence

from .board import Board

TICK_RATE = 0.5
SPEEDUP = 0.05
HEADLESS_CELL_MAP = {0: " .", 1: " █", 2: " █", 3: " ░"}


@dataclass
class Game:
    board: Board
    drop_interval: float = TICK_RATE
    last_tick: float = time.monotonic()
    paused: bool = False
    game_over: bool = False

    def update_speed(self) -> None:
        self.drop_interval = max(0.1, TICK_RATE - SPEEDUP * (self.board.level - 1))


def draw_board(stdscr: "curses._CursesWindow", game: Game) -> None:
    stdscr.clear()
    board = game.board
    rows = board.as_rows()

    stdscr.addstr(0, 0, "Tetris")
    stdscr.addstr(1, 0, f"Score: {board.score}")
    stdscr.addstr(2, 0, f"Level: {board.level}")
    stdscr.addstr(3, 0, f"Lines: {board.lines_cleared}")
    stdscr.addstr(5, 0, "Controls: ← → move, ↑ rotate, ↓ soft drop, space hard drop")
    stdscr.addstr(6, 0, "          p pause, q quit")

    offset_x = 0
    offset_y = 8
    for y, row in enumerate(rows):
        line = ""
        for cell in row:
            if cell == 0:
                line += " ."
            elif cell == 1:
                line += " █"
            elif cell == 2:
                line += " ▓"
            else:
                line += " ░"
        stdscr.addstr(offset_y + y, offset_x, line)

    stdscr.addstr(offset_y, offset_x + len(rows[0]) * 2 + 4, "Next:")
    for idx, row in enumerate(board.next_piece.rotated(0)):
        line = ""
        for cell in row:
            line += " █" if cell else "  "
        stdscr.addstr(offset_y + 2 + idx, offset_x + len(rows[0]) * 2 + 4, line)

    if game.paused:
        stdscr.addstr(offset_y + board.height // 2, offset_x, "Paused - press p to resume")
    if game.game_over:
        stdscr.addstr(offset_y + board.height // 2 + 2, offset_x, "Game over - press q to exit")

    stdscr.refresh()


def handle_input(stdscr: "curses._CursesWindow", game: Game) -> None:
    board = game.board
    try:
        key = stdscr.getch()
    except curses.error:
        return
    if key == -1:
        return

    if key in (ord("q"), ord("Q")):
        game.game_over = True
    elif key in (ord("p"), ord("P")):
        game.paused = not game.paused
    elif game.paused or game.game_over:
        return
    elif key == curses.KEY_LEFT:
        board.move(-1, 0)
    elif key == curses.KEY_RIGHT:
        board.move(1, 0)
    elif key == curses.KEY_DOWN:
        board.move(0, 1)
    elif key == curses.KEY_UP:
        board.rotate(1)
    elif key == ord(" "):
        board.hard_drop()


def update_game(game: Game) -> None:
    if game.paused or game.game_over:
        return
    now = time.monotonic()
    if now - game.last_tick >= game.drop_interval:
        moved = game.board.move(0, 1)
        if not moved:
            if not game.board.spawn_piece():
                game.game_over = True
        game.last_tick = now
        game.update_speed()



def run(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(False)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    game = Game(Board())
    if not game.board.spawn_piece():
        return

    while True:
        handle_input(stdscr, game)
        update_game(game)
        draw_board(stdscr, game)
        if game.game_over:
            time.sleep(0.1)
            continue
        time.sleep(0.01)


def _can_use_curses() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty() and os.environ.get("TERM")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Tetris game.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="在不支持 curses 的环境下以文本模式演示",
    )
    parser.add_argument(
        "--pieces",
        type=int,
        default=8,
        help="文本模式中自动下落的方块数量",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="文本模式下使用的随机种子，保证演示可复现",
    )
    return parser.parse_args(argv)


def run_headless(*, pieces: int, seed: int) -> int:
    print("以文本模式运行俄罗斯方块演示。")
    random = Random(seed)
    board = Board(random=random)
    if not board.spawn_piece():
        print("初始化方块失败。")
        return 1

    for index in range(pieces):
        print(f"\n第 {index + 1} 个方块：{board.current.tetromino.name}")
        print(_render_rows(board.as_rows()))
        board.hard_drop()
        if not board.spawn_piece():
            print("游戏结束，无法生成新的方块。")
            print(_render_rows(board.as_rows()))
            break

    print("\n最终状态：")
    print(_render_rows(board.as_rows()))
    print(
        f"得分: {board.score}  消除行数: {board.lines_cleared}  等级: {board.level}"
    )
    return 0


def _render_rows(rows: Sequence[Sequence[int]]) -> str:
    rendered = ["".join(HEADLESS_CELL_MAP.get(cell, " ?") for cell in row) for row in rows]
    return "\n".join(rendered)


def main() -> None:
    args = parse_args()
    if args.headless or not _can_use_curses():
        sys.exit(run_headless(pieces=args.pieces, seed=args.seed))

    try:
        curses.wrapper(run)
    except curses.error as exc:
        print(
            "无法启动 curses 界面 ({}). 改用文本模式演示。".format(exc),
            file=sys.stderr,
        )
        sys.exit(run_headless(pieces=args.pieces, seed=args.seed))


if __name__ == "__main__":
    main()
