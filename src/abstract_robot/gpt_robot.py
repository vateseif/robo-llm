import os
import ast
import openai
from dotenv import load_dotenv

load_dotenv()
try:
  openai.api_key = open(os.path.dirname(__file__) + '/openai.key', 'r').readline().rstrip()
except:
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
Call the finished() function once you think you are done with the task.
Always make sure to explore everything. Because if you don't you might not be able to complete the task. Only call one API function at a time and provide the argument correctly to within the function."""

FUNCTIONS = [
      {
        "name": "explore",
        "description": "Explores the room the robot is currently in and returns objects that are in the same room",
        "parameters": {
          "type":"object",
          "properties": {}
        }
      }, 
      {
        "name": "goto",
        "description": "Moves the robot to the location of the object provided as a string with its name",
        "parameters":{
          "type": "object",
          "properties":{
            "objectname":{
              "type": "string",
              "description": "Name of the object the robot has to go to",
            }
          }
          
        },
        "required": ["objectname"]
      },
      {
        "name": "pickup",
        "description": "Robot picks up an object provided as a string with its name. The robot has to be at the same location as the object",
        "parameters":{
          "type": "object",
          "properties":{
            "objectname":{
              "type": "string",
              "description": "Name of the object the robot has to pick up",
            }
          }
          
        },
        "required": ["objectname"]
      },
      {
        "name": "drop",
        "description": "Robot drops an object that it peviously picked up. Object is to be provided as a string with its name. The robot has to be at the same location as the object",
        "parameters":{
          "type": "object",
          "properties":{
            "objectname":{
              "type": "string",
              "description": "Name of the object the robot has to drop",
            }
          }
          
        },
        "required": ["objectname"]
      },
      {
        "name": "opendoor",
        "description": "Robot opens a door with its key",
        "parameters":{
          "type": "object",
          "properties":{
            "doorname":{
              "type": "string",
              "description": "Name of the door the robot has to open",
            },
            "keyname":{
              "type": "string",
              "description": "Name of the key the robot uses to open doorname",
            }
          }
          
        },
        "required": ["doorname", "keyname"]
      },
      {
        "name": "finished",
        "description": "Stops the robots and closes the simulation",
        "parameters": {
          "type":"object",
          "properties": {}
        }
      }, 
    ]

class GPTRobot():
    def __init__(self, task_message, robot_explore, robot_pickup, robot_moveto, robot_putdown, robot_opendoor, finished):
        self.task_message = task_message
        self.messages = [
                    {"role": "system", "content": SYSTEM_PROMPT_SIMPLE},
                    {"role": "user", "content": "Please complete the following task: " + self.task_message + "\nAlways explain what you are doing and why (without naming the functions explicitely). Then in a new line call the API function of the robot. Call one API function at a time."},
                ]
        self.functions = {
          "explore": robot_explore,
          "pickup": robot_pickup,
          "drop": robot_putdown,
          "goto": robot_moveto,
          "opendoor": robot_opendoor,
          "finished": finished
        }

    def next_action(self, robot_answer=None):
        if robot_answer is not None:
            self.messages.append({"role": "user", "content": robot_answer})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages = self.messages,
            functions=FUNCTIONS,
            max_tokens=256,
        )
        
        fn = completion.choices[0].message["function_call"].name
        args = completion.choices[0].message["function_call"].arguments
        message_string = fn + args

        #print message
        print('\033[91m' + message_string + '\033[0m')
        
        # apply message
        result = self.functions[fn](*list(ast.literal_eval(args).values()))
        
        return result
    



