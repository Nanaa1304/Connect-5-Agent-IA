#!/usr/bin/env python3
from __future__ import annotations
import math
import sys
import signal
import time
from typing import List, Optional, Tuple
from functools import partial

import pygame
from player import HumanPlayer, BasePlayer
from board import Board

import argparse
import importlib


class PygameUI:
    def __init__(self, board: Board, cell_size: int = 52, margin: int = 20, header_h: int = 90):
        pygame.init()
        pygame.display.set_caption(f"Connect-5 ({board.H}x{board.W})")

        self.board = board
        self.cell = cell_size
        self.margin = margin
        self.header_h = header_h

        self.W_px = margin * 2 + board.W * cell_size
        self.H_px = header_h + margin * 2 + board.H * cell_size
        self.screen = pygame.display.set_mode((self.W_px, self.H_px))

        self.font = pygame.font.SysFont(None, 24)
        self.font_big = pygame.font.SysFont(None, 32)

        self.status_line = ""
        self.flash_until = 0.0
        self.flash_text = ""

    def set_status(self, text: str) -> None:
        self.status_line = text

    def flash_message(self, text: str, seconds: float = 0.8) -> None:
        self.flash_text = text
        self.flash_until = time.perf_counter() + seconds

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        x = self.margin + col * self.cell
        y = self.header_h + self.margin + row * self.cell
        return pygame.Rect(x, y, self.cell, self.cell)

    def _col_from_mouse(self, mx: int, my: int) -> Optional[int]:
        # columns only if click is in the board area
        if my < self.header_h + self.margin or my >= self.header_h + self.margin + self.board.H * self.cell:
            return None
        if mx < self.margin or mx >= self.margin + self.board.W * self.cell:
            return None
        return (mx - self.margin) // self.cell

    def pump_quit(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

    def wait_for_human_column_click(self, board: Board) -> Optional[int]:
        while True:
            self.pump_quit()
            self.draw(board)

            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                col = self._col_from_mouse(mx, my)
                return int(col) if col is not None else None

    def draw(self, board: Board, winner: int = 0, current_player: Optional[BasePlayer] = None) -> None:
        self.screen.fill((25, 25, 28))

        # Header
        title = f"Connect-5 ({board.H}x{board.W}, gravity)"
        title_surf = self.font_big.render(title, True, (235, 235, 240))
        self.screen.blit(title_surf, (self.margin, 12))

        if current_player is not None:
            turn_surf = self.font.render(f"Turn: {current_player.name} (P{current_player.player_id})", True, (220, 220, 220))
            self.screen.blit(turn_surf, (self.margin, 50))

        # Status line
        status = self.status_line
        if time.perf_counter() < self.flash_until:
            status = self.flash_text
        status_surf = self.font.render(status, True, (210, 210, 210))
        self.screen.blit(status_surf, (self.margin, 70))

        # Board background
        board_rect = pygame.Rect(
            self.margin,
            self.header_h + self.margin,
            board.W * self.cell,
            board.H * self.cell,
        )
        pygame.draw.rect(self.screen, (40, 40, 48), board_rect, border_radius=10)

        # Grid + pieces
        for r in range(board.H):
            for c in range(board.W):
                rect = self._cell_rect(r, c)
                pygame.draw.rect(self.screen, (60, 60, 72), rect, width=1)

                v = board.grid[r][c]
                if v == 0:
                    continue
                if v == 1:
                    color = (230, 80, 70)
                else:
                    color = (80, 170, 240)

                cx = rect.x + rect.w // 2
                cy = rect.y + rect.h // 2
                radius = int(self.cell * 0.38)
                pygame.draw.circle(self.screen, color, (cx, cy), radius)

        # Winner banner
        if winner != 0:
            msg = "Draw!" if winner == -1 else f"Player {winner} wins!"
            banner = self.font_big.render(msg, True, (250, 250, 250))
            self.screen.blit(banner, (self.margin + 240, 32))

        pygame.display.flip()


class Game:
    def __init__(self, board: Board, ui: PygameUI, p1: BasePlayer, p2: BasePlayer):
        self.board = board
        self.ui = ui
        self.players = {1: p1, 2: p2}
        self.current_id = 1

    def run(self) -> None:
        winner = 0
        while True:
            current = self.players[self.current_id]
            if self.ui is not None:
                self.ui.pump_quit()
                self.ui.draw(self.board, winner=0, current_player=current)

            status = None

            terminal, w = self.board.terminal_status()
            if terminal:
                if w == 0:
                    winner = -1
                    status = "Game over: draw. Close window to exit."
                else:
                    winner = w
                    status = f"Game over: Player {winner} wins. Close window to exit."
                # keep showing final board until quit
                if self.ui is not None:
                    while True:
                        self.ui.pump_quit()
                        self.ui.draw(self.board, winner=winner, current_player=current)
                        pygame.time.delay(30)
                else:
                    return
            mv_fn = partial(current.choose_move, self.board.clone())
            try:
                mv = execute_with_limits(mv_fn, 500000, 1000000)
            except TimeoutError as e:
                mv = None
            lost = False

            if mv is None:
                lost = True
                # illegal move => immediate loss
                loser = self.current_id
                winner = 1 if loser == 2 else 2
                status = f"P{loser} took too long. P{winner} wins. Close window to exit."
            elif not self.board.is_valid_move(mv.col):
                lost = True
                # illegal move => immediate loss
                loser = self.current_id
                winner = 1 if loser == 2 else 2
                status = f"Illegal move by P{loser}. P{winner} wins. Close window to exit."

            if lost and self.ui is not None:
                self.ui.set_status(status)
                while True:
                    self.ui.pump_quit()
                    self.ui.draw(self.board, winner=winner, current_player=current)
                    pygame.time.delay(30)
            elif lost:
                return

            self.board.apply_move(mv.col, self.current_id)
            self.current_id = 1 if self.current_id == 2 else 2

def load_class(full_name: str):
    module_name, class_name = full_name.rsplit(".", 1)
    module = importlib.import_module(module_name)
    return getattr(module, class_name)

def build_player(player_id: int, player_label: str, spec: str, ui):
    cls = load_class(spec)

    if issubclass(cls, HumanPlayer):
        return cls(player_id, player_label, ui)
    elif issubclass(cls, BasePlayer):
        return cls(player_id, player_label)

def handle_timeout(signum, frame):
    # This exception is raised when either timer expires
    raise TimeoutError("Limit reached: Function interrupted!")

import os

def execute_with_limits(func, cpu_ms=500, wall_ms=5000):

    # Windows ne supporte pas SIGALRM
    if os.name == "nt":
        return func()

    signal.signal(signal.SIGALRM, handle_timeout)
    signal.signal(signal.SIGVTALRM, handle_timeout)

    try:
        signal.setitimer(signal.ITIMER_REAL, wall_ms / 1000.0)
        signal.setitimer(signal.ITIMER_VIRTUAL, cpu_ms / 1000.0)
        return func()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.setitimer(signal.ITIMER_VIRTUAL, 0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p1", type=str, default="player.HumanPlayer")
    parser.add_argument("--p2", type=str, default="player.HumanPlayer")
    args = parser.parse_args()

    board = Board(width=16, height=16, connect_k=5)
    ui = PygameUI(board, cell_size=32, margin=18, header_h=90)

    p1 = build_player(1, "Player 1", args.p1, ui)
    p2 = build_player(2, "Player 2", args.p2, ui)

    game = Game(board, ui, p1, p2)
    game.run()

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
