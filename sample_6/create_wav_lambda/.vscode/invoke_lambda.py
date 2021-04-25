import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import index as target
event = {
	"start_time": "2021-04-23 12:52:00",
	"period_sec": 60,
	"output_filename": "out.wav"
}

response = target.lambda_handler(event, None)
print(response)
