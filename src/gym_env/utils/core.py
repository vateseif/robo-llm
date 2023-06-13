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


class Room(Entity):
  def __init__(self, name:str, size:int):
    # name
    self.name = name
    # room size (indicates how much to go down and left from top right point of main room)
    self.size = size
    # room vertices
    self.vtl, self.vbl, self.vbr, self.vtr = (np.array([0, 0]), np.array([0, size]), np.array([size, size]), np.array([size, 0]))
    # door, TODO: change door name
    if name.startswith("main"):
      self.door = Door(name="main_door", loc=np.mean((self.vbl, self.vbr), 0), room=self, is_open=True)
    else:
      self.door = Door(name="door_0", loc=np.mean((self.vbl, self.vbr), 0), room=self, is_open=False) # main room has no door (u cannot escape)

  def draw(self, canvas: pygame.Surface, pix_square_size: float):
    # draw delimiting edges of canvas
    pygame.draw.line(canvas, 0, self.vtl*pix_square_size, self.vbl*pix_square_size, width=3)
    pygame.draw.line(canvas, 0, self.vbl*pix_square_size, self.vbr*pix_square_size, width=3)
    pygame.draw.line(canvas, 0, self.vbr*pix_square_size, self.vtr*pix_square_size, width=3)
    pygame.draw.line(canvas, 0, self.vtr*pix_square_size, self.vtl*pix_square_size, width=3)
    # draw door
    self.door.draw(canvas, pix_square_size)

class Door(Entity):
  def __init__(self, name: str, loc: np.ndarray, room: Room, is_open: bool):
    super().__init__()
    self.name = name
    # location
    self.state.p_pos = loc
    # door always starts off closed
    self.open = is_open
    # room
    self.room = room
    # key that opens this door
    self.key: Key = None


  def draw(self, canvas: pygame.Surface, pix_square_size: float):
    # if door is open color it white
    color = (255, 255, 255) if self.open else (0, 0, 0)
    # Draw key as a rectangle
    pygame.draw.rect(
        canvas,
        color,
        pygame.Rect(
            (self.state.p_pos - np.array([0, 0.5]))*pix_square_size,
            (pix_square_size, pix_square_size),
        ),
    )


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
    # room
    self.room: Room = None

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
      entity = list(self.world.keys.values())[entity]
    elif isinstance(entity, str):
      entity = self.world.keys[entity]
    elif isinstance(entity, Entity) and not isinstance(entity, Room):
      pass
    else:
      raise Exception("entity provided is not any of these [int, str, Entity]")

    return entity

  def act(self, action):
    # applies action to move robot
    self.world.step(action)

  def explore(self):
    """
    GPT function: returns id and name of keys in same room as agent
    """
    # returns the objects found in the room
    # returns a key if in main room or if it's in an open room 
    # otherwise it returns the door of the closed room
    s = f"I found the following objects in the room: "
    s += ", ".join([k.name if k.room.door.open else k.room.door.name for k in list(self.world.keys.values())])
    return s

  def goto(self, entity_name: str):
    """
    GPT function: moves the robot to same location as entity.
    The entity can be passed as its id, name or Entity object.
    """
    # get entity object
    entity = self.world.entities[entity_name]
    if isinstance(entity, Room): entity = entity.door

    # check if it was a key and it was picked already
    if isinstance(entity, Key) and not entity.draw_entity:
      return f"{entity_name} was picked already."

    try:
      # compute path from source to target (tuples as input for dijkstra)
      path = nx.dijkstra_path(self.world.graph,
        tuple(self.state.p_pos), 
        tuple(entity.state.p_pos)
      )[1:] # remove source
    except:
      return f"{entity.name} is not accesible because you didn't open {entity.room.door.name} yet"
    
    # convert waypoints to np.array
    path = [np.array(xy) for xy in path]

    # compute needed action from current pos to next waypoint
    for xy in path:
      action = xy - self.state.p_pos
      self.world.step(action)
      sleep(self.world.wait_time_s) # sleep as in rendering

    return f"You have moved correctly to the same location as {entity.name}."

  def pick(self, key_name: str):
    """
    GPT function: agent picks entity. It simply stops drawing the object
    """
    # for the moment it simply doesn't draw the entity that is picked up
    #entity = self._get_entity(entity)
    key = self.world.keys[key_name]

    # check if key was already picked
    if not key.draw_entity:
      return f"{key_name} is already picked."

    # check that agent is at entity's location
    if not np.array_equal(self.state.p_pos, key.state.p_pos):
      return f"Cannot pick {key_name} because you are not at the same location."

    key.draw_entity = False
    return f"{key_name} was picked up"

  def drop(self, key_name: str):
    """
    GPT function: Agent drops entity at its location. It simply starts drawing again the entity
    """
    key = self.world.keys[key_name]

    # check that entity was actually picked
    if key.draw_entity:
      return f"entity {key.name} was not picked. You need pick it first before dropping it."

    # update entity's position and draw it since it's dropped
    key.state.p_pos = self.state.p_pos
    key.draw_entity = True
    return f"entity {key.name} was dropped."

  def open(self, door_name:str, key_name:str):
    """
    GPT function: opens a room givent its name and the name of the key. Thekey has to be picked
    """
    door = self.world.entities[door_name]
    key = self.world.keys[key_name]
    # check that key was actually picked
    if key.draw_entity:
      return f"{key.name} cannot be used to open {door_name} because it was not picked"

    # check that the key is the one that opens the dorr
    if door.key.name != key_name:
      return f"{key_name} cannot be used to open {door_name}. You have to open {door_name} with {door.key.name}."
    
    # goto room
    self.goto(door_name)
    # open door
    door.open = True
    # add new room to navigation graph
    room_graph = nx.grid_graph(dim=(door.room.size, door.room.size))
    self.world.graph = nx.compose(self.world.graph, room_graph)
    self.world.graph.add_edge(tuple(door.state.p_pos), tuple(door.state.p_pos-np.array([0, 1])))

    return f"{door_name} has been opened correctly"

