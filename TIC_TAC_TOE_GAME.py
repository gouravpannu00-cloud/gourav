board = ["1","2","3","4","5","6","7","8","9"]

def show():
    print(board[0] + " | " + board[1] + " | " + board[2])
    print("---------")
    print(board[3] + " | " + board[4] + " | " + board[5])
    print("---------")
    print(board[6] + " | " + board[7] + " | " + board[8])

def check_winner():
    winner = [
        (0,1,2), (3,4,5), (6,7,8),
        (0,3,6), (1,4,7), (2,5,8),
        (0,4,8), (2,4,6)
    ]

    for combo in winner:
        if board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]

    return None

player = "X"

for i in range(9):
    show()
    print("Player", player, "'s turn.")
    p = int(input("Enter a number (1-9): "))

    if board[p-1] not in ["X", "O"]:
        board[p-1] = player
        if player == "X":
            player = "O"
        else:
            player = "X"
    else:
        print("Invalid move. Try again.")
        i -= 1

winner = check_winner()
show()
if winner:
    print(f"Player {winner} wins!")
else:
    print("It's a tie!")

    print("Game over !")