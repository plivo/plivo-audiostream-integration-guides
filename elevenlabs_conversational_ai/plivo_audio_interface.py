import asyncio
from typing import Callable
import queue
import threading
import base64
from elevenlabs.conversational_ai.conversation import AudioInterface


class PlivoAudioInterface(AudioInterface):
    def __init__(self, websocket):
        self.websocket = websocket
        self.output_queue = queue.Queue()
        self.should_stop = threading.Event()
        self.stream_uuid = None
        self.input_callback = None
        self.output_thread = None

    def start(self, input_callback: Callable[[bytes], None]):
        self.input_callback = input_callback
        self.output_thread = threading.Thread(target=self._output_thread)
        self.output_thread.start()

    def stop(self):
        self.should_stop.set()
        if self.output_thread:
            self.output_thread.join(timeout=5.0)
        self.stream_uuid = None

    def output(self, audio: bytes):
        self.output_queue.put(audio)

    def interrupt(self):
        try:
            while True:
                _ = self.output_queue.get(block=False)
        except queue.Empty:
            pass
        asyncio.run(self._send_stop_message_to_plivo())

    async def handle_plivo_message(self, data):
        try:
            event_type = data['event']

            if event_type == "start":
                self.stream_uuid = data['start']['streamId']
                print(f"Started stream with stream_uuid: {self.stream_uuid}")

            elif event_type == "media":
                payload = data['media']['payload']
                audio_data = base64.b64decode(payload)
                if self.input_callback:
                    self.input_callback(audio_data)
        except Exception as e:
            print(f"Error in input_callback: {e}")

    def _output_thread(self):
        while not self.should_stop.is_set():
            asyncio.run(self._send_audio_to_plivo())

    async def _send_audio_to_plivo(self):
        try:
            audio = self.output_queue.get(timeout=0.2)
            audio_payload = base64.b64encode(audio).decode("utf-8")
            audio_message = {
                "event": "playAudio",
                "media": {
                    "contentType": "audio/x-mulaw",
                    "sampleRate": 8000,
                    "payload": audio_payload
                }
            }

            await self.websocket.send_json(audio_message)
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error sending audio: {e}")

    async def _send_stop_message_to_plivo(self):
        try:
            stop_message = {
                "event": "clearAudio",
                "stream_uuid": self.stream_uuid
            }
            await self.websocket.send_json(stop_message)
        except Exception as e:
            print(f"Error sending stop message to Plivo: {e}")