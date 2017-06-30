import boto3
import time
import urllib
import requests

print('Loading function')

# s3 = boto3.client('s3')
ddb = boto3.client('dynamodb')
table_name = 'Booking'
s3_base_url = 'https://s3-ap-southeast-2.amazonaws.com/'
openalpr_url = 'https://api.openalpr.com/v2/recognize_url?recognize_vehicle=1&country=au&secret_key=sk_DEMODEMODEMODEMODEMODEMO&return_image=false'

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    s3_url = s3_base_url + bucket + '/' + key
    r = requests.post(openalpr_url, {'image_url': s3_url})
    if r.status_code != 200:
        # something went wrong, let's cheat
        # assume car plate is file key
        number = key.split('.')[0][5:]
    else:
        resp = r.json()
        number = resp['results'][0]['plate']

    print('Got car number: %s' % number)

    # find account id from car number
    cf = {'CarPlateNo': {'ComparisonOperator': 'EQ', 'AttributeValueList': [{'S': number}]}}
    account_id = number
    try:
        accounts = ddb.scan(TableName='UserAccount', ScanFilter=cf)
        if accounts and accounts['Count'] > 0:
            print("Retrieved accounts: %s" % accounts)
            account_id = accounts['Items'][0]['AccountId']['S']

        qf = {'AccId': {'ComparisonOperator': 'EQ', 'AttributeValueList':[{'S':account_id}]}, 'ParkId': {'ComparisonOperator':'EQ', 'AttributeValueList':[{'S':'cp-1'}]}}
        bookings = ddb.scan(TableName=table_name, ScanFilter=qf)
        print("Retrieved bookings: %s" % bookings)
        if bookings and bookings['Count'] > 0:
            booking = bookings['Items'][0]
            b_id = booking['BookingId']
            in_time = str(time.time())
            print("Updating BookingId=%s with InTime=%s" % (b_id, in_time))
            ddb.update_item(
                    TableName=table_name,
                    Key={'BookingId': b_id},
                    AttributeUpdates={'InTime':{'Value':{'S':in_time}, 'Action':'PUT'}})
    except Exception as e:
        print(e)
