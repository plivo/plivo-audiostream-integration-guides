import plivo

client = plivo.RestClient('<Auth_Id>', '<Auth_Token>')


def fetch_stream_id(call_uuid):
    response = client.calls.get_all_streams(call_uuid=call_uuid)
    stream_id = response['objects'][0]['stream_id']
    return stream_id
