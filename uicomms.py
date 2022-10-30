from socket import *
import os

class UiComms:
    def __init__(self):
        self.localPort = 55556
        self.BUFF_SIZE = 1024
        self.client_addr = ("127.0.0.1", 55557)
        self.ui_file_name = ""

        self.init_sock()
        # self.open_ui_file()

    def init_sock(self):
        self.sock = socket(family=AF_INET, type=SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.localPort))

    def open_ui_file(self):
        os.startfile(self.ui_file_name)

    def send_msg_to_ui(self, msg):
        self.sock.sendto(msg, self.client_addr)