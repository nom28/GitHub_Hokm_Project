id = 4

lst = [1, 3, 2, 4]

lst = lst[lst.index(id):] + lst[:lst.index(id)]

print(lst)