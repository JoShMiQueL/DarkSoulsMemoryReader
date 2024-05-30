import asyncio
from enum import Enum
import json
import os
import time
from pymem import Pymem
import pymem

from WebSocketServer import WebSocketServer
from utils import getPointerAddress

class ValueName(Enum):
    HP = "hp"
    IN_GAME = "inGame"
    IN_LOADING_SCREEN = "inLoadingScreen"
    IS_ALIVE = "isAlive"

class GameReader:
  __memory: Pymem
  __prev_state: dict = {}
  __curr_state = __prev_state
  __websocket_server: WebSocketServer

  def __init__(self, websocket_server: WebSocketServer):
    self.__websocket_server = websocket_server
    try:
      self.__memory = Pymem("DarkSoulsRemastered")
    except pymem.exception.CouldNotOpenProcess:
      print("Please run this script as administrator.")
      os._exit(1)
    except pymem.exception.ProcessNotFound:
      print("Dark Souls Remastered is not running.")
      os._exit(1)
    except Exception as ex:
      print(f"An error occurred: {ex}")
      os._exit(1)
  
  def __read_state(self):
    inGame = self.__read_value(ValueName.IN_GAME)
    hp = self.__read_value(ValueName.HP)
    inLoadingScreen = self.__read_value(ValueName.IN_LOADING_SCREEN)
    # isAlive = self.__read_value(ValueName.IS_ALIVE)

    state = {
      "inGame": inGame,
      "inLoadingScreen": inLoadingScreen,
      "hp": hp,
    }

    return state

  def __read_value(self, value_name: ValueName):
    try:
        baseAddress = self.__memory.base_address
        if value_name == value_name.HP:
            value = self.__memory.read_int(getPointerAddress(self.__memory, baseAddress + 0x01ACD758, [0, 0x3E8]))
            value = value if not value <= 0 else 0 # If hp has negative values return 0
        elif value_name == value_name.IN_GAME:
            value = self.__memory.read_bool(baseAddress + 0x1D260A8)
        elif value_name == value_name.IN_LOADING_SCREEN:
            value = self.__read_value(value_name.IN_GAME) and (self.__read_value(value_name.HP) is None)
        elif value_name == value_name.IS_ALIVE:
            value = self.__read_value(value_name.IN_GAME) and (not self.__read_value(value_name.HP) <= 0)
        else:
            raise ValueError(f"Invalid value name: {value_name}")
    except Exception as e:
        # print(f"Error reading {value_name}: {e}")
        value = None

    return value
  
  def __detect_state_change(self, prev_state: dict) -> tuple:
    current_state = self.__read_state()
    if current_state != prev_state:
      return current_state, True
    else:
      return current_state, False
  
  async def __state_monitor(self):
    while True:
      self.__curr_state = self.__detect_state_change(self.__prev_state)
      if (self.__curr_state[1] == True):
        print("State has changed!", self.__curr_state[0])
        self.__prev_state = self.__curr_state[0]
        self.__websocket_server.prev_state = self.__prev_state
        await self.__websocket_server.broadcast(json.dumps(self.__prev_state))
      await asyncio.sleep(0.01)
  
  async def start(self):
     await self.__state_monitor()
