import sys
from socket import AF_INET, SOCK_STREAM, socket

if __name__ == "__main__":
    serverPort = 80
    serverName = sys.argv[1]
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((serverName, serverPort))

        print("Input HTTP request line (e.g., GET /test.html HTTP/1.1):\n")
        requests = []
        while True:
            request_line = input()
            if request_line == "":
                break
            requests.append(request_line)

        fullRequest = "\r\n".join(requests)
        request = f"{fullRequest}\r\n\r\n"

        print(f"Sending request:\n{request}")
        clientSocket.sendall(request.encode())

        fullResponse = []
        while True:
            responseSection = clientSocket.recv(1024).decode()
            if not responseSection:
                break
            fullResponse.append(responseSection)

        response = "".join(fullResponse)
        print(response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        clientSocket.close()
