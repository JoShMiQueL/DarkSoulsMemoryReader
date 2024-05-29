import asyncio
import websockets

class WebSocketServer:
  def __init__(self):
    self.clients = set()

  async def handler(self, websocket, path):
    self.clients.add(websocket)
    try:
      async for message in websocket:
        pass
    finally:
      self.clients.remove(websocket)

  async def broadcast(self, message):
    if self.clients:
      await asyncio.wait([asyncio.create_task(client.send(message)) for client in self.clients])

  async def start(self, host='localhost', port=8765):
    async with websockets.serve(self.handler, host, port):
      await asyncio.Future()  # Run forever