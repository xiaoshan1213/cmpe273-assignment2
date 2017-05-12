from __future__ import print_function
from boto3.dynamodb.conditions import Key, Attr

import boto3
import json

print('Loading function')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):

    # print("Received event: " + json.dumps(event, indent=2))

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']


    if operation in operations:
        if operation == 'GET':

            dynamo = boto3.resource('dynamodb').Table('menu')
            response = dynamo.scan(FilterExpression=Attr('menu_id').eq(event['menu_id']))
            return respond(None, response)

        elif operation == 'POST':

            dynamo = boto3.resource('dynamodb').Table('menu')
            response = dynamo.put_item(
                Item={
                    'menu_id': event['menu_id'],
                    'store_name': event['store_name'],
                    'selection': event['selection'],
                    'size': event['size'],
                    'price': event['price'],
                    'store_hours': event['store_hours']
                }
            )
            return respond(None, "200 OK")

        elif operation == 'PUT':
            menu_id = event['menu_id']
            dynamo = boto3.resource('dynamodb').Table('menu')
            response = {}
            if event['selection'] != "":
                response1 = dynamo.update_item(
                    Key={
                        'menu_id': menu_id,
                    },
                    UpdateExpression="set selection=:a",
                    ExpressionAttributeValues={
                        ':a': event['selection']
                    },
                    ReturnValues="UPDATED_NEW"
                )
                response.update(response1['Attributes'])

            if event['size'] != "":
                response1 = dynamo.update_item(
                    Key={
                        'menu_id': menu_id,
                    },
                    UpdateExpression="set size=:a",
                    ExpressionAttributeValues={
                        ':a': event['size']
                    },
                    ReturnValues="UPDATED_NEW"
                )
                response.update(response1['Attributes'])

            if event['price'] != "":
                response1 = dynamo.update_item(
                    Key={
                        'menu_id': menu_id,
                    },
                    UpdateExpression="set price=:a",
                    ExpressionAttributeValues={
                        ':a': event['price']
                    },
                    ReturnValues="UPDATED_NEW"
                )
                response.update(response1['Attributes'])

            if event['store_hours'] != "":
                response1 = dynamo.update_item(
                    Key={
                        'menu_id': menu_id,
                    },
                    UpdateExpression="set store_hours=:a",
                    ExpressionAttributeValues={
                        ':a': event['store_hours']
                    },
                    ReturnValues="UPDATED_NEW"
                )
                response.update(response1['Attributes'])

            return respond(None, response)


        elif operation == "DELETE":

            dynamo = boto3.resource('dynamodb').Table('menu')
            response = dynamo.delete_item(
                Key={
                    'menu_id': event['menu_id']
                }
            )
            return respond(None, "200 OK")
        else:
            return respond(ValueError('Unsupported PUT "{}"'.format(operation)))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))