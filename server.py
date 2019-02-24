import locationdata
import json

from flask import Flask, request

# Get a compiler
from pybars import Compiler
compiler = Compiler()

# Compile the template
x = open("template.html")
source = x.read()
template = compiler.compile(source)

app = Flask(__name__)

data_index = 0
data = {}
url="localhost:5000/"

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
        scores = list(map(lambda x: {'hood': x[1], 'score': x[0]['total'], 'subscores': x[0]['subscores']}, scores))
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
