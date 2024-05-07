import socket
import ipaddress
import threading
import time
import contextlib
import errno
from dataclasses import dataclass
import random
import sys

maxPacketSize = 1024
defaultPort = 8888  # TODO: Set this to your preferred port


def GetFreePort(minPort: int = 1024, maxPort: int = 65535):
    for i in range(minPort, maxPort):
        print("Testing port", i)
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as potentialPort:
            try:
                potentialPort.bind(('localhost', i))
                potentialPort.close()
                print("Server listening on port", i)
                return i
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    print("Port", i, "already in use. Checking next...")
                else:
                    print("An exotic error occurred:", e)


def GetServerData() -> []:
    import MongoDBConnection as mongo
    return mongo.QueryDatabase()


def ListenOnTCP(tcpSocket: socket.socket, socketAddress):
    payload = str(tcpSocket.recv(1024).decode())
    if (payload == 'exit'):
        exitSignal = 1
        print('exit wopped')
    print('current payload {}'.format(payload))
    reply = str(GetServerData()).encode('utf-8')
    tcpSocket.send(reply)
    print('Original: {} ; Reply: {}'.format(str(payload), str(reply)))
    # TODO: Implement TCP Code, use GetServerData to query the database.


def CreateTCPSocket() -> socket.socket:
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpPort = defaultPort
    print("TCP Port:", tcpPort)
    tcpSocket.bind(('localhost', tcpPort))
    return tcpSocket


def LaunchTCPThreads():
    tcpSocket = CreateTCPSocket()
    tcpSocket.listen(5)
    while True:
        connectionSocket, connectionAddress = tcpSocket.accept()
        connectionThread = threading.Thread(
            target=ListenOnTCP, args=[connectionSocket, connectionAddress])
        connectionThread.start()


if __name__ == "__main__":
    exitSignal = 0
    tcpThread = threading.Thread(target=LaunchTCPThreads)
    tcpThread.start()

    while not exitSignal:
        time.sleep(1)
    print("Ending program by exit signal...")
