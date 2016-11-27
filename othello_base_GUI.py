import othello_base as ob
import pygame
import time
from multiprocessing import Process, Value

BOARD_X0 = 290
BOARD_Y0 = 10
SQUARE_WIDTH = 70


class OthelloGUI(ob.OthelloBase):

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))

        self.board_image = pygame.image.load("othello.png")
        black_piece_image = pygame.image.load("square-black.png").convert()
        black_piece_images = [pygame.transform.scale(black_piece_image, (10 + 10 * i, 10 + 10 * i)) for i in range(7)]
        white_piece_image = pygame.image.load("square-white.png").convert()
        white_piece_images = [pygame.transform.scale(white_piece_image, (10 + 10 * i, 10 + 10 * i)) for i in range(7)]
        self.player_images = {ob.BLACK: black_piece_images,
                              ob.WHITE: white_piece_images}
        white_sound = pygame.mixer.Sound("gem_ping_A.wav")
        black_sound = pygame.mixer.Sound("gem_ping_B.wav")
        self.player_sounds = {ob.BLACK: black_sound,
                              ob.WHITE: white_sound}
        self.flip_sound = pygame.mixer.Sound("flip2.wav")

        self.score_font = pygame.font.SysFont("charter", size=60, bold=True)
        self.name_font = pygame.font.SysFont("charter", size=30, bold=False)

    def idx2rc(self, idx):
        return(idx//10, idx%10)

    def draw_move(self, move, player, board, animate = True):
        (row, col) = self.idx2rc(move)
        putX = BOARD_X0 + col * SQUARE_WIDTH
        putY = BOARD_Y0 + row * SQUARE_WIDTH
        if animate:
            for (d,img) in zip(range(30,-1,-5),self.player_images[player]):
                self.screen.blit(img, (putX+d, putY+d, SQUARE_WIDTH-2*d, SQUARE_WIDTH-2*d))
                pygame.display.update(pygame.Rect(putX, putY, SQUARE_WIDTH-2*d, SQUARE_WIDTH-2*d))
        else:
            self.screen.blit(self.player_images[player][-1], (putX, putY, SQUARE_WIDTH, SQUARE_WIDTH))
            pygame.display.flip()

    def draw_flip(self, move: object, player: object, board: object, update_screen = True) -> object:
        (row, col) = self.idx2rc(move)
        putX = BOARD_X0 + col * SQUARE_WIDTH
        putY = BOARD_Y0 + row * SQUARE_WIDTH

        img = self.player_images[player][-1]
        self.screen.blit(img, (putX, putY, SQUARE_WIDTH, SQUARE_WIDTH))
        if update_screen:
            pygame.display.update(pygame.Rect(putX, putY, SQUARE_WIDTH, SQUARE_WIDTH))

    def make_move(self, move, player, board, silent = True):
        """Update the board to reflect the move by the specified player."""
        board[move] = player
        if not silent:
            self.draw_move(move, player, board)
            self.player_sounds[player].play()
        for d in ob.DIRECTIONS:
            self.make_flips(move, player, board, d, silent)
        return board

    def make_flips(self, move, player, board, direction, silent = True):
        """Flip pieces in the given direction as a result of the move by player."""
        bracket = self.find_bracket(move, player, board, direction)
        if not bracket:
            return
        square = move + direction
        while square != bracket:
            board[square] = player
            if not silent:
                self.draw_flip(square, player, board)
                self.flip_sound.play()
            square += direction
            #print(direction, player, move)

    def count_up(self, board, player):
        return len([i for i in board if i == player])

    def count_blacks(self, board):
        return self.count_up(board, ob.BLACK)

    def count_whites(self, board):
        return self.count_up(board, ob.WHITE)

    def text_objects(self, text, font):
        textSurface = font.render(text, True, (255, 255, 240))
        return textSurface, textSurface.get_rect()

    def update_score(self, board):
        score_w, rect_w = self.text_objects(str(self.count_whites(board)), self.score_font)
        score_b, rect_b = self.text_objects(str(self.count_blacks(board)), self.score_font)
        rect_b.midtop = 190, 150
        rect_w.midtop = 1090, 150
        # pygame.draw.rect(screen, (180, 180, 180), rect_b)
        # pygame.draw.rect(screen, (180, 180, 180), rect_w)
        self.screen.blit(self.board_image, (140, 70), (140, 70, 100, 150))
        self.screen.blit(self.board_image, (140, 70), (140, 70, 100, 150))
        self.screen.blit(self.board_image, (1050, 70), (1050, 70, 100, 150))
        self.screen.blit(score_w, rect_w)
        self.screen.blit(score_b, rect_b)
        pygame.display.flip()

    def show_player_names(self, black = "Black", white = "White"):
        name_b, rect_b = self.text_objects(black, self.name_font)
        name_w, rect_w = self.text_objects(white, self.name_font)
        rect_b.midbottom = 190, 60
        rect_w.midbottom = 1090,60
        self.screen.blit(name_w, rect_w)
        self.screen.blit(name_b, rect_b)

    def post_winner(self, winner):
        if winner=="Tie":
            winner = "Tie Game!"
        else:
            winner = winner + " Wins!"
        text, rect = self.text_objects(winner, self.name_font)
        rect.bottomright = 1260, 700
        self.screen.blit(text, rect)
        pygame.display.flip()

    def setup_board(self, board, black_name, white_name):
        imagerect = self.board_image.get_rect()
        self.screen.blit(self.board_image, imagerect)

        self.draw_flip(44, ob.WHITE, board, update_screen=False)
        self.draw_flip(55, ob.WHITE, board, update_screen=False)
        self.draw_flip(45, ob.BLACK, board, update_screen=False)
        self.draw_flip(54, ob.BLACK, board, update_screen=False)
        self.show_player_names(black_name, white_name)
        pygame.display.flip()


    def play(self, black_strategy, white_strategy, black_name, white_name):
        """Play a game of Othello and return the final board and score."""
        board = self.initial_board()
        self.setup_board(board, black_name, white_name)
        self.update_score(board)

        player = ob.BLACK
        strategy = lambda who: black_strategy if who == ob.BLACK else white_strategy
        start_time = time.time()
        while player is not None:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mousepos = pygame.mouse.get_pos()
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    break

            #move = self.get_move(strategy(player), player, board)
            best_shared = Value("i", -1)
            best_shared.value = 11
            p = Process(target=self.get_move, args=(strategy(player), player, board, best_shared))
            p.start()
            t1 = time.time()
            print("starting %i" % p.pid, "*"*50, t1-start_time)
            p.join(1.5)
            move = best_shared.value
            p.terminate()
            t2 = time.time()
            print("Killing  %i" % p.pid,"&"*50, t2-t1)

            #while p.is_alive():
                #pass
            t3 = time.time()
            print("Killed", "-"*60, t3-t2)
            print("move = ", move, "best = ", best_shared.value)
            self.make_move(move, player, board, silent = False)
            self.update_score(board)
            # print(self.print_board(board))
            player = self.next_player(board, player)

        black_score = self.score(ob.BLACK, board)
        if black_score > 0:
            winner = black_name
        elif black_score < 0:
            winner = white_name
        else:
            winner = "TIE"

        self.post_winner(winner)
        return board, self.score(ob.BLACK, board)

    def end_wait(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousepos = pygame.mouse.get_pos()
            elif event.type == pygame.QUIT:
                pygame.quit()
                break



