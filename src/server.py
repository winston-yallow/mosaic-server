import asyncio
import logging
import ssl
import websockets
from message import Message


# This is a small websocket server. It keeps track of
# all connected clients. When a new client joins or
# leaves, it will notify all other clients. Clients
# can use this server as a relay to send messages to
# other clients or to broadcast messages to all the
# clients.


SERVER_ID = 0
BROADCAST_ID = 1
FIRST_CLIENT_ID = 2

MSG_INIT = 'INIT'
MSG_DISCOVER = 'DISCOVER'
MSG_ERROR = 'ERROR'
MSG_DISCONNECT = 'DISCONNECT'

client_id_autoincrement = FIRST_CLIENT_ID
clients = {}


async def handle_message(client_id, raw_message):
    logging.info(f'Received from #{client_id}: {raw_message}')
    message = Message(raw_message)

    if not message.valid:
        await clients[client_id].send(f'{SERVER_ID} {MSG_ERROR} invalid message: {raw_message}')
        return

    if message.target_id == SERVER_ID:
        # ToDo: handle server messages
        # (eg for restoring broken webrtc connections by re-discovering)
        await clients[client_id].send(f'{SERVER_ID} {MSG_ERROR} server messages are not implemented yet')
    elif message.target_id == BROADCAST_ID:
        await asyncio.wait([ws.send(f'{client_id} {message.content}') for ws in clients.values()])
    elif message.target_id in clients:
        await clients[message.target_id].send(f'{client_id} {message.content}')
    else:
        await clients[client_id].send(f'{SERVER_ID} {MSG_ERROR} target client does not exist: {raw_message}')


async def dispatch_discovery(new_id):
    global clients
    client_ids = ','.join([str(idx) for idx in clients.keys() if idx != new_id])
    tasks = [clients[new_id].send(f'{SERVER_ID} {MSG_DISCOVER} {client_ids}')]
    tasks += [
        ws.send(f'{SERVER_ID} {MSG_DISCOVER} {new_id}')
        for idx, ws in clients.items()
        if idx != new_id
    ]
    await asyncio.wait(tasks)


async def dispatch_disconnect(client_id):
    tasks = [ws.send(f'{SERVER_ID} {MSG_DISCONNECT} {client_id}') for ws in clients.values()]
    if tasks:
        # We need to check if tasks has items because
        # asyncio does not like empty lists
        await asyncio.wait(tasks)


async def signalling(ws, path):
    global client_id_autoincrement

    client_id = client_id_autoincrement
    client_id_autoincrement += 1
    clients[client_id] = ws

    logging.info(f'Connected #{client_id}')
    await ws.send(f'{SERVER_ID} {MSG_INIT} {client_id},{len(clients)-1}')
    await dispatch_discovery(client_id)

    try:
        async for raw_message in ws:
            if type(raw_message) is bytes:
                raw_message = raw_message.decode()
            await handle_message(client_id, raw_message)
    except websockets.exceptions.ConnectionClosedError:
        logging.debug(f'Connection closed by remote #{client_id}')
    except Exception as e:
        logging.warning(f'Client #{client_id}: {e.__class__.__name__} ({e})')
    finally:
        logging.info(f'Disconnected #{client_id}')
        del clients[client_id]
        await dispatch_disconnect(client_id)


def run(host, port, cert=None, key=None):
    if cert and key:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert, key)
        start_server = websockets.serve(signalling, host, port, ssl=ssl_context)
    else:
        start_server = websockets.serve(signalling, host, port)
    logging.info(f'Server listening on {host}:{port}')
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
