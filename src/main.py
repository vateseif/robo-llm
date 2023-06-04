import gymnasium

from gym_env.grid_world import GridWorldEnv

env = GridWorldEnv(render_mode='human', size=10)
env.reset()

for i in range(100):
  env.step(i%4)

env.close()