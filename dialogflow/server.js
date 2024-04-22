require("dotenv").config();
const express = require("express");
const hbs = require("express-handlebars");
const expressWebSocket = require("express-ws");
const websocket = require("websocket-stream");
const websocketStream = require("websocket-stream/stream");
const { DialogflowService } = require("./dialogflow");

const PORT = process.env.PORT || 8000;

const app = express();
// extend express app with app.ws()
expressWebSocket(app, null, {
  perMessageDeflate: false
});

app.ws("/audiostream", (ws, req) => {
  // This will get populated on callStarted
  let callId;
  let streamId;
  // MediaStream coming from Plivo
  const mediaStream = websocketStream(ws, {
    binary: false
  });
  const dialogflowService = new DialogflowService();

  mediaStream.on("data", data => {
    dialogflowService.send(data);
  });

  mediaStream.on("finish", () => {
    console.log("MediaStream has finished");
    dialogflowService.finish();
  });

  dialogflowService.on("callStarted", data => {
    callId = data.callId;
    streamId = data.streamId;
  });

  // Send audio back to plivo audio stream 
  dialogflowService.on("audio", audio => {
    const mediaMessage = {
      streamId,
      event: "playAudio",
      media: {
        contentType: "raw",
		    sampleRate: 8000,
        payload: audio
      }
    };
    const mediaJSON = JSON.stringify(mediaMessage);
    console.log(`Sending audio (${audio.length} characters)`);
    mediaStream.write(mediaJSON);
    // If this is the last message
    if (dialogflowService.isStopped) {
      const CheckpointMessage = {
        streamId,
        event: "checkpoint",
        "name": "customer greeting audio"
      };
      const checkpointJSON = JSON.stringify(CheckpointMessage);
      console.log("Sending end of interaction checkpoint", checkpointJSON);
      mediaStream.write(checkpointJSON);
    }
  });

  dialogflowService.on("interrupted", transcript => {
    console.log(`Interrupted with "${transcript}"`);
    if (!dialogflowService.isInterrupted) {
      console.log("Clearing...");
      const clearMessage = {
        event: "clearAudio",
        streamId
      };
      console.log("interrupted")
      mediaStream.write(JSON.stringify(clearMessage));
      dialogflowService.isInterrupted = true;
    }
  });

  dialogflowService.on("endOfInteraction", (queryResult) => {
    console.log("query result", queryResult)
  });
});

const listener = app.listen(PORT, () => {
  console.log("Your app is listening on port " + listener.address().port);
});
