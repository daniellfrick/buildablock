import locationdata
import json

from flask import Flask, request
app = Flask(__name__)


@app.route("/get/neighborhood", methods=['POST'])
def neighborhood():
    if request.method == "POST":
        print(request.data)
        gameState = request.get_json(force=True)
        print(gameState)
        #print("test")
        scores = locationdata.evaluate(gameState)
        maxScore = 0
        bestHood = None
        for s in scores:
            if s[0] > maxScore:
                maxScore = s[0]
                bestHood = s[1]
        print(str(maxScore) + "  " + bestHood)
        return "success"


print("started")
