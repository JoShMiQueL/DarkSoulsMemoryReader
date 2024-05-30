import asyncio
import json
import websockets

class WebSocketServer:
  def __init__(self):
    self.prev_state = None
    self.clients = set()

  async def handler(self, websocket):
    self.clients.add(websocket)
    try:
      await self.broadcast(json.dumps(self.prev_state))
      async for message in websocket:
        pass
    finally:
      self.clients.remove(websocket)

  async def broadcast(self, message):
    if self.clients:
      await asyncio.wait([asyncio.create_task(client.send(message)) for client in self.clients])

  async def start(self, host='0.0.0.0', port=8765):
    async with websockets.serve(self.handler, host, port):
      await asyncio.Future()  # Run forever