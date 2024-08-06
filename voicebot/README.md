# Plivo Audio Streaming Integration with Deepgram, OpenAI, and ElevenLabs

This project demonstrates a proof of concept (POC) for integrating Plivo's audio streaming with Deepgram for transcription, OpenAI's GPT-3.5-turbo for conversational responses, and ElevenLabs for text-to-speech conversion. The system is designed to act as a general assistant that can transcribe live audio, respond to queries, and convert responses back to audio.

## Features

1. Receive audio streaming data from Plivo through an exposed websocket.
2. Buffer audio until a pause of more than 500ms is detected using voice activity detection.
3. Send the buffered audio to Deepgram for transcription.
4. Send the transcription to ChatGPT (using GPT-3.5-turbo) to generate a response.
5. Convert the response to speech using ElevenLabs.
6. Send the converted speech back to Plivo.

## Requirements

- Plivo API Key
- Deepgram API Key
- OpenAI API Key
- ElevenLabs API Key

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/plivo/plivo-audiostream-integration-guides.git
   cd voicebot

2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```
   
## Running the Server

1. Replace the placeholders in the script with your actual API keys:

   - YOUR_DEEPGRAM_API_KEY
   - YOUR_OPENAI_API_KEY
   - YOUR_ELEVENLABS_API_KEY

2. Run the server:
    ```bash
    python server.py
    ```
   The server will start on `ws://localhost:5678`.

## Making the Server Publicly Accessible

To make your local server accessible over the internet, you can use tools like ngrok or localtunnel. These tools create a secure tunnel to your local server and provide a public URL that you can use for testing.

### Using ngrok

1. Install ngrok:
    ```bash
    brew install ngrok  # macOS
    # or download from https://ngrok.com/download and follow the instructions for your OS
    ```

2. Start ngrok to forward the WebSocket server port:
    ```bash
    ngrok http 5678
    ```

3. ngrok will provide a public URL (e.g., `http://your-ngrok-subdomain.ngrok.io`). Use this URL to configure Plivo and connect clients.

### Using localtunnel

1. Install localtunnel:
    ```bash
    npm install -g localtunnel
    ```

2. Start localtunnel to forward the WebSocket server port:
    ```bash
    lt --port 5678
    ```

3. localtunnel will provide a public URL (e.g., `http://your-subdomain.loca.lt`). Use this URL to configure Plivo and connect clients.


