import openai
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT_FULL = """You are the cognitive center of a robot. This means, you have a task to complete and you can use the given API of the robot to complete the task. The robot will tell you if an API call failed or how it succeeded, so you can react to it.
The robot acts in 2D, so no need to worry about the height coordinate.

The API at your disposal (the call function is in big letters):
 * EXPLORE(roomname)
 * PICKUP(objectname)
 * OPENDOOR(doorname)
 * MOVETO(objectname or roomname or doorname)
 * PUTDOWNSOMEWHERE(objectname)
 * PUTDOWN(objectname)
 * GETLOCATION(objectname)

call FINISHED as soon as you think you're done.

Always make sure to explore everything. Because if you don't you might not be able to complete the task. Each room only needs to be explored once."""

SYSTEM_PROMPT_SIMPLE = """You are the cognitive center of a robot. This means, you have a task to complete and you can use the given API of the robot to complete the task. The robot will tell you if an API call failed or how it succeeded, so you can react to it.

The API at your disposal (the call function is in big letters):
 * EXPLORE()
 * PICKUP(objectname)
 * MOVETO(objectname)
 * PUTDOWN(objectname)

call FINISHED as soon as you think you're done.

Always make sure to explore everything. Because if you don't you might not be able to complete the task. Only call one API function at a time."""

class GPTRobot():
    def __init__(self, task_message, robot_explore, robot_pickup, robot_moveto, robot_putdown, finished):
        self.task_message = task_message
        self.messages = [
                    {"role": "system", "content": SYSTEM_PROMPT_SIMPLE},
                    {"role": "user", "content": "Please complete the following task: " + self.task_message + "\nAlways explain what you are doing and why before calling the API function of the robot."},
                ]
        self.robot_explore = robot_explore
        self.robot_pickup = robot_pickup
        self.robot_moveto = robot_moveto
        self.robot_putdown = robot_putdown
        self.finished = finished

    def next_action(self, robot_answer=None):
        if robot_answer is not None:
            self.messages.append({"role": "user", "content": robot_answer})
        if self.messages == []:
            bot_answer = "EXPLORE()"
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages = self.messages,
            max_tokens=256,
        )
        message_string = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": message_string})
        result = self.apply_message(message_string)
        return result
    
    def apply_message(self, message_string):
        if "FINISEHD" in message_string:
            return self.finished()
        if "EXPLORE" in message_string:
            # EXPLORE(roomname), extract roomname
            # roomname = message_string.split("EXPLORE(")[1].split(")")[0]
            return self.robot_explore()
        if "PICKUP" in message_string:
            # PICKUP(objectname), extract objectname
            objectname = message_string.split("PICKUP(")[1].split(")")[0]
            return self.robot_pickup(objectname)
        if "MOVETO" in message_string:
            # MOVETO(objectname or roomname or doorname), extract objectname
            objectname = message_string.split("MOVETO(")[1].split(")")[0]
            return self.robot_moveto(objectname)
        if "PUTDOWN" in message_string:
            # PUTDOWN(objectname), extract objectname
            objectname = message_string.split("PUTDOWN(")[1].split(")")[0]
            return self.robot_putdown(objectname)



