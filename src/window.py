from tetris import Tetris
import pygame

class Window:
    def __init__(self):
        self.RES = (1000,1000)
        self.game_agent = Tetris()
        self.AGENT = (50, 450) # where the board starts and ends

        self.game_player = Tetris()
        self.PLAYER = (550, 950) # where the board starts and ends

        self.BLOCK_SIZE = 40 # 40x40 pixels

        self.HEIGHT = 100 # we'll start at y=100 up to y=900


        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 30)
        self.screen = pygame.display.set_mode(self.RES)
        self.clock = pygame.time.Clock()

    def draw_game(self):
        for row in range(len(self.game_agent.board) - 2):
            for col in range(2, len(self.game_agent.board[0]) - 2):
                # Agent Board
                if self.game_agent.board[row][col] == 0:
                    pygame.draw.rect(self.screen, (0,0,0), (self.AGENT[0] + self.BLOCK_SIZE*(col-2), self.HEIGHT + self.BLOCK_SIZE*row, self.BLOCK_SIZE, self.BLOCK_SIZE), 1)
                else:
                    pygame.draw.rect(self.screen, (255,0,0), (self.AGENT[0] + self.BLOCK_SIZE*(col-2), self.HEIGHT + self.BLOCK_SIZE*row, self.BLOCK_SIZE, self.BLOCK_SIZE), 0)

                # Player board
                if self.game_player.board[row][col] == 0:
                    pygame.draw.rect(self.screen, (0,0,0), (self.PLAYER[0] + self.BLOCK_SIZE*(col-2), self.HEIGHT + self.BLOCK_SIZE*row, self.BLOCK_SIZE, self.BLOCK_SIZE), 1)
                else:
                    pygame.draw.rect(self.screen, (255,0,0), (self.PLAYER[0] + self.BLOCK_SIZE*(col-2), self.HEIGHT + self.BLOCK_SIZE*row, self.BLOCK_SIZE, self.BLOCK_SIZE), 0)
    
    def draw_text(self):
        agent_text = self.font.render("Agent", True, (0,0,0))
        player_text = self.font.render("Player", True, (0,0,0))
        self.screen.blit(agent_text, ((self.AGENT[1] - self.AGENT[0]) / 2, 50))
        self.screen.blit(player_text, ((self.PLAYER[1] - self.PLAYER[0]) / 2 + 500, 50))
                
    def start(self):
        running = True
        MOVEEVENT, t = pygame.USEREVENT+1, 500
        AGENTEVENT, t2 = pygame.USEREVENT+2, 1000

        pygame.time.set_timer(MOVEEVENT, t)
        pygame.time.set_timer(AGENTEVENT, t2)
        while running:
            self.screen.fill("white")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.game_player.rotate_piece()
                    elif event.key == pygame.K_a:
                        self.game_player.move_left_piece()
                    elif event.key == pygame.K_d:
                        self.game_player.move_right_piece()
                    elif event.key == pygame.K_s:
                        self.game_player.move_down_piece()

                if event.type == MOVEEVENT:
                    self.game_player.move_down_piece()
                if event.type == AGENTEVENT:
                    self.game_agent.agent_random_move()

            self.draw_game()
            self.draw_text()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

