from newspaper import Article
import json
import boto3
import shortuuid
from boto3.dynamodb.conditions import Key, Attr
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
queue_url = 'https://sqs.eu-west-1.amazonaws.com/396320213893/ArticlesQueue'

def handler(event, context):
    table = dynamodb.Table('articles')
    response = table.scan(FilterExpression=Attr('createCollection').eq(1))
    items = response['Items']
    key = items[0]['id']
    itemurl = items[0]['url']

    article = Article(itemurl, language="en")  # en for English
    article.download()
    article.parse()

    message = {"id": key, "title": article.title, "url": article.url,
               "content": article.text}
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message))

    table.update_item(Key={'id': key},  UpdateExpression='SET createCollection = :val1', ExpressionAttributeValues={':val1': 0})
    return response
