import numpy as np
import random
from enum import Enum
from queue import Queue
import time

class Hit(Enum):
    NO_HIT = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    ALL = 4

class BFS_STATUS(Enum):
    DIDNT_VISIT = 0
    VISIT = 1
    FINISHED = 2

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

        self.x = 6
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

    def _insert_piece(self, x = None, y = None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                # self.board[y+row][x+col] ^= self.cur_piece[row][col]
                if self.cur_piece[row][col] == 1:
                    self.board[y + row][x + col] = 1
                    

    def _remove_piece(self, x = None, y = None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                if self.cur_piece[row][col] == 1:
                    self.board[y + row][x + col] = 0

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
                

    def can_rotate(self, x = None, y = None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        if self.cur_piece_index == 1: # if square don't do anything
            return False

        did_rotate = True
        self.old_piece = self.cur_piece
        self._remove_piece()
        self.cur_piece = np.rot90(self.cur_piece, -1)
        if self.can_draw(x, y, Hit.ALL) != Hit.NO_HIT:
            self.cur_piece = self.old_piece
            did_rotate = False

        return did_rotate
    
    def rotate_piece(self, x = None, y = None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        did_rotate = self.can_rotate(x, y)
        if did_rotate:
            self._remove_piece()
            self._insert_piece()

        return did_rotate

    def move_down_piece(self, draw_new=True):
        if self.can_draw(self.x, self.y+1, Hit.DOWN) == Hit.DOWN: 
            if draw_new:
                self.clear_up_lines()
                self.new_next_piece()
                self._insert_piece()
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
        self.x = 6
        self.y = 0

        self.cur_piece_index = self.next_piece_index
        self.cur_piece = np.array(self.pieces[self.cur_piece_index])
        self.next_piece_index = random.randint(0, len(self.pieces)-1)
        self.next_piece = np.array(self.pieces[self.next_piece_index])

    def grade_board(self):
        FULL_ROW_SCORE = 10
        HOLE_PENALTY = -5
        HEIGHT_PENALTY = -0.5
        BUMPINESS_PENALTY = -0.5

        grade = 0
        heights = [0] * 10

        # Heights + holes
        for col in range(2, 12):
            block_found = False
            for row in range(1, 20):
                if self.board[row][col] == 1:
                    if not block_found:
                        heights[col - 2] = 20 - row
                        block_found = True
                    else:
                        continue
                elif block_found:
                    grade += HOLE_PENALTY

        # Full rows
        for row in range(1, 20):
            if all(self.board[row][col] == 1 for col in range(2, 12)):
                grade += FULL_ROW_SCORE

        # Height penalty
        grade += HEIGHT_PENALTY * sum(heights)

        # Bumpiness
        for i in range(9):
            grade += BUMPINESS_PENALTY * abs(heights[i] - heights[i + 1])

        return grade

    '''
    Function that finds every possible end move
    @param orig_x - original x position of piece
    @param orig_y - original y position of the piece
    @param rotation - how many rotation we have done
    @return every possible end move and its rotation
    '''
    def every_possible_end_move(self, orig_x, orig_y):
        end_moves = []

        self._remove_piece(orig_x, orig_y)
        
        status = [[BFS_STATUS.DIDNT_VISIT for _ in range(10)] for _ in range(20)]
        q = Queue()

        element = (orig_x, orig_y)
        x, y = element
        q.put(element)
        while not q.empty():
            status[y][x] = BFS_STATUS.VISIT # updating that we finished
            element = q.get()
            x, y = element
        
            down_result = self.can_draw(x, y + 1, Hit.DOWN)
            
            if y < 20 and down_result == Hit.NO_HIT and status[y + 1][x] == BFS_STATUS.DIDNT_VISIT:
                q.put((x, y + 1))
                status[y + 1][x] = BFS_STATUS.VISIT
            if x > 0 and self.can_draw(x - 1, y, Hit.LEFT) == Hit.NO_HIT and status[y][x - 1] == BFS_STATUS.DIDNT_VISIT:
                q.put((x - 1, y))
                status[y][x - 1] = BFS_STATUS.VISIT
            if x < 9 and self.can_draw(x + 1, y, Hit.RIGHT) == Hit.NO_HIT and status[y][x + 1] == BFS_STATUS.DIDNT_VISIT:
                q.put((x + 1, y))
                status[y][x + 1] = BFS_STATUS.VISIT

            if down_result == Hit.DOWN and status[y + 1][x] == BFS_STATUS.DIDNT_VISIT:
                self._insert_piece(x, y)
                end_moves.append((x, y, self.grade_board()))
                self._remove_piece(x, y)

            status[y][x] = BFS_STATUS.FINISHED # updating that we finished the current

        self._insert_piece(orig_x, orig_y)
        return end_moves
            

    def agent_random_move(self):
        orig_x = self.x
        orig_y = self.y
        end_moves = {0: [], 1: [], 2: [], 3: []} 
        
        end_moves[0] = self.every_possible_end_move(orig_x, orig_y)
        for rot in range(1, 4):
            if self.rotate_piece(orig_x, orig_y):
                moves = self.every_possible_end_move(orig_x, orig_y)

                for move in moves:
                    end_moves[rot].append(move)


        # We assume there has to be at least one move
        best_move = end_moves[0][0]
        rotation = 0
        for rot in range(4):
            for move in end_moves[rot]:
                if move[2] > best_move[2]:
                    best_move = move
                    rotation = rot

        for _ in range(rotation):
            self.rotate_piece(orig_x, orig_y)

        x, y = best_move[0], best_move[1]
        for _ in range(rotation):
            self.rotate_piece(orig_x, orig_y)

        self._remove_piece(orig_x, orig_y)
        self._insert_piece(x, y)

        self.clear_up_lines()
        self.new_next_piece()
        self._insert_piece()

