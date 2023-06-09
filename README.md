# robo-llm

### Setup
~~~
conda create --name robollm python=3.9
conda activate robollm
pip install -r requirements.txt
~~~

### Run
Make sure to be in `src/`
~~~
python -i main.py
~~~
For the moment you can only move the agent up, down, left or right:
~~~
>> agent.act(0) # arg should be 0, 1, 2, 3
~~~
