import boto3
import json

comprehend = boto3.client('comprehend')


def detect_sentiment(text, file_name):
    print('Calling DetectSentiment for %s', file_name)
    sentiment = json.dumps(comprehend.detect_sentiment(Text=text, LanguageCode='en'), sort_keys=True,
                           indent=4)
    print(sentiment)
    print('End of DetectSentiment\n')
