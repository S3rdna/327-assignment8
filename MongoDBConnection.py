import pymongo
from pymongo import MongoClient, database
import subprocess
import threading
from datetime import datetime, timedelta, timezone
import time

DBName = "test" 
connectionURL = "mongodb+srv://jason200116:Barber2904@assigment7.4w53oop.mongodb.net/?retryWrites=true&w=majority&appName=Assigment7"

def QueryToList(query):
	return list(query)  

def QueryDatabase() -> []:
	global DBName
	global connectionURL
	global currentDBName
	global running
	global filterTime
	global sensorTable
	cluster = None
	client = None
	db = None
	try:
		cluster = connectionURL
		client = MongoClient(cluster)
		db = client[DBName]
	
		sensorTable = db["Sensor Data"]
		sensorTable_meta = db["Sensor Data_metadata"]
		
		timeCutOff = datetime.now(timezone.utc) - timedelta(minutes=5)

		documents = QueryToList(sensorTable.find({"time":{"$gte":timeCutOff}}))
		documents_meta = QueryToList(sensorTable_meta.find())

		if len(documents) == 0:
			print("No data found, converting to all data")
			documents = QueryToList(sensorTable.find({"time":{"$lte":timeCutOff}}))

		highway_lookup = {}
		for doc_meta in documents_meta:
			asset_uid = doc_meta.get("assetUid")
			event_types = doc_meta.get("eventTypes", [])
			if event_types:
				device = event_types[0][0].get("device", {})
				highway_name = device.get("name", "").replace(" Device", "")
				highway_lookup[asset_uid] = highway_name
		sensor_data = []
		for doc in documents:
			sensor_payload = doc.get("payload", {})
			sensor_values = list(sensor_payload.values())
			if len(sensor_values) == 4:
				sensor_id = sensor_values[2]
				sensor_value = sensor_values[3]
				highway_name = highway_lookup.get(sensor_id, "Unknown Highway")
				sensor_data.append({"highway_name": highway_name, "sensor_value": int(sensor_value)})
		print("Task completed")
		return sensor_data

	except Exception as e:
		print("Please make sure that this machine's IP has access to MongoDB.")
		print("Error:",e)
		exit(0)