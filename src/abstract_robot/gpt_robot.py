import openai
from dotenv import load_dotenv
import os
load_dotenv()
openai.api_key = open(os.path.dirname(__file__) + '/openai.key', 'r').readline().rstrip()

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
 * PICKUP(keyname)
 * MOVETO(keyname)
 * PUTDOWN(keyname)
 * OPENDOOR(doorname, keyname)

call FINISHED as soon as you think you're done.

Always make sure to explore everything. Because if you don't you might not be able to complete the task. Only call one API function at a time and provide the argument correctly to within the function."""

class GPTRobot():
    def __init__(self, task_message, robot_explore, robot_pickup, robot_moveto, robot_putdown, robot_opendoor, finished):
        self.task_message = task_message
        self.messages = [
                    {"role": "system", "content": SYSTEM_PROMPT_SIMPLE},
                    {"role": "user", "content": "Please complete the following task: " + self.task_message + "\nAlways explain what you are doing and why (without naming the functions explicitely). Then in a new line call the API function of the robot. Call one API function at a time."},
                ]
        self.robot_explore = robot_explore
        self.robot_pickup = robot_pickup
        self.robot_moveto = robot_moveto
        self.robot_putdown = robot_putdown
        self.robot_opendoor = robot_opendoor
        self.finished = finished

    def next_action(self, robot_answer=None):
        if robot_answer is not None:
            self.messages.append({"role": "user", "content": robot_answer})
        if self.messages == []:
            bot_answer = "EXPLORE()"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.messages,
            max_tokens=256,
        )
        options = ['EXPLORE', 'PICKUP', 'MOVETO', 'PUTDOWN', 'FINISHED']
        # if multiple options in completion.choices[0]
        if len([option for option in options if option in completion.choices[0].message.content])>1:
            print("retrying becuse multiuple API calls")
            self.messages.append({"role": "user", "content": "Can't process that. Please only call one API function at a time. Please try again and give me only the next API call."})
            return self.next_action()
        message_string = completion.choices[0].message.content
        # replace ' and " with empty string
        message_string = message_string.replace("'", "").replace('"', '')
        self.messages.append({"role": "assistant", "content": message_string})
        result = self.apply_message(message_string)
        return result
    
    def apply_message(self, message_string):
        print('\033[91m' + message_string + '\033[0m')
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
        if "OPENDOOR" in message_string:
            # OPENDOOR(objectname), extract objectname
            doorname = message_string.split("OPENDOOR(")[1].split(",")[0]
            keyname = message_string.split(f"OPENDOOR({doorname}, ")[1].split(")")[0]
            return self.robot_opendoor(doorname, keyname)
        if "FINISHED" in message_string:
            return self.finished()
        else:
            print("ERROR: unknown message: " + message_string)


