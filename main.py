from card_classes import *

x = "rank_J"
z = "rank_K"
y = "rank_6"
l = [Rank[x], Rank[y], Rank[z]]
print(max(l, key=lambda a: a.value))


print(Rank[x].value)

print(Rank[x].value + Rank[y].value)