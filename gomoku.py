import sys
import pygame
import numpy as np
import random

SQUARESIZE = 32
RADIUS = int(SQUARESIZE / 2 - 4)

PLAYER_PIECE = 1
AI_PIECE = 2
WIN_COUNT = 5

row = col = 15
width = col * SQUARESIZE
height = row * SQUARESIZE + 20
board = None
screen = None
last_move = None
game_over = False
turn = 0
first_move = True

## making a new game by reseting the board
def reset_game():
    global board, game_over, turn, first_move, last_move
    board = create_board()
    game_over = False
    turn = random.randint(0, 1)
    first_move = True
    last_move = None

## creating a new board
def create_board():
    return np.zeros((row, col), dtype=int)

## checking if a place is available
def is_available_place(b, r, c):
    return 0 <= r < row and 0 <= c < col and b[r, c] == 0

## placing a new piece
def drop_piece(b, r, c, piece):
    if is_available_place(b, r, c):
        b[r, c] = piece

## checking if there is a sequence of 5 pieces and return True if so as a win for the player
def winning_move(b, piece):
    for r in range(row):
        for c in range(col - WIN_COUNT + 1):
            if all(b[r, c + i] == piece for i in range(WIN_COUNT)):
                return True
    for c in range(col):
        for r in range(row - WIN_COUNT + 1):
            if all(b[r + i, c] == piece for i in range(WIN_COUNT)):
                return True
    for r in range(row - WIN_COUNT + 1):
        for c in range(col - WIN_COUNT + 1):
            if all(b[r + i, c + i] == piece for i in range(WIN_COUNT)):
                return True
    for r in range(WIN_COUNT - 1, row):
        for c in range(col - WIN_COUNT + 1):
            if all(b[r - i, c + i] == piece for i in range(WIN_COUNT)):
                return True
    return False

