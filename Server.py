import socket
import ipaddress
import threading
import time
import contextlib
import errno
import json
from dataclasses import dataclass
import random
import sys
from collections import defaultdict
from MongoDBConnection import QueryDatabase

maxPacketSize = 1024
defaultPort = 5050

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def GetFreePort(minPort: int = 1024, maxPort: int = 65535):
    for i in range(minPort, maxPort):
        print("Testing port",i);
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as potentialPort:
            try:
                potentialPort.bind(('localhost', i));
                potentialPort.close();
                print("Server listening on port",i);
                return i
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    print("Port",i,"already in use. Checking next...");
                else:
                    print("An exotic error occurred:",e);

def GetServerData() -> []:
    import MongoDBConnection as mongo
    return mongo.QueryDatabase()


def SortSensors(sensors):
    saved_sensors = defaultdict(list)
    for sensor in sensors:
        saved_sensors[sensor["highway_name"]].append(sensor["sensor_value"])
    return dict(saved_sensors)

def BestHighway(highways):
    if not highways:
        return None

    min_weighted_mean = float('inf')
    best_highway = None

    for highway, readings in highways.items():
        total_weight = 0
        weighted_sum = 0

        for i, reading in enumerate(readings):
            weight = i + 1  # Weight increases linearly from 1 for oldest reading to len(readings) for newest
            total_weight += weight
            weighted_sum += reading * weight

        weighted_mean = weighted_sum / total_weight
        #print(weighted_mean)
        if weighted_mean < min_weighted_mean:
            min_weighted_mean = weighted_mean
            best_highway = highway

    return best_highway

def ListenOnTCP(tcpSocket: socket.socket, socketAddress):
    try:
        with tcpSocket:
            while True:
                client_data = tcpSocket.recv(1024)
                if not client_data:
                    print("No data received. Closing connection.")
                    break
                server_response = GetServerData()
                sorted_sensors = SortSensors(server_response)
                #print(sorted_sensors)
                best_highway = BestHighway(sorted_sensors)
                data = {"Best Highway": best_highway}
                json_data = json.dumps(data)

                tcpSocket.sendall(json_data.encode())
                print("Data sent to client.")

    except socket.error as e:
        print(f"Socket error occurred: {e}")

    finally:
        print("Connection closed.")

def CreateTCPSocket() -> socket.socket:
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpPort = defaultPort
    print("TCP Port:",tcpPort)
    try:
        tcpSocket.bind(('10.128.0.2', tcpPort))
    except:
        print("could not bind to given ip, binding to local host")
        tcpSocket.bind(('127.0.0.1', tcpPort))
    return tcpSocket

def LaunchTCPThreads():
    tcpSocket = CreateTCPSocket();
    tcpSocket.listen(5)
    while True:
        connectionSocket, connectionAddress = tcpSocket.accept();
        connectionThread = threading.Thread(target=ListenOnTCP, args=[connectionSocket, connectionAddress]);
        connectionThread.start()

if __name__ == "__main__":
    tcpThread = threading.Thread(target=LaunchTCPThreads);
    tcpThread.start();