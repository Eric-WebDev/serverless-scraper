from newspaper import Article
import json
import boto3
import shortuuid
from boto3.dynamodb.conditions import Key, Attr
dynamodb = boto3.resource('dynamodb')
BUCKET_NAME = 'articlessource'


def handler(event, context):
    table = dynamodb.Table('articles')
    # body = table.scan()
    # items = body['Items']
    # urlgenerator = items[-1]['url']

    response = table.scan(FilterExpression=Attr('createCollection').eq(1))
    items = response['Items']
    key = items[0]['id']
    itemurl = items[0]['url']

    article = Article(itemurl, language="en")  # en for English
    article.download()
    article.parse()
    s3 = boto3.resource("s3").Bucket('articles-bucket-arek')
    json.dump_s3 = lambda obj, f: s3.Object(key=f).put(Body=json.dumps(obj))
    data = {"title": article.title, "url": article.url}
    json.dump_s3(data, shortuuid.uuid())  # saves json to s3://bucket/key

    table.update_item(Key={'id': key},  UpdateExpression='SET createCollection = :val1', ExpressionAttributeValues={':val1': 0})
    return {

        'statusCode': 200,
        'body': {
            'article': itemurl

        }
    }
