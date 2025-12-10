import numpy as np
import random
from enum import Enum

class Hit(Enum):
    NO_HIT = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    ALL = 4

class Tetris:
    def __init__(self):
        self._init_game()
        self.pieces = [[[0,1,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]], # line
                                [[1,1], [1,1]], # square
                                [[0,1,0], [1,1,0], [0,1,0]], # t shaped
                                [[0,0,1], [0,1,1], [0,1,0]], # S shaped
                                [[1,0,0], [1,1,0], [0,1,0]], # Reversed S
                                [[0,1,0], [0,1,0], [0,1,1]], # L 
                                [[0,1,0], [0,1,0], [1,1,0]], # Reversed L
                                ]

        self.x = 4
        self.y = 0

        self.cur_piece_index = random.randint(0, len(self.pieces)-1)
        self.cur_piece = np.array(self.pieces[self.cur_piece_index])
        self.next_piece_index = random.randint(0, len(self.pieces)-1)
        self.next_piece = np.array(self.pieces[self.next_piece_index])
        self._insert_piece()


    def _init_game(self):
        self.board = [[1 if i == 0 or i == 1 or i == 12 or i == 13 else 0 for i in range(14)] for _ in range(20)]
        self.board.append([1 for _ in range(14)]) # padding down
        self.board.append([1 for _ in range(14)]) # padding down
        self.board = np.array(self.board)

    def _insert_piece(self):
        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                self.board[self.y+row][self.x+col] ^= self.cur_piece[row][col]

    def _remove_piece(self):
        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                if self.cur_piece[row][col] == 1:
                    self.board[self.y+row][self.x+col] = 0

    def can_draw(self, x, y, what):
        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                if self.cur_piece[row][col] != 1:
                    continue

                if (what == Hit.DOWN or what == Hit.ALL) and (row == len(self.cur_piece) - 1 or self.cur_piece[row + 1][col] == 0):
                    if self.board[row + y][col + x] == 1:
                        return Hit.DOWN

                if (what == Hit.LEFT or what == Hit.ALL) and (col == 0 or self.cur_piece[row][col - 1] == 0):
                    if self.board[row + y][col + x] == 1:
                        return Hit.LEFT

                if (what == Hit.RIGHT or what == Hit.ALL) and (col == len(self.cur_piece[0]) - 1 or self.cur_piece[row][col + 1] == 0):
                    if self.board[row + y][col + x] == 1:
                        return Hit.RIGHT

        return Hit.NO_HIT

    def clear_up_lines(self):
        row = len(self.board) - 3
        while row != 0:
            isRowFull = True 
            for col in range(1, len(self.board[row]) - 1):
                if self.board[row][col] == 0:
                    isRowFull = False 

            if isRowFull:
                for row_idx in range(row, 0, -1):
                    for col in range(1, len(self.board[row_idx]) - 1):
                        self.board[row_idx][col] = self.board[row_idx - 1][col]
                row += 1

            row -= 1
                
    
    def rotate_piece(self):
        if self.cur_piece_index == 1: # if square don't do anything
            return False

        did_rotate = True
        self.old_piece = self.cur_piece
        self._remove_piece()
        self.cur_piece = np.rot90(self.cur_piece, -1)
        if self.can_draw(self.x, self.y, Hit.ALL) != Hit.NO_HIT:
            self.cur_piece = self.old_piece
            did_rotate = False

        self._insert_piece()
        return did_rotate
        

    def move_down_piece(self, draw_new=True):
        if self.can_draw(self.x, self.y+1, Hit.DOWN) == Hit.DOWN: 
            if draw_new:
                self.clear_up_lines()
                self.new_next_piece()
                self._insert_piece()
                return False
            else:
                return False

        self._remove_piece()
        self.y += 1
        self._insert_piece()
        return True

    def move_right_piece(self):
        if self.can_draw(self.x + 1, self.y, Hit.RIGHT) == Hit.RIGHT:
            return False

        self._remove_piece()
        self.x += 1
        self._insert_piece()
        return True

    def move_left_piece(self):
        if self.can_draw(self.x - 1, self.y, Hit.LEFT) == Hit.LEFT:
            return False

        self._remove_piece()
        self.x -= 1
        self._insert_piece()
        return True

    def new_next_piece(self):
        self.x = 4
        self.y = 0

        self.cur_piece_index = self.next_piece_index
        self.cur_piece = np.array(self.pieces[self.cur_piece_index])
        self.next_piece_index = random.randint(0, len(self.pieces)-1)
        self.next_piece = np.array(self.pieces[self.next_piece_index])

    def agent_random_move(self):
        pass

