from flask import *
rows = 100
cols = 70
# Normal grid will be marked as 0
grid = [[0 for _ in range(cols)] for _ in range(rows)]

# Racket center will be like  # # # # # ! # # # # # (! is center)
playerRacketWidth = 11
playerRacketCenterPos = 35


# The pingpongball will be 3x3 pixels and it will also be marked as a number 4
pingpongballx = 50
pingpongbally = 35


# The left and right sides that are not the racket will be marked as a 2
for row in range(rows):
    grid[row][0] = 2       # Left-most column
    grid[row][cols - 1] = 2  # Right-most column





