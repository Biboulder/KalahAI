import pygame
import sys
import threading
from kalah import Kalah
from minimax import minimax

# ── Window ─────────────────────────────────────────────────────────────────────
BOARD_W  = 780
LOG_W    = 200
WIDTH    = BOARD_W + LOG_W
HEIGHT   = 520
FPS      = 60
AI_PLAYER = 1
AI_DEPTH  = 6

# ── Colours ────────────────────────────────────────────────────────────────────
BG         = (30,  20,  10)
WOOD       = (139, 90,  43)
WOOD_DARK  = (95,  60,  25)
WOOD_LIGHT = (180, 130, 70)
PIT_EMPTY  = (60,  40,  15)
PIT_HOVER  = (200, 160, 80)
PIT_VALID  = (220, 180, 100)
STORE_COL  = (80,  50,  18)
BALL_P0    = (220, 200, 100)   # gold  – human
BALL_P1    = (100, 180, 220)   # blue  – AI
TXT_LIGHT  = (255, 240, 210)
ACCENT     = (255, 200, 60)
LOG_BG     = (18,  12,  4)
LOG_LINE   = (80,  55,  20)

# ── Board layout (all coords relative to board area 0..BOARD_W) ────────────────
PAD_X    = 50        # space from board edge to store
STORE_W  = 75
STORE_H  = 240
PIT_R    = 36
PIT_GAP  = 14

# vertical centre of the board area
BOARD_TOP    = 80
BOARD_BOTTOM = HEIGHT - 40
BOARD_MID_Y  = (BOARD_TOP + BOARD_BOTTOM) // 2

STORE_Y   = BOARD_MID_Y - STORE_H // 2
ROW_GAP   = 20       # gap between the two pit rows
ROW_AI_Y  = BOARD_MID_Y - ROW_GAP // 2 - PIT_R      # top row centre y
ROW_YOU_Y = BOARD_MID_Y + ROW_GAP // 2 + PIT_R      # bottom row centre y

# x positions
STORE_LEFT_X  = PAD_X
STORE_RIGHT_X = BOARD_W - PAD_X - STORE_W
PITS_LEFT_X   = STORE_LEFT_X + STORE_W + PIT_GAP + PIT_R
STEP_X        = PIT_R * 2 + PIT_GAP

# labels / numbers
NUM_AI_Y  = ROW_AI_Y  - PIT_R - 24
NUM_YOU_Y = ROW_YOU_Y + PIT_R + 14
LBL_AI_Y  = NUM_AI_Y  - 18
LBL_YOU_Y = NUM_YOU_Y + 16


def pit_cx(i):
    return PITS_LEFT_X + i * STEP_X


def store_rect(player):
    x = STORE_RIGHT_X if player == 0 else STORE_LEFT_X
    return pygame.Rect(x, STORE_Y, STORE_W, STORE_H)


# ── AI thread ──────────────────────────────────────────────────────────────────
def run_ai(game, depth, result):
    _, pit = minimax(game, game.board, game.current_player, depth, AI_PLAYER)
    result[0] = pit if pit is not None else -1


# ── Draw helpers ───────────────────────────────────────────────────────────────
def blit_center(surf, img, cx, cy):
    surf.blit(img, img.get_rect(center=(cx, cy)))


def draw_circle(surf, col, cx, cy, r, border_col=None, border_w=2):
    pygame.draw.circle(surf, WOOD_DARK, (cx + 3, cy + 3), r)
    pygame.draw.circle(surf, col,       (cx,     cy),     r)
    if border_col:
        pygame.draw.circle(surf, border_col, (cx, cy), r, border_w)


