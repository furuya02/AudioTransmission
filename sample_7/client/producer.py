import json
from datetime import datetime
import base64
import boto3
from boto3.session import Session
import time
import random
import struct

class Producer():
    def __init__(self):
        self.__identity_id = "ap-northeast-1:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        self.__region = "ap-northeast-1"
        self.__stream_name = 'audio_transmission_data_stream'
        self.__kinesis = self.__get_kinesis()
    
    def __get_kinesis(self):
        client = boto3.client('cognito-identity', self.__region)
        resp =  client.get_id(IdentityPoolId = self.__identity_id)
        resp = client.get_credentials_for_identity(IdentityId=resp['IdentityId'])
        secretKey = resp['Credentials']['SecretKey']
        accessKey = resp['Credentials']['AccessKeyId']
        token = resp['Credentials']['SessionToken']
        session = Session(aws_access_key_id = accessKey,
                  aws_secret_access_key = secretKey,
                  aws_session_token = token,
                  region_name = self.__region)
        return session.client('kinesis')

    def send(self, data):
        now = datetime.now()
        # 時刻とデータの結合
        ts = now.timestamp()
        ts = struct.pack('<d', ts)
        transfer_data = ts + data
        try:
            response = self.__kinesis.put_record(
                StreamName = self.__stream_name, 
                PartitionKey = str(random.randrange(0,100)), 
                Data = transfer_data
            )
        except Exception as e:
            print("Exception: {}", e.args)
        print('put_record SequenceNumber:{}'.format(response['SequenceNumber']))
