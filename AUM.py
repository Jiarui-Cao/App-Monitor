import requests
import json
import time

api_endpoint = "http://localhost:3000"

while True:
    payload = {
        'misc' : {
            'username' : 'jcjr',
            'email' : 'jerrycao2025@u.northwestern.edu'
        },
        'counter' : {
            'total_login' : '3',
            'total_signout' : '2'
        },
        'time-series' : {
            'CPU_usage' : 0.5,
            'GPU_usage' : 0.2,
            'time' : int(time.time())
        }
    }

    r = requests.post(url = api_endpoint, data = payload)

    # TODO: add sleep() to make sure AUM doesn't bombard the server
