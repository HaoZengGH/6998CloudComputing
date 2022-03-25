import json
import os
import math
import dateutil.parser
import datetime
import time

import boto3
import requests
from requests_aws4auth import AWS4Auth

# from botocore.vendored import requests

credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    client = boto3.client('lex-runtime')

    response_lex = client.post_text(
        botName='photo',
        botAlias="searchphoto",
        userId="test",
        inputText="photos with Cat"
    )

    if 'slots' in response_lex:
        keys = [response_lex['slots']['keyone'], response_lex['slots']['keytwo']]
        print(keys)
        pictures = search(keys)  # get images keys from elastic search labels
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps(pictures),
            "isBase64Encoded": False
        }
    else:
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": [],
            "isBase64Encoded": False}
    # logger.debug('event.bot.name={}'.format(event['bot']['name'])

    print(response)
    return response


# def dispatch(intent_request):
#     #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
#     intent_name = intent_request['currentIntent']['name']
#     return search_intent(intent_request)

#     raise Exception('Intent with name ' + intent_name + ' not supported')

def search(keys):
    #    key1 = get_slots(intent_request)['keyone']
    #     # key2 = get_slots(intent_request)['keytwo']
    #     # key3 = get_slots(intent_request)['keythree']
    print('ready to enter opensearch')
    url = 'https://search-photoalbum-cn3cdbz3grdr76hntdhosnnqpy.us-east-1.es.amazonaws.com/photos/photo/_search?q='

    resp = []

    for label in keys:
        if (label is not None) and label != '':
            url2 = url + label.lower()
            resp.append(requests.get(url2,auth=awsauth).json())
    print(resp)

#     output = []
#     for r in resp:
#         if 'hits' in r:
#              for val in r['hits']['hits']:
#                 key = val['_source']['objectKey']
#                 if key not in output:
#                     output.append(key)
# #url = "https://vpc-photos-b4al4b3cnk5jcfbvlrgxxu3vhu.us-east-1.es.amazonaws.com/photos/_search?pretty=true&q=*:*"
# #print(url)
# #resp = requests.get(url,headers={"Content-Type": "application/json"}).json()
# #resp = requests.get(url)
# print(output)

# return output
# # return close(intent_request['sessionAttributes'],
# #          'Fulfilled',
# #          {'contentType': 'PlainText',
# #           'content': ''.join(output)})

