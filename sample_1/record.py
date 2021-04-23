import pyaudio
import wave
import numpy as np

DEVICE_INDEX = 0
CHANNELS = 2 
SAMPLE_RATE = 32000 # サンプルレート
CHUNK = SAMPLE_RATE # 1秒ごとに取得する
FORMAT = pyaudio.paInt16
RECORD_SECONDS = 10 # 10秒間録音する

# open stream
p = pyaudio.PyAudio()
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = SAMPLE_RATE,
                input =  True,
                input_device_index = DEVICE_INDEX,
                frames_per_buffer = CHUNK)
# recording
print("recording ...")
frames = []
for _ in range(0, int(SAMPLE_RATE / CHUNK * RECORD_SECONDS)):
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
    frames.append(data)
    print ("data size:{}".format(len(data)))
data = b''.join(frames)
print("done.")

# close strema
stream.stop_stream()
stream.close()
p.terminate()

# save
CHANNELS = 1 # 1ch
SAMPLE_RATE = 8000 # 8kHz
file_name = "./sample.wav"
wf = wave.open(file_name, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(SAMPLE_RATE)
wf.writeframes(data)
wf.close()