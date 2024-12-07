import random
import os

import yaml

jokes = None

def load_jokes(file_path: str):
    global jokes
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            jokes = yaml.safe_load(f.read())
    

def choose_joke(index: int):
    global jokes
    jl = jokes["jokes"]
    if index < 0:
        index = random.randint(0, len(jl) - 1)
    index = index % len(jl)
    return f"{jl[index]["title"]}\n{jl[index]["content"]}"
    
if __name__ == "__main__":
    load_jokes("knowledge-base/jokes.yaml")
    print(choose_joke(-1))