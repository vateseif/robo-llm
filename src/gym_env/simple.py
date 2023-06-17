import os
import pygame
import threading
import numpy as np
import gymnasium as gym

from time import sleep

from gym_env.utils.core import World

# set pygame window always on corner of screen
os.environ['SDL_VIDEO_WINDOW_POS'] = str(0) + "," + str(0)

class GridWorldEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None, size=10, wait_time_s=0.2, cfg=None):
        
        # create world
        self.world = World(size=size, wait_time_s=wait_time_s, cfg=cfg)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.size = size
        self.window = None
        self.clock = None
        self.window_size = 512  # The size of the PyGame window
        self.wait_time_s = wait_time_s
        self.open_thread = False

        # open thread
        self.open_thread = True
        if self.render_mode == "human":
            self._render_frame()
        

    def _get_obs(self):
        return {"agent": self._agent_location, "target": self._target_location}

    def _get_info(self):
        return {
            "distance": np.linalg.norm(
                self._agent_location - self._target_location, ord=1
            )
        }

    def reset(self, seed=None, options=None):
        # reset world
        observation, info = self.world.reset(seed)
        # open thread
        self.open_thread = True
        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self):
        # An episode is done iff the agent has reached the target
        terminated = False
        reward = 1 if terminated else 0  # Binary sparse rewards
        observation = self.world._get_obs()
        info = self.world._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info

    def _run(self, wait_time_s):
        while self.open_thread:
            self.step()
            sleep(wait_time_s)

    def run(self):
        # Create a background thread
        self.thread = threading.Thread(target=self._run, args=(self.wait_time_s,))
        self.thread.daemon = True  # Set the thread as a daemon (will exit when the main program ends)
        # Start the background thread
        self.thread.start()

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.world.window_size, self.world.window_size)
            )
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        # create and draw on canvas
        canvas = self.world._render_frame()

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        # close thread
        self.open_thread = False
        self.thread.join()
        # close window
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()