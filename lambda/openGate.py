from __future__ import print_function
import sys
import logging
import boto3
from boto3 import Session
from contextlib import closing


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def openGate(accName, carParkName, bookNum):
        session = Session(region_name="us-east-1")
        polly = session.client('polly') 
        s3 = boto3.client('s3')
        filename = "voice/", bookNum,".mp3"
        filename = str(filename)
        text = accName + \
            ". Welcome to " + \
            carParkName + \
            ". The gate will now open. Enjoy your last day at S.A. Launch."
        print (text)
        #try:
        response = polly.synthesize_speech(
                Text=str(text),
                OutputFormat="mp3",
                VoiceId="Joanna")
        with closing(response["AudioStream"]) as stream:
            s3.put_object(ACL='public-read', Bucket='sa-launch-demo-onedimsum', Key='voice/filename.mp3', Body=stream.read())
    #    except BotoCoreError as error:
     #       logging.error(error)
            

def getClientName(state):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('UserAccount')
    
    response = table.get_item(
        Key={
            'AccountId': state
        }
    )

    if 'Item' not in response:
        return False
    else:
        return response['Item']['Name']
        
def getParkName(state):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('CarPark')
    
    response = table.get_item(
        Key={
            'CarParkId': state
        }
    )

    if 'Item' not in response:
        return False
    else:
        return response['Item']['Name']
        
def getAccountId(event):
    if event[0]['eventName'] == "MODIFY":
        dynamo = event[0]['dynamodb']
        bookId = dynamo['Keys']['BookingId']['S']
        
        dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
        table = dynamodb.Table('Booking')
        
        response = table.get_item(
            Key={
                'BookingId': bookId
            }
        )
    
        if 'Item' not in response:
            return False
        else:
            return response['Item']['AccId']
            
    #if event[0]['eventName'] == "MODIFY":
     #   dynamo = event[0]['dynamodb']
      #  if "InTime" in dynamo['NewImage']:
       #     return dynamo['NewImage']['AccId']['S']
    
def getParkId(event):
    
    if event[0]['eventName'] == "MODIFY":
        dynamo = event[0]['dynamodb']
        bookId = dynamo['Keys']['BookingId']['S']
        
        dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
        table = dynamodb.Table('Booking')
        
        response = table.get_item(
            Key={
                'BookingId': bookId
            }
        )
    
        if 'Item' not in response:
            return False
        else:
            return response['Item']['ParkId']
        
        #if "InTime" in dynamo['NewImage']:
        #    print (event)
        #    return dynamo['NewImage']['ParkId']['S']
            

def lambda_handler(event, context):
    #print (event)
    accName = ""
    accId = getAccountId(event['Records'])
    print ("Account ID = ", accId)
    
    if accId:
        accName = getClientName(accId)
        parkName = getParkName(getParkId(event['Records']))
        if event['Records'][0]['eventName'] == "MODIFY":
            dynamo = event['Records'][0]['dynamodb']
            bookId = dynamo['Keys']['BookingId']['S']
            openGate(accName, parkName, bookId)
            print (accName, ". Welcome to ", parkName)
    return event
    