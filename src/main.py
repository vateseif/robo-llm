from gym_env.simple import GridWorldEnv

# init env
env = GridWorldEnv(render_mode='human')
# start env
env.reset()
env.run()
# get agent
agent = env.world.agent