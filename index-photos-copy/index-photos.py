import json
import boto3
import datetime
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
import requests

def lambda_handler(event, context):

    s3 = boto3.client('s3')

    bucket = event['Records'][0]['s3']['bucket']['name']
    photo = event['Records'][0]['s3']['object']['key']
    #createdTimestamp = event['Records'][0]['eventTime']
    createdTimestamp = str(datetime.datetime.now())

    print(bucket,photo)

    client=boto3.client('rekognition')
    print('enter rekognition success')

    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},MaxLabels=10)

    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])

    print(labels)

  

    # retrieve the metadata
    metadata = s3.head_object(Bucket=bucket,Key=photo)
    print(metadata)

    #detect customlabels if applicable
    if 'ResponseMetadata' in metadata:
        responsemetadata = metadata['ResponseMetadata']
        if 'HTTPHeaders' in responsemetadata:
            httpheaders = responsemetadata['HTTPHeaders']
            if 'x-amz-meta-customlabels' in httpheaders:
                customlabels = httpheaders['x-amz-meta-customlabels']
                customlabel = customlabels.split(',')
                for label in customlabel:
                    labels.append(label)
        
    #store in opensearch
    item = {
        'objectKey': photo,
        'bucket': bucket,
        'createdTimestamp': createdTimestamp,
        'labels': labels
    }

    print(item)


    host = 'search-photoalbum-cn3cdbz3grdr76hntdhosnnqpy.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()

    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    search = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    
    search.index(index="photos", doc_type="photo", id = createdTimestamp, body=item)
    
    print('upload success')
    
    print(search.get(index="photos", doc_type="photo", id="2"))
    