class World:
  def __init__(self, size, wait_time_s) -> None:

    # world dimensions
    self.size = size  # The size of the square grid
    self.window_size = 512
    self.vertices = list(product([0, self.window_size], 
                              [0, self.window_size])
              ) # list of coordinates of world vertices
    self.pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels
    # wait time when updating state
    self.wait_time_s = wait_time_s

    # init agent
    self.agent: Agent = Agent(name="agent", world=self)

    # create rooms
    self.rooms = {(name:="main_room") : Room(name, size=size)} # room that contains all other rooms
    self.rooms.update({(name:=f"room_{i}") : Room(name, size=size//3) for i in range(1)})

    # init keys
    self.keys = {(name:=f"key_{i}") : Key(name=name, i=i) for i in range(3)}

    # store all entities
    self.entities = self.rooms | self.keys
    # add doors to entity
    self.entities.update({r.door.name: r.door for r in self.rooms.values() if not r.door.name.startswith("main")})

    # create navigation graph
    self.graph = self._init_graph()

  def _init_graph(self):
    # create navigation graph
    graph = nx.grid_graph(dim=(self.size, self.size))
    # remove nodes of closed rooms
    for room in self.rooms.values():
      if room.name.startswith("main"): continue
      room_nodes = product(list(range(room.size)), list(range(room.size)))
      for node in room_nodes:
        graph.remove_node(node)
    return graph

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

    # set random location of agent always in main_room
    self.agent.state.p_pos = np.random.randint(self.rooms['room_0'].size, self.size-1, (2,))
    # init first key always in main_room
    self.keys['key_0'].state.p_pos = np.random.randint(self.rooms['room_0'].size, self.size-1, (2,))
    self.keys['key_0'].draw_entity = True
    self.keys['key_0'].room = self.rooms['main_room']
    # init second key always in room_0 
    self.keys['key_1'].state.p_pos = np.random.randint(0, self.rooms['room_0'].size-1, (2,))
    self.keys['key_1'].draw_entity = True
    self.keys['key_1'].room = self.rooms['room_0']
    self.rooms['room_0'].door.key = self.keys['key_0']
    self.rooms['room_0'].door.open = False
    # set random location of all keys apart from first 2
    for obj in list(self.keys.values())[2:]:
      obj.state.p_pos = np.random.randint(0, self.size-1, (2, ))
      obj.draw_entity = True
      if np.any(obj.state.p_pos > self.rooms['room_0'].size-1):
        obj.room = self.rooms['main_room']
      else:
        obj.room = self.rooms['room_0']

    # init  graph
    self.graph = self._init_graph()

    return self._get_obs(), self._get_info()


  def _get_obs(self):
    # return position of agent and keys
    return {entity.name: entity.state.p_pos for entity in [self.agent]+list(self.keys.values())}

  def _get_info(self):
    # added this function to be conformed with gymnasium's way of doing
    return None

  def render(self):
    pass

  def _render_frame(self):
    # create canvas to draw on
    canvas = pygame.Surface((self.window_size, self.window_size))
    canvas.fill((255, 255, 255))
    # draw keys
    for obj in self.keys.values():
      obj.draw(canvas, self.pix_square_size)
    # draw rooms
    for room in self.rooms.values():
      room.draw(canvas, self.pix_square_size)
    # draw agent
    self.agent.draw(canvas, self.pix_square_size)

    return canvas

    