# ── Main draw ──────────────────────────────────────────────────────────────────
def draw_board(surf, game, hover_pit, ai_thinking, F):
    fb, fm, fs, ft = F
    surf.fill(BG)

    # board backing rectangle
    bx = PAD_X - 8
    by = STORE_Y - 8
    bw = BOARD_W - 2 * (PAD_X - 8)
    bh = STORE_H + 16
    br = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(surf, WOOD_DARK,  br.move(4, 4), border_radius=18)
    pygame.draw.rect(surf, WOOD,       br,            border_radius=18)
    pygame.draw.rect(surf, WOOD_LIGHT, br, width=3,   border_radius=18)

    # stores
    for p in (0, 1):
        r   = store_rect(p)
        pygame.draw.rect(surf, WOOD_DARK,  r.move(3, 3), border_radius=12)
        pygame.draw.rect(surf, STORE_COL,  r,            border_radius=12)
        pygame.draw.rect(surf, WOOD_LIGHT, r, width=2,   border_radius=12)
        idx = 6 if p == 0 else 13
        col = BALL_P0 if p == 0 else BALL_P1
        txt = fb.render(str(game.board[idx]), True, col)
        surf.blit(txt, txt.get_rect(center=r.center))

    # player labels (inside board, between rows)
    cx_mid = BOARD_W // 2
    surf.blit(ft.render("AI  (Player 1)", True, BALL_P1),
              ft.render("AI  (Player 1)", True, BALL_P1).get_rect(centerx=cx_mid, bottom=LBL_AI_Y + 16))
    surf.blit(ft.render("YOU  (Player 0)", True, BALL_P0),
              ft.render("YOU  (Player 0)", True, BALL_P0).get_rect(centerx=cx_mid, top=LBL_YOU_Y))

    valid = game.get_actions(game.board, game.current_player) \
            if (game.current_player != AI_PLAYER and not ai_thinking) else []

    for i in range(6):
        cx0 = pit_cx(i)
        cx1 = pit_cx(5 - i)   # AI pits are mirrored

        # pit numbers
        surf.blit(ft.render(str(i + 1), True, BALL_P1),
                  ft.render(str(i + 1), True, BALL_P1).get_rect(centerx=cx1, centery=NUM_AI_Y))
        surf.blit(ft.render(str(i + 1), True, BALL_P0),
                  ft.render(str(i + 1), True, BALL_P0).get_rect(centerx=cx0, centery=NUM_YOU_Y))

        # human pit (bottom)
        count0   = game.board[i]
        is_hover = hover_pit == ('p0', i)
        is_valid = i in valid
        col0     = PIT_HOVER if is_hover else (PIT_VALID if is_valid else PIT_EMPTY)
        draw_circle(surf, col0, cx0, ROW_YOU_Y, PIT_R, WOOD_LIGHT)
        blit_center(surf, fm.render(str(count0), True, BALL_P0), cx0, ROW_YOU_Y)

        # AI pit (top)
        count1 = game.board[7 + i]
        draw_circle(surf, PIT_EMPTY, cx1, ROW_AI_Y, PIT_R, WOOD_LIGHT)
        blit_center(surf, fm.render(str(count1), True, BALL_P1), cx1, ROW_AI_Y)

    # turn message
    if ai_thinking or game.current_player == AI_PLAYER:
        msg, col = "AI is thinking...", BALL_P1
    else:
        msg, col = "Your turn  -  click a pit", BALL_P0
    txt = fs.render(msg, True, col)
    surf.blit(txt, txt.get_rect(centerx=BOARD_W // 2, top=14))


def draw_log(surf, move_log, fs, ft):
    panel = pygame.Rect(BOARD_W, 0, LOG_W, HEIGHT)
    pygame.draw.rect(surf, LOG_BG, panel)
    pygame.draw.line(surf, LOG_LINE, (BOARD_W, 0), (BOARD_W, HEIGHT), 2)

    title = fs.render("Move Log", True, ACCENT)
    surf.blit(title, title.get_rect(centerx=BOARD_W + LOG_W // 2, top=14))
    pygame.draw.line(surf, LOG_LINE,
                     (BOARD_W + 8, 40), (BOARD_W + LOG_W - 8, 40), 1)

    line_h    = 21
    max_lines = (HEIGHT - 55) // line_h
    for idx, entry in enumerate(move_log[-max_lines:]):
        col = BALL_P0 if "You" in entry else BALL_P1
        surf.blit(ft.render(entry, True, col), (BOARD_W + 8, 48 + idx * line_h))


def draw_winner(surf, winner, fb, fm):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 165))
    surf.blit(ov, (0, 0))
    if winner == -1:
        msg, col = "Draw!", ACCENT
    elif winner == 0:
        msg, col = "You Win!", BALL_P0
    else:
        msg, col = "AI Wins!", BALL_P1
    txt = fb.render(msg, True, col)
    surf.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 28)))
    sub = fm.render("R = restart    Q = quit", True, TXT_LIGHT)
    surf.blit(sub, sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 26)))


# ── Hit test ───────────────────────────────────────────────────────────────────
def get_hover(mx, my):
    if mx >= BOARD_W:
        return None
    for i in range(6):
        cx = pit_cx(i)
        if (mx - cx) ** 2 + (my - ROW_YOU_Y) ** 2 <= PIT_R ** 2:
            return ('p0', i)
        cx1 = pit_cx(5 - i)
        if (mx - cx1) ** 2 + (my - ROW_AI_Y) ** 2 <= PIT_R ** 2:
            return ('p1', i)
    return None


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kalah")
    clock  = pygame.time.Clock()

    F = (
        pygame.font.SysFont("Georgia", 38, bold=True),  # fb
        pygame.font.SysFont("Georgia", 24, bold=True),  # fm
        pygame.font.SysFont("Georgia", 18),             # fs
        pygame.font.SysFont("Georgia", 14),             # ft
    )

    def reset():
        g = Kalah()
        return g, None, False, None, g.current_player == AI_PLAYER, False, [None], [], [1]

    game, hover, game_over, winner, ai_pend, ai_think, ai_res, log, num = reset()

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_r:
                    game, hover, game_over, winner, ai_pend, ai_think, ai_res, log, num = reset()

            if not game_over and not ai_think and ev.type == pygame.MOUSEBUTTONDOWN:
                if game.current_player != AI_PLAYER:
                    hit = get_hover(*ev.pos)
                    if hit and hit[0] == 'p0':
                        pit = hit[1]
                        if pit in game.get_actions(game.board, game.current_player):
                            try:
                                log.append(f"{num[0]:2}. You  pit {pit + 1}")
                                num[0] += 1
                                game.move(pit)
                                if game.is_game_over(game.board):
                                    winner, game_over = game.get_winner(), True
                                elif game.current_player == AI_PLAYER:
                                    ai_pend = True
                            except ValueError:
                                pass

        # start AI thread
        if ai_pend and not ai_think and not game_over:
            ai_pend  = False
            ai_think = True
            ai_res   = [None]
            threading.Thread(target=run_ai,
                             args=(game, AI_DEPTH, ai_res),
                             daemon=True).start()

        # AI done
        if ai_think and ai_res[0] is not None:
            ai_think = False
            pit = ai_res[0]
            ai_res[0] = None
            if pit != -1:
                log.append(f"{num[0]:2}. AI   pit {pit + 1}")
                num[0] += 1
                game.move(pit)
            if game.is_game_over(game.board):
                winner, game_over = game.get_winner(), True
            elif game.current_player == AI_PLAYER:
                ai_pend = True

        hover = get_hover(*pygame.mouse.get_pos()) \
                if (not game_over and not ai_think
                    and game.current_player != AI_PLAYER) else None

        draw_board(screen, game, hover, ai_think, F)
        draw_log(screen, log, F[2], F[3])
        if game_over:
            draw_winner(screen, winner, F[0], F[1])
        pygame.display.flip()


if __name__ == "__main__":
    main()