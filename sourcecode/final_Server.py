from socket import *
from threading import *

class FinalServer:
    clients = []   # 접속한 클라이언트를 담을 리스트
    gamers = []   # 가위바위보 게임을 플레이할 클라이언트를 담을 리스트
    gameValue = []   # 클라리언트가 가위바위보 게임에서 선택한 값(가위,바위,보)을 담을 리스트
    final_received_message = ""   # 서버에서 클라리언트로 메시지를 전송할 때 사용할 변수

    def __init__(self):   # 서버 소켓을 생성하고 주소를 할당하는 함수(최초실행시 한번만 진행)
        self.s_sock = socket(AF_INET, SOCK_STREAM)  # 서버 소켓을 ipv4프로토콜 방식을 사용하고 TCP 프로토콜의 전송 방식을 사용
        self.ip = ''  # 서버의 ip를 담을 변수
        self.port = 2500  # 서버의 port를 담을 변수
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)   # 이미 사용중인 포트에 대해서 바인드 허용 
        self.s_sock.bind((self.ip, self.port)) # 서버 소켓의 주소 할당
        print("Waiting for clients...")
        self.s_sock.listen(100)
        self.accept_client()

    def accept_client(self):  # 클라이언트의 접속을 수락하는 함수
        while True:
            client = c_socket, (ip, port) = self.s_sock.accept() # client에 클라이언트의 소켓, ip와 port에 클라리언트 소켓의 주소
            if client not in self.clients:  # clients 리스트에 client가 없으면 
                self.clients.append(client)  # clients 리스트에 client 추가
            print(ip, ':', str(port), ' 가 연결되었습니다')
            t = Thread(target=self.receive_messages, args=(c_socket,))  # 클라이언트의 메시지를 받을 thread 생성
            t.start()

    def receive_messages(self, c_socket):   # 클라이언트의 메시지를 받을 함수
        while True:
            try:
                incoming_message = c_socket.recv(1024)   # incoming_message에 클라이언트의 메시지
                if not incoming_message:
                    break
            except:
                continue
            else:
                self.final_received_message = incoming_message.decode('utf-8')  # final_receive_message에 클라이언트가 보내온 메시지
                contain_check = 'GAME START!!!' in self.final_received_message  # 클라이언트가 가위바위보 게임을 했는지 메시지를 보냈는지 확인
                if contain_check: # 가위바위보 게임을 했다면
                    self.gamers.append(c_socket)  # gamers 리스트에 클라이언트 소켓 추가
                    self.gameValue.append(self.final_received_message[13:])  # gameValue 리스트에 가위바위보 게임에서 선택한 값 추가
                    gThread = Thread(target=self.game_start, args=(c_socket,))  # 가위바위보 게임을 시작할 준비를 할 thread 생성
                    gThread.start()
                else:  # 메시지를 보냈다면
                    print(self.final_received_message)
                    self.send_all_clients(c_socket)
        c_socket.close()  # 클라이언트 소켓 종료

    def game_start(self, c_socket):  # 가위바위보 게임을 시작할 준비를 할 함수
        if len(self.gamers) == 2:  # gamer가 2명이 됐다면
            self.play_game(c_socket)  # 가위바위보 게임 시작

    def play_game(self,c_socket):  # 가위바위보 게임을 하고 결과를 보내줄 함수
        # 가위바위보 게임 진행
        if self.gameValue[0] == 'rock': 
            if self.gameValue[1] == 'rock':
                self.gamers[0].send('Draw'.encode('utf-8'))
                self.gamers[1].send('Draw'.encode('utf-8'))
            if self.gameValue[1] == 'scissors':
                self.gamers[0].send('Win'.encode('utf-8'))
                self.gamers[1].send('Lose'.encode('utf-8'))
            if self.gameValue[1] == 'paper':
                self.gamers[0].send('Lose'.encode('utf-8'))
                self.gamers[1].send('Win'.encode('utf-8'))
        if self.gameValue[0] == 'scissors':
            if self.gameValue[1] == 'rock':
                self.gamers[0].send('Lose'.encode('utf-8'))
                self.gamers[1].send('Win'.encode('utf-8'))
            if self.gameValue[1] == 'scissors':
                self.gamers[0].send('Draw'.encode('utf-8'))
                self.gamers[1].send('Draw'.encode('utf-8'))
            if self.gameValue[1] == 'paper':
                self.gamers[0].send('Win'.encode('utf-8'))
                self.gamers[1].send('Lose'.encode('utf-8'))
        if self.gameValue[0] == 'paper':
            if self.gameValue[1] == 'rock':
                self.gamers[0].send('Win'.encode('utf-8'))
                self.gamers[1].send('Lose'.encode('utf-8'))
            if self.gameValue[1] == 'scissors':
                self.gamers[0].send('Lose'.encode('utf-8'))
                self.gamers[1].send('Win'.encode('utf-8'))
            if self.gameValue[1] == 'paper':
                self.gamers[0].send('Draw'.encode('utf-8'))
                self.gamers[1].send('Draw'.encode('utf-8'))
        
        self.gamers.clear()  # 가위바위보 게임이 끝났으니 gamers 리스트 비우기
        self.gameValue.clear()  # 가위바위보 게임이 끝났으니 gameValue 리스트 비우기

    def send_all_clients(self, senders_socket):  # 클라이언트에 메시지를 전송할 함수
        # clients 리스트에 있는 클라이언트 소켓을 하나씩 꺼내서 클라이언트에서 보내온 메시지를
        # 다른 클라이언트에게 전송하는 과정을 진행함
        for client in self.clients:
            socket, (ip, port) = client
            if socket is not senders_socket:
                try:
                    socket.sendall(self.final_received_message.encode('utf-8'))
                except:
                    self.clients.remove(client)
                    print("{}, {} 연결이 종료되었습니다".format(ip, port))

if __name__ == "__main__":
    FinalServer()
