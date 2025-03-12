import json
import traceback
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from plivo_audio_interface import PlivoAudioInterface

def load_config(file_path='config.json'):
    global CONFIG
    with open(file_path, 'r') as f:
        CONFIG = json.load(f)
    return CONFIG


# Initialize configuration from the JSON file
CONFIG = load_config()

# Initialize FastAPI app
app = FastAPI()

# Initialize ElevenLabs client
eleven_labs_client = ElevenLabs(api_key=CONFIG['elevenlabs_api_key'])
ELEVEN_LABS_AGENT_ID = CONFIG['elevenlabs_agent_id']


@app.get("/")
async def root():
    return {"message": "Plivo-ElevenLabs Integration Server"}


@app.websocket("/stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    audio_interface = PlivoAudioInterface(websocket)
    conversation = None

    try:
        conversation = Conversation(
            client=eleven_labs_client,
            agent_id=ELEVEN_LABS_AGENT_ID,
            requires_auth=False,
            audio_interface=audio_interface,
            callback_agent_response=lambda text: print(f"Agent said: {text}"),
            callback_user_transcript=lambda text: print(f"User said: {text}"),
        )

        conversation.start_session()
        print("Conversation session started")

        async for message in websocket.iter_text():
            if not message:
                continue

            try:
                data = json.loads(message)
                await audio_interface.handle_plivo_message(data)
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                traceback.print_exc()

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        if conversation:
            print("Ending conversation session...")
            conversation.end_session()
            conversation.wait_for_session_end()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)