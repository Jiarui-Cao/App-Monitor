import requests
import json
import pandas as pd

api_url = "http://127.0.0.1:5000"

### Querying data
queries = [
        #    "/data",
        #    "/data/misc",
         #   "/data/misc/alpha",
        #    "/data/misc/lolol",
        #    "/data/counter",

        #    "/data/time_series",
         #   "/data/time_series/weight",
        #    "/data/time_series/lolol",

        #    "/metric_names/misc",
        #    "/metric_names/counter",
        #    "/metric_names/time_series"
           ]

# for q in queries:
#     response = requests.get(api_url + q)
#     print(q, ": ", response.json(), "\n")


### Deleting data
# response = requests.delete(api_url + "/time_series/gamma")
# print("After deletion:", response.json(), "\n")


# ### Updating data
# data = {"datatype": "time_series",
#         "metric": "weight",
#         "value": 75,
#         "unit": "kg"}
# headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# response = requests.post(api_url + '/update', json=data, headers=headers)
# print(response.json())


data = requests.get(api_url + "/data/time_series/revenue").json()
data = pd.DataFrame(data, columns=['id', 'time', 'metric', 'value', 'unit'])
data['time'] = pd.to_datetime(data['time'], unit='s')
data.set_index('time', inplace=True)

print(data)