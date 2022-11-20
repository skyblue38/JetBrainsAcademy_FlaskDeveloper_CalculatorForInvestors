col = int(input())
row = int(input())
moves = 0
if 1 < col < 8:
    if 1 < row < 8:
        moves = 8
    else:
        moves = 5
elif 1 < row < 8:
    moves = 5
else:
    moves = 3
print(moves)
