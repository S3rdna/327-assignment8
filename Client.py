import socket
import ipaddress
import threading
import time
import contextlib
import errno

maxPacketSize = 1024
defaultPort = 8888  # TODO: Change this to your expected port
serverIP = '127.0.0.1'  # TODO: Change this to your instance IP

try:
    tcpPort = int(input("Please enter the TCP port of the host..."))
except Exception:
    tcpPort = 0
if tcpPort == 0:
    tcpPort = defaultPort

clientMessage = ""
while clientMessage != "exit":
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.connect((serverIP, tcpPort))
    clientMessage = input("Please type the message that you'd like to" +
                          " send (Or type \"exit\" to exit):\n>")

    # TODO: Send the message to your server
    tcpSocket.send(clientMessage.encode('utf-8'))
    # TODO: Receive a reply from the server for the best highway to take
    reply = tcpSocket.recv(1024).decode('utf-8')
    # TODO: Print the best highway to take
    print('Server reply: ', reply)

    tcpSocket.close()
