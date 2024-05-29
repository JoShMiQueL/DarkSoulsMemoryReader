import asyncio
from GameReader import GameReader
from WebSocketServer import WebSocketServer

async def main():
    websocket_server = WebSocketServer()
    game_reader = GameReader(websocket_server)
    
    websocket_server_task = asyncio.create_task(websocket_server.start())
    game_reader_task = asyncio.create_task(game_reader.start())
    
    await asyncio.gather(websocket_server_task, game_reader_task)

if __name__ == "__main__":
  asyncio.run(main())