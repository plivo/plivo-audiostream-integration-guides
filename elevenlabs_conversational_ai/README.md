# Plivo Audio Streaming Integration with ElevenLabs Conversational Agent

This project demonstrates a proof of concept (POC) for integrating Plivo's audio streaming with ElevenLabs Conversational AI Agent.

### Prerequisites
Sign up for the following services and get an API key for each:
* [ElevenLabs](https://elevenlabs.io/app/sign-up)

### How to setup locally?

### 1. Create a virtual environment named `venv`
```
pip install virtualenv
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
```

### 2. Install requirements: 
```
pip install -r requirements.txt`
```

### 3. Start an [ngrok](https://ngrok.com) tunnel for port `9000`:
As we are running this application locally, we'll need to open a tunnel to forward requests to the local development server. In this setup, we are using ngrok.

Open terminal and run:
```
ngrok http 9000
```
Once the tunnel has been opened, copy the Forwarding URL. It will look something like: https://[your-ngrok-subdomain].ngrok.app or https://[your-ngrok-subdomain].ngrok-free.app if you are using free version (eg. https://2073-49-207-221-93.ngrok-free.app). You will need this when creating the Plivo Answer XML.

### 4. Configure Environment Variables
Update `config.json` to add uour credentials:
```
{
    "auth_id": "your_auth_id",
    "auth_token": "your_auth_token",
    "github_token": "your_github_token",
    "elevenlabs_api_key": "your_elevenlabs_api_key",
    "elevenlabs_agent_id": "your_elevenlabs_agent_key"
}
```
If you do not have a GitHub token, you can generate one by following steps mentioned [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). When creating the token, please make sure that it has Read and Write permission for Gists

### 5. Start your server
```
python server.py
```

### 6. Configure Incoming phone number
Configure an active phone number by using  [Plivo Console](https://console.plivo.com/active-phone-numbers/)

You can also execute below command to configure your number
```commandline
 python number_setup.py your-plivo-number ws://[your-ngrok-subdomain].ngrok.app/stream
```
In the command, replace "your-plivo-number" with your Plivo number and "[your-ngrok-subdomain].ngrok.app" with the Forwarding URL generated in step 3 (eg. "ws://2073-49-207-221-93.ngrok-free.app/stream").

### 7. Testing your Application
You are now all set to test your application and converse with a Voice Agent. Just place a call to the Plivo number you have configured for your setup, and connect to your AI based Voice Agent.
