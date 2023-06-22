import json
from flask import Flask, request, json, jsonify
from sql_main import database
from config import config

app = Flask(__name__)

db = database(config())

### GET ###
@app.route('/data', methods=['GET'])
def query_all_data():
    misc = db.get_all_metrics("misc")
    counter = db.get_all_metrics("counter")
    time_series = db.get_all_metrics("time_series")
    return {"misc": misc, 
            "counter": counter, 
            "time_series": time_series}

@app.route('/data/<datatype>', methods=['GET'])
def query_all_metrics(datatype):
    return db.get_all_metrics(datatype)

@app.route('/data/<datatype>/<metric>', methods=['GET'])
def query_metric(datatype, metric):
    return db.get_metric(datatype, metric)

@app.route('/metric_names/<datatype>', methods=['GET'])
def get_all_metric_names(datatype):
    lst = db.get_all_metric_names(datatype)
    for i in range(len(lst)):
        lst[i] = lst[i][0]
    return lst


### DELETE ###
@app.route('/<datatype>/<metric>', methods=['DELETE'])
def delete_metric(datatype, metric):
    res = db.get_metric(datatype, metric)
    if len(res) != 0:
        db.delete_metric(datatype, metric)
    return db.get_all_metrics(datatype)


### POST ###
@app.route('/update', methods=['POST'])
def update_metric():
    if request.is_json:
        data = request.json
        res = db.get_metric(data['datatype'], data['metric'])
        if len(res) == 0:
            db.insert_metric(data['datatype'], data['metric'], data['value'], data['unit'])
        else:
            db.update_metric(data['datatype'], data['metric'], data['value'])
    else:
        return "Content type is not supported"
    return data



# TODO: Need to implement start time, end time, & granularity (automatic computation) level of time-series data fetches, also need defaults!


app.run(debug=True)