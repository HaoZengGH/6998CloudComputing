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
        inputText= event['queryStringParameters']['q']
    )

    if 'slots' in response_lex:
        keys = [response_lex['slots']['keyone'], response_lex['slots']['keytwo']]
        print(keys)
        
        photos = search(keys) 
        print(photos)
        
        if photos:
            #For API Gateway to handle a Lambda function's response, the function must return output according to the following JSON format:
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
                "body": '[]',
                "isBase64Encoded": False
            }
    else:
        response = {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": '[]',
            "isBase64Encoded": False}
   
    print(response)
    return response


def search(keys):

    print('ready to enter opensearch')
    url = 'https://search-photoalbum-cn3cdbz3grdr76hntdhosnnqpy.us-east-1.es.amazonaws.com/photos/_search?q='
    headers = { "Content-Type": "application/json" }

    result_key0 = []
    result_key1 = []
    result = []
    
    if None not in keys and '' not in keys:
        if keys[0].endswith('s'):
            key0 = keys[0][:-1]
        else:
            key0 = keys[0]
        if keys[1].endswith('s'):
            key1 = keys[1][:-1]
        else:
            key1 = keys[1]
        new_url_key0 = url + key0.lower()
        new_url_key1 = url + key1.lower()
        res_key0 = requests.get(new_url_key0,headers=headers,auth=awsauth).json()
        res_key1 = requests.get(new_url_key1,headers=headers,auth=awsauth).json()
        if 'hits' in res_key0:
            for object in res_key0['hits']['hits']:
                objectKey0 = object['_source']['objectKey']
                if objectKey0 not in result:
                    result_key0.append(objectKey0)
        print(result_key0)
        if 'hits' in res_key1:
            for object in res_key1['hits']['hits']:
                objectKey1 = object['_source']['objectKey']
                if objectKey1 not in result:
                    result_key1.append(objectKey1)
        print(result_key1)
        for objectKey in result_key0:
            if objectKey in result_key1 and objectKey not in result:
                result.append(objectKey)
        print(result)
                
    
    else:
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


