from socket import *
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
from threading import *

class FinalClient:
    client_socket = None  # 클라이언트 소켓 변수  

    def __init__(self, ip, port):  # 클라이언트 소켓을 생성하고 GUI를 생성하고 서버에서 보내온 메시지를 받을 thread를 생성(최초실행시 한번만 실행)
        self.initialize_socket(ip, port)
        self.initialize_gui()
        self.listen_thread()

    def initialize_socket(self, ip, port): # 클라이언트 소켓을 생성하는 함수
        self.client_socket = socket(AF_INET, SOCK_STREAM)  # 클라이언트 소켓을 ipv4프로토콜 방식을 사용하고 TCP프로토콜의 전송 방식을 사용
        remote_ip = ip  # 접속할 서버에 ip
        remote_port = port  # 접속할 서버에 port
        self.client_socket.connect((remote_ip, remote_port))  # 서버에 접속

    def send_chat(self):  # 메시지 보내는 함수
        senders_name = self.name_widget.get().strip() + ":"  # 작성자를 담을 변수
        data = self.enter_text_widget.get(1.0, 'end').strip()  # 보낼 내용을 담을 변수
        message = (senders_name + data).encode('utf-8')  # 작성자 + 내용을 담을 변수 
        self.chat_transcript_area.insert('end',message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)  # 서버에 message 전송
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def start_signal(self):  # 가위바위보 게임을 시작할 함수
        game_value = self.select_entry.get().strip()  # 가위바위보 게임에서 선택한 값을 담을 변수
        value_check = ['rock','scissors','paper']  # 제대로된 값이 들어왔는지 체크할 리스트
        if game_value in value_check: # 제대로된 값이 들어왔다면
            self.display_label.configure(text='상대방을 기다리고있습니다.')
            send_message = ('GAME START!!!' + game_value).encode('utf-8')
            self.client_socket.send(send_message)  # 서버에 가위바위보 게임에서 선택한 값 전달
            self.input_button['state'] = DISABLED
        else:  # 제대로된 값이 들어오지않았다면
            self.display_label.configure(text='제대로된값을 입력해주세요.(rock,scissors,paper)')

    def chat_event(self,e):  # 채팅 이벤트(ENTER 키 로 작동) 함수
        self.send_chat()

    def initialize_gui(self):  # GUI 설정 함수
        self.root = Tk()
        fr = []
        for i in range(0,8):
            fr.append(Frame(self.root))
            fr[i].pack(fill=BOTH)

        self.root.bind('<Return>', self.chat_event)  # 채팅을 ENTER 키로  이벤트 처리

        self.name_label = Label(fr[3], text='사용자 이름')
        self.recv_label = Label(fr[4], text='수신 메시지:')
        self.send_label = Label(fr[6], text='송신 메시지:')
        self.send_btn = Button(fr[6], text='전송', command=self.send_chat)
        self.chat_transcript_area = ScrolledText(fr[5], height=10, width=60)
        self.enter_text_widget = ScrolledText(fr[7], height=2, width=60)
        self.name_widget = Entry(fr[3], width=15)
        self.title_label = Label(fr[0], text='가위바위보게임', font=20)
        self.input_button = Button(fr[2], text='입력', command=self.start_signal)
        self.select_entry = Entry(fr[2])
        self.display_label = Label(fr[1], text='rock,scissors,paper중에 하나를 입력해주세요', font=12)
        self.label1 = Label(fr[2], text='값 입력')

        self.name_label.pack(side=LEFT)
        self.name_widget.pack(side=LEFT)
        self.recv_label.pack(side=LEFT)
        self.send_btn.pack(side=RIGHT, padx=20)
        self.chat_transcript_area.pack(side=LEFT, padx=2, pady=2)
        self.send_label.pack(side=LEFT)
        self.enter_text_widget.pack(side=LEFT, padx=2, pady=2)
        self.title_label.pack(padx=2)
        self.input_button.pack(side=RIGHT, padx=20,pady=5)
        self.label1.pack(side=LEFT)
        self.select_entry.pack(side=LEFT,padx=20)
        self.display_label.pack(side=LEFT)

    def listen_thread(self):  # 서버로 부터 메시지를 받을 thread 생성 함수
        t = Thread(target=self.receive_message, args=(self.client_socket,))  # 서버로 부터 메시지를 받을 thread
        t.start()

    def receive_message(self, so):  # 서버로부터 메시지를 받는 함수
        while True:
            buf = so.recv(256)  # 서버에서 보내온 메시지를 담을 변수
            if not buf:
                break
            message = buf.decode('utf-8')
            if message == 'Win':  # 가위바위보 게임에서 이겼다면
                messagebox.showinfo("게임결과", "승리!!")
                self.end_game()
            elif message == 'Draw':  # 가위바위보 게임에서 비겼다면
                messagebox.showinfo("게임결과", "무승부")
                self.end_game()
            elif message == 'Lose':  # 가위바위보 게임에서 졌다면
                messagebox.showinfo("게임결과", "패배..")
                self.end_game()
            else:   # 가위바위보 게임이아니라 채팅 기능을 이용했다면
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
        so.close()  # 클라이언트 소켓 종료

    def end_game(self):  # 가위바위보 게임이 종료되었을때 설정 함수
        self.input_button['state'] = NORMAL
        self.display_label.configure(text='rock,scissors,paper중에 하나를 선택해주세요.')

if __name__ == "__main__":
    ip = input("server IP addr: ")
    if ip == '':  # ip값을 입력하지 않으면 기본값 사용
        ip = '127.0.0.1'
    port = 2500
    FinalClient(ip,port)
    mainloop()
