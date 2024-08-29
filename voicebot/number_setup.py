import json
import sys
from plivo import plivoxml
import plivo
import xml.etree.ElementTree as ET
import requests

CONFIG = {}


def load_config(file_path='config.json'):
    global CONFIG
    with open(file_path, 'r') as f:
        CONFIG = json.load(f)


def create_xml(ws_url):
    response = plivoxml.ResponseElement().add(
        plivoxml.StreamElement(ws_url,
                               bidirectional="true",
                               audioTrack="inbound",
                               keepCallAlive="true",
                               contentType="audio/x-l16;rate=8000"))
    return response.to_string()


def upload_xml(xml_string):
    root = ET.fromstring(xml_string)

    tree = ET.ElementTree(root)

    tree.write('voicebot.xml', encoding='utf-8', xml_declaration=True)

    url = "http://plivobin-prod-usw.plivops.com/api/v1/xml"

    payload = {}
    files = [
        ('file', ('voicebot.xml', open('voicebot.xml', 'rb'), 'text/xml'))
    ]

    response = requests.request("POST", url, data=payload, files=files)

    if response.status_code == 200:
        return True
    return False


def create_application():
    client = plivo.RestClient(CONFIG['auth_id'], CONFIG['auth_token'])
    response = client.applications.create(
        app_name='voice-bot-application',
        answer_url='https://plivobin-prod-usw.plivops.com/api/v1/voicebot.xml', )

    return response['app_id']


def update_phone_number(phoneNumber, appId):
    client = plivo.RestClient(CONFIG['auth_id'], CONFIG['auth_token'])
    number = client.numbers.get(
        number=phoneNumber, )
    response = number.update(
        app_id=appId, )

    if response['message'] == 'changed':
        return True

    return False


if __name__ == "__main__":
    phoneNumber = sys.argv[1]
    url = sys.argv[2]

    load_config()

    xmlString = create_xml(url)
    xmlUploaded = upload_xml(xmlString)
    if xmlUploaded:
        appId = create_application()
        update_phone_number(phoneNumber, appId)

    print("Number setup completed")
