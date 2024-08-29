import asyncio
import base64
import json
import sys
import websockets
from pydub import AudioSegment
from deepgram import Deepgram
import openai
import requests

CONFIG = {}


def load_config(file_path='config.json'):
    global CONFIG
    with open(file_path, 'r') as f:
        CONFIG = json.load(f)


# Initialize Deepgram SDK
deepgram = Deepgram(CONFIG['deepgram_api_key'])

# Configure OpenAI
openai.api_key = CONFIG['openai_api_key']

messages = []

system_msg = """You are Plivo, a chatbot assistant that helps in resolving general queries related to any fields.
When someone says hello, you will greet them and answer their questions in a polite way.
"""

messages.append({"role": "system", "content": system_msg})


async def generate_response(input_message):
    messages.append({"role": "user", "content": input_message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    reply = response.choices[0].message['content']
    messages.append({"role": "assistant", "content": reply})
    return reply


async def transcribe_audio(audio_data):
    response = await deepgram.transcription.prerecorded({'buffer': audio_data, 'mimetype': 'audio/wav'},
                                                        {'punctuate': True})
    return response['results']['channels'][0]['alternatives'][0]['transcript']


async def text_to_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech"
    headers = {
        'xi-api-key': CONFIG['elevenlabs_api_key'],
        'Content-Type': 'application/json'
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=data)
    return base64.b64encode(response.content).decode('utf-8')


async def plivo_handler(plivo_ws):
    audio_queue = asyncio.Queue()
    streamId_queue = asyncio.Queue()

    async def plivo_receiver(plivo_ws):
        print('plivo_receiver started')
        inbuffer = bytearray(b'')
        latest_inbound_timestamp = 0
        inbound_chunks_started = False

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
                            latest_inbound_timestamp = int(media['timestamp']) - 20
                        latest_inbound_timestamp = int(media['timestamp'])
                        inbuffer.extend(chunk)

                if data['event'] == 'stop':
                    break

                # Process buffer for voice activity detection
                audio_segment = AudioSegment(
                    data=inbuffer,
                    sample_width=1,
                    frame_rate=8000,
                    channels=1
                )
                if is_silent(audio_segment, 500):
                    audio_data = inbuffer[:]
                    inbuffer = bytearray(b'')
                    transcription = await transcribe_audio(audio_data)
                    chatgpt_response = await generate_response(transcription)
                    tts_audio = await text_to_speech(chatgpt_response)
                    await plivo_ws.send(json.dumps({
                        "event": "playAudio",
                        "media": {
                            "contentType": "raw",
                            "sampleRate": 8000,
                            "payload": tts_audio
                        }
                    }))

            except Exception as e:
                print(f"Error processing message: {e}")

    await plivo_receiver(plivo_ws)


def is_silent(audio_segment, pause_length_ms):
    silence_threshold = -40.0  # Adjust threshold as necessary
    silent_chunks = [chunk for chunk in audio_segment[::20] if chunk.dBFS < silence_threshold]
    silent_duration_ms = len(silent_chunks) * 20
    return silent_duration_ms >= pause_length_ms


async def router(websocket, path):
    if path == '/stream':
        print('plivo connection incoming')
        await plivo_handler(websocket)


def main():
    load_config()
    server = websockets.serve(router, 'localhost', 5678)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    sys.exit(main() or 0)