## drawing the board
def draw_board(b):
    global screen
    screen.fill((50, 50, 50))
    for c in range(col):
        for r in range(row):
            rect = pygame.Rect(c * SQUARESIZE, r * SQUARESIZE, SQUARESIZE, SQUARESIZE)
            pygame.draw.rect(screen, (200, 180, 120), rect, 0)
            pygame.draw.rect(screen, (120, 100, 80), rect, 1)

    for c in range(col):
        for r in range(row):
            if b[r, c] == PLAYER_PIECE:
                pygame.draw.circle(screen, (255, 255, 255),
                                   (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)),
                                   RADIUS)
            elif b[r, c] == AI_PIECE:
                pygame.draw.circle(screen, (0, 0, 0),
                                   (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)),
                                   RADIUS)
    
    if last_move:
        r, c = last_move
        pygame.draw.circle(screen, (255, 0, 0),
                           (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE / 2)),
                           5)
    
    font_name = pygame.font.match_font('arial,helvetica,dejavusans,liberationsans,sans')
    font = pygame.font.Font(font_name, 16)
    text = font.render("Press 'R' to Restart", True, (200, 200, 200))
    text_rect = text.get_rect(center=(width // 2, height - 10))
    screen.blit(text, text_rect)
                           
    pygame.display.update()

## helper for score_position function
## getting the score of a line by checking the number of pieces in sequence and calculate the score using the calculate_shape_score function
def get_line_score(line, piece, opp_piece):
    score = 0
    s = "".join(['X' if x == piece else 'O' if x == opp_piece else '.' for x in line])
    
    count = 0
    block_start = -1
    
    for i, char in enumerate(s):
        if char == 'X':
            if count == 0:
                block_start = i
            count += 1
        else:
            if count > 0:
                length = count
                left_open = (block_start > 0 and s[block_start-1] == '.')
                right_open = (char == '.')
                score += calculate_shape_score(length, left_open, right_open)
                count = 0
    
    if count > 0:
        length = count
        left_open = (block_start > 0 and s[block_start-1] == '.')
        right_open = False
        score += calculate_shape_score(length, left_open, right_open)
        
    return score

## helper for get_line_score function 
## calculate the score of a shape
def calculate_shape_score(length, left_open, right_open):
    if length >= 5: ## win and game over
        return 100000
    if length == 4: ## garuanteed win
        if left_open and right_open:
            return 50000
        if left_open or right_open:
            return 10000
    if length == 3:
        if left_open and right_open: ## a real threat 
            return 10000
        if left_open or right_open: ## a potential threat
            return 500
    if length == 2:
        if left_open and right_open: ## start of the threat
            return 100
    return 0

## Heuristic 1
def heuristic_1(b, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    
    lines = []
    
    for r in range(row):
        lines.append(b[r, :])
        
    for c in range(col):
        lines.append(b[:, c])
        
    for k in range(-row + 1, col):
        d1 = b.diagonal(k)
        if len(d1) >= 5:
            lines.append(d1)
        d2 = np.fliplr(b).diagonal(k)
        if len(d2) >= 5:
            lines.append(d2)
            
    for line in lines:
        score += get_line_score(line, piece, opp_piece)
        score -= get_line_score(line, opp_piece, piece) * 1.5 ## defensive model
        
    center_r, center_c = row // 2, col // 2
    if b[center_r, center_c] == piece:
        score += 20
        
    return score

# Heuristic 2
def heuristic_2(b, piece):
    opp = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    score = 0
    center_r, center_c = row // 2, col // 2
    for r in range(row):
        for c in range(col):
            if b[r, c] == piece:
                score += 10 - (abs(center_r - r) + abs(center_c - c))
            elif b[r, c] == opp:
                score -= 8 - (abs(center_r - r) + abs(center_c - c))
    return score

## the main function for running specific heuristic
def heuristic(b, piece):
    return heuristic_1(b, piece)

## check if the game is over
def is_terminal_node(b):
    return winning_move(b, PLAYER_PIECE) or winning_move(b, AI_PIECE) or not np.any(b == 0)

## get the candidate moves for the AI
def get_candidate_moves(b, distance=2):
    occupied = list(zip(*np.where(b != 0)))
    if not occupied:
        return [(row // 2, col // 2)]
    candidates = set()
    for (r0, c0) in occupied:
        for dr in range(-distance, distance + 1):
            for dc in range(-distance, distance + 1):
                r, c = r0 + dr, c0 + dc
                if 0 <= r < row and 0 <= c < col and b[r, c] == 0:
                    candidates.add((r, c))
    return list(candidates)

## running the minimax algorithm
def minimax(b, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or is_terminal_node(b):
        if is_terminal_node(b):
            if winning_move(b, AI_PIECE):
                return (None, None, float('inf'))
            elif winning_move(b, PLAYER_PIECE):
                return (None, None, -float('inf'))
            else:
                return (None, None, 0)
        else:
            return (None, None, heuristic(b, AI_PIECE))

    ## maximizing player is the ai
    if maximizingPlayer:
        value = -float('inf')
        best_move = (None, None)
        for (r, c) in get_candidate_moves(b):
            temp = b.copy()
            drop_piece(temp, r, c, AI_PIECE)
            _, _, new_score = minimax(temp, depth - 1, alpha, beta, False)
            if new_score > value:
                value = new_score
                best_move = (r, c)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return (best_move[0], best_move[1], value)
    else:
        value = float('inf')
        best_move = (None, None)
        for (r, c) in get_candidate_moves(b):
            temp = b.copy()
            drop_piece(temp, r, c, PLAYER_PIECE)
            _, _, new_score = minimax(temp, depth - 1, alpha, beta, True)
            if new_score < value:
                value = new_score
                best_move = (r, c)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return (best_move[0], best_move[1], value)

## calculate the dynamic depth for the AI according to the number of moves left
def dynamic_depth(b):
    moves_left = np.count_nonzero(b == 0)
    if moves_left > (row * col) * 0.7:
        return 1
    elif moves_left > (row * col) * 0.4:
        return 2
    else:
        return 3

def ai_turn(b):
    current_depth = dynamic_depth(b)
    rAI, cAI, _ = minimax(b, current_depth, -float('inf'), float('inf'), True)
    if rAI is not None and cAI is not None:
        drop_piece(b, rAI, cAI, AI_PIECE)
    return rAI, cAI


pygame.init()
pygame.display.set_caption("Gomoku")

if board is None:
    reset_game()

screen = pygame.display.set_mode((width, height))
draw_board(board)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
                draw_board(board)

        if not game_over and turn == 0 and event.type == pygame.MOUSEBUTTONDOWN:
            mouseX = event.pos[0] // SQUARESIZE
            mouseY = event.pos[1] // SQUARESIZE
            if is_available_place(board, mouseY, mouseX):
                drop_piece(board, mouseY, mouseX, PLAYER_PIECE)
                last_move = (mouseY, mouseX)
                draw_board(board)
                if winning_move(board, PLAYER_PIECE):
                    font_name = pygame.font.match_font('arial,helvetica,dejavusans,liberationsans,sans')
                    font = pygame.font.Font(font_name, 72)
                    text = font.render("Player Wins!", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(width // 2, height // 2))
                    bg_rect = text_rect.inflate(20, 20)
                    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
                    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
                    screen.blit(text, text_rect)
                    pygame.display.update()
                    game_over = True
                else:
                    turn = 1

    if not game_over and turn == 1:
        rAI, cAI = ai_turn(board)
        if rAI is not None and cAI is not None:
            if board[rAI, cAI] == 0: 
                drop_piece(board, rAI, cAI, AI_PIECE)
            last_move = (rAI, cAI)
            draw_board(board)
            if winning_move(board, AI_PIECE):
                font_name = pygame.font.match_font('arial,helvetica,dejavusans,liberationsans,sans')
                font = pygame.font.Font(font_name, 72)
                text = font.render("AI Wins!", True, (255, 50, 50))
                text_rect = text.get_rect(center=(width // 2, height // 2))
                bg_rect = text_rect.inflate(20, 20)
                pygame.draw.rect(screen, (0, 0, 0), bg_rect)
                pygame.draw.rect(screen, (255, 50, 50), bg_rect, 2)
                screen.blit(text, text_rect)
                pygame.display.update()
                game_over = True
            else:
                turn = 0
