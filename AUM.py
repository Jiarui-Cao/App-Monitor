import requests
import json
import time
import string
import random
import numpy as np

api_url = "http://127.0.0.1:5000"

x = 0
while True:

    d = time.time()
    res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=10))
    num = random.randrange(0,100)
    # print(d)
    # print(num)
    # print('\n')

    noise = np.random.normal(0, 1)
    x += 1 + noise
    print(x)

    data = {
        'misc': [['curr_time', d, 'sec'],
                 ['random', num, 'N/A']],
        'counter' : [['random_count', num, 'N/A'],
                     ['monthly_users', 1, 'people']],
        'time_series' : [['CPU_usage', random.random() * 100, '%'],
                         ['wait_time', random.random(), 'ms'],
                         ['revenue', x, '$']]
    }

    for key in data:
        d = data[key]
        for i in range(len(d)):
            payload = {
                'datatype': key,
                'metric': d[i][0],
                'value': d[i][1],
                'unit': d[i][2]
            }
            # print(payload)
            response = requests.post(api_url + '/update', json=payload)

    time.sleep(10)

