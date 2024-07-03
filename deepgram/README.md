# Deepgram and Plivo Integration for Live Transcription

This project demonstrates how to integrate Deepgram's speech-to-text capabilities with Plivo's audio streaming service to achieve live transcription. The server handles incoming audio streams from Plivo, processes them, and sends the audio to Deepgram for real-time transcription. Clients can connect to the server to receive live transcription updates.

## Table of Contents

- [Objective](#objective)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Testing the Integration](#testing-the-integration)
- [Making the Server Publicly Accessible](#making-the-server-publicly-accessible)

## Objective

The objective of this project is to create a system that streams audio from Plivo to Deepgram for live transcription and allows clients to receive transcription updates in real-time.

## Prerequisites

- Python 3.7+
- Plivo account and configured audio streaming
- Deepgram account and API key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/plivo/plivo-audiostream-integration-guides.git
    cd deepgram
    ```

2. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

1. Save your Deepgram API key in the `deepgram_connect` function:
    ```python
    extra_headers = {
        'Authorization': 'Token YOUR_DEEPGRAM_API_KEY'
    }
    ```

2. Run the server:
    ```bash
    python server.py
    ```

   The server will start on `ws://localhost:5678`.

## Testing the Integration

1. **Plivo Setup**: Configure your Plivo account to stream audio to the `/stream` endpoint of your server.

2. **Client Subscription**: Connect a WebSocket client to the `/client` endpoint and subscribe to a stream by sending the `callSid` of the desired stream.

3. **Transcription**: The client will receive live transcription text from the server.

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
