from __future__ import print_function

import boto3
import json
import uuid

print('Loading function')
#dynamo = boto3.client('dynamodb',region_name='ap-southeast-2')
dynamo = boto3.resource("dynamodb", region_name='ap-southeast-2')

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    #print("Received event: " + json.dumps(event, indent=2))
    accountId = event['accountId']
    cpId = event['carparkId']
    reservationTime = event['reservationTime']

    cpTable = dynamo.Table('CarPark')
    response = cpTable.get_item(Key={'CarParkId': cpId})
    item = response['Item']
    availableslot = int(item['AvailableSlot'])

    return_msg = None

    if availableslot>0:

        #generate booking id
        _uuid = str(uuid.uuid4())
        bookingId = _uuid[0:6]

        #write item to ddb (booking table)
        bookingTable = dynamo.Table('Booking')
        response = bookingTable.put_item(
            Item={
                'AccId': accountId,
                'BookingId': bookingId,
                'ReservationTime': reservationTime,
                "ParkId": cpId
            }
        )

        response = cpTable.update_item(
            Key={'CarParkId': cpId},
            UpdateExpression="set AvailableSlot=:a",
            ExpressionAttributeValues={
                ':a': availableslot-1
            },
            ReturnValues="UPDATED_NEW"
        )

        return_msg='Success with Booking id: '+bookingId

    else:
        return_msg='Sorry, No Available Slot'

    return respond(None, return_msg)