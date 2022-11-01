from socket import *
from card_classes import *

# import re
# import random

# change to username string on tournament day
USERNAME = None


class Client:
    def __init__(self, server_ip="localhost", server_port=55555):
        self.server_addr = server_ip, server_port

        self.cards = []
        self.cards_left = [(Card(Suit(suit + 1), Rank(rank + 2))) for rank in range(13) for suit in range(4)]
        print(*self.cards_left, sep=", ")
        self.id = -1
        self.teammate = -1
        self.strong = ""
        self.played_suit = ""

        self.init_sock()

    def init_sock(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(self.server_addr)

    def get_id_and_identify_to_server(self):
        my_id, work = self.recv()
        if not work:
            print(f"error when recv id: {my_id}")
            exit()
        self.id = my_id.split(":")[1]
        print("my id:", self.id)

        if USERNAME:
            self.send(f"username:{USERNAME}")

    def start_game(self):
        self.get_id_and_identify_to_server()

        self.ruler_and_strong_card()

        cards_teams_strong, work = self.recv()
        if not work:
            print(f"error when recv cards_teams_strong {cards_teams_strong}")
            exit()
        # print("raw data of cards, teams and strong suite:", cards_teams_strong)

        # if the data in corrupted then request new turn and data
        if len(cards_teams_strong.split(",")) != 3:
            cards_teams_strong = self.handle_value_error()

        cards, teams, strong = cards_teams_strong.split(",")

        self.cards = [Card(Suit[c.split("*")[0]], Rank[c.split("*")[1]]) for c in cards.split("|")]
        print(*self.cards)
        print("teams:", teams)
        teams = teams.split(":")[1].split("|")
        my_team = teams[0].split("+") if self.id in teams[0] else teams[1].split("+")
        self.teammate = int(my_team[0]) if my_team[1] == self.id else int(my_team[1])

        print("strong suit:", strong.split(":")[1], "\n")

        self.strong = Suit[strong.split(":")[1]]

        self.game_loop()

    def handle_value_error(self):
        print("**value error**")
        # recv to clear the buffer
        _, work = self.recv()

        # request new cards,teams and strong info
        self.send(f"request_start_info")

        cards_teams_strong, work = self.recv()
        if not work:
            print(f"error when recv cards_teams_strong number 2 {cards_teams_strong}")
            exit()

        # request new turn
        self.send(f"request_turn")
        print("requested new turn")

        return cards_teams_strong

    def ruler_and_strong_card(self):
        ruler, work = self.recv()
        if not work:
            print(f"error when recv ruler {ruler}")
            exit()

        # print("ruler id:", ruler.split(":")[1])
        # ^ It is only relevent if we are the ruler, so print only if we are the ruler
        ruler = ruler.split(":")[1]

        first_5_cards, work = self.recv()

        if not work:
            print(f"error when recv 5 cards {first_5_cards}")
            exit()
        first_5_cards = first_5_cards.split("|")

        if ruler == self.id:  # v need to change this to pick best card
            print("we are the ruler")

            sum_of_suits = {
                "DIAMONDS": 0,
                "HEARTS": 0,
                "SPADES": 0,
                "CLUBS": 0
            }
            for card in first_5_cards:
                suit = card.split("*")[0]
                sum_of_suits[suit] += Rank[card.split("*")[1]].value

            strong_suit = max(sum_of_suits, key=lambda x: sum_of_suits[x])

            print("chosen strong suit:", strong_suit)
            self.send(f"set_strong:{strong_suit}")

            response, work = self.recv()

            if not work:
                print(f"error when recv response strong {response}")
                exit()
            print("response on strong card proposal:", response)

    def game_loop(self):
        print("Game has started \n")
        while True:
            status, work = self.recv()
            if not work:
                print(f"error when recv status {status}")
                exit()

            if status == "GAME_OVER":
                print("\ngame over!")
                print(*self.cards_left, sep=", ")
                exit()
            elif status.startswith("PLAYER_DISCONNECTED"):
                print("\nplayer disconnected\nexiting game")
                exit()
            elif status == "SERVER_DISCONNECTED":
                self.handle_server_crash()
                continue  # using that to do a new turn

            print("\nstart of round:")
            print(status.split(",")[0])
            print(status.split(",")[1])  # v could optimize the way this looks

            self.played_suit = status.split(",")[0].split(":")[1]
            # played_cards = status.split(",")[1].split(":")[1].split("|")
            played_cards = [Card(Suit[c.split("*")[0]], Rank[c.split("*")[1]]) if c != "" else
                            Card(Suit["NONE"], Rank["NONE"])
                            for c in status.split(",")[1].split(":")[1].split("|")]

            card = self.choose_card(played_cards)
            print("chosen card:", card)

            self.send(f"play_card:{card}")

            response, work = self.recv()

            if not work:
                print(f"error when recv response play {response}")
                exit()
            print("response data:", response)

            if response == "SERVER_DISCONNECTED":
                self.handle_server_crash()
                continue  # using that to do a new turn
            elif response.startswith("PLAYER_DISCONNECTED"):
                print("player disconnected")
                exit()
            elif response == "ok":
                self.cards.remove(card)
            else:
                print("unexepted error has occurred\nexiting")

            game_status, work = self.recv()
            if not work:
                print(f"error when recv game status {game_status}")
                exit()

            if game_status.startswith("PLAYER_DISCONNECTED"):
                print("player disconnected")
                exit()
            elif game_status == "SERVER_DISCONNECTED":
                self.handle_server_crash()

                # get new game status
                game_status, work = self.recv()
                if not work:
                    print(f"error when recv game status 2 {game_status}")
                    exit()

            print("round over")
            print(game_status.split(",")[0])

            try:
                scores = game_status.split(",")[1].split("|")
                if str(self.id) in scores[0].split("*")[0]:
                    print(f"Us - {scores[0].split('*')[1]}| Opp - {scores[1].split('*')[1]}")
                else:
                    print(f"Us - {scores[1].split('*')[1]}| Opp - {scores[0].split('*')[1]}")
            except IndexError:
                print(game_status.split(",")[1])
                raise

            print(game_status.split(",")[2])  # round cards

            round_cards = [Card(Suit[str_card.split("*")[0]], Rank[str_card.split("*")[1]])
                           for str_card in game_status.split(",")[2].split(":")[1].split("|")]

            for round_card in round_cards:
                self.cards_left.remove(round_card)

    def handle_server_crash(self):
        self.client.close()

        input("**server crashed**\npress enter when server has been reloaded")

        self.init_sock()
        self.get_id_and_identify_to_server()

    def choose_card(self, played_cards):  # v add the whole logic in here
        if self.played_suit == "":
            return self.__get_strongest()

        self.played_suit = Suit[self.played_suit]

        turn = self.__get_turn_in_round(played_cards)
        strongest_on_board_id, strongest_on_board = self.__get_strongest_card_on_board(played_cards)

        if turn == 2:
            pass
        elif turn == 3:
            pass
        elif turn == 4:
            if strongest_on_board_id == self.teammate:
                card = self.__get_weakest()

        # for card in self.cards:
        #     if card.suit == played_suit:
        #         return card
        #
        # for card in self.cards:
        #     if card.suit == self.strong:
        #         return card

        return self.cards[0]

    def __get_turn_in_round(self, played_cards):
        turns = 1
        for card in played_cards:
            if card.suit is not Suit.NONE:
                turns = turns + 1

        return turns

    def __get_strongest_card_on_board(self, played_cards):
        strong_cards = list(filter(lambda x: x.suit == self.strong, played_cards.copy()))
        if len(strong_cards) > 0:
            strongest_card = max(strong_cards, key=lambda x: x.rank.value)
        else:
            strong_cards = list(filter(lambda x: x.suit == self.played_suit, played_cards.copy()))
            strongest_card = max(strong_cards, key=lambda x: x.rank.value)

        return played_cards.index(strongest_card) + 1, strongest_card

    def __get_weakest(self):
        weakest_cards = list(filter(lambda x: x.suit == self.played_suit, self.cards.copy()))
        if len(weakest_cards) > 0:
            weakest_card = min(weakest_cards, key=lambda x: x.rank.value)
        else:
            weakest_cards = list(filter(lambda x: x.suit != self.strong, self.cards.copy()))
            if len(weakest_cards) > 0:
                weakest_card = min(weakest_cards, key=lambda x: x.rank.value)
            else:
                weakest_card = min(self.cards, key=lambda x: x.rank.value)
        return weakest_card

    def __get_strongest(self):
        suit_cards = list(filter(lambda x: x.suit == self.played_suit, self.cards.copy()))
        if len(suit_cards) > 0:
            strongest_card = max(suit_cards, key=lambda x: x.rank.value)
        else:
            strong_cards = list(filter(lambda x: x.suit == self.strong, self.cards.copy()))
            if len(strong_cards) > 0:
                strongest_card = max(strong_cards, key=lambda x: x.rank.value)
            else:
                strongest_card = max(self.cards, key=lambda x: x.rank.value)
        return strongest_card

        # strong_cards = list(filter(lambda x: x.suit != self.strong, self.cards.copy()))
        # if len(strong_cards) > 0:
        #     return max(strong_cards, key=lambda x: x.rank.value)
        # else:
        #     return max(self.cards.copy(), key=lambda x: x.rank.value)

    def recv(self):
        try:
            msg_size = self.client.recv(8)
        except:
            return "recv error", False

        if not msg_size:
            return "msg length error", False

        try:
            msg_size = int(msg_size)
        except:  # not an integer
            return "msg length error", False

        msg = b''
        while len(msg) < msg_size:  # this is a fail - safe -> if the recv not giving the msg in one time
            try:
                msg_fragment = self.client.recv(msg_size - len(msg))
            except:
                return "recv error", False
            if not msg_fragment:
                return "msg data is none", False
            msg = msg + msg_fragment

        msg = msg.decode(errors="ignore")

        return msg, True

    def send(self, data):
        self.client.send(str(len(data.encode())).zfill(8).encode() + data.encode())


client = Client()
client.start_game()
