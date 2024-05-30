import asyncio
from enum import Enum
import json
import os
from typing import List
from pymem import Pymem
import pymem

from Offsets import GameData, Offsets
from WebSocketServer import WebSocketServer
from utils import getPointerAddress

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
    inGame = self.__read_value(GameData.IN_GAME)
    inLoadingScreen = self.__read_value(GameData.IN_LOADING_SCREEN)
    # isAlive = self.__read_value(GameData.IS_ALIVE)
    hp = self.__read_value(GameData.HP)
    maxHp = self.__read_value(GameData.MAX_HP)
    stamina = self.__read_value(GameData.STAMINA) 
    maxStamina = self.__read_value(GameData.MAX_STAMINA)
    level = self.__read_value(GameData.LEVEL)
    souls = self.__read_value(GameData.SOULS)

    state = {
      "inGame": inGame,
      "inLoadingScreen": inLoadingScreen,
      "level": level,
      "souls": souls,
      "hp": {
         "current": hp,
         "max": maxHp
      },
      "stamina": {
         "current": stamina,
         "max": maxStamina
      }
    }

    return state

  def __read_value(self, value_name: GameData):
    try:
        baseAddress = self.__memory.base_address
        playerPtr = self.__get_offset_value(Offsets.PLAYER_PTR)
        gameDataManagerPtr = self.__get_offset_value(Offsets.GAME_DATA_MANAGER_PTR)
        if value_name == GameData.HP:
            value = self.__get_offset_value(Offsets.HP_OFFSET)
            value = value if not value <= 0 else 0 # If hp has negative values return 0
        elif value_name == GameData.MAX_HP:
            value = self.__get_offset_value(Offsets.MAX_HP_OFFSET)
        elif value_name == GameData.STAMINA:
            value = self.__get_offset_value(Offsets.STAMINA_OFFSET)
        elif value_name == GameData.MAX_STAMINA:
            value = self.__get_offset_value(Offsets.MAX_STAMINA_OFFSET)
        elif value_name == GameData.LEVEL:
            value = self.__get_offset_value(Offsets.LEVEL_OFFSET)
        elif value_name == GameData.SOULS:
            value = self.__get_offset_value(Offsets.SOULS_OFFSET)
        elif value_name == GameData.IN_GAME:
            value = self.__get_offset_value(Offsets.IN_GAME_OFFSET)
        elif value_name == GameData.IN_LOADING_SCREEN:
            value = self.__read_value(GameData.IN_GAME) and (self.__read_value(GameData.HP) is None)
        elif value_name == GameData.IS_ALIVE:
            value = self.__read_value(GameData.IN_GAME) and (not self.__read_value(GameData.HP) <= 0)
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
  
  def __get_offset_value(self, ptrAddress: List[int] | int, type: int | float | str = int):
    addr = 0
    if isinstance(ptrAddress, int):
      addr = self.__memory.base_address + ptrAddress
    elif len(ptrAddress) == 1:
      addr = self.__memory.base_address + ptrAddress[0]
    else:
      addr = getPointerAddress(self.__memory, self.__memory.base_address + ptrAddress[0], ptrAddress[1:])

    if type == int:
      return self.__memory.read_int(addr)
    elif type == float:
      return self.__memory.read_float(addr)
    elif type == str:
      return self.__memory.read_string(addr)
    
  async def start(self):
     await self.__state_monitor()
