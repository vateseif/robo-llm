import pygame
import numpy as np
from itertools import product

from typing import Optional, Tuple



class EntityState:  # physical/external base state of all entities
  def __init__(self):
    # physical position
    self.p_pos: Optional[np.ndarray] = None

class Action:  # action of the agent
  def __init__(self):
    """
    The following dictionary maps abstract actions from `self.action_space` to
    the direction we will walk in if that action is taken.
    I.e. 0 corresponds to "right", 1 to "up" etc.
    """
    self._action_to_direction = {
        0: np.array([1, 0]),
        1: np.array([0, 1]),
        2: np.array([-1, 0]),
        3: np.array([0, -1]),
    }

    # physical action
    self.u: Optional[np.ndarray] = None


class Entity:  # properties and state of physical world entity
  def __init__(self):
    # name
    self.name: str = ""
    # id
    self.id: Optional[int] = None
    # color TODO: randomize color
    self.color: Optional[Tuple[float]] = None
    # state
    self.state = EntityState()
    # size when drawing
    self.size = 50 # TODO 

  def draw(self, canvas: pygame.Surface):
    # Draws the entity on the canvas
    pass


class Agent(Entity):  # properties of agent entities
  def __init__(self, name, world):
    super().__init__()
    self.name = name
    # the world the agent is in
    self.world = world
    # state
    self.state = EntityState()
    # color
    self.color = (0, 0, 255) # blue
    # action
    self.action = Action()
    # script behavior to execute
    self.action_callback = None

  def draw(self, canvas: pygame.Surface, pix_square_size):
    # draw agent as a circle
    pygame.draw.circle(
      canvas, 
      self.color,
      (self.state.p_pos + 0.5) * pix_square_size,
      pix_square_size/3
    )

  def act(self, action):
    # applies action to move robot
    self.world.step(action)

    

class Key(Entity):
  def __init__(self, name):
    super().__init__()
    self.name = name
    # state
    self.state = EntityState()
    # color
    self.color = (255, 0, 0) # red 

  def draw(self, canvas: pygame.Surface, pix_square_size):
    # Draw key as a rectangle
    pygame.draw.rect(
        canvas,
        self.color,
        pygame.Rect(
            pix_square_size * self.state.p_pos,
            (pix_square_size/3, pix_square_size/3),
        ),
    )
     

class World:
  def __init__(self, size=10) -> None:

    # world dimensions
    self.size = size  # The size of the square grid
    self.window_size = 512
    self.edges = list(product([0, self.window_size], 
                              [0, self.window_size])
              ) # list of coordinates of world vertices
    self.pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels
    

    # init agent
    self.agent: Agent = Agent(name="agent", world=self)

    # init objects
    self.objects = [Key(name="key")]


  def step(self, action):
    # Map the action (element of {0,1,2,3}) to the direction we walk in
    direction = self.agent.action._action_to_direction[action]
    # We use `np.clip` to make sure we don't leave the grid
    self.agent.state.p_pos = np.clip(
        self.agent.state.p_pos + direction, 0, self.size - 1
    )


  def reset(self, seed=None):
    # random seed
    np.random.seed(seed)

    # set random location of agent
    self.agent.state.p_pos = np.random.randint(0, self.size-1, (2,))
    # set random location of objects
    for obj in self.objects:
      obj.state.p_pos = np.random.randint(0, self.size-1, (2, ))

    return self._get_obs(), self._get_info()


  def _get_obs(self):
    # return position of agent and objects
    return {entity.name: entity.state.p_pos for entity in [self.agent]+self.objects}

  def _get_info(self):
    # added this function to be conformed with gymnasium's way of doing
    return None

  def render(self):
    pass

  def _render_frame(self):
    # create canvas to draw on
    canvas = pygame.Surface((self.window_size, self.window_size))
    canvas.fill((255, 255, 255))

    # draw agent and objects on canvas
    for entity in [self.agent]+self.objects:
      entity.draw(canvas, self.pix_square_size)

    # draw delimiting edges of canvas
    pygame.draw.line(canvas, 0, self.edges[0], self.edges[1], width=3)
    pygame.draw.line(canvas, 0, self.edges[1], self.edges[3], width=3)
    pygame.draw.line(canvas, 0, self.edges[3], self.edges[2], width=3)
    pygame.draw.line(canvas, 0, self.edges[2], self.edges[0], width=3)

    return canvas

    
