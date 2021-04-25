from mqtt import Mqtt
import json
from datetime import datetime
import struct
import requests
import boto3
import random

class Producer():
    def __init__(self):

        self.__cert = "./certs/xxxxxxxx-certificate.pem.crt"
        self.__key = "./certs/xxxxxxxx-private.pem.key"
        self.__endpoint = "https://xxxxxxxxxxxx.credentials.iot.ap-northeast-1.amazonaws.com"
        self.__role_alias = 'audio_transmission_role_alias'
        
        self.__stream_name = 'audio_transmission_data_stream'
        self.__region = 'ap-northeast-1'
        self.__kinesis = self.__get_kinesis()
    
    def __get_kinesis(self):
        result = requests.get(
            '{}/role-aliases/{}/credentials'.format(self.__endpoint, self.__role_alias),
            cert=(self.__cert, self.__key)
        )
        print(result)
        if(result.status_code != 200):
            exit()

        body = json.loads(result.text)
        access_key = body["credentials"]["accessKeyId"]
        secret_key = body["credentials"]["secretAccessKey"]
        token = body["credentials"]["sessionToken"]

        session = boto3.Session(aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    aws_session_token=token,
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


