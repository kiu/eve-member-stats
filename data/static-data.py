#!/usr/bin/python
import MySQLdb
import json
from lxml import etree
import requests

# ---------------------------------------------

online = True

db = MySQLdb.connect(host="localhost", user="toolkit", passwd="toolkit", db="toolkit_carnyx")
cur = db.cursor()

# ---------------------------------------------

regions = []
region_to_name = dict()

cur.execute("SELECT regionId, regionName FROM mapRegions")
for res in cur.fetchall() :
	region_id = str(res[0])
	region_name = str(res[1])

	regions.append({
	    'region_id': region_id,
	    'region_name': region_name,
	})

	region_to_name[region_id] = region_name

f = open("static-data-regions.json",'w')
json.dump(regions, f)
f.close()

# ---------------------------------------------

systems = []
system_to_region = dict()
system_to_security = dict()
system_to_name = dict()

cur.execute("SELECT solarSystemID, SolarSystemName, security, regionID FROM mapSolarSystems")
for res in cur.fetchall() :
	system_id = str(res[0])
	system_name = str(res[1])
	security = str(res[2])
	region_id = str(res[3])

	systems.append({
	    'system_id': system_id,
	    'system_name': system_name,
	    'region_id': region_id,
	    'region_name': region_to_name[region_id],
	    'security': security,
	})

	system_to_region[system_id] = region_id
	system_to_security[system_id] = security
	system_to_name[system_id] = system_name

f = open("static-data-systems.json",'w')
json.dump(systems, f)
f.close()

# ---------------------------------------------

stations = []
cur.execute("SELECT stationID, solarSystemID, regionID, stationName FROM staStations")
for res in cur.fetchall() :
	station_id = str(res[0])
	station_name = str(res[3])

	system_id = str(res[1])
	system_name = system_to_name[system_id]
	security = system_to_security[system_id]
	region_id = str(res[2])

	stations.append({
	    'station_id': station_id,
	    'station_name': station_name,
	    'system_id': system_id,
	    'system_name': system_name,
	    'region_id': region_id,
	    'region_name': region_to_name[region_id],
	    'security': security,
	})


if (online):
        req = requests.get('https://api.eveonline.com/eve/ConquerableStationList.xml.aspx')
        root = etree.fromstring(req.text.encode("utf-8"))
else:
        root = etree.parse(open('ConquerableStationList.xml.aspx','r'))

rows = root.xpath("/eveapi/result/rowset/row")
for row in rows:
        station_id = row.xpath("@stationID")[0]
        station_name = row.xpath("@stationName")[0]

        system_id = row.xpath("@solarSystemID")[0]
	system_name = system_to_name[system_id]
	security = system_to_security[system_id]
	region_id = system_to_region[system_id]

	stations.append({
	    'station_id': station_id,
	    'station_name': station_name,
	    'system_id': system_id,
	    'system_name': system_name,
	    'region_id': region_id,
	    'region_name': region_to_name[region_id],
	    'security': security,
	})

f = open("static-data-stations.json",'w')
json.dump(stations, f)
f.close()

# ---------------------------------------------

