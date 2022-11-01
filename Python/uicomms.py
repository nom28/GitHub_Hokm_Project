from socket import *
import os
from card_classes import *

class UiComms:
    def __init__(self):
        self.localPort = 55557
        self.BUFF_SIZE = 1024
        self.client_addr = ("127.0.0.1", 55557)

        self.ui_file_name = os.getcwd() + "\\HokmAI\\HokmAI\\bin\\Debug\\HokmAI.exe"

        self.init_sock()
        #self.open_ui_file()

    def init_sock(self):
        self.sock = socket(family=AF_INET, type=SOCK_STREAM)
        self.sock.bind(("127.0.0.1", self.localPort))

        self.sock.listen(3)
        self.conn, addr = self.sock.accept()
        print(f"Connected to ui at {addr}")

    def open_ui_file(self):
        os.startfile(self.ui_file_name)

    def send_msg_to_ui(self, code, data):
        num_to_letter = {
            1: "S",
            2: "C",
            3: "D",
            4: "H"
        }

        if code == 1:
            message = "01-" + data + "!"
        elif code == 2:
            message = "02"
            for card in data:
                message += "-" + num_to_letter[card.suit.value] + card.rank.value
            message += "!"
        elif code == 3:
            card = num_to_letter[data[1].suit.value] + str(data[1].rank.value)
            message = "03-" + str(data[0]) + "-" + card + "!"
        elif code == 4:
            message = "04-" + str(data) + "!"
        else:
            return
        self.conn.send(message.encode("utf-8"))


if __name__ == '__main__':
    ui = UiComms()
    c = Card(Suit["DIAMONDS"], Rank["rank_J"])
    ui.send_msg_to_ui(3, (2, c))