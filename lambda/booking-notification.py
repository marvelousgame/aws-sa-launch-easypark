
import json
import boto3

print('Loading function')
sns = boto3.client('sns')
ddb = boto3.client('dynamodb')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        print(record)
        if record['eventName'] == 'INSERT':
            ddb_record = record['dynamodb']['NewImage']
            if 'AccId' not in ddb_record.keys():
                return
            acc_id = ddb_record['AccId']
            if 'ParkId' not in ddb_record.keys():
                return
            cp_id = ddb_record['ParkId']
            if acc_id:
                ua_item = ddb.get_item(TableName='UserAccount', Key={'AccountId': acc_id})
                cp_item = ddb.get_item(TableName='CarPark', Key={'CarParkId': cp_id})
                if ua_item and cp_item:
                    ua = ua_item['Item']
                    phone = ua['Phone']['S']
                    name = ua['Name']['S']
                    booking_id = ddb_record['BookingId']['S']
                    cp_name = cp_item['Item']['Name']['S']
                    msg = "Hello %s, your booking for %s is successful. Here is your ref: %s" % (name, cp_name, booking_id)
                    print('Sending SNS to %s, msg=%s' % (phone, msg))
                    sns.publish(PhoneNumber=phone, Message=msg)
                    
    return 'Successfully processed {} records.'.format(len(event['Records']))
