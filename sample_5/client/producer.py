from mqtt import Mqtt
import json
from datetime import datetime
import struct

class Producer():
    def __init__(self):
        self.__topic = "$aws/rules/audio_transmission_rule/topic/audio_transmission"
        root_ca = "./certs/RootCA.pem"
        cert = "./certs/xxxxxxxxxx-certificate.pem.crt"
        key = "./certs/xxxxxxxxxx-private.pem.key"
        endpoint = "xxxxxxxxxxx-ats.iot.ap-northeast-1.amazonaws.com"

        self.__mqtt = Mqtt(root_ca, key, cert, endpoint)
        
    def send(self, data):
        now = datetime.now()
        # 時刻とデータの結合
        ts = now.timestamp()
        ts = struct.pack('<d', ts)
        transfer_data = ts + data
        try:
            self.__mqtt.publish(self.__topic, transfer_data)
            print("publish {}byte".format(len(transfer_data)))
        except Exception as e:
            print("Exception: {}", e.args)


