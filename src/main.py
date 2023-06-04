from gym_env import simple_continuous


from pettingzoo.mpe import simple_v3

env = simple_continuous.parallel_env(max_cycles=10000,render_mode='human', continuous_actions=True)
env.reset()


while env.agents:
    # this is where you would insert your policy
    actions = {agent: env.action_space(agent).sample() for agent in env.agents}  
    
    observations, rewards, terminations, truncations, infos = env.step(actions)
env.close()