import requests

### Querying data
queries = ["/data",
           "/data/misc",
           "/data/misc/lolol",
           "/data/counter",
           "/metric_names/misc",
           ]
api_url = "http://127.0.0.1:5000"

for q in queries:
    response = requests.get(api_url + q)
    print(q, ": ", response.json(), "\n")


### Deleting data
response = requests.delete(api_url + "/misc/beta")
print("After deletion:", response.json(), "\n")


### Updating data