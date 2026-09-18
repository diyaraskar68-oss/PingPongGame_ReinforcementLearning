import random
import pygame
import sys

pygame.init()

GRID_COLS = 100
GRID_ROWS = 50
CELL_SIZE = 10

prevballx = GRID_COLS * CELL_SIZE // 2
prevbally = GRID_ROWS * CELL_SIZE // 2
ballx = GRID_COLS * CELL_SIZE // 2
bally = GRID_ROWS * CELL_SIZE // 2
ballx_velocity = random.choice((-5, 5))
bally_velocity = random.choice((-5, 5))

print(f"ballx_velocity: {ballx_velocity}")
print(f"bally_velocity: {bally_velocity}")

SCREEN_WIDTH = GRID_COLS * CELL_SIZE
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE
PADDLE_WIDTH = CELL_SIZE
PADDLE_HEIGHT = 100
PADDLE_SPEED = 5
PADDLE_COLOR = (255, 255, 255)

left_paddle = pygame.Rect(
    0,
    (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
)
right_paddle = pygame.Rect(
    SCREEN_WIDTH - PADDLE_WIDTH,
    (SCREEN_HEIGHT - PADDLE_HEIGHT) // 2,
    PADDLE_WIDTH,
    PADDLE_HEIGHT,
)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Grid")
clock = pygame.time.Clock()

grid_data = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

for row in range(GRID_ROWS):
    grid_data[row][0] = 2
    grid_data[row][GRID_COLS - 1] = 2

BG_COLOR = (25, 25, 25)
GRID_COLOR = (50, 50, 50)
FILLED_COLOR = (0, 153, 255)
font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 36)

def step():
    global ballx, bally, ballx_velocity, bally_velocity

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s]:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP]:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN]:
        right_paddle.y += PADDLE_SPEED

    left_paddle.y = max(0, min(left_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))
    right_paddle.y = max(0, min(right_paddle.y, SCREEN_HEIGHT - PADDLE_HEIGHT))

    ballx += ballx_velocity
    bally += bally_velocity

    ball_rect = pygame.Rect(round(ballx), round(bally), CELL_SIZE, CELL_SIZE)
    if bally < 0 or bally > SCREEN_HEIGHT - CELL_SIZE:
        bally_velocity *= -1
        bally = max(0, min(bally, SCREEN_HEIGHT - CELL_SIZE))

    hit_paddle = False
    if ball_rect.colliderect(left_paddle) and ballx_velocity < 0:
        hit_paddle = True
        ballx = left_paddle.right
        ballx_velocity = abs(ballx_velocity)
        hit_position = (bally + CELL_SIZE / 2 - left_paddle.centery) / (PADDLE_HEIGHT / 2)
        bally_velocity = hit_position * 4
    elif ball_rect.colliderect(right_paddle) and ballx_velocity > 0:
        hit_paddle = True
        ballx = right_paddle.left - CELL_SIZE
        ballx_velocity = -abs(ballx_velocity)
        hit_position = (bally + CELL_SIZE / 2 - right_paddle.centery) / (PADDLE_HEIGHT / 2)
        bally_velocity = hit_position * 4

    if not hit_paddle and ballx <= 0:
        return True
    elif not hit_paddle and ballx >= SCREEN_WIDTH - CELL_SIZE:
        return True

    return False


def create_model():
    from keras import Sequential, layers, losses, optimizers

    model = Sequential([
        layers.Input(shape=(5,)),
        layers.Dense(64, activation="relu"),
        layers.Dense(64, activation="relu"),
        layers.Dense(3, activation="linear")
    ])
    model.compile(optimizer=optimizers.Adam(learning_rate=0.001), loss=losses.Huber())
    return model


running = True
game_state = "start"
countdown_started_at = None
lost_at = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if game_state == "start":
                game_state = "countdown"
                countdown_started_at = pygame.time.get_ticks()

    current_time = pygame.time.get_ticks()
    if game_state == "countdown":
        if current_time - countdown_started_at >= 3000:
            game_state = "playing"
        else:
            countdown_number = 3 - (current_time - countdown_started_at) // 1000
    elif game_state == "playing" and step():
        game_state = "lost"
        lost_at = current_time
    elif game_state == "lost" and current_time - lost_at >= 3000:
        running = False


    screen.fill(BG_COLOR)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            
            if grid_data[row][col] == 1:
                pygame.draw.rect(screen, FILLED_COLOR, rect)
            elif grid_data[row][col] == 2:
                pygame.draw.rect(screen, (255, 0, 0), rect)
            else:
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    ball_rect = pygame.Rect(round(ballx), round(bally), CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, FILLED_COLOR, ball_rect)
    pygame.draw.rect(screen, PADDLE_COLOR, left_paddle)
    pygame.draw.rect(screen, PADDLE_COLOR, right_paddle)

    if game_state == "start":
        message = font.render("PRESS SPACE TO START", True, PADDLE_COLOR)
        screen.blit(message, message.get_rect(center=screen.get_rect().center))
    elif game_state == "countdown":
        message = font.render(str(countdown_number), True, PADDLE_COLOR)
        screen.blit(message, message.get_rect(center=screen.get_rect().center))
    elif game_state == "lost":
        message = font.render("YOU LOSE", True, (255, 80, 80))
        screen.blit(message, message.get_rect(center=screen.get_rect().center))
        submessage = small_font.render("Closing in 3 seconds...", True, PADDLE_COLOR)
        screen.blit(submessage, submessage.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

