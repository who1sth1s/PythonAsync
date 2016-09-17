import asyncio
import traceback
import socket
import select

class ChatServer():
    def __init__(self):
        self.HOST = ''
        self.SOCKET_LIST = []
        self.RECV_BUFFER = 4096
        self.PORT = 33137
        pass

    @asyncio.coroutine
    def chatServerMain(self):
        try:
            serverSocket = yield from self.chatServerSetting()
            self.SOCKET_LIST.append(serverSocket)
            print('Chat server started on port ' + str(self.PORT))
            while 1:
                ready_to_read, \
                ready_to_write, \
                in_error = select.select(self.SOCKET_LIST, [], [], 0)

                for sock in ready_to_read:
                    if sock == serverSocket:
                        sockfd, addr = serverSocket.accept()
                        self.SOCKET_LIST.append(sockfd)
                        print('Client ({addr}, {addr})').format(addr=addr)
                        yield from self.broadcast(serverSocket, sockfd,
                                                  '[{addr}:{addr}] entered our chatting room\n'.format(addr=addr))

        except:
            print(traceback.format_exc().strip().split('\n'))

    @asyncio.coroutine
    def chatServerSetting(self):
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((self.HOST, self.PORT))
        serverSocket.listen(10)
        return serverSocket

    @asyncio.coroutine
    def broadcast(self, serverSocket, sock, message):
        for socket in self.SOCKET_LIST:
            if socket != serverSocket and socket != sock:
                try:
                    socket.send(message)
                except:
                    socket.close()
                    if socket in self.SOCKET_LIST:
                        self.SOCKET_LIST.remove(socket)