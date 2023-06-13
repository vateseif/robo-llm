from gpt_robot import GPTRobot



robot_head = GPTRobot(
    task_message="put the apple on the table",
    # Define the robot's behavior
    robot_explore=lambda: print("I am exploring"),
    robot_pickup=lambda objectname: print("I am picking up the " + objectname),
    robot_moveto=lambda objectname: print("I am moving to the " + objectname),
    robot_putdown=lambda objectname: print("I am putting down the " + objectname),
    finished=lambda: print("I am finished"),
)

robot_head.next_action()
print("I found: apple, table, chair")
robot_head.next_action("I found: apple, table, chair")
robot_head.next_action("moved to the apple")
robot_head.next_action("picked up the apple")
robot_head.next_action("moved to the table")
robot_head.next_action("put down the apple")
robot_head.next_action()
robot_head.next_action()
