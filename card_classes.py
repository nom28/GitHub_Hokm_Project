from enum import Enum


class Suit(Enum):
    SPADES = 1
    CLUBS = 2
    DIAMONDS = 3
    HEARTS = 4

    def __init__(self, val) -> None:
        super().__init__()
        self.val = val


class Rank(Enum):
    rank_2 = 2
    rank_3 = 3
    rank_4 = 4
    rank_5 = 5
    rank_6 = 6
    rank_7 = 7
    rank_8 = 8
    rank_9 = 9
    rank_10 = 10
    rank_J = 11
    rank_Q = 12
    rank_K = 13
    rank_A = 14

    def __init__(self, val) -> None:
        super().__init__()
        self.val = val


class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.suit.name}*{self.rank.name}"

    def __eq__(self, other):
        if self.rank == other.rank and self.suit == other.suit:
            return True
        return False
