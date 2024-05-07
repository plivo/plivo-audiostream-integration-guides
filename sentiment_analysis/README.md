# Amazon Transcribe & Comprehend reference Application

#### `How to setup locally?`

* Create a virtual environment named `venv`
```
pip install virtualenv
virtualenv -p /usr/bin/python2 venv
source venv/bin/activate
```

* Install requirements: 
```
pip install -r requirements.txt`
```

* Install 'ffmpeg'

* To run you can start the server by 
```
python server.py
```

## About this Reference Application

In this Amazon Transcribe & Comprehend reference Application, we make use of [Streaming feature](https://www.plivo.com/docs/voice/api/stream/). Plivo’s audio streaming resource lets you receive raw audio input over WebSocket (wss or ws) URLs from live phone calls in near real time.

In this reference application, we expose a websocket which receives raw audio streams from live phone calls. Once the call is hung up, this application receives a hangup callback and then pushes the raw audio file to S3 to fetch the transcripts and sentiment scores.