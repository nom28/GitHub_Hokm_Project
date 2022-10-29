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
    rank_2 = 1
    rank_3 = 2
    rank_4 = 3
    rank_5 = 4
    rank_6 = 5
    rank_7 = 6
    rank_8 = 7
    rank_9 = 8
    rank_10 = 9
    rank_J = 10
    rank_Q = 11
    rank_K = 12
    rank_A = 13

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
