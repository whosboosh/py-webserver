#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import sys
import threading

class WebServer:

    MAX_CONNECTIONS = 5

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def generateHeader(self, code):
        header = ""
        if code == 200:
            header += "HTTP/21.1 200 OK\n"
        elif code == 404:
            header += "HTTP/1.1 404 Not Found\n"

        header += "Connection: close\n\n"
        return header.encode()

    def handleRequest(self, tcpSocket):
        data = tcpSocket.recv(1024).decode()

        # Get hostname from request
        try:
            requestName = data.split(' ')[1].split("http://")[1]
        except:
            print("Only http requests can be made")
            tcpSocket.close()
            return

        requestMethod = data.split(' ')[0]

        # Remove trailing / on hostname
        if (requestName[len(requestName)-1] == "/"):
            requestName = requestName[:-1]
        requestName+=".html"

        response = ""
        if requestMethod == "GET":
            # Check if on base directory, if so make file requested simply 'index.html'
            try:
                fileToServe = requestName.split("/")[1]
            except:
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
                responseData = "<head><title>404</title><body>404</body></head>".encode()
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
            self.server.close()

        self.server.listen(self.MAX_CONNECTIONS) # Listen to connections (MAX 5)

        # Indefinetly listen for any new incoming connections
        while True:
            (client, address) = self.server.accept()
            client.settimeout(60)
            print("Received connection from {addr}".format(addr=address))
            threading.Thread(target=self.handleRequest, args=([client])).start() # Create a thread for this connection

server = WebServer("localhost", 3003)
server.startServer()