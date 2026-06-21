from typing import List, Optional, Tuple
from dataclasses import dataclass

@dataclass(frozen=True)
class Move:
    col: int


class Board:
    """
    Gravity board:
    - grid[r][c] with r=0 at top, r=H-1 at bottom
    - cells: 0 empty, 1 player1, 2 player2
    """
    def __init__(self, width: int = 12, height: int = 12, connect_k: int = 5):
        self.W = width
        self.H = height
        self.K = connect_k
        self.grid: List[List[int]] = [[0 for _ in range(self.W)] for _ in range(self.H)]
        self.heights: List[int] = [self.H - 1 for _ in range(self.W)]  # next free row per col from bottom up
        self.last_move: Optional[Tuple[int, int]] = None  # (row, col)

    def clone(self) -> "Board":
        '''
        Clones the board and returns a copy
        '''
        b = Board(self.W, self.H, self.K)
        b.grid = [row[:] for row in self.grid]
        b.heights = self.heights[:]
        b.last_move = self.last_move
        return b

    def is_valid_move(self, col: int | Move) -> bool:
        '''
        Returns True if a move is valid, False otherwise
        '''
        if isinstance(col, Move):
            col = col.col
        return 0 <= col < self.W and self.heights[col] >= 0

    def legal_moves(self) -> List[Move]:
        '''
        Returns a list of valid moves
        '''
        return [Move(c) for c in range(self.W) if self.is_valid_move(c)]

    def apply_move(self, col: int, player_id: int) -> Tuple[int, int]:
        '''
        Applies a move to the board returns the coordinates of the new piece
        '''
        if not self.is_valid_move(col):
            raise ValueError(f"Invalid move: col={col}")
        row = self.heights[col]
        self.grid[row][col] = player_id
        self.heights[col] -= 1
        self.last_move = (row, col)
        return row, col

    def undo_move(self, col: int) -> None:
        '''
        Revert last piece in that column
        '''
        row = self.heights[col] + 1
        if row < 0 or row >= self.H:
            raise ValueError("Cannot undo: column state invalid")
        self.grid[row][col] = 0
        self.heights[col] += 1
        self.last_move = None

    def is_full(self) -> bool:
        '''
        Check if the board has been filled (draw)
        '''
        return all(h < 0 for h in self.heights)

    def check_winner(self) -> int:
        """
        Returns:
          0 no winner
          1 player 1 wins
          2 player 2 wins
        """
        # For speed, you could check only around last_move; here we scan all directions safely.
        K = self.K
        g = self.grid
        H, W = self.H, self.W

        def in_bounds(r: int, c: int) -> bool:
            return 0 <= r < H and 0 <= c < W

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(H):
            for c in range(W):
                p = g[r][c]
                if p == 0:
                    continue
                for dr, dc in directions:
                    rr, cc = r, c
                    count = 0
                    while in_bounds(rr, cc) and g[rr][cc] == p:
                        count += 1
                        if count >= K:
                            return p
                        rr += dr
                        cc += dc
        return 0

    def terminal_status(self) -> Tuple[bool, int]:
        """
        Returns (is_terminal, winner):
          winner in {0,1,2} where 0 means draw or no winner.
        """
        w = self.check_winner()
        if w != 0:
            return True, w
        if self.is_full():
            return True, 0
        return False, 0
