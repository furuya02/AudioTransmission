import json
import datetime
import os
import boto3
import base64
import numpy as np

def lambda_handler(event, context):

    topic = 'topic/level_meter'
    iot = boto3.client('iot-data')
    if("IsLocal" in os.environ and os.environ["IsLocal"] == "Yes"):
        session = boto3.Session(profile_name="developer")
        iot = session.client('iot-data')


    records = event["Records"]
    for record in records:
        payload = json.loads(base64.b64decode(record["kinesis"]["data"]).decode())
        timestamp = payload["timestamp"]
        print("timestamp: {}".format(timestamp))

        # テキストデータをバイナリに戻す
        b64_data = payload["raw_data"].encode()
        data = base64.b64decode(b64_data)
        print("len:{}".format(len(data)))
        # 1データを2byteとして扱う
        data = np.frombuffer(data, dtype="int16")
        # 最大値を取得する
        max = data.max()

        payload = {
            "timestamp": payload["timestamp"],
            "level": int(max)
        }
        print("payload:{}".format(payload))
        iot.publish(
            topic=topic,
            qos=0,
            payload=json.dumps(payload)
        )

    return {}
