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

maxPacketSize = 1024
defaultPort = 5050

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
    return min(highways, key=lambda h: sum(highways[h]) / len(highways[h]))

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
    tcpSocket.bind(('10.128.0.2', tcpPort))
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