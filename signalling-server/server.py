import asyncio
import websockets
import json

users = []
channel = 'signalling'
method = 'method'
login = 'login'
sendOffer = "sendOffer"
receiveOffer = 'receiveOffer'
uid = 'uid'
connect = 'connect'
userJoined = 'userJoined'
data = 'data'


async def inputSocket(websocket):
    for i in range(0, 1000000000):
        try:
            if websocket.open:
                message = await websocket.recv()
                print(f'server received {message}')
                await handleMessage(message, websocket)
        except Exception as e:
            print(f'Failed to establish a websocket {e}')
            raise e


async def handleMessage(message, websocket):
    try:
        result = checkMessage(message, websocket)
        await broadcastMessages(result)
    except Exception as e:
        await websocket.send(f'error {e}')


async def broadcastMessages(message):
    for user in users:
        print(f'sending message to {user[uid]}')
        try:
            await user[connect].send(json.dumps(message))
        except Exception as e:
            print(f'failed to send message {e}')
            await user[connect].wait_closed()
            users.remove(user)


def checkMessage(message, websocket):
    msg = {}
    try:
        msg = json.loads(message)
    except Exception as e:
        return {message: "message format not supported"}
    print(f'handling message: {message}')
    if (msg[method] == login):
        return loginUser(msg, websocket)
    elif msg[method] == "sendOffer":
        return sendOffer(msg)
    return {message: "can't handle message"}


def loginUser(msg, websocket):
    user = msg[uid]
    users.append({
        uid: user,
        connect: websocket,
    })
    return createUserJoinedMessage(user)


def createUserJoinedMessage(user):
    message = {
        method: userJoined,
        data:
        {uid: user}
    }
    return message


def sendOffer(msg):
    return {method: receiveOffer, data: msg[data]}


async def main():
    async with websockets.serve(inputSocket, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
