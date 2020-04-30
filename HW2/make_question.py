import random
import time
from main import *


def make_question(BoardSize, num_mines, num_Hint):
    '''
    make a random Question board
    '''
    ans = [[None for j in range(BoardSize[1])]for i in range(BoardSize[0])]

    # randomly generate mines and make sure every mines have at least
    # one constraint
    for _ in range(num_mines):
        i = random.randint(0, BoardSize[0]-1)
        j = random.randint(0, BoardSize[1]-1)
        while ans[i][j] is not None:
            i = random.randint(0, BoardSize[0]-1)
            j = random.randint(0, BoardSize[1]-1)
        ans[i][j] = 'X'
        N = Neighbor(BoardSize, i, j)
        random.shuffle(N)
        for (Nx, Ny) in N:
            if ans[Nx][Ny] is None:
                ans[Nx][Ny] = 'Hint'
                num_Hint -= 1
                break
            if ans[Nx][Ny] == 'Hint':
                break

    # make sure every variable have at least one constraint
    for i in range(BoardSize[0]):
        for j in range(BoardSize[1]):
            if ans[i][j] is None:
                BREAK = False
                for (Nx, Ny) in Neighbor(BoardSize, i, j):
                    if ans[Nx][Ny] is not None:
                        BREAK = True
                        break
                if BREAK:
                    continue
                ans[i][j] = 'Hint'
                num_Hint -= 1

    # generate other constraints
    for _ in range(num_Hint):
        i = random.randint(0, BoardSize[0]-1)
        j = random.randint(0, BoardSize[1]-1)
        while ans[i][j] is not None:
            i = random.randint(0, BoardSize[0]-1)
            j = random.randint(0, BoardSize[1]-1)
        ans[i][j] = 'Hint'

    # generate the constraint's real value
    for i in range(BoardSize[0]):
        for j in range(BoardSize[1]):
            if ans[i][j] == 'Hint':
                ans[i][j] = 0
                for (Nx, Ny) in Neighbor(BoardSize, i, j):
                    if ans[Nx][Ny] == 'X':
                        ans[i][j] += 1

    # generate the Question board
    Q = [[None for j in range(BoardSize[1])]for i in range(BoardSize[0])]
    for i in range(BoardSize[0]):
        for j in range(BoardSize[1]):
            if type(ans[i][j]) == int:
                Q[i][j] = ans[i][j]
            else:
                Q[i][j] = -1

    return Q, ans


def check(BoardSize, num_mines, MAP):
    '''
    check all constraint's if the MAP is an answer.
    '''
    CountTotal = 0
    for i in range(BoardSize[0]):
        for j in range(BoardSize[1]):
            if MAP[i][j] == 'X':
                CountTotal += 1
            if type(MAP[i][j]) == int:
                Count = 0
                for (Nx, Ny) in Neighbor(BoardSize, i, j):
                    if MAP[Nx][Ny] == 'X':
                        Count += 1
                if Count != MAP[i][j]:
                    return False
    if CountTotal == num_mines:
        return True
    else:
        return False
