import json
from flask import Flask, request, jsonify
import sql_main

app = Flask(__name__)


### GET ###
@app.route('/data', methods=['GET'])
def query_all_data():
    misc = sql_main.get_all_metrics("misc")
    counter = sql_main.get_all_metrics("counter")
    return [misc, counter]

@app.route('/data/<datatype>', methods=['GET'])
def query_all_metrics(datatype):
    return sql_main.get_all_metrics(datatype)

@app.route('/data/<datatype>/<metric>', methods=['GET'])
def query_metric(datatype, metric):
    return sql_main.get_metric(datatype, metric)

@app.route('/metric_names/<metric_name>', methods=['GET'])
def get_all_metric_names(metric_name):
    return sql_main.get_all_metric_names(metric_name)


### DELETE ###
@app.route('/<datatype>/<metric>', methods=['DELETE'])
def delete_metric(datatype, metric):
    res = sql_main.get_metric(datatype, metric)
    if len(res) != 0:
        sql_main.delete_metric(datatype, metric)
    return sql_main.get_all_metrics(datatype)


### PUT ###
@app.route('/update', methods=['PUT'])
def update_metric(datatype, metric, value, unit):
    res = sql_main.get_metric(datatype, metric)
    if len(res) == 0:
        sql_main.insert_metric(datatype, metric, value, unit)
    else:
        sql_main.update_metric(datatype, metric, value)



### POST ###


app.run(debug=True)