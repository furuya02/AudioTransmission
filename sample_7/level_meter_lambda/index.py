import json
import datetime
import os
import boto3
import base64
import numpy as np
import struct

def lambda_handler(event, context):

    topic = 'topic/level_meter'
    iot = boto3.client('iot-data')
    if("IsLocal" in os.environ and os.environ["IsLocal"] == "Yes"):
        session = boto3.Session(profile_name="developer")
        iot = session.client('iot-data')


    records = event["Records"]
    for record in records:
        data = base64.b64decode(record["kinesis"]["data"])
        print("{} {}".format(type(data), len(data)))

        # データを分離
        ts = data[:8]
        raw_data = data[8:]

        ts = struct.unpack('<d', ts)[0]
        now = datetime.datetime.fromtimestamp(ts)
        
        # 1データを2byteとして扱う
        raw_data = np.frombuffer(raw_data, dtype="int16")
        # 最大値を取得する
        max = int(raw_data.max())
        
        payload = {
            "timestamp": now.strftime('%Y-%m-%dT%H:%M:%S.%f'),
            "level": max
        }
        print("payload:{}".format(payload))
        iot.publish(
            topic=topic,
            qos=0,
            payload=json.dumps(payload)
        )

    return {}
