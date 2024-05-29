from typing import List
from pymem.ptypes import RemotePointer
import pymem

def getPointerAddress(memory: pymem.Pymem, base: int, offsets: List[int]):
    remote_pointer = RemotePointer(memory.process_handle, base)
    for offset in offsets:
        if offset != offsets[-1]:
            remote_pointer = RemotePointer(memory.process_handle, remote_pointer.value + offset)
        else:
            return remote_pointer.value + offset

def read_value(memory, value_name):
    try:
        if value_name == "hp":
            baseAddress = memory.base_address
            value = memory.read_int(getPointerAddress(memory, baseAddress + 0x01ACD758, [0, 0x3E8]))
            value = value if not value <= 0 else 0 # If hp has negative values return 0
        elif value_name == "inGame":
            baseAddress = memory.base_address
            value = memory.read_bool(baseAddress + 0x1D260A8)
        elif value_name == "inLoadingScreen":
            value = read_value(memory, "inGame") and (read_value(memory, "hp") is None)
        elif value_name == "isAlive":
            value = read_value(memory, "inGame") and (not read_value(memory, "hp") <= 0)
        else:
            raise ValueError(f"Invalid value name: {value_name}")
    except Exception as e:
        # print(f"Error reading {value_name}: {e}")
        value = None

    return value