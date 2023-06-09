from gym_env.simple import GridWorldEnv

# init env
env = GridWorldEnv(render_mode='human', size=30, wait_time_s=0.1)
# start env
env.reset()
env.run()
# get agent
agent = env.world.agent