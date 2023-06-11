import requests

def get_user_input():
    return input('Enter instruction for robot: ')

def send_instruction_to_robot(instruction):
    response = requests.post('http://127.0.0.1:5000/robot_action', json={'instruction': instruction})
    # print(response.text, flush=True)
    return response.json()['result']

if __name__ == '__main__':
    while True:
        instruction = get_user_input()
        result = send_instruction_to_robot(instruction)
        print("robot answered:", result)