import pyaudio
from producer import Producer
import numpy as np

DEVICE_INDEX = 0
CHANNELS = 2 
SAMPLE_RATE = 32000 # サンプルレート
FORMAT = pyaudio.paInt16
CHUNK = SAMPLE_RATE # 1秒ごとに取得する

# open stream
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = SAMPLE_RATE,
                input =  True,
                input_device_index = DEVICE_INDEX,
                frames_per_buffer = CHUNK)

producer = Producer()

try:
    print("start ...")
    while True: 
        # 1秒分のデータ読み込み
        data = stream.read(CHUNK)

        # numpy配列に変換    
        data = np.frombuffer(data, dtype="int16")
        # チャンネル 2ch -> 1ch
        data = data[0::2] 
        # サンプルレート  32000Hz -> 8000Hz
        data = data[0::4] 
        # byteに戻す 
        data = data.tobytes()

        producer.send(data)
except:
    stream.stop_stream()
    stream.close()
    p.terminate()


