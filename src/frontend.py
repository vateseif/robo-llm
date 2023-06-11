from flask import Flask, request

app = Flask(__name__)

@app.route('/robot_action', methods=['POST'])
def robot_action():
    # Get the instruction from the request
    instruction = request.json['instruction']
    print("received instruction: " + instruction)
    # Send the instruction to the robot and get the result
    result = send_instruction_to_robot(instruction)
    print("result: " + result)

    # Return the result to the backend as a JSON
    return {'result': result}

def send_instruction_to_robot(instruction):
    # Code to send instruction to the robot and get the result
    return f'Instruction {instruction} executed successfully'

if __name__ == '__main__':
    app.run()