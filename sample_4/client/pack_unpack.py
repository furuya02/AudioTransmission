import datetime
import struct

def disp(dt, data):
    print("{} {} type:{} len:{}".format(dt, data, type(data), len(data)))


# 転送前のデータ
print("- before -")
raw_data = bytes(range(0, 10)) 
now = datetime.datetime.now()
disp(now, raw_data)
# 時刻とデータの結合
transfer_data = struct.pack('<d', now.timestamp()) + raw_data


print("- transfer -")
print("{} type:{} len:{}".format(transfer_data, type(transfer_data), len(transfer_data)))

# 転送後のデータ
print("- after -")
# 時刻とデータの分離
ts = transfer_data[:8]
raw_data_2 = transfer_data[8:]
now_2 = datetime.datetime.fromtimestamp(struct.unpack('<d', ts)[0])
disp(now_2, raw_data_2)



