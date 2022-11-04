from socket import *
from card_classes import *
from uicomms import UiComms
import sys

# import re
# import random

# change to username string on tournament day
USERNAME = None


class Client:
    def __init__(self, server_ip="localhost", server_port=55555):
        self.server_addr = server_ip, server_port

        self.cards = []
        self.cards_left = [(Card(Suit(suit + 1), Rank(rank + 2))) for rank in range(13) for suit in range(4)]
        self.id = -1
        self.teammate = -1
        self.strong = ""
        self.played_suit = ""
        self.score_us = 0
        self.score_opp = 0
        self.ui = UiComms()
        self.turn_order = [1, 3, 2, 4]
        self.have_played = []

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

        id_index = self.turn_order.index(int(self.id))
        self.turn_order = self.turn_order[id_index:] + self.turn_order[:id_index]

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
        self.ui.send_msg_to_ui(1, str(strong.split(":")[1]).lower())

        self.cards = [Card(Suit[c.split("*")[0]], Rank[c.split("*")[1]]) for c in cards.split("|")]
        self.ui.send_msg_to_ui(2, self.cards)
        print(*self.cards)
        print(teams)
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
        print("Game has started")
        while True:
            status, work = self.recv()
            if not work:
                print(f"error when recv status {status}")
                exit()

            if status == "GAME_OVER":
                print("\ngame over!")
                # print(*self.cards_left, sep=", ")
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

            for i, card in enumerate(played_cards):
                if card.suit.value != 0:
                    self.ui.send_msg_to_ui(3, (self.turn_order.index(i+1), card))
                    self.have_played.append(self.turn_order.index(i+1))

            card = self.choose_card(played_cards)
            print("chosen card:", card)
            self.ui.send_msg_to_ui(3, (self.turn_order.index(int(self.id)), card))
            self.have_played.append(self.turn_order.index(int(self.id)))

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

            round_cards = [Card(Suit[str_card.split("*")[0]], Rank[str_card.split("*")[1]])
                           for str_card in game_status.split(",")[2].split(":")[1].split("|")]

            for i, card in enumerate(round_cards):
                if self.turn_order.index(i + 1) not in self.have_played:
                    if card.suit.value != 0:
                        self.ui.send_msg_to_ui(3, (self.turn_order.index(i + 1), card))

            self.have_played = []

            print(game_status.split(",")[0])

            try:
                scores = game_status.split(",")[1].split("|")
                if str(self.id) in scores[0].split("*")[0]:
                    us_current_score = scores[0].split('*')[1]
                    opp_current_score = scores[1].split('*')[1]
                else:
                    us_current_score = scores[1].split('*')[1]
                    opp_current_score = scores[0].split('*')[1]

                print(f"Us - {us_current_score}| Opp - {opp_current_score}")

                if self.score_us < int(us_current_score):
                    self.score_us += 1
                    self.ui.send_msg_to_ui(4, 0)
                else:
                    self.score_opp += 1
                    self.ui.send_msg_to_ui(4, 1)

            except IndexError:
                print(game_status.split(",")[1])
                raise

            print(game_status.split(",")[2])  # round cards

            for round_card in round_cards:
                self.cards_left.remove(round_card)

    def handle_server_crash(self):
        self.client.close()

        input("**server crashed**\npress enter when server has been reloaded")

        self.init_sock()
        self.get_id_and_identify_to_server()

    def choose_card(self, played_cards):  # v add the whole logic in here

        only_strong_cards = list(filter(lambda x: x.suit == self.strong, self.cards.copy()))
        no_strong_cards = list(filter(lambda x: x.suit != self.strong, self.cards.copy()))

        if self.played_suit == "":
            return self.__get_strongest_first_turn(no_strong_cards, only_strong_cards)

        self.played_suit = Suit[self.played_suit]

        only_played_suit_cards = list(filter(lambda x: x.suit == self.played_suit, self.cards.copy()))

        turn = self.__get_turn_in_round(played_cards)
        strongest_on_board_id, strongest_on_board = self.__get_strongest_card_on_board(played_cards)

        if turn == 2 or turn == 3:
            if strongest_on_board_id == self.teammate:
                return self.__get_weakest(only_played_suit_cards, no_strong_cards)
            self.__get_optimized(only_played_suit_cards, only_strong_cards, 6, strongest_on_board, no_strong_cards)  # 6 gave me the best result but difference was small
        elif turn == 4:
            if strongest_on_board_id == self.teammate:
                return self.__get_weakest(only_played_suit_cards, no_strong_cards)
            return self.__get_lowest_winning(strongest_on_board, only_played_suit_cards, only_strong_cards,
                                             no_strong_cards)

        for card in self.cards:
            if card.suit == self.played_suit:
                return card

        for card in self.cards:
            if card.suit == self.strong:
                return card

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
            suit_cards = list(filter(lambda x: x.suit == self.played_suit, played_cards.copy()))
            strongest_card = max(suit_cards, key=lambda x: x.rank.value)

        return played_cards.index(strongest_card) + 1, strongest_card

    def __get_weakest(self, only_played_suit_cards, no_strong_cards):
        if len(only_played_suit_cards) > 0:
            weakest_card = min(only_played_suit_cards, key=lambda x: x.rank.value)
        else:
            if len(no_strong_cards) > 0:
                weakest_card = min(no_strong_cards, key=lambda x: x.rank.value)
            else:
                weakest_card = min(self.cards, key=lambda x: x.rank.value)
        return weakest_card

    def __get_strongest(self, only_played_suit_cards, only_strong_cards):
        if len(only_played_suit_cards) > 0:
            strongest_card = max(only_played_suit_cards, key=lambda x: x.rank.value)
        else:
            if len(only_strong_cards) > 0:
                strongest_card = max(only_strong_cards, key=lambda x: x.rank.value)
            else:
                strongest_card = min(self.cards, key=lambda x: x.rank.value)
        return strongest_card

    def __get_strongest_first_turn(self, no_strong_cards, only_strong_cards):
        if len(no_strong_cards) > 0:
            strongest_card = max(no_strong_cards, key=lambda x: x.rank.value)
        else:
            if len(only_strong_cards) > 0:
                strongest_card = max(only_strong_cards, key=lambda x: x.rank.value)
            else:
                strongest_card = max(self.cards, key=lambda x: x.rank.value)
        return strongest_card

    def __get_optimized(self, only_played_suit_cards, only_strong_cards, increased_index, strongest_on_board, no_strong_cards):
        if len(only_played_suit_cards) > 0:
            if strongest_on_board.suit == self.played_suit:
                optimized_cards = [x for x in only_played_suit_cards if x.rank.value > strongest_on_board.rank.value]
                optimized_cards = list(sorted(optimized_cards, key=lambda x: x.rank.value, reverse=True))
                if len(optimized_cards) > 0:
                    if len(optimized_cards) == 1:
                        return optimized_cards[0]
                    for changed_index in range(increased_index, 14):
                        for card in optimized_cards:
                            if card.rank.value - changed_index < strongest_on_board.rank.value:
                                return card
                else:
                    return self.__get_weakest(only_played_suit_cards, no_strong_cards)
            else:
                return self.__get_weakest(only_played_suit_cards, no_strong_cards)
        else:
            if len(only_strong_cards) > 0:
                return min(only_strong_cards, key=lambda x: x.rank.value)
            else:
                 return min(self.cards, key=lambda x: x.rank.value)

    def __get_lowest_winning(self, strongest_on_board, only_played_suit_cards, only_strong_cards, no_strong_cards):
        if strongest_on_board.suit == self.played_suit:
            only_played_suit_cards.sort(reverse=False, key=lambda x: x.rank.value)
            if len(only_played_suit_cards) > 0:
                for card in only_played_suit_cards:
                    if card.rank.value > strongest_on_board.rank.value:
                        return card
                return self.__get_weakest(only_played_suit_cards, no_strong_cards)
            elif len(only_strong_cards) > 0:
                return min(only_strong_cards, key=lambda x: x.rank.value)
            else:
                return self.__get_weakest(only_played_suit_cards, no_strong_cards)
        else:
            '''
            only_strong_cards.sort(reverse=False, key=lambda x: x.rank.value)
            for card in only_strong_cards:
                if card.rank.value > strongest_on_board.rank.value:
                    return card
            return self.__get_weakest(only_played_suit_cards, no_strong_cards)
            '''
            return self.__get_weakest(only_played_suit_cards, no_strong_cards)


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


if __name__ == '__main__':
    p = 55555 if len(sys.argv) == 1 else int(sys.argv[1])
    client = Client(server_port=p)
    client.start_game()

