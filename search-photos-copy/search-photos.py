import boto3
import json
import os
import math
import dateutil.parser
import datetime
import time


import requests
from requests_aws4auth import AWS4Auth


region = 'us-east-1'
service = 'es'

awsauth = AWS4Auth('AKIAQ3YKJCFDQ6OW3N6E', 'QG8zrlu17whNRR2V5fojQC9ihYJhtDe3gEt/m3u9', region, service, session_token=None)

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
    
    #define the client to interact with Lex
    client = boto3.client('lex-runtime')

    response_lex = client.post_text(
        botName='photo',
        botAlias="searchphoto",
        userId="test",
        inputText="photos with dogs and cats"
    )

    if 'slots' in response_lex:
        keys = [response_lex['slots']['keyone'], response_lex['slots']['keytwo']]
        print(keys)
        photo = search(keys) 
        if photo:
            response = {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                "body": json.dumps(photo),
                "isBase64Encoded": False
            }
        else:
            response = {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                "body": "no such photos",
                "isBase64Encoded": False}


    print(response)
    return response


def search(keys):
    print('ready to enter opensearch')
    url = 'https://search-photosnew-lf5tuedyumkti2aas2mfctqdtu.us-east-1.es.amazonaws.com/photos/photo/_search?q='


    photo = []

    for key in keys:
        if key:
            if key.endswith('s'):
                key = key[:-1]
        if (key is not None) and key != '':
            final_url = url + key.lower()
            finding = requests.get(final_url,auth=awsauth).json()
            print(finding)
            #res.append(finding)
            #for r in finding:
            if 'hits' in finding:
                if finding['hits']['total']['value'] >=1:
                    print('find: ' + str(finding['hits']['total']['value']) + ' for ' + key)
                    for val in finding['hits']['hits']:
                        objectkey = val['_source']['objectKey']
                        if objectkey not in photo:
                            photo.append(objectkey)

    print(photo)
    return photo        


   
# # return close(intent_request['sessionAttributes'],
# #          'Fulfilled',
# #          {'contentType': 'PlainText',
# #           'content': ''.join(output)})

