import os
import time
import pymem
from utils import read_value

def main():
    mem = None
    try:
        mem = pymem.Pymem("DarkSoulsRemastered")
    except pymem.exception.CouldNotOpenProcess:
        print("Please run this script as administrator.")
        os._exit(1)
    except pymem.exception.ProcessNotFound:
        print("Dark Souls Remastered is not running.")
        os._exit(1)
    except Exception as ex:
        print(f"An error occurred: {ex}")
        os._exit(1)

    state_monitor(mem)
    

def read_state(memory: pymem.Pymem):
    inGame = read_value(memory, "inGame")
    hp = read_value(memory, "hp")
    inLoadingScreen = read_value(memory, "inLoadingScreen")
    isAlive = read_value(memory, "isAlive")

    state = {
      "inGame": inGame,
      "inLoadingScreen": inLoadingScreen,
      "hp": hp,
    }

    return state

def detect_state_change(memory: pymem.Pymem, previous_state: dict) -> tuple:
    current_state = read_state(memory)
    if current_state!= previous_state:
        return current_state, True
    else:
        return current_state, False

def state_monitor(memory: pymem.Pymem):
    prev_state = None
    while True:
        curr_state = detect_state_change(memory, prev_state)
        if (curr_state[1] == True):
            print("State has changed!", curr_state[0])
            prev_state = curr_state[0]
        time.sleep(.01)


if __name__ == "__main__":
  main()