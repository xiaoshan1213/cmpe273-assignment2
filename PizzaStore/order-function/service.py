from __future__ import print_function
from boto3.dynamodb.conditions import Key, Attr
from time import gmtime, strftime
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

    print("Received event: " + json.dumps(event, indent=2))

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']


    if operation in operations:

        if operation == 'GET':
            order_id = event['order_id']
            dynamo = boto3.resource('dynamodb').Table('order')
            response = dynamo.scan(FilterExpression=Attr('order_id').eq(order_id))
            # items = response['Items'][0]
            print(response)
            # print(type(items))
            return respond(None, response)

        elif operation == 'POST':
            # print(payload)
            menu_table = boto3.resource('dynamodb').Table('menu')
            menu = menu_table.scan(FilterExpression=Attr('menu_id').eq(event['menu_id']))
            print(menu['Items'])
            selection = menu['Items'][0]['selection']
            size = menu['Items'][0]['size']
            costs = menu['Items'][0]['price']


            order_table = boto3.resource('dynamodb').Table('order')
            response = order_table.put_item(
                Item={
                    'menu_id': event['menu_id'],
                    'order_id': event['order_id'],
                    'customer_name': event['customer_name'],
                    'customer_email': event['customer_email'],
                    'order_status': 'selection',
                    'orders': {
                        'selection': selection,
                        'size': size,
                        'costs': costs,
                        # mm - dd - yyyy @ hh:mm:ss UTC
                        'order_time': strftime("%m-%d-%Y %H:%M:%S", gmtime())
                    }
                }
            )
            str1 = ''
            for i in range(len(selection)):
                str1 += str(i)+'. '+selection[i]+" "
            return respond(None, "Hi"+event['customer_name']+", please choose from "+str1)

        elif operation == 'PUT':
            input = event['input']
            order_id = event['order_id']
            order_table = boto3.resource('dynamodb').Table('order')
            order = order_table.scan(FilterExpression=Attr('order_id').eq(order_id))
            if order['Items'][0]['order_status'] == 'selection':
                selection_list = order['Items'][0]['orders']['selection']
                print(selection_list)
                response = order_table.update_item(
                    Key={
                        'order_id': order_id,
                    },
                    UpdateExpression="set orders.selection=:a, order_status=:b",
                    ExpressionAttributeValues={
                        ':a': selection_list[int(input)],
                        ':b': 'size'
                    },
                    ReturnValues="UPDATED_NEW"
                )
                str1 = ''
                for i in range(len(order['Items'][0]['orders']['size'])):
                    str1 += str(i) + '. ' + order['Items'][0]['orders']['size'][i] + " "
                return respond(None, "Which size do you want?"+str1)

            elif order['Items'][0]['order_status'] == 'size':
                size_list = order['Items'][0]['orders']['size']
                costs_list = order['Items'][0]['orders']['costs']
                response = order_table.update_item(
                    Key={
                        'order_id': order_id,
                    },
                    UpdateExpression="set orders.size=:a, orders.costs=:b, order_status=:c, orders.order_time=:d",
                    ExpressionAttributeValues={
                        ':a': size_list[int(input)],
                        ':b': costs_list[int(input)],
                        ':c': 'processing',
                        ':d': strftime("%m-%d-%Y %H:%M:%S", gmtime())
                    },
                    ReturnValues="UPDATED_NEW"
                )
                return respond(None, "Your order costs: "+costs_list[int(input)]+", We will email you when the order is ready. Thank you!")

            return respond(None, "empty query")


        # elif operation == "DELETE":
        #     payload = event['body']
        #     dynamo = boto3.resource('dynamodb').Table(payload['TableName'])
        #     response = dynamo.delete_item(
        #         Key={
        #             'menu_id': payload['menu_id']
        #         }
        #     )
        #     return respond(None, response)
        else:
            return respond(ValueError('Unsupported PUT "{}"'.format(operation)))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))