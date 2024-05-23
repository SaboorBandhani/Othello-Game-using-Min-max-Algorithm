import pygame
import sys
import math
import copy

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 550
HEIGHT = 550
ROWS = 8
COLS = 8
SQUARE_SIZE = (HEIGHT // ROWS)
EMPTY = 0
BLACK = -1
WHITE = 1

# Colors
black = (10, 10, 10)
white = (255, 255, 255)
red = (255, 0, 0)

# Initialize the screen
screen = pygame.display.set_mode((WIDTH + 200, HEIGHT))
pygame.display.set_caption("Othello")

# Create the initial board state
board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
board[3][3] = 1
board[3][4] = -1
board[4][3] = -1
board[4][4] = 1

# Load images
bg_img = pygame.Surface((WIDTH + 140, HEIGHT))
bg_img.fill((24, 78, 51))
game_over_img = pygame.image.load("go_bg.png")
game_over_img = pygame.transform.scale(game_over_img, (370, 170))
board_img = pygame.image.load("board.jpg")
board_img = pygame.transform.scale(board_img, (WIDTH, HEIGHT))
white_disc_img = pygame.image.load("white_disc.png")
white_disc_img = pygame.transform.scale(white_disc_img, (SQUARE_SIZE, SQUARE_SIZE))
black_disc_img = pygame.image.load("black_disc.png")
black_disc_img = pygame.transform.scale(black_disc_img, (SQUARE_SIZE, SQUARE_SIZE))



# Function to draw the board
def draw_board():
    screen.blit(bg_img, (0, 0))
    screen.blit(board_img, (0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == 1:
                screen.blit(white_disc_img, ((col * SQUARE_SIZE), (row * SQUARE_SIZE)))
            elif board[row][col] == -1:
                screen.blit(black_disc_img, ((col * SQUARE_SIZE), (row * SQUARE_SIZE)))


# Function to check if a move is valid
def is_valid_move(row, col, color):
    if board[row][col] != 0:
        return False
    for drow in range(-1, 2):
        for dcol in range(-1, 2):
            if drow == 0 and dcol == 0:
                continue
            r, c = row + drow, col + dcol
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == -color:
                r += drow
                c += dcol
            if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == color and (r - row != drow or c - col != dcol):
                return True
    return False


# Function to flip discs
def flip_discs(row, col, color):
    for drow in range(-1, 2):
        for dcol in range(-1, 2):
            if drow == 0 and dcol == 0:
                continue
            r, c = row + drow, col + dcol
            discs_to_flip = []
            while 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == -color:
                discs_to_flip.append((r, c))
                r += drow
                c += dcol
            if 0 <= r < ROWS and 0 <= c < COLS and board[r][c] == color and discs_to_flip:
                for flip_row, flip_col in discs_to_flip:
                    board[flip_row][flip_col] = color


# Function to make a move
def make_move(row, col, color):
    if not is_valid_move(row, col, color):
        return False
    board[row][col] = color
    flip_discs(row, col, color)
    return True


# Function to get the score
def get_score():
    white_score = sum(row.count(1) for row in board)
    black_score = sum(row.count(-1) for row in board)
    return white_score, black_score


# Function to check if the game is over
def is_game_over(board):
    # Check for a full board
    if all(all(cell != EMPTY for cell in row) for row in board):
        return True

    # Check for no valid moves for any one player
    elif not any(is_valid_move(row, col, BLACK) for row in range(ROWS) for col in range(COLS)) and \
            not any(is_valid_move(row, col, WHITE) for row in range(ROWS) for col in range(COLS)):
        return True

    return False


# Function to evaluate board
def evaluate_board(board):
    black_count = sum(row.count(BLACK) for row in board)
    white_count = sum(row.count(WHITE) for row in board)
    return black_count - white_count
    

# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, maximizing_player, alpha, beta):
    if depth == 0 or is_game_over(board):
        return evaluate_board(board)
    if maximizing_player:
        max_eval = float("-inf")
        for row in range(ROWS):
            for col in range(COLS):
                if is_valid_move(row, col, BLACK):
                    board_copy = [row[:] for row in board]
                    make_move(row, col, BLACK)
                    eval = minimax(board, depth - 1, False, alpha, beta)
                    board = [row[:] for row in board_copy]
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return max_eval
    else:
        min_eval = float("inf")
        for row in range(ROWS):
            for col in range(COLS):
                if is_valid_move(row, col, WHITE):
                    board_copy = [row[:] for row in board]
                    make_move(row, col, WHITE)
                    eval = minimax(board, depth - 1, True, alpha, beta)
                    board = [row[:] for row in board_copy]
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return min_eval


# Function to make the computer's move
def make_computer_move():
    global board
    best_score = float("-inf")
    best_move = None
    for row in range(ROWS):
        for col in range(COLS):
            if is_valid_move(row, col, BLACK):
                board_copy = [row[:] for row in board]
                make_move(row, col, BLACK)
                score = minimax(board, 3, False, float("-inf"), float("inf"))
                board = [row[:] for row in board_copy]
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
    if best_move:
        make_move(best_move[0], best_move[1], BLACK)


# Function to Show game is over
def show_game_over_message():
    font = pygame.font.Font(None, 36)
    f = pygame.font.Font(None, 20)
    white_score, black_score = get_score()
    replay_text = f.render("Press Spacebar to Play Again", True, white)
    if white_score == black_score:
        game_over_text = font.render("Tie Game", True, red)
        return game_over_text, replay_text
    elif white_score > black_score:
        game_over_text = font.render("Congratulations. You Won!", True, red)
        return game_over_text, replay_text
    elif white_score < black_score:
        game_over_text = font.render("Game Over. You lose!", True, red)
        return game_over_text, replay_text

# Main game loop
turn = WHITE 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not is_game_over(board) and turn == WHITE:
                if pygame.mouse.get_pressed()[0]:
                    x, y = pygame.mouse.get_pos()
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    if is_valid_move(row, col, WHITE):
                        make_move(row, col, WHITE)
                        turn = BLACK
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
                board[3][3] = 1
                board[3][4] = -1
                board[4][3] = -1
                board[4][4] = 1
                turn = WHITE

    draw_board()

    # Display
    white_score, black_score = get_score()
    font = pygame.font.Font(None, 36)
    white_text = font.render(f"White: {white_score}", True, white)
    black_text = font.render(f"Black: {black_score}", True, black)
    screen.blit(white_text, (565, 100))
    screen.blit(black_text, (565, 140))

    if not is_game_over(board):
        if turn == WHITE:
            if not any(is_valid_move(row, col, WHITE) for row in range(ROWS) for col in range(COLS)):
                turn = BLACK
        elif turn == BLACK:
            make_computer_move()
            turn = WHITE

    else:
        game_over_text, replay_text = show_game_over_message()
        game_over_text_pos = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        game_over_img_pos = game_over_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        replay_text_pos = replay_text.get_rect(center=(WIDTH // 2, (HEIGHT // 2) + 28))
        screen.blit(game_over_img, game_over_img_pos)
        screen.blit(game_over_text, game_over_text_pos)
        screen.blit(replay_text, replay_text_pos)

    pygame.display.flip()