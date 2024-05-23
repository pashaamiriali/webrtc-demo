import asyncio
import websockets
async def hello ():
    uri = 'ws://192.168.30.10:8765'
    async with websockets.connect(uri) as websocket:
        name =input("What's your name? ")
        await websocket.send(name)
        print(f'Client sent {name}')

        greeting = await websocket.recv()
        print(f'Client received {greeting}')
        await hello()


if __name__ == "__main__":
    asyncio.run(hello())