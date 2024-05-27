import asyncio
import websockets
import json


# Constants for clarity and maintainability
METHOD = "method"
LOGIN = "login"
PING = "ping"
PONG = "pong"
SEND_OFFER = "sendOffer"
RECEIVE_OFFER = "receiveOffer"
UID = "uid"
CONNECT = "connect"
USER_JOINED = "userJoined"
DATA = "data"
ERROR = "error"  # Added for error messages
users = []

# User object to encapsulate user data and connection


class User:
    def __init__(self, uid, connect):
        self.uid = uid
        self.connect = connect


async def input_socket(websocket):
    # Iterate until the connection is closed
    while True:
        try:
            if websocket.open:
                message = await websocket.recv()
                print(f"Server received: {message}")
                await handle_message(message, websocket)
        except Exception as e:
            print(f"Failed to handle websocket connection: {e}")
            # Exit the loop on error


async def handle_message(message, websocket):
    try:
        message_dict = json.loads(message)  # Load message as a dictionary
        await process_message(message_dict, websocket)  # Send error message
    except Exception as e:
        await websocket.send(json.dumps({f"Failed to parse the message {message} {e}"}))


async def process_message(message, websocket):
    print('processing message')
    if METHOD not in message:
        await websocket.send(json.dumps({ERROR: "Missing method field"}))

    # Use a dictionary for dispatching based on methods
    method_handlers = {
        LOGIN: login_user,
        SEND_OFFER: send_offer,
        PING: ping,
    }
    handler = method_handlers.get(message[METHOD])

    if handler:
        await handler(message, websocket)
    else:
        await websocket.send(json.dumps({ERROR: f"Unknown method: {message[METHOD]}"}))


async def ping(message, websocket):
    await websocket.send({PONG: 'pong'})


async def broadcast_messages(message):
    for user in users:
        try:
            print(f"Sending message to user {user.uid}")
            await user.connect.send(json.dumps(message))
        except Exception as e:
            print(f"Failed to send message: {e}")
            await user.connect.wait_closed()
            users.remove(user)


async def login_user(message, websocket):
    user = User(message[UID], websocket)
    users.append(user)
    await broadcast_messages(create_user_joined_message(user.uid))


def create_user_joined_message(uid):
    return {METHOD: USER_JOINED, DATA: {UID: uid}}


async def send_offer(message):
    await broadcast_messages({METHOD: RECEIVE_OFFER, DATA: message[DATA]})


async def main():
    async with websockets.serve(input_socket, "0.0.0.0", 8765):
        await asyncio.Future()  # Run server indefinitely


if __name__ == "__main__":
    asyncio.run(main())
