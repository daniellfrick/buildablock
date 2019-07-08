import locationdata
import json

from flask import Flask, request

# Get a compilerpip
from pybars import Compiler
compiler = Compiler()

# Compile the template
x = open("template.html")
source = x.read()
template = compiler.compile(source)

app = Flask(__name__)

data_index = 0
data = {}
url="shanemendez.com:5000/"

@app.route("/get/neighborhood", methods=['POST'])
def neighborhood():
    global data
    global data_index
    global url
    if request.method == "POST":
        print(request.data)
        gameState = request.get_json(force=True)
        print(gameState)
        #print("test")
        scores = locationdata.evaluate(gameState)
        maxScore = 0
        bestHood = None
        for s in scores:
            print(s)
            if s[0]['total'] > maxScore:
                maxScore = s[0]['total']
                bestHood = s[1]
        scores.sort(reverse=True, key=lambda x:x[0]['total'])
        print(str(maxScore) + "  " + bestHood)
        data_index += 1
        scores = list(map(lambda x: {'hood': x[1], 'score': round(x[0]['total'],1), 'subscores': list(map(lambda y: {'location_type': y[0], 'subscore': y[1], 'name': y[2], 'rating': y[3], 'dist': y[4], 'address': y[5]}, x[0]['subscores']))}, scores))
        data[str(data_index)] = {'hoods': scores}
        return url + str(data_index)

@app.route('/<path:path>')
def catch_all(path):
    global data
    global data_index
    global template
    print(data[path])
    if path in data:
        return template(data[path])
    return "bad request"

print("started")
