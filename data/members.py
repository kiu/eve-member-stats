#!/usr/bin/python
import requests
import re
import json
import operator
from lxml import etree
import sys
import time
import datetime
import random
from collections import Counter

# ---------------------------------------------

online = True

if (len(sys.argv) != 3):
    print sys.argv[0] + " <keyID> <vCode>"
    sys.exit(1)

api_keyid = sys.argv[1]
api_vcode = sys.argv[2]

# ---------------------------------------------

colors = [
    "#00ffff",
    "#f0ffff",
    "#f5f5dc",
    "#000000",
    "#0000ff",
    "#a52a2a",
    "#00ffff",
    "#00008b",
    "#008b8b",
    "#a9a9a9",
    "#006400",
    "#bdb76b",
    "#8b008b",
    "#556b2f",
    "#ff8c00",
    "#9932cc",
    "#8b0000",
    "#e9967a",
    "#9400d3",
    "#ff00ff",
    "#ffd700",
    "#008000",
    "#4b0082",
    "#f0e68c",
    "#add8e6",
    "#e0ffff",
    "#90ee90",
    "#d3d3d3",
    "#ffb6c1",
    "#ffffe0",
    "#00ff00",
    "#ff00ff",
    "#800000",
    "#000080",
    "#808000",
    "#ffa500",
    "#ffc0cb",
    "#800080",
    "#800080",
    "#ff0000",
    "#c0c0c0",
    "#ffffff",
    "#ffff00"
]

# ---------------------------------------------

now = int(time.time())

if (online):
	req = requests.get('https://api.eveonline.com/corp/MemberTracking.xml.aspx?keyID=' + api_keyid + "&vCode=" + api_vcode + "&extended=1")
	root = etree.fromstring(req.text.encode("utf-8"))
else:
	root = etree.parse(open('MemberTracking.xml.aspx','r'))

rows = root.xpath("/eveapi/result/rowset/row")


# ---------------------------------------------

with open('static-data-regions.json') as data_file:
    regions = json.load(data_file)

with open('static-data-systems.json') as data_file:
    systems = json.load(data_file)

with open('static-data-stations.json') as data_file:
    stations = json.load(data_file)

# ---------------------------------------------

def store(name, data):
    f = open("../webroot/" + name ,'w')
    json.dump(data, f)
    f.close()


def findRegion(id):
    return regions[id]

def findSystem(id):
    for s in systems:
	if s['system_id'] == id:
	    return s
    return None

def findStation(id):
    for s in stations:
	if s['station_id'] == id:
	    return s
    return None


def findSystemName(name):
    for s in systems:
	if s['system_name'] == name:
	    return s
    return None

def findStationName(name):
    for s in stations:
	if s['station_name'] == name:
	    return s
    return None

def findRegionName(name):
    for r in regions:
	if r['region_name'] == name:
	    return r
    return None

def findColorForLocationName(name):
    match = findStationName(name)
    if not match:
	match = findSystemName(name)
    if not match:
	match = findRegionName(name)
    if not match:
	return "#FF00FF"
    return colors[int(match['region_id']) % len(colors)]

# ---------------------------------------------

data = []
for row in rows:
	location_id = str(row.xpath("@locationID")[0])
	location_name = str(row.xpath("@location")[0])

	logon = datetime.datetime.strptime(row.xpath("@logonDateTime")[0], "%Y-%m-%d %H:%M:%S")
	logon_days =  int((now - int(time.mktime(logon.timetuple()))) / 60 / 60 / 24)

	logoff = datetime.datetime.strptime(row.xpath("@logoffDateTime")[0], "%Y-%m-%d %H:%M:%S")
	logoff_days =  int((now - int(time.mktime(logoff.timetuple()))) / 60 / 60 / 24)

	match = findStation(location_id)
	if not match:
	    match = findSystem(location_id)
	if not match:
	    print("Warning: Could not resolve {0} {1}".format(location_id, location_name))
	    continue

	item = {
        'system': match,
        'logon_days': logon_days,
        'logoff_days': logoff_days,
	}

	data.append(item)

# ---------------------------------------------

