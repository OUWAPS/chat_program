from socket import *

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
