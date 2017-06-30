from __future__ import print_function

import boto3

ddb = boto3.client('dynamodb')

def lambda_handler(event, context):
    car_park_id = event['CarParkId']
    car_plate_no = event['CarPlateNo']

    status=False

    #From DDB table UserAccount, match CarPlateNo?, then get account_id
    cf = {'CarPlateNo': {'ComparisonOperator': 'EQ', 'AttributeValueList': [{'S': car_plate_no}]}}
    accounts = ddb.scan(TableName='UserAccount', ScanFilter=cf)
    if accounts and accounts['Count'] > 0:
        account_id = accounts['Items'][0]['AccountId']['S']

        #From DDB table Booking, match AccountId + CarParkId & inTime!=null
        qf = {'AccId': {'ComparisonOperator': 'EQ', 'AttributeValueList': [{'S': account_id}]},
              'ParkId': {'ComparisonOperator': 'EQ', 'AttributeValueList': [{'S': car_park_id}]}}
        bookings = ddb.scan(TableName='Booking', ScanFilter=qf)
        if bookings and bookings['Count'] > 0:
            booking = bookings['Items'][0]
            if 'InTime' in booking.keys():
                in_time = booking['InTime']
                if in_time:
                    print('A')
                    status=True
                else:
                    print('B')
            else:
                print('C')
        else:
            print('D')

    return respond(status)

def respond(status):
    return {
        'open': status
    }

