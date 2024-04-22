# Plivo Dialogflow Audio Streaming Integration

This Express application integrates Plivo's audio streaming with Dialogflow for seamless voice-based interactions.

## Prerequisites

- Set up a [Dialogflow Agent](https://cloud.google.com/dialogflow/docs/agents-overview) and take note of the Google Project ID.
- Download your [Google Credentials](https://cloud.google.com/docs/authentication/getting-started) (which should have access to your Dialogflow project) and save it as `google_creds.json` in the root directory of this project.


## Setting Up Dialogflow Agent for Project
If you haven't set up a Google Dialogflow agent yet, follow these steps to create one for this project.

Required Information

### Google Cloud Project ID:

1. Go to the Dialogflow console.
2. Select your Dialogflow agent and click on the gear icon in the settings.
3. Note down the Project ID displayed. This value will be used as GCLOUD_PROJECT_ID in the subsequent sections.


### Google Application Credentials JSON File:

1. From the Dialogflow console, click on your Project ID link.
2. Navigate to '-> Go to project settings' > 'Service Accounts'.
3. Click '+ CREATE SERVICE ACCOUNT'.
4. Enter a name for the service account, for example, PlivoDF, and click CREATE.
5. Select 'Dialogflow API' client as the role. (Note: Role permissions are not covered in this demo.)
6. Click CONTINUE, then DONE.
7. Under 'Actions', click the 3 vertical dots > 'Create key' > 'JSON' > CREATE.
8. Save the downloaded JSON file to your application folder.
9. The filename of the saved JSON file, for example, mydfagent-plivo-05768e59b7c5.json, will be used as GOOGLE_APPLICATION_CREDENTIALS in  the subsequent sections of this project.

## Installation

1. **Install dependencies:**

    ```bash
    npm install
    ```

2. **Populate your `.env` file:**

    Copy from `.env.example` and use `configure-env` to fill in the necessary environment variables:

    ```bash
    npx configure-env
    ```

## XML Configuration

Create an XML to call the audio stream, passing your exposed WebSocket (ws) URL:

```xml
<Response>
    <Stream bidirectional="true" keepCallAlive="true">wss://yourstream.websocket.io/audiostream</Stream>
</Response>
```

## Local Development

1. **Start the server locally:**

    ```bash
    npm start
    ```

2. **Expose your localhost to the internet using [ngrok](https://ngrok.com):**

    ```bash
    ngrok http 8000
    ```

3. **Wire up your Plivo number with the ngrok HTTPS URL for incoming calls.**


### Deploy to AppEngine

```bash
gcloud app deploy
```
Point your Plivo Incoming Webhook to your deployed AppEngine instance and attach it to your Plivo number.