import json
import datetime
import os
import boto3
import base64
import wave

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
        # 1行が、1秒分のデータとなっている
        lines = body.decode().split('\n') 
        for line in lines:
            if(line==''):
                continue
            s = json.loads(line)
            timestamp = datetime.datetime.strptime(s["timestamp"], '%Y-%m-%dT%H:%M:%S')
            # 取得期間のデータは、framesに追加する
            if(start_time_jst <= timestamp and timestamp <= end_time_jst):
                # テキストデータをバイナリに戻す
                b64_data = s["raw_data"].encode()
                # d = base64.b64decode(b64_data)
                frames.append(base64.b64decode(b64_data))
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
