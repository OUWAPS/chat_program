import threading
from threading import Thread
import socketserver

HOST = ''
PORT = 9009
lock = threading.Lock()  # syncronized 동기화 진행하는 스레드 생성
from socket import *
import time
import os

class main:
    def __init__(self):
        self.menu()

    def menu(self):
        print("----------통신 프로그램입니다.----------")
        print("")
        print("1. 1:1 Server 만들기")
        print("2. 1:1 Client 접속")
        print("3. 다중 Server 만들기")
        print("4. 다중 Client 접속")
        print("5. 종료")
        print()
        print("")
        print("-----------------------------------")
        print("")
        n = input("수행할 번호를 입력해주세요: ")

        if n == "1":
            self.server() # 1:1 Server 만들기
        elif n == "2":
            self.clinet() # 1:1 Client 접속
        elif n == "3":
            runServer() # 다중 Server 만들기
        elif n == "4":
            runChat() # 다중 Client 접속
        elif n == "5":
            print("")
            print("종료")
            exit()
        else:
            print("잘못 입력하셨습니다.")
            print("")
            self.menu()

    def send(self, sock):
        while True:
            sendData = input('>>>')
            sock.send(sendData.encode('utf-8'))


    def receive(self, sock):
        while True:
            recvData = sock.recv(1024)
            print('상대방 :', recvData.decode('utf-8'))

    def server(self):
        ip = input("ip를 입력해주세요: ")
        port = int(input("port를 입력해주세요: "))

        serverSock = socket(AF_INET, SOCK_STREAM) # 소켓 설정
        serverSock.bind((ip, port)) # 컴퓨터에서 소켓 열기
        serverSock.listen(1) # 소켓으로 접속할때까지 기다린다.

        print('ip: {}, port: {}로 접속 대기중...'.format(ip, port))

        connectionSock, addr = serverSock.accept() # 접속한 사람 정보 받아오기.

        os.system('cls')
        print(str(addr), '에서 접속되었습니다.') # 접속한 사람 ip 출력

        sender = threading.Thread(target=self.send, args=(connectionSock,)) # 상대방 아이피를 넘겨주고 메세지 보내는 쓰레드 생성
        receiver = threading.Thread(target=self.receive, args=(connectionSock,)) # 상대방 아이피 넘겨주고 메세지 받는 쓰레드 생성

        sender.start() # 메세지 보내는 쓰레드 시작.
        receiver.start() # 메세지 받는 쓰레드 시작.
        while True:
            time.sleep(1)
            pass

    def clinet(self):
        ip = input("ip를 입력해주세요: ")
        port = int(input("port를 입력해주세요: "))

        clientSock = socket(AF_INET, SOCK_STREAM) # 소켓 설정
        clientSock.connect((ip, port)) # 해당 ip, port로 소켓 접속

        print('접속 완료')

        sender = threading.Thread(target=self.send, args=(clientSock,)) # 상대방 아이피를 넘겨주고 메세지 보내는 쓰레드 생성
        receiver = threading.Thread(target=self.receive, args=(clientSock,)) # 상대방 아이피 넘겨주고 메세지 받는 쓰레드 생성

        sender.start() # 메세지 보내는 쓰레드 시작.
        receiver.start() # 메세지 받는 쓰레드 시작.

        while True:
            time.sleep(1)
            pass

class UserManager:
    def __init__(self):
        self.users = {}  # 사용자의 등록 정보를 담을 사전 {사용자 이름:(소켓,주소),...}

    def addUser(self, username, conn, addr):  # 사용자 ID를 self.users에 추가하는 함수
        if username in self.users:  # 이미 등록된 사용자라면
            conn.send('이미 등록된 사용자입니다.\n'.encode())
            return None

        # 새로운 사용자를 등록함
        lock.acquire()  # 스레드 동기화를 막기위한 락
        self.users[username] = (conn, addr)
        lock.release()  # 업데이트 후 락 해제

        self.sendMessageToAll('[%s]님이 입장했습니다.' % username)
        print('+++ 대화 참여자 수 [%d]' % len(self.users))

        return username

    def removeUser(self, username):  # 사용자를 제거하는 함수
        if username not in self.users:
            return

        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('[%s]님이 퇴장했습니다.' % username)
        print('--- 대화 참여자 수 [%d]' % len(self.users))

    def messageHandler(self, username, msg):  # 전송한 msg를 처리하는 부분
        if msg[0] != '/':  # 보낸 메세지의 첫문자가 '/'가 아니면
            self.sendMessageToAll('[%s] %s' % (username, msg))
            return

        if msg.strip() == '/quit':  # 보낸 메세지가 'quit'이면
            self.removeUser(username)
            return -1

    def sendMessageToAll(self, msg):
        for conn, addr in self.users.values():
            conn.send(msg.encode())

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()

    def handle(self):  # 클라이언트가 접속시 클라이언트 주소 출력
        print('[%s] 연결됨' % self.client_address[0])

        try:
            username = self.registerUsername() # 상대 이름 받아오기
            msg = self.request.recv(1024) # 메세지 받아오기
            while msg:
                print(msg.decode())
                if self.userman.messageHandler(username, msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)

        except Exception as e:
            print(e)

        print('[%s] 접속종료' % self.client_address[0])
        self.userman.removeUser(username)

    def registerUsername(self):
        while True:
            self.request.send('로그인ID:'.encode()) # 로그인 ID 요청
            username = self.request.recv(1024)
            username = username.decode().strip()
            if self.userman.addUser(username, self.request, self.client_address):
                return username

class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
