import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random


class VisualPingPongEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self, render_mode="human"):
        super().__init__()
        self.render_mode = render_mode

        # Grid Sizing Config
        self.GRID_COLS = 100
        self.GRID_ROWS = 50
        self.CELL_SIZE = 10

        self.FILLED_COLOR = (0, 152, 255)
        self.GRID_COLOR = (0,0,0)
        self.BG_COLOR = (111, 111, 111)

        # State Vectors
        self.PongRacketPos = 25
        self.PongWidth = 6 # From center ! = center # = around ###!###
        self.prevballx = 50
        self.prevbally = 25
        self.ballx = 50
        self.bally = 25
        self.pong_color = (0, 255, 0)
        
        # FIXED: Enclosed items inside valid Python list brackets []
        self.ballx_velocity = random.choice([-2, 2])
        self.bally_velocity = random.choice([-2, 2])

        # Sizing Variables
        self.SCREEN_WIDTH = self.GRID_COLS * self.CELL_SIZE
        self.SCREEN_HEIGHT = self.GRID_ROWS * self.CELL_SIZE

        if self.render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("Grid")
            self.clock = pygame.time.Clock() # <--- Add this
        else:
            self.screen = None
            self.clock = None

        # Grid Array Layout Setup
        self.grid_data = [[0 for _ in range(self.GRID_COLS)] for _ in range(self.GRID_ROWS)]

        for row in range(self.GRID_ROWS):
            self.grid_data[row][0] = 2
            self.grid_data[row][self.GRID_COLS - 1] = 2
            
        # Standard Gymnasium Spaces Setup 
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, -5, -5], dtype=np.float32),
            high=np.array([self.GRID_ROWS, self.GRID_COLS, self.GRID_ROWS, 5, 5], dtype=np.float32),
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        # 1. Clear and seed the random generator engine
        super().reset(seed=seed)
        
        # 2. Reset the paddle position to the vertical middle of the grid
        self.Pong_height = 6
        self.PongRacketPos = self.SCREEN_HEIGHT // (2 * 10) # Centered in grid units
        
        # 3. Reset ball tracking coordinates back to the center spawn location
        self.prevballx = 50
        self.prevbally = 25
        self.ballx = 50
        self.bally = 25
        self.FILLED_COLOR = (0, 152, 255)
        self.GRID_COLOR = (0,0,0)
        self.BG_COLOR = (111, 111, 111)
        
        
        # 4. Generate new starting speeds
        self.ballx_velocity = random.choice([-2, 2])
        self.bally_velocity = random.choice([-2, 2])

        # 5. Extract the initial state array and pass along with empty info dict
        observation = self._get_obs()
        info = {}
        
        return observation, info


    def render(self):
        pygame.event.pump()
        self.screen.fill(self.BG_COLOR)
        for row in range(self.GRID_ROWS):
                for col in range(self.GRID_COLS):
                    x = col * self.CELL_SIZE
                    y = row * self.CELL_SIZE
                    rect = pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)

                    if self.grid_data[row][col] == 1:
                       pygame.draw.rect(self.screen, self.FILLED_COLOR, rect)
                    elif self.grid_data[row][col] == 2:
                        pygame.draw.rect(self.screen, (255, 0, 0), rect)
                    else:
                        pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)

        # Interpolate smoothly between the previous position and current position
        # (You can use an interpolation factor 'alpha' from 0.0 to 1.0)
        alpha = 1.0  # Set this if you add sub-frame timing, or keep it 1.0 for standard step-to-step smoothing
        
        render_ballx = self.prevballx + (self.ballx - self.prevballx) * alpha
        render_bally = self.prevbally + (self.bally - self.prevbally) * alpha

        ball_rect = pygame.Rect(
            int(render_ballx * self.CELL_SIZE), 
            int(render_bally * self.CELL_SIZE), 
            self.CELL_SIZE, 
            self.CELL_SIZE
        )
        pygame.draw.rect(self.screen, self.pong_color, ball_rect)

        half_span = int((self.PongWidth - 1) / 2)
        for r_offset in range(-half_span, half_span + 1):
            p_row = int(self.PongRacketPos + r_offset)
            if 0 <= p_row < self.GRID_ROWS:
                paddle_rect = pygame.Rect(1 * self.CELL_SIZE, p_row * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(self.screen, self.pong_color, paddle_rect)

        pygame.display.flip()
        
        # Limit the frame rate to 60 FPS if running in human mode
        if self.clock is not None:
            self.clock.tick(self.metadata["render_fps"])

    def step(self, action):
        reward = 0.0
        terminated = False
        truncated = False
        self.prevballx = self.ballx
        self.prevbally = self.bally
        self.ballx += self.ballx_velocity
        self.bally += self.bally_velocity
    
        if action == 0:
            pass  # Stay
        elif action == 1:
            if self.PongRacketPos > 4:
                self.PongRacketPos += 1
        elif action == 2:
            if self.PongRacketPos < 46:
                self.PongRacketPos -= 1
        else:
            print(f"Unexpected Input of ACTION! Got: {action}")

        # Pong and ball logic
        if self.ballx <= 1 and abs(self.bally - self.PongRacketPos) > (self.PongWidth - 1) / 2:
            reward -= 10 # punishes ai if die
            terminated = True
        elif self.ballx <= 1 and abs(self.bally - self.PongRacketPos) <= (self.PongWidth - 1) / 2:
            reward += 10.0
            self.ballx_velocity *= -1  # Bounce the ball back
        else:
            reward += 0.1 # give ai small bonus for staying alive
        
        # Top and Bottom Wall Bouncing logic (Clamped to prevent skipping)
        if self.bally <= 0:
            self.bally = 0          # Snap back to the top boundary
            self.bally_velocity *= -1 # Reverse vertical direction
        elif self.bally >= self.GRID_ROWS - 1:
            self.bally = self.GRID_ROWS - 1  # Snap back to the bottom boundary
            self.bally_velocity *= -1        # Reverse vertical direction
        
        # Right Wall Bouncing logic
        if self.ballx >= self.GRID_COLS - 1:
            self.ballx = self.GRID_COLS - 1
            self.ballx_velocity *= -1
        

        
        observation = self._get_obs()
        info = {}

        return observation, reward, terminated, truncated, info

    def _get_obs(self):
        return np.array([self.PongRacketPos,
                          self.ballx,
                          self.bally,
                          self.ballx_velocity,
                          self.bally_velocity
                        ], dtype=np.float32)
    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None







if __name__ == "__main__":
    import time

    # Initialize your environment
    env = VisualPingPongEnv(render_mode="human")
    
    # Run a few test episodes with random actions
    for episode in range(5):
        observation, info = env.reset()
        terminated = False
        truncated = False
        
        print(f"Starting Test Episode {episode + 1}")
        
        while not terminated and not truncated:
            action = env.action_space.sample()  # Random action: 0, 1, or 2
            observation, reward, terminated, truncated, info = env.step(action)
            env.render()
            
            # Optional: A tiny delay so the game doesn't run too fast to see
            time.sleep(0.02)
            
        print(f"Episode {episode + 1} ended.")

    env.close()