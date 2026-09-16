import tensorflow as tf
from keras import Sequential

rows = 70
cols = 100

# Normal grid = 0
# Out zones = 2
# Paddle = 3
# Ball = 4
grid = [[0 for _ in range(cols)] for _ in range(rows)]

# Left and right out zones
for row in range(rows):
    grid[row][0] = 2
    grid[row][cols - 1] = 2

# Paddle
playerRacketHeight = 11
playerRacketCenterPos = 35

# Ball (top-left position)
pingpongballx = 50
pingpongbally = 35

# Ball velocity
ball_velocity_x = -1
ball_velocity_y = 0

def move_paddle(action):
    global playerRacketCenterPos

    if action == UP:
        playerRacketCenterPos -= 1

    elif action == DOWN:
        playerRacketCenterPos += 1

    # Keep paddle inside the grid
    half = playerRacketHeight // 2

    playerRacketCenterPos = max(
        half,
        min(rows - 1 - half, playerRacketCenterPos)
    )

def get_state():
    return [
        pingpongballx / cols,
        pingpongbally / rows,
        ball_velocity_x,
        ball_velocity_y,
        playerRacketCenterPos / rows
    ]

def ball_hits_paddle():
    ball_left = pingpongballx
    ball_right = pingpongballx + 2

    ball_top = pingpongbally
    ball_bottom = pingpongbally + 2

    paddle_top = playerRacketCenterPos - 5
    paddle_bottom = playerRacketCenterPos + 5

    paddle_x = 2

    return (
        ball_left <= paddle_x and
        ball_right >= paddle_x and
        ball_bottom >= paddle_top and
        ball_top <= paddle_bottom
    )

#if pingpongballx <= 0 or pingpongballx >= cols - 3:
#    reward = -1

#if ball_hits_paddle():
#    ball_velocity_x *= -1
#    reward = 1