import pygame
import numpy as np
import networkx as nx
import seaborn as sns
import colorcet as cc
from time import sleep
from itertools import product

from typing import Optional, Tuple, Union

color_palette = sns.color_palette(cc.glasbey, n_colors=3).as_hex() # TODO

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
    self.i: Optional[int] = None
    # color TODO: randomize color
    self.color: Optional[Tuple[float]] = None
    # state
    self.state = EntityState()
    # size when drawing
    self.size = 50 # TODO 
    # whether to draw entity
    self.draw_entity = True

  def draw(self):
    # Draws the entity on the canvas
    pass


class Key(Entity):
  def __init__(self, name, i):
    super().__init__()
    # name
    self.name = name
    # id
    self.i = i
    # state
    self.state = EntityState()
    # color
    self.color = color_palette[self.i] # red 

  def draw(self, canvas: pygame.Surface, pix_square_size: float):
    # check whether to draw entity from parent class
    if not self.draw_entity: return
    # Draw key as a rectangle
    pygame.draw.rect(
        canvas,
        self.color,
        pygame.Rect(
            pix_square_size * self.state.p_pos,
            (pix_square_size, pix_square_size),
        ),
    )
     

class Agent(Entity):  # properties of agent entities
  def __init__(self, name, world):
    super().__init__()
    self.name = name
    # the world the agent is in
    self.world: World = world
    # state
    self.state = EntityState()
    # color
    self.color = (0, 0, 255) # blue
    # action
    self.action = Action()
    # script behavior to execute
    self.action_callback = None

  def draw(self, canvas: pygame.Surface, pix_square_size: float):
    # check whether to draw entity from parent class
    if not self.draw_entity: return
    # draw agent as a circle
    pygame.draw.circle(
      canvas, 
      self.color,
      (self.state.p_pos + 0.5) * pix_square_size,
      pix_square_size/3
    )

  def _get_entity(self, entity: Union[int, str, Entity]):
    # gets correct entity given multi-type input
    if isinstance(entity, int):
      entity = list(self.world.objects.values())[entity]
    elif isinstance(entity, str):
      entity = self.world.objects[entity]
    elif isinstance(entity, Entity):
      pass
    else:
      raise Exception("entity provided is not any of these [int, str, Entity]")

    return entity

  def act(self, action):
    # applies action to move robot
    self.world.step(action)

  def explore(self):
    """
    GPT function: returns id and name of objects in same room as agent
    """
    # returns the objects found in the room
    print(f"""I found the following objects in the room:
    {[(i, n) for i, n in enumerate(list(self.world.objects.keys()))]}
    """)
    #return self.world.objects

  def goto(self, entity: Union[int, str, Entity]):
    """
    GPT function: moves the robot to same location as entity.
    The entity can be passed as its id, name or Entity object.
    """
    # get entity object
    entity = self._get_entity(entity)

    # compute path from source to target (tuples as input for dijkstra)
    path = nx.dijkstra_path(self.world.graph,
      tuple(self.state.p_pos), 
      tuple(entity.state.p_pos)
    )[1:] # remove source
    # convert waypoints to np.array
    path = [np.array(xy) for xy in path]

    # compute needed action from current pos to next waypoint
    for xy in path:
      action = xy - self.state.p_pos
      self.world.step(action)
      sleep(self.world.wait_time_s) # sleep as in rendering

    print(f"Agent is at same location as {entity.name}")

  def pick(self, entity: Union[int, str, Entity]):
    """
    GPT function: agent picks entity. It simply stops drawing the object
    """
    # for the moment it simply doesn't draw the entity that is picked up
    entity = self._get_entity(entity)

    # check that agent is at entity's location
    if not np.array_equal(self.state.p_pos, entity.state.p_pos):
      print("Agent is not at same location as entity")
      return 

    entity.draw_entity = False
    print(f"Entity {entity.name} was picked up")

  def drop(self, entity: Union[int, str, Entity]):
    """
    GPT function: Agent drops entity at its location. It simply starts drawing again the entity
    """
    entity = self._get_entity(entity)

    # check that entity was actually picked
    if entity.draw_entity:
      print(f"entity {entity.name} was not picked")
      return

    # update entity's position and draw it since it's dropped
    entity.state.p_pos = self.state.p_pos
    entity.draw_entity = True
    print(f"entity {entity.name} was dropped at {list(entity.state.p_pos)}")

    


class World:
  def __init__(self, size, wait_time_s) -> None:

    # world dimensions
    self.size = size  # The size of the square grid
    self.window_size = 512
    self.edges = list(product([0, self.window_size], 
                              [0, self.window_size])
              ) # list of coordinates of world vertices
    self.pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels
    # create navigation graph
    self.graph = nx.grid_graph(dim=(size,size))
    # wait time when updating state
    self.wait_time_s = wait_time_s

    # init agent
    self.agent: Agent = Agent(name="agent", world=self)

    # init objects
    self.objects = {(name:=f"key_{i}") : Key(name=name, i=i) for i in range(3)}


  def step(self, action: Union[int, np.ndarray]):
    if isinstance(action, int):
      # Map the action (element of {0,1,2,3}) to the direction we walk in
      direction = self.agent.action._action_to_direction[action]
    else:
      assert isinstance(action, np.ndarray), "action neither Int nor np.array"
      direction = action
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
    for obj in list(self.objects.values()):
      obj.state.p_pos = np.random.randint(0, self.size-1, (2, ))
      obj.draw_entity = True

    return self._get_obs(), self._get_info()


  def _get_obs(self):
    # return position of agent and objects
    return {entity.name: entity.state.p_pos for entity in [self.agent]+list(self.objects.values())}

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
    for entity in list(self.objects.values())+[self.agent]:
      entity.draw(canvas, self.pix_square_size)

    # draw delimiting edges of canvas
    pygame.draw.line(canvas, 0, self.edges[0], self.edges[1], width=3)
    pygame.draw.line(canvas, 0, self.edges[1], self.edges[3], width=3)
    pygame.draw.line(canvas, 0, self.edges[3], self.edges[2], width=3)
    pygame.draw.line(canvas, 0, self.edges[2], self.edges[0], width=3)

    return canvas

    
