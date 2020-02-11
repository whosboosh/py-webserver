#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import sys
import threading
import time
import signal

class WebServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port


    def generateHeader(self, code):
        header = ""
        if code == 200:
            header += "HTTP/1.1 200 OK\n"
        elif code == 404:
            header += "HTTP/1.1 404 Not Found\n"

        header += "Connection: close\n\n"
        return header.encode()

    def handleRequest(self, tcpSocket):
        data = tcpSocket.recv(1024)

        requestMethod = data.split(' ')[0]

        # Build string without query parameters
        fileToServe = data.split(' ')[1].split('?')[0]
        fileToServe+=".html"

        if requestMethod == "GET":       
            if fileToServe.split(".html")[0] == "/": # Remove the '.html' part and check if on base directory
                fileToServe = "index.html"

            print("Serving page {pages}".format(pages=fileToServe))

            # Attempt to open file
            try:
                file = open(fileToServe,"rb")
                responseData = file.read()
                responseHeader = self.generateHeader(200)
                file.close()                
            except:
                print("File not found")
                responseData = "<head><title>404</title><body>404</body></head>"
                responseHeader = self.generateHeader(404)

            response = (responseHeader+responseData)

            tcpSocket.send(response)
            tcpSocket.close()

    def startServer(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket object

        # Attempt to bind to address and port
        try:
            self.server.bind((self.host, self.port))
            print("Started server on port: {port}".format(port=self.port))
        except:
            print("Failed to bind to port {port}".format(port=self.port))
            self.shutdownServer()
            sys.exit(1)

        self.server.listen(5) # Listen to connections

        # Indefinetly listen for any new incoming connections
        while True:
            (client, address) = self.server.accept()
            client.settimeout(60)
            print("Received connection from {addr}".format(addr=address))
            threading.Thread(target=self.handleRequest, args=([client])).start() # Create a thread for this connection

    def shutdownServer(self):
        try:
            self.server.close()
            self.server.shutdown(socket.SHUT_RDWR)
            sys.exit(1)
        except:
            pass

def shutdown(signal, unused):
    server.shutdownServer()
    sys.exit(1)

signal.signal(signal.SIGINT, shutdown)
server = WebServer("localhost", 3003)
server.startServer()