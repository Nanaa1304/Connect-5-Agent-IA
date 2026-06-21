from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from board import Board, Move

if TYPE_CHECKING:
    from game import PygameUI

# =========================
# Players
# =========================

class BasePlayer(ABC):
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        self.opp_id = 1 if player_id == 2 else 2

    @abstractmethod
    def choose_move(self, board: Board) -> Move:
        """
        Return a move (column). UI is provided for human interaction.
        """
        raise NotImplementedError


class HumanPlayer(BasePlayer):
    def __init__(self, player_id: int, name: str, ui: "PygameUI"):
        super().__init__(player_id, name)
        self.ui = ui

    def choose_move(self, board: Board) -> Move:
        # Wait for a click on a valid column
        while True:
            col = self.ui.wait_for_human_column_click(board)
            if col is None:
                continue
            if board.is_valid_move(col):
                return Move(col)
            self.ui.flash_message(f"Column {col} is full!", seconds=0.6)

