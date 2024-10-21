import os
from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread


def handleResponse(connectionSocket, addr):
    print("start Message")
    full_message = []
    unImplemented = ["HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]
    implemented = ["GET"]
    while True:
        messageSection = connectionSocket.recv(1024).decode()
        full_message.append(messageSection)
        print(messageSection)
        if "\r\n\r\n" in messageSection:
            break
    message = "".join(full_message)
    print(message)
    request = message.split("\r\n")
    requestLine = request[0].split(" ")
    if "GET" == requestLine[0]:
        filePath = requestLine[1].lstrip("/")

        headers = {}
        for header in request[1:]:
            if ": " in header:
                key, value = header.split(": ", 1)
                headers[key] = value

        try:
            lastModifiedTimestamp = os.path.getmtime(filePath)
            modifiedTime = datetime.utcfromtimestamp(lastModifiedTimestamp)
            if "Host" not in headers:
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"

            elif "If-Modified-Since" in headers:
                clientTimeString = headers["If-Modified-Since"]
                try:
                    client_time = datetime.strptime(
                        clientTimeString, "%a, %d %b %Y %H:%M:%S GMT"
                    )
                    if client_time >= modifiedTime:
                        response = "HTTP/1.1 304 Not Modified\r\n\r\n"
                    else:
                        file = open(filePath, "r")
                        file_content = file.read()
                        response = (
                            f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nLast-Modified: {modifiedTime}\r\n\r\n"
                            + file_content
                        )
                except ValueError:
                    response = "HTTP/1.1 400 Bad request\r\n\r\n"

            else:
                file = open(filePath, "r")
                file_content = file.read()
                response = (
                    f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nLast-Modified: {modifiedTime}\r\n\r\n"
                    + file_content
                )
        except FileNotFoundError:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
    else:
        if requestLine[0] not in implemented:
            response = "HTTP/1.1 501 Not Implemented\r\n\r\n"

    connectionSocket.sendall(response.encode())
    connectionSocket.close()
    print("Message Complete")
    print(response)


if __name__ == "__main__":
    serverPort = 80
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.bind(("", serverPort))
    serverSocket.listen(1)
    print("Server is ready\n")
    while True:
        connectionSocket, addr = serverSocket.accept()
        client_thread = Thread(target=handleResponse, args=(connectionSocket, addr))
        client_thread.start()
