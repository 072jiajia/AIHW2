

def print_2dboard(BoardSize, MAP):
    '''
    Print a 2D Map out in grid form.
    '''
    for i in range(BoardSize[0]):

        print(end=' ')
        for j in range(BoardSize[1]):
            print('---', end=' ')
        print()

        print(end='| ')
        for j in range(BoardSize[1]):
            print(MAP[i][j], end=' | ')
        print()

    print(end=' ')
    for j in range(BoardSize[1]):
        print('---', end=' ')
    print()


def get_answer_map(BoardSize, board, Assigned):
    '''
    get the map of answer
    - X -> mine
    - space -> not mine
    - . -> have not assigned
    - else -> Hint
    '''
    MAP = [[None for j in range(BoardSize[1])]
           for i in range(BoardSize[0])]

    for i in range(BoardSize[0]):
        for j in range(BoardSize[1]):
            if board[i][j] < 0:
                if (i, j) not in Assigned:
                    MAP[i][j] = '.'
                else:
                    block = Assigned[(i, j)]
                    if block == 0:
                        MAP[i][j] = ' '
                    elif block == 1:
                        MAP[i][j] = 'X'
            else:
                MAP[i][j] = board[i][j]
    return MAP
