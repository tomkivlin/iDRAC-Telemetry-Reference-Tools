
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs
from datetime import datetime
from flask import Flask, jsonify, request, Blueprint
import json 
import copy
import re
from os import listdir
from os.path import isfile, join


esxtop_bp = Blueprint('esxtop', __name__)

columnMap = dict()
metrics = dict()
hostname=""

print(">>>> Initializing esxtop datasource")

@esxtop_bp.route("/esxtop/api/v1/label/__name__/values", methods=['GET'])
def labels():
    #reloadMetrics()
    labels = []
    outResults = {
        "status": "success",
        "data": labels
    }
    for col in columnMap:
        if col == "time":
            continue
        labels.append(col)
    return json.dumps(outResults)
    
@esxtop_bp.route("/esxtop/api/v1/values", methods=['GET'])
@esxtop_bp.route("/esxtop/api/v1/query", methods=['GET'])
@esxtop_bp.route("/esxtop/api/v1/query_range", methods=['GET'])
def query():
    # reloadMetrics()
    query_parameters = request.args
    
    query_val = query_parameters.get('query')
    start_time = query_parameters.get('start')
    end_time = query_parameters.get('end')
    return populateResults(query_val,start_time,end_time)
    

@esxtop_bp.route("/esxtop/api/v1/metadata", methods=['GET'])
def metadata():
    return getMetadata()


metadataResults = {
    "status": "success",
    "data": {
    }
}

results = {
    "status": "success",
    "data": {
        "resultType": "matrix",
        "result": [

        ]
    }
}

result = {
    "metric": {
        "__name__":"",
        "job": "",
        "instance": ""
    },
    "values": []
}

def getMetadata():
    outResults = copy.deepcopy(metadataResults)
    for col in columnMap:
        if col == "time":
            continue
        outResults["data"][col] = [{
            "type": "gauge",
            "help": "",
            "unit": ""
        }]
        
    return json.dumps(outResults)

def populateResults(query, start, end):
    outResults = copy.deepcopy(results)
    resultMap = {}
    
    for col in columnMap:        
        if col == "time" or (query != None and col.find(query) == -1):
            continue
        thisResult = copy.deepcopy(result)
        resultMap[col] = thisResult
        thisResult["metric"]["__name__"] = col    
        thisResult["metric"]["instance"] = hostname

    index = 0

    for t in metrics["time"]:
        if (start != None and (t < float(start))) or (end != None and (t > float(end)) ):
            index = index + 1
        else:
            for col in columnMap:            
                if col == "time" or (query != None and col.find(query) == -1):
                    continue                
                resultMap[col]["values"].append([t,metrics[col][index]])
            index = index + 1    
        

    for col in columnMap:
        if col in resultMap:
            outResults["data"]["result"].append(resultMap[col])    
    
    return json.dumps(outResults)

def timeToMillis(time):    
    return datetime.strptime(time,'%m/%d/%Y %H:%M:%S').timestamp()

def reloadMetrics():
    global hostname, columnMap, metrics
    columnMap = dict()
    metrics = dict()

    for fname in listdir('/import/data/esxtop'):
        fullPath = join('/import/data/esxtop',fname)
        if isfile(fullPath) and fname[0] != "." :
            print(">>>> Loading " + fname)
            with open(fullPath) as f:    
                print(">>>> Opened " + fname)
                firstLine = True
                for line in f:
                    columns = line.split(",")        
                    index = 0
                    # count_vals_c0 = 0
                    # sum_vals_c0 = 0
                    # count_vals_c1 = 0
                    # sum_vals_c1 = 0
                    # count_vals_c2 = 0
                    # sum_vals_c2 = 0
                    if firstLine:
                        firstLine = False
                        metrics["time"] = []
                        for col in columns:
                            try:
                                col = col[3:]
                                #try: 
                                hostnameLoc = col.index("\\")   
                                if hostname == "":
                                    hostname = col[0:hostnameLoc]           
                                    print("hn:"+hostname)      
                                name = col[hostnameLoc+1:-1]
                                name = re.sub("[() ]","",name).replace('\\', '_')                    
                                # except ValueError:
                                #     name = fname+"_"+col
                                #     name = re.sub("[() ]","",name).replace('\\', '_')                    
                                columnMap[name] = index
                                metrics[name] = []
                                index = index + 1
                            except ValueError:
                                index = index + 1
                                continue                 
                    else:
                        metrics["time"].append(timeToMillis(columns[0].replace('"', '')))
                        for col in columnMap:
                            val = columns[columnMap[col]].replace('"', '')
                            # if "StateC0" in col:
                            #     sum_vals_c0 = sum_vals_c0 + float(val)
                            #     count_vals_c0 = count_vals_c0 + 1
                            # elif "StateC1" in col:
                            #     sum_vals_c1 = sum_vals_c1 + float(val)
                            #     count_vals_c1 = count_vals_c1 + 1
                            # elif "StateC2" in col:
                            #     sum_vals_c2 = sum_vals_c2 + float(val)
                            #     count_vals_c2 = count_vals_c2 + 1
                            metrics[col].append(val)
                        # avg_c0 = sum_vals_c0 / count_vals_c0
                        # print(avg_c0)
                        # avg_c1 = sum_vals_c1 / count_vals_c1
                        # print(avg_c1)
                        # avg_c2 = sum_vals_c2 / count_vals_c2
                        # print(avg_c2)

print(">>>> Initialized esxtop datasource")

reloadMetrics()


