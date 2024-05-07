import os

import boto3
import time
import urllib
import json
from convert import convert_audio
from sentiment import detect_sentiment
from stream_client import fetch_stream_id

transcribe_client = boto3.client('transcribe')


def transcribe_file(job_name, file_uri, transcribe_client):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='wav',
        LanguageCode='en-US'
    )

    max_tries = 60
    while max_tries > 0:
        max_tries -= 1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            print(f"Job {job_name} is {job_status}.")
            if job_status == 'COMPLETED':
                response = urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])
                data = json.loads(response.read())
                text = data['results']['transcripts'][0]['transcript']
            return text
        else:
            print(f"Waiting for {job_name}. Current status is {job_status}.")
        time.sleep(5)
    return None


def upload_file_to_s3(file_name, bucket_name, object_name=None):
    """Upload a file to an S3 bucket and return the URL

    :param file_name: File to upload
    :param bucket_name: Bucket to upload to
    :param object_name: S3 object name (path within the bucket). If not specified, file_name is used
    :return: URL of the uploaded file if successful, else None
    """

    # If S3 object_name is not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Create S3 client
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except Exception as e:
        print(f"Error uploading file '{file_name}' to bucket '{bucket_name}': {str(e)}")
        return None

    # Generate the URL for the uploaded file
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
    print(f"File '{file_name}' uploaded successfully to bucket '{bucket_name}' with object name '{object_name}'")
    print(f"URL of the uploaded file: {s3_url}")
    return s3_url


async def start_transcribe(call_uuid):
    stream_id = fetch_stream_id(call_uuid)

    time.sleep(10)

    outbound_raw_file = f"{stream_id}_outbound.raw"
    if check_file_exists(outbound_raw_file):
        outbound_file = convert_audio(outbound_raw_file)
        transcribe(outbound_file, '<bucket_name>', outbound_file.split('.')[0])

    inbound_raw_file = f"{stream_id}_inbound.raw"
    if check_file_exists(inbound_raw_file):
        inbound_file = convert_audio(inbound_raw_file)
        print(inbound_file)
        transcribe(inbound_file, '<bucket_name>', inbound_file.split('.')[0])


def check_file_exists(file_name):
    return os.path.exists(file_name)


def transcribe(file_name, bucket_name, job_name):
    file_uri = upload_file_to_s3(file_name, bucket_name)
    text = transcribe_file(job_name, file_uri, transcribe_client)
    detect_sentiment(text, file_name)
