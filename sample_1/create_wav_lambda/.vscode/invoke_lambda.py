import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import index as target
event = {
	"start_time": "2021-04-14 13:24:00",
	"period_sec": 50,
	"output_filename": "out.wav"
}

response = target.lambda_handler(event, None)
print(response)
