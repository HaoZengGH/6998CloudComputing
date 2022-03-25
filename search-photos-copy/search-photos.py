import json
import os
import time
import boto3
import requests
from requests_aws4auth import AWS4Auth



credentials = boto3.Session().get_credentials()
region = 'us-east-1'
service = 'es'

awsauth = AWS4Auth(credentials.access_key,credentials.secret_key, region, service, session_token=credentials.token)


def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    client = boto3.client('lex-runtime')
    
    print(event)

    response_lex = client.post_text(
        botName='photo',
        botAlias="photo",
        userId="test",
        inputText=event['queryStringParameters']['q']
    )

    if 'slots' in response_lex:
        keys = [response_lex['slots']['keyone'], response_lex['slots']['keytwo']]
        print(keys)
        
        photos = search(keys) 
        print(photos)
        
        if photos:
            response = {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                "body": json.dumps(photos),
                "isBase64Encoded": False
            }
        else:
            response = {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
                "body": [],
                "isBase64Encoded": False}
   
    print(response)
    return response


def search(keys):

    print('ready to enter opensearch')
    url = 'https://search-photoalbum-cn3cdbz3grdr76hntdhosnnqpy.us-east-1.es.amazonaws.com/photos/_search?q='
    headers = { "Content-Type": "application/json" }

    result = []

    for key in keys:
        if (key is not None) and key != '':
            if key.endswith('s'):
                key = key[:-1]
            new_url = url + key.lower()
            res = requests.get(new_url,headers=headers,auth=awsauth).json()
            print(res)
            if 'hits' in res:
                for object in res['hits']['hits']:
                    objectKey = object['_source']['objectKey']
                    if objectKey not in result:
                        result.append(objectKey)
    print(result)
    return(result)


