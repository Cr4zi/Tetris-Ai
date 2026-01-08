import numpy as np
import random
from enum import Enum
from queue import Queue

class Hit(Enum):
    NO_HIT = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    ALL = 4
    WALL = 5

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

    def _insert_piece(self, x = None, y = None, val = 1):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                # self.board[y+row][x+col] ^= self.cur_piece[row][col]
                if self.cur_piece[row][col] == 1:
                    self.board[y + row][x + col] = val
                    

    def _remove_piece(self, x = None, y = None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[0])):
                if self.cur_piece[row][col] == 1 and self.board[y + row][x + col] > 0: # because it can be 1 or 2
                    self.board[y + row][x + col] = 0

    def can_draw(self, x, y, what):
        for row in range(len(self.cur_piece)):
            for col in range(len(self.cur_piece[row])):
                if self.cur_piece[row][col] == 1:
                    if what in (Hit.DOWN, Hit.ALL):
                        last_row = row == len(self.cur_piece) - 1 or self.cur_piece[row + 1][col] == 0
                        if last_row and self.board[y + row + 1][x + col] == 1:
                            return Hit.DOWN

                    if what in (Hit.LEFT, Hit.ALL):
                        left_column = col == 0 or self.cur_piece[row][col - 1] == 0
                        if left_column and self.board[y + row][x + col - 1] == 1:
                            return Hit.LEFT

                    if what in (Hit.RIGHT, Hit.ALL):
                        right_column = col == len(self.cur_piece[row]) - 1 or self.cur_piece[row][col + 1] == 0
                        if right_column and self.board[y + row][x + col + 1] == 1:
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
        self._remove_piece(x, y)
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
            self._remove_piece(x, y)
            self._insert_piece(x, y)

        return did_rotate

    def move_down_piece(self, draw_new=True):
        if self.can_draw(self.x, self.y, Hit.DOWN) == Hit.DOWN: 
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
        right = self.can_draw(self.x, self.y, Hit.RIGHT) 
        if right == Hit.RIGHT or right == Hit.WALL:
            return False

        self._remove_piece()
        self.x += 1
        self._insert_piece()
        return True

    def move_left_piece(self):
        left = self.can_draw(self.x, self.y, Hit.LEFT) 
        if left == Hit.LEFT or left == Hit.WALL:
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

    def _max_line_height(self):
        max_line_height = 0

        for i in range(2, 12):
            for j in range(20):
                if self.board[j][i] == 1:
                    max_line_height = max(max_line_height, 20 - j)
                    break

        return max_line_height

    def _full_rows(self):
        rows_cleared = 0
        for i in range(20):
            clear = True
            for j in range(len(self.board[i])):
                if self.board[i][j] == 0:
                    clear = False
        
            if clear:
                rows_cleared += 1
            
        return rows_cleared

    def _holes(self):
        holes = 0
        open_holes = 0

        for j in range(2, 12):
            blocks_found = False
            for i in range(20):
                if self.board[i][j] == 1:
                    blocks_found = True
                elif blocks_found:
                    if self.board[i][j - 1] == 0 and self.board[i][j - 2] == 0:
                        open_holes += 1
                        continue

                    if self.board[i][j + 1] == 0 and self.board[i][j + 2] == 0:
                        open_holes += 1
                        continue
                    holes += 1
                
        return holes, open_holes

    def _row_transitions(self):
        row = 0

        for i in range(20):
            for j in range(2, 12):
                if self.board[i][j] == 1 and self.board[i][j - 1] == 0:
                    row += 1
                if self.board[i][j] == 1 and self.board[i][j + 1] == 0:
                    row += 1
        return row

    def _col_transitions(self):
        col = 0

        for j in range(2, 12):
            for i in range(20):
                if self.board[i][j] == 1 and self.board[i - 1][j] == 0:
                    col += 1
                if self.board[i][j] == 1 and self.board[i + 1][j] == 0:
                    col += 1

        return col

    # bampiness is defined as the total difference between column heights
    def _bumpiness(self):
        bumpiness = 0
        previous_height = None 

        for i in range(2, 12):
            curr = 0
            for j in range(20):
                if self.board[j][i] == 1:
                    curr = 20 - j
                    break

            if previous_height is not None:
                bumpiness += abs(previous_height - curr)

            previous_height = curr

        return bumpiness

    def _total_height(self):
        total_height = 0
        for j in range(2, 12):
            for i in range(20):
                if self.board[i][j] == 1:
                    total_height += 20 - i
                    break
        return total_height
                

    def grade_board(self):
        # features at: https://inria.hal.science/hal-00926213/document page 4 + some of mine
        holes, open_holes = self._holes()
        bumpiness = self._bumpiness()
        row_transitions = self._row_transitions()
        col_transitions = self._col_transitions()
        max_height = self._max_line_height()
        full_rows = self._full_rows()

        score = (
            - 40.0 * holes
            - 20.0 * open_holes
            - 8.0 * bumpiness
            - 9.0 * row_transitions
            - 7.0 * col_transitions
            - 15.0 * max_height
            # - 2.0 * total_height
            + 50000.0 * full_rows
        )

        return score

    def every_possible_end_move(self, orig_x, orig_y):
        end_moves = []


        status = [[BFS_STATUS.DIDNT_VISIT for _ in range(14)] for _ in range(23)]
        q = Queue()
        x, y = orig_x, orig_y
        q.put((x, y))
        status[y][x] = BFS_STATUS.VISIT
        while not q.empty():
            x, y = q.get()

            if self.can_draw(x, y, Hit.DOWN) == Hit.NO_HIT and status[y + 1][x] == BFS_STATUS.DIDNT_VISIT:
                q.put((x, y + 1))
                status[y + 1][x] = BFS_STATUS.VISIT
            if self.can_draw(x, y, Hit.LEFT) == Hit.NO_HIT and status[y][x - 1] == BFS_STATUS.DIDNT_VISIT:
                q.put((x - 1, y))
                status[y][x - 1] = BFS_STATUS.VISIT
            if self.can_draw(x, y, Hit.RIGHT) == Hit.NO_HIT and status[y][x + 1] == BFS_STATUS.DIDNT_VISIT:
                q.put((x + 1, y))
                status[y][x + 1] = BFS_STATUS.VISIT

            if self.can_draw(x, y, Hit.DOWN) == Hit.DOWN:
                self._insert_piece(x, y)
                end_moves.append((x, y, self.grade_board()))
                self._remove_piece(x, y)

            status[y][x] = BFS_STATUS.FINISHED

        return end_moves

    def next(self):
        self.clear_up_lines()
        self.new_next_piece()
        self._insert_piece()

    def graded_moves(self):
        # SAVE STATE
        saved_board = self.board.copy()
        saved_piece = self.cur_piece.copy()
        saved_x, saved_y = self.x, self.y
        saved_index = self.cur_piece_index

        orig_x = self.x
        orig_y = self.y

        end_moves = {0: [], 1: [], 2: [], 3: []}

        # rotation 0
        self._remove_piece(orig_x, orig_y)
        end_moves[0] = self.every_possible_end_move(orig_x, orig_y)
        self._insert_piece(orig_x, orig_y)

        # rotations 1–3
        for rot in range(1, 4):
            self._remove_piece(orig_x, orig_y)
            self.cur_piece = np.rot90(self.cur_piece, -1)
            end_moves[rot] = self.every_possible_end_move(orig_x, orig_y)
            self._insert_piece(orig_x, orig_y)

        # RESTORE STATE
        self.board = saved_board
        self.cur_piece = saved_piece
        self.x, self.y = saved_x, saved_y
        self.cur_piece_index = saved_index

        return end_moves
    
    def agent_random_move(self):
        orig_x = self.x
        orig_y = self.y

        self._remove_piece(orig_x, orig_y)
        end_moves = self.graded_moves()
        print(end_moves)

        # We assume there has to be at least one move
        best_move = end_moves[0][0]
        rotation = 0
        for rot in range(4):
            for move in end_moves[rot]:
                if move[2] > best_move[2]:
                    best_move = move
                    rotation = rot

        x, y = best_move[0], best_move[1]
        for _ in range(rotation):
            self.cur_piece = np.rot90(self.cur_piece, -1)

        if self.cur_piece_index == 0:
            print(f"Chose {x}, {y}")

        self._insert_piece(x, y)

        self.next()

