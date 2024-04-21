from sanic import Sanic, response
import json
import base64
from transcribe import start_transcribe

app = Sanic(__name__)


def parse_and_save_to_file(json_data):
    try:
        # Parse JSON data
        data = json.loads(json_data)
        if data["event"] == "media":
            # Decode Base64 payload
            payload_base64 = data['media']['payload']
            decoded_payload = base64.b64decode(payload_base64)

            # Generate file name
            stream_id = data['streamId']
            track_type = data['media']['track']
            file_name = f"{stream_id}_{track_type}.raw"

            # Write decoded payload to a file
            with open(file_name, 'ab') as file:
                file.write(decoded_payload)
                print("Written to file : ", file_name)
    except Exception as e:
        print("Error : recieved bad data", e)


async def receive_streams(request, ws):
    while True:
        try:
            message = await ws.recv()
            parse_and_save_to_file(message)
        except Exception as e:
            print("Error receiving message:", e)


@app.route('/hangup_url/', methods=['POST'])
async def hangup(request):
    call_uuid = request.form.get('CallUUID')
    await start_transcribe(call_uuid)

    return response.text("OK")


app.add_websocket_route(receive_streams, '/stream')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765)
