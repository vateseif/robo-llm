from gym_env.simple import GridWorldEnv
from abstract_robot.gpt_robot import GPTRobot
import time
import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="../configs", config_name="simple_room")
def run(cfg : DictConfig) -> None:
    print("starting")
    # init env
    env = GridWorldEnv(render_mode='human', size=100, wait_time_s=0.1, cfg=cfg)
    # start env
    # env.reset()
    env.run()
    # get agent
    agent = env.world.agent

    # task_message = "Put key_0 on key_1"
    task_message = input("Please enter the task message: ")

    explore = agent.explore
    pickup = agent.pick
    moveto = agent.goto
    putdown = agent.drop
    opendoor = agent.open
    isfinished = False
    def finished():
        global isfinished
        print("finished. shutting down.")
        time.sleep(3)
        isfinished = True


    brain = GPTRobot(task_message, explore, pickup, moveto, putdown, opendoor, finished)
    last_robot_message = None
    while not isfinished:
        print("next action")
        last_robot_message = brain.next_action(last_robot_message)
        if last_robot_message != None:
            print(f"\33[92m {last_robot_message} \033[0m")


if __name__ == "__main__":
    run()