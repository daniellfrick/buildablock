import googlemaps
import untangle
import geopy.distance
import json
import time
import re
import math

from json import JSONEncoder

locationTypes = ['restaurant', 'bar', 'transit_station', 'park', 'supermarket', 'church', 'mosque', 'coffee_shop', 'gym', 'library']
#locationTypes = ['coffee shop']


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)


class Neighborhood:
    def __init__(self, name, lat, long):
        self.name = name
        self.latitude = lat
        self.longitude = long
        self.scores = {}

    def __str__(self):
        return self.name + " " + str(self.latitude) + " " + str(self.longitude)

    def reprJSON(self):
        return self.__dict__


def evaluate(gameState):
    if 'work_address' in gameState.keys():
        if 'desired_work_distance' in gameState.keys():
            work_address = gameState['work_address']
            neighborhoods = loadNeighborhoods()

            scores = []
            for n in neighborhoods:
                score = {}

                w_dis = distanceToWork(googleKey, (n['latitude'], n['longitude']), work_address)
                d_w_d = gameState['desired_work_distance']
                d_dis = gameState['distances']
                dis = n['scores']

                score['total'] = 10
                score['subscores'] = []
                if w_dis > d_w_d:
                    score['total'] = score['total'] - abs(math.log(2 * (w_dis - d_w_d + .1) / d_w_d))

                for i in d_dis:
                    if dis[i] > d_dis[i]:
                        #print(dis[i])
                        #print(d_dis[i])
                        num = abs(d_dis[i] - 6) * abs(math.log((float(dis[i]) - d_dis[i] + .1)) / 3)
                        score['total'] = score['total'] - num
                        score['subscores'].append((i, 10 - num))
                    else:
                        score['subscores'].append((i, 10))
                scores.append((score, n['name']))
    else:
        neighborhoods = loadNeighborhoods()

        scores = []
        for n in neighborhoods:
            score = {}

            d_dis = gameState['distances']
            dis = n['scores']

            score['total'] = 10
            score['subscores'] = []

            for i in d_dis:
                if dis[i] > d_dis[i]:
                    # print(dis[i])
                    # print(d_dis[i])
                    num = abs(d_dis[i] - 6) * abs(math.log((float(dis[i]) - d_dis[i] + .1)) / 3)
                    score['total'] = score['total'] - num
                    score['subscores'].append((i, 10 - num))
                else:
                    score['subscores'].append((i, 10))
            scores.append((score, n['name']))
    return scores


def getLocationTypes():
    return locationTypes


def placesSearch(key, location, loctype, radius=5000):
    gmaps = googlemaps.Client(key=key)
    locquery = re.sub('[_]', '', loctype)
    placesnearby = gmaps.places(query=locquery, type=loctype, location=location, radius=radius)
    closestloc = (None,)
    for _ in range(1):
        for result in placesnearby['results']:
            #print(result['name'])
            loc = result['geometry']['location']
            destloc = (loc['lat'], loc['lng'])
            dist = geopy.distance.distance(location, destloc).km
            if closestloc[0] is None:
                closestloc = (result, dist)
            elif dist < closestloc[1]:
                closestloc = (result, dist)
        #time.sleep(1)
        try:
            placesnearby = gmaps.places_nearby(type=loctype, location=location, radius=radius, page_token=placesnearby['next_page_token'])
        except (KeyError, googlemaps.exceptions.ApiError):
            break
    if closestloc[0] is None:
        print("No " + loctype + " found")
        closestloc = ("None found", 20)
    return closestloc


def neighborhoodScores(key, name, lat, long):
    neighborhood = Neighborhood(name, lat, long)
    for loc_type in locationTypes:
        neighborhood.scores[loc_type] = placesSearch(key, (neighborhood.latitude, neighborhood.longitude), loc_type)[1]
    return neighborhood


def distanceToWork(key, loc, work_address):
    gmaps = googlemaps.Client(key=key)
    work_loc = gmaps.geocode(work_address)[0]
    work_coords = (work_loc['geometry']['location']['lat'], work_loc['geometry']['location']['lng'])
    return geopy.distance.distance(loc, work_coords).km


def loadNeighborhoods():
    with open('data.json') as data_file:
        data = json.load(data_file)
    return data

googleKey = "AIzaSyCJ0jtUgY5aGjEPy9BGvgHS-Hs0vE6PEDo"

"""gmaps = googlemaps.Client(key=key)

place_result = gmaps.places(query='', type='', location=(32.984971, -96.753445), radius=10000)
for x in place_result['results']:
    print(x['name'])"""

#print(distanceToWork(googleKey, (32.981098, -96.761414), "1380 W Campbell Rd, Richardson, TX 75080"))

"""zillowKey = "X1-ZWz1gxbgzsa617_26nu3"

#r = requests.get("http://www.zillow.com/webservice/GetRegionChildren.htm?zws-id=" + zillowKey + "&state=tx&city=dallas&childtype=neighborhood")
#content = r.content.decode("utf-8")
content = open("fileContent").readline()
obj = untangle.parse(content)
zillown = obj.children[0].response.list

neighborhoods = []

n = zillown.region[0]

temp = neighborhoodScores(googleKey, n.name.cdata, n.latitude.cdata, n.longitude.cdata)

with open('test.json', 'w') as outfile:
    json.dump(temp, outfile, cls=ComplexEncoder)

for n in zillown.region:
    print(n.name.cdata)
    neighborhoods.append(neighborhoodScores(googleKey, n.name.cdata, n.latitude.cdata, n.longitude.cdata))

with open('data.json', 'w') as outfile:
    json.dump(neighborhoods, outfile, cls=ComplexEncoder)"""
