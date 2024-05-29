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