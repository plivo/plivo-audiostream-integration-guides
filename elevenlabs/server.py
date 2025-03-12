import asyncio
import base64
import json
import sys
import websockets
import traceback
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs


# Load the configuration from a JSON file (API keys, settings, etc.)
def load_config(file_path='config.json'):
    global CONFIG
    with open(file_path, 'r') as f:
        CONFIG = json.load(f)
    return CONFIG


# Initialize configuration from the JSON file
CONFIG = load_config()

# Initialize the ElevenLabs client using the API key from the config file
tts_client = ElevenLabs(api_key=CONFIG['elevenlabs_api_key'])


# Converts text to speech using ElevenLabs API and sends it via Plivo WebSocket
async def text_to_speech_file(text: str, plivo_ws):
    """
    Converts the given text into speech using the ElevenLabs API and sends the audio data
    to Plivo via WebSocket.

    Args:
        text (str): The text to be converted into speech.
        plivo_ws: The Plivo WebSocket connection.
    """
    # Call ElevenLabs API to convert text into speech
    response = tts_client.text_to_speech.convert(
        voice_id="XrExE9yKIg1WjnnlVkGX",  # Using a pre-made voice (Adam)
        output_format="ulaw_8000",  # 8kHz audio format
        text=text,
        model_id="eleven_turbo_v2_5",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    # Collect the audio data from the response
    output = bytearray(b'')
    for chunk in response:
        if chunk:
            output.extend(chunk)

    # Encode the audio data in Base64 format for transmission
    encode = base64.b64encode(output).decode('utf-8')

    # Send the audio data to Plivo WebSocket in the expected JSON format
    await plivo_ws.send(json.dumps({
        "event": "playAudio",
        "media": {
            "contentType": "audio/x-mulaw",
            "sampleRate": 8000,
            "payload": encode
        }
    }))


# Handles Plivo WebSocket communication for receiving and processing audio
async def plivo_handler(plivo_ws):
    """
    Handles incoming WebSocket messages from Plivo and processes them accordingly.
    """

    async def plivo_receiver(plivo_ws):
        print('Plivo receiver started')
        try:
            async for message in plivo_ws:
                try:
                    # Decode incoming WebSocket message
                    data = json.loads(message)

                    # If the event is 'start', generate and send speech
                    if data['event'] == 'start':
                        text = generate_text()
                        await text_to_speech_file(text, plivo_ws)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    traceback.print_exc()
        except websockets.exceptions.ConnectionClosedError:
            print(f"WebSocket connection closed")
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()

    # Start receiving messages from the WebSocket
    await plivo_receiver(plivo_ws)


# Router to handle incoming WebSocket connections and direct them to plivo_handler
async def router(websocket, path):
    """
    Handles WebSocket connections and routes requests to appropriate handlers.

    Args:
        websocket: The WebSocket connection object.
        path (str): The WebSocket request path.
    """
    if path == '/stream':
        print('Plivo connection incoming')
        await plivo_handler(websocket)


# Generates a sample text for speech synthesis
def generate_text():
    """
    Generates a sample text to be converted into speech.

    Returns:
        str: The generated text message.
    """
    txt = 'This is a sample text message to text-to-speech capabilities of ElevenLabs. Based on the use case, this text can be generated using LLM.'
    return txt


# Main function to start the WebSocket server
def main():
    """
    Initializes and starts the WebSocket server on localhost at port 9000.
    """
    # Start WebSocket server on localhost:9000
    server = websockets.serve(router, 'localhost', 9000)

    # Run the event loop for the WebSocket server
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()


# Entry point for running the script
if __name__ == '__main__':
    sys.exit(main() or 0)
