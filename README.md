# Plivo Audio Stream Integration Guides

This repo contains following guides:

## Voice Agent

This project showcases a proof of concept (POC) that integrates Plivo's audio streaming with Deepgram for live transcription, OpenAI for generating conversational responses, and ElevenLabs for text-to-speech conversion. The system functions as a general assistant, capable of transcribing real-time audio, understanding and responding to user queries, and converting those responses back into audio. This end-to-end solution demonstrates the potential for creating intelligent, voice-interactive applications.

## Deepgram

This project focuses on integrating Deepgram's advanced speech-to-text technology with Plivo's audio streaming service to enable seamless live transcription. The system is designed to handle real-time audio streams from Plivo, process them on the server, and forward the audio data to Deepgram for transcription. Clients can connect to the server and receive continuous updates of the live transcriptions, providing an efficient solution for real-time speech-to-text conversion in various applications.

## Dialogflow

This project is an Express application that integrates Plivo's audio streaming service with Dialogflow to enable smooth voice-based interactions. The system captures audio streams from Plivo, processes them, and sends the data to Dialogflow for natural language understanding, allowing users to interact with the application via voice commands in real-time. This integration provides an efficient solution for building voice-driven applications and services

## Sentiment Analysis

This reference application demonstrates how to leverage Amazon Transcribe and Comprehend's streaming capabilities alongside Plivo’s audio streaming service for real-time call analysis. The application exposes a WebSocket that receives raw audio streams from live phone calls via Plivo's service. Once a call ends, the application handles a hangup callback and uploads the raw audio to an S3 bucket. The audio is then processed to generate transcripts and sentiment analysis, offering insights into the call's content and tone.