from player import BasePlayer
from board import Board, Move
import random

class RandomPlayer(BasePlayer):
    '''
    A reference random player. Chooses a move at random.
    '''
    def __init__(self, player_id: int, name: str = "Random"):
        super().__init__(player_id, name)

    def choose_move(self, board: Board) -> Move:
        while True:
            # Get a list of all legal moves from the board
            moves = board.legal_moves()
            # Choose one move randomly
            move = random.choice(moves)
            if board.is_valid_move(move):
                # Return the chosen move
                return move

