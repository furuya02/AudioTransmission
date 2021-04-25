import json
import datetime
import os
import boto3
import base64
import wave
import struct

def lambda_handler(event, context):

    BUCKET_NAME = os.environ['BUCKET_NAME']
    output_filename = event["output_filename"]

    start_time_str = event["start_time"]
    period_sec = int(event["period_sec"])
    print("start_time:{} period_sec:{}".format(start_time_str, period_sec))
    
    # 開始時間と終了時間(JST)
    start_time_jst = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    end_time_jst = start_time_jst + datetime.timedelta(seconds=period_sec)
    print("JST {} - {} ".format(start_time_jst, end_time_jst))
    
    # S3上のオブジェクト名を検索するため
    # 開始時間と終了時間(UTC) ファイル検索用なので、開始時間は、1分前とする
    start_time_utc = start_time_jst + datetime.timedelta(hours=-9)
    end_time_utc = start_time_utc + datetime.timedelta(seconds=period_sec)
    start_time_utc = start_time_utc + datetime.timedelta(minutes=-1)
    print("UTC {} - {}".format(start_time_utc, end_time_utc))

    s3client = boto3.client('s3')
    if("IsLocal" in os.environ and os.environ["IsLocal"] == "Yes"):
        session = boto3.Session(profile_name="developer")
        s3client = session.client('s3')

    # 当日分のオブジェクト名を列挙する
    prefix = "{:4d}/{:02d}/{:02d}".format(
        start_time_utc.year,
        start_time_utc.month,
        start_time_utc.day
    )
    response = s3client.list_objects_v2(
                Bucket = BUCKET_NAME,
                Prefix = prefix
            )
        
    # オブジェクト名から、対象期間ヒットするオブジェクトを列挙する
    target_keys = []
    if("Contents" in response):
        for content in response["Contents"]:
            # オブジェクト名からtimestampを取得する
            key = content["Key"]
            tmp = key.split('/')[4].split('-')
            year = int(tmp[2])
            month = int(tmp[3])
            day = int(tmp[4])
            hour = int(tmp[5])
            minute = int(tmp[6])
            second = int(tmp[7])
            dt = datetime.datetime(year, month, day, hour, minute, second, microsecond=0)
            if(start_time_utc <= dt and dt <= end_time_utc):
                target_keys.append(key)
    target_keys.sort()

    # オブジェクトをダウンロードして、timestampが取得期間ヒットするRAWデータを取得する
    frames = []
    for key in target_keys:
        body = s3client.get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read()
        
        # 8008byte単位で処理する
        data_size = 8008
        start = 0
        for _ in range(int(len(body)/data_size)):
            data = body[start:start+data_size]
            
            raw_data = data[8:]
            ts = data[:8]
            
            ts = struct.unpack('<d', ts)[0]
            now = datetime.datetime.fromtimestamp(ts)
            time_str = now.strftime('%Y-%m-%dT%H:%M:%S.%f')
            timestamp = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%f')

            # 取得期間のデータは、framesに追加する
            if(start_time_utc <= timestamp and timestamp <= end_time_utc):
                frames.append(raw_data)
            start += data_size
    data = b''.join(frames)

    # RAWデータをwavファイルとして保存する
    CHANNELS = 1 # 1ch
    SAMPLE_RATE = 8000 # 8kHz
    SAMPLE_WIDTH = 2 
    tmp_file_name = "/tmp/tmp.wav"
    wf = wave.open(tmp_file_name, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(data)
    wf.close()

    s3client.upload_file(tmp_file_name, BUCKET_NAME, output_filename)

    return {}