def groupBySecurity(data, maxage):

    result = {
	'highsec':0,
	'lowsec':0,
	'nullsec':0,
	'thera':0,
	'wormhole':0,
    }

    for item in data:
	if item['logon_days'] > maxage:
	    continue
	if float(item['system']['security']) >= 0.5:
	    result['highsec'] = result['highsec'] + 1
	    continue
	if float(item['system']['security']) > 0.0:
	    result['lowsec'] = result['lowsec'] + 1
	    continue
	if float(item['system']['security']) != -0.99:
	    result['nullsec'] = result['nullsec'] + 1
	    continue
	if "11000031" in item['system']['region_id']:
	    result['thera'] = result['thera'] + 1
	    continue
	result['wormhole'] = result['wormhole'] + 1


    return [
	{
	    'value': result['highsec'],
	    'color': '#00EF47',
	    'highlight': "#d8e081",
	    'label': 'Highsec',
	},
	{
	    'value': result['lowsec'],
	    'color': '#F06000',
	    'highlight': "#d8e081",
	    'label': 'Lowsec',
	},
	{
	    'value': result['nullsec'],
	    'color': '#F00000',
	    'highlight': "#d8e081",
	    'label': 'Nullsec',
	},
	{
	    'value': result['thera'],
	    'color': '#242479',
	    'highlight': "#d8e081",
	    'label': 'Thera',
	},
	{
	    'value': result['wormhole'],
	    'color': '#494949',
	    'highlight': "#d8e081",
	    'label': 'Wormhole',
	},
    ]

def groupByRegion(data, maxage, maxresult):

    result = dict()

    for item in data:
	if item['logon_days'] > maxage:
	    continue

	region_name = item['system']['region_name']

	if float(item['system']['security']) == -0.99:
	    if "11000031" in item['system']['region_id']:
		region_name = "Thera"
	    else:
		region_name = "Wormhole"

	if  region_name in result.keys():
	    result[region_name] = result[region_name] + 1
	else:
	    result[region_name] = 1

    c = Counter(result)
    rss = c.most_common(maxresult)
    items = []
    for region_name, amount in rss:
	item = {
	    'value': amount,
	    'color': findColorForLocationName(region_name),
	    'highlight': "#d8e081",
	    'label': region_name,
	}
	items.append(item)
    return items

def groupBySystem(data, maxage, maxresult):

    result = dict()

    for item in data:
	if item['logon_days'] > maxage:
	    continue

	system_name = item['system']['system_name']

	if float(item['system']['security']) == -0.99:
	    if not "11000031" in item['system']['region_id']:
		system_name = "Wormhole"

	if system_name in result.keys():
	    result[system_name] = result[system_name] + 1
	else:
	    result[system_name] = 1

    c = Counter(result)
    rss = c.most_common(maxresult)
    items = []
    for system_name, amount in rss:
	item = {
	    'value': amount,
	    'color': findColorForLocationName(system_name),
	    'highlight': "#d8e081",
	    'label': system_name,
	}
	items.append(item)
    return items

def countByDays(data, maxage):

    last_login = [0 for i in range(maxage + 1)]
    for item in data:
	logon_days = item['logon_days']
	if  logon_days > maxage:
	    continue
	last_login[logon_days] = last_login[logon_days] + 1


    points = []
    sum = 0;
    for i in range(0, maxage):
	sum = sum + last_login[i]
	points.append(sum)

    return {
	'labels': range(maxage, 0, -1),
	'datasets': [
	    {
	    'label': "All members",
	    'fillColor': "rgba(151,187,205,0.2)",
	    'strokeColor': "rgba(151,187,205,1)",
	    'pointColor': "rgba(151,187,205,1)",
	    'pointStrokeColor': "#fff",
	    'pointHighlightFill': "#fff",
	    'pointHighlightStroke': "rgba(151,187,205,1)",
	    'data': list(reversed(points))
	    },
	]
    }

# ---------------------------------------------

store('stats_history.json', countByDays(data, 28))

store('stats_security-7.json', groupBySecurity(data, 7))
store('stats_security-14.json', groupBySecurity(data, 14))
store('stats_security-21.json', groupBySecurity(data, 21))
store('stats_security-28.json', groupBySecurity(data, 28))

store('stats_region-7.json', groupByRegion(data, 7, 20))
store('stats_region-14.json', groupByRegion(data, 14, 20))
store('stats_region-21.json', groupByRegion(data, 21, 20))
store('stats_region-28.json', groupByRegion(data, 28, 20))

store('stats_system-7.json', groupBySystem(data, 7, 20))
store('stats_system-14.json', groupBySystem(data, 14, 20))
store('stats_system-21.json', groupBySystem(data, 21, 20))
store('stats_system-28.json', groupBySystem(data, 28, 20))

store("stats_last_update.json", {'last_update': root.xpath("/eveapi/currentTime")[0].text})

# ---------------------------------------------
