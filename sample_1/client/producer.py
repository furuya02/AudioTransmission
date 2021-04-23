from mqtt import Mqtt
import json
from datetime import datetime
import base64

class Producer():
    def __init__(self):
        self.__topic = "topic/audio_transmission"

        root_ca = "./certs/RootCA.pem"
        key = "./certs/xxxxxxxx-private.pem.key"
        cert = "./certs/xxxxxxxx-certificate.pem.crt"
        endpoint = "xxxxxxxxxxx-ats.iot.ap-northeast-1.amazonaws.com"
        self.__mqtt = Mqtt(root_ca, key, cert, endpoint)
        
    def send(self, data):
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        b64_data = base64.b64encode(data)
        raw_data = b64_data.decode()
        # デバッグ用にデータ削減
        #raw_data = raw_data[0:40]

        payload = json.dumps({
            "timestamp": now,
            "raw_data": raw_data
        })
        self.__mqtt.publish(self.__topic, payload)
        print("publish {}byte".format(len(payload)))

