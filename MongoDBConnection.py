from pymongo import MongoClient, database
import subprocess
import threading
import pymongo
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

DBName = os.getenv("DBname")  # Use this to change which Database we're accessing
# Put your database URL here
connectionURL = os.getenv("mongoURL")
# Change this to the name of your sensor data table
sensorTableName = os.getenv("TABLEname")


class Payload:
    def __init__(self, timestamp, topic, uid, sensor_data):
        self.timestamp = int(timestamp)
        self.topic = topic
        self.device_asset_uid = uid
        self.sensor_data = sensor_data

    def before5mins(self, other, fiveafter):
        return fiveafter > self.timestamp - other.timestamp

    def __str__(self):
        return "Timestamp: {}\n\tTopic: {}\n\tDevice Asset UID: {}\n\tSensor Data: {}".format(self.timestamp, self.topic, self.device_asset_uid, self.sensor_data)

    def __repr__(self):
        return "Timestamp: {}\n\tTopic: {}\n\tDevice Asset UID: {}\n\tSensor Data: {}".format(self.timestamp, self.topic, self.device_asset_uid, self.sensor_data)


def QueryToList(query):
    retlist = []
    for i in query:
        timestamp = i['payload']['timestamp']
        topic = i['payload']['topic']
        device_asset_uid = i['payload']['device_asset_uid']
        sensor_data = list(i['payload'].items())[-1]
        payload = Payload(timestamp, topic, device_asset_uid, sensor_data)

        retlist.append(payload)
    return retlist


def QueryDatabase() -> []:
    global DBName
    global connectionURL
    global currentDBName
    global running
    global filterTime
    global sensorTableName
    sensorTable = None
    cluster = None
    client = None
    db = None
    print("in query:",DBName,connectionURL,sensorTableName,cluster,client,db)
    try:
        cluster = connectionURL
        client = MongoClient(cluster,tlsCAFile=certifi.where())
        db = client[DBName]
        # print("cluster:",cluster,client,db)
        print("Database collections: ", db.list_collection_names())

        # We first ask the user which collection they'd like to draw from.
        sensorTable = db[sensorTableName]
        print("Table:", sensorTable)
        # We convert the cursor that mongo gives us to a list for easier iteration.
        # TODO: Set how many minutes you allow
        timeCutOff = datetime.now() - timedelta(minutes=1)

        oldDocuments = QueryToList(
            sensorTable.find({"time": {"$gte": timeCutOff}}))
        currentDocuments = QueryToList(
            sensorTable.find({"time": {"$lte": timeCutOff}}))

        # print("Current Docs: {}".format (currentDocuments))
        # print("Old Docs: {}".format(oldDocuments))



        cur_avgs = (getAvgs(currentDocuments))
        old_avgs = (getAvgs(oldDocuments))

        return [cur_avgs,old_avgs]
         
        #print("cur avgs",cur_avgs)
        #print("old avgs",old_avgs)

    
            




        # TODO: Parse the documents that you get back for the sensor data that you need
        # Return that sensor data as a list

    except Exception as e:
        print("Please make sure that this machine's IP has access to MongoDB.")
        print("Error:", e)
        exit(0)


def getAvgs(l):
        data_temp = {}
        # TODO: based off last entry should be off 5minsafternow > abs(self.timestamp - other.timestamp)
        cur_payload = None
        five_after = None

        for i in l[::-1]:
            if cur_payload == None:
                cur_payload = i
                five_after = (cur_payload.timestamp) + 300

            elif cur_payload.before5mins(i, five_after):
                key = i.sensor_data[0]
                val = i.sensor_data[1]
                if key not in data_temp:
                    data_temp[key] = i.sensor_data[1]
                    data_temp[key+"-count"] = 1
                else:
                    data_temp[key] += i.sensor_data[1]
                    data_temp[key+"-count"] += 1

        amounts = {}
        counts = {}
        for i in data_temp.items():
            if "count" in i[0]:
                counts[i[0]] = i[1]
            else:
                amounts[i[0]] = i[1]

        # get avgs 
        avgs = {}
        for i in amounts.items():
            sensor_name = i[0]
            sensor_val = i[1]
            sensor_count = counts[sensor_name+"-count"]
            avgs[sensor_name] = sensor_val/sensor_count

        return avgs

if __name__ == "__main__":
    print(QueryDatabase())
