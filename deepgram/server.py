import asyncio
import base64
import json
import sys
import websockets
from pydub import AudioSegment

subscribers = {}


async def deepgram_connect():
    extra_headers = {
        'Authorization': 'Token YOUR_DEEPGRAM_API_KEY'
    }
    while True:
        try:
            deepgram_ws = await websockets.connect(
                'wss://api.deepgram.com/v1/listen?encoding=mulaw&sample_rate=8000&channels=2&multichannel=true',
                extra_headers=extra_headers,
                ping_interval=10,
                ping_timeout=None
            )
            return deepgram_ws
        except Exception as e:
            print(f"Connection error: {e}, retrying in 5 seconds...")
            await asyncio.sleep(5)


async def plivo_handler(plivo_ws):
    audio_queue = asyncio.Queue()
    streamId_queue = asyncio.Queue()

    async def deepgram_sender(deepgram_ws):
        print('deepgram_sender started')
        while True:
            chunk = await audio_queue.get()
            if deepgram_ws.closed:
                deepgram_ws = await deepgram_connect()
            await deepgram_ws.send(chunk)

    async def deepgram_receiver(deepgram_ws):
        print('deepgram_receiver started')
        streamId = await streamId_queue.get()
        subscribers[streamId] = []
        async for message in deepgram_ws:
            data = json.loads(message)
            transcription = data.get('channel', {}).get('alternatives', [{}])[0].get('transcript', '')
            print("Transcription: ", transcription)
            for client in subscribers[streamId]:
                client.put_nowait(transcription)
        for client in subscribers[streamId]:
            client.put_nowait('close')
        del subscribers[streamId]

    async def plivo_receiver(plivo_ws):
        print('plivo_receiver started')
        BUFFER_SIZE = 20 * 160
        inbuffer = bytearray(b'')
        outbuffer = bytearray(b'')
        inbound_chunks_started = False
        outbound_chunks_started = False
        latest_inbound_timestamp = 0
        latest_outbound_timestamp = 0
        async for message in plivo_ws:
            try:
                data = json.loads(message)
                if data['event'] == 'start':
                    start = data['start']
                    streamId = start['streamId']
                    streamId_queue.put_nowait(streamId)
                if data['event'] == 'media':
                    media = data['media']
                    chunk = base64.b64decode(media['payload'])
                    if media['track'] == 'inbound':
                        if inbound_chunks_started:
                            if latest_inbound_timestamp + 20 < int(media['timestamp']):
                                bytes_to_fill = 8 * (int(media['timestamp']) - (latest_inbound_timestamp + 20))
                                inbuffer.extend(b'\xff' * bytes_to_fill)
                        else:
                            inbound_chunks_started = True
                            latest_inbound_timestamp = int(media['timestamp'])
                            latest_outbound_timestamp = int(media['timestamp']) - 20
                        latest_inbound_timestamp = int(media['timestamp'])
                        inbuffer.extend(chunk)
                    if media['track'] == 'outbound':
                        outbound_chunks_started = True
                        if latest_outbound_timestamp + 20 < int(media['timestamp']):
                            bytes_to_fill = 8 * (int(media['timestamp']) - (latest_outbound_timestamp + 20))
                            outbuffer.extend(b'\xff' * bytes_to_fill)
                        latest_outbound_timestamp = int(media['timestamp'])
                        outbuffer.extend(chunk)
                if data['event'] == 'stop':
                    break
                while len(inbuffer) >= BUFFER_SIZE and len(outbuffer) >= BUFFER_SIZE:
                    asinbound = AudioSegment(inbuffer[:BUFFER_SIZE], sample_width=1, frame_rate=8000, channels=1)
                    asoutbound = AudioSegment(outbuffer[:BUFFER_SIZE], sample_width=1, frame_rate=8000, channels=1)
                    mixed = AudioSegment.from_mono_audiosegments(asinbound, asoutbound)
                    audio_queue.put_nowait(mixed.raw_data)
                    inbuffer = inbuffer[BUFFER_SIZE:]
                    outbuffer = outbuffer[BUFFER_SIZE:]
            except:
                break
        audio_queue.put_nowait(b'')

    while True:
        try:
            deepgram_ws = await deepgram_connect()
            await asyncio.wait([
                asyncio.ensure_future(deepgram_sender(deepgram_ws)),
                asyncio.ensure_future(deepgram_receiver(deepgram_ws)),
                asyncio.ensure_future(plivo_receiver(plivo_ws))
            ])
        except websockets.exceptions.ConnectionClosedError:
            print("Connection to Deepgram lost, reconnecting...")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
        await plivo_ws.close()


async def client_handler(client_ws):
    client_queue = asyncio.Queue()
    await client_ws.send(json.dumps(list(subscribers.keys())))
    try:
        streamId = await client_ws.recv()
        streamId = streamId.strip()
        if streamId in subscribers:
            subscribers[streamId].append(client_queue)
        else:
            await client_ws.close()
    except:
        await client_ws.close()

    async def client_sender(client_ws):
        while True:
            message = await client_queue.get()
            if message == 'close':
                break
            try:
                await client_ws.send(message)
            except:
                subscribers[streamId].remove(client_queue)
                break

    await asyncio.wait([
        asyncio.ensure_future(client_sender(client_ws)),
    ])
    await client_ws.close()


async def router(websocket, path):
    if path == '/client':
        print('client connection incoming')
        await client_handler(websocket)
    elif path == '/stream':
        print('plivo connection incoming')
        await plivo_handler(websocket)


def main():
    server = websockets.serve(router, 'localhost', 5678)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    sys.exit(main() or 0)
