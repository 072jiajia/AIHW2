from Tools import *
import time
from MineSweeper import *


def main():
    while True:
        # get Question
        INPUT = input('Inputs: (board size, #mines, board (-1: variable)):\n')
        try:
            # split it and get the board's parameter
            splitted_input = INPUT.split(' ')
            splitted = []
            for i in splitted_input:
                try:
                    INT = int(i)
                    splitted.append(INT)
                except:
                    continue

            if len(splitted) != 3 + splitted[0] * splitted[1]:
                print('input might be wrong.')
                continue
            BoardSize = (splitted[0], splitted[1])
            num_mines = splitted[2]
            board = [[splitted[3+i*BoardSize[1]+j]
                      for j in range(BoardSize[1])]for i in range(BoardSize[0])]
        except:
            print('input might be wrong.')
            continue

        # make object of Board
        BOARD = Board(BoardSize, num_mines, board)

        # there are 9 ways to solve the problem
        # - using nothing
        # - using forward checking but don't use any heuristic
        # - using MRV / Degreeheuristic / LCV (8 ways)


        print('using no heuristic and forward checking:')
        time0_st = time.time()
        map0, expanded_node0 = BOARD.solve(forward_checking=False, MRV=False,
                                           Degree_heuristic=False, LCV=False)
        time0_ed = time.time()
        print('expanded node =', expanded_node0)
        print('time =', time0_ed - time0_st, 's\n')


if __name__ == "__main__":
    main()
