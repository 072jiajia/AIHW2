from .NODE import *
from .UnassignedBlock import *
from Tools import *


class Board:
    '''
    It is a Board about the Minesweeper game.
    '''

    def __init__(self, BoardSize, num_mines, board):
        '''
        Storing the data about the game.
        '''
        self.BoardSize = BoardSize
        self.num_mines = num_mines
        self.board = board
        self.num_variable = 0
        for i in range(BoardSize[0]):
            for j in range(BoardSize[1]):
                if board[i][j] < 0:
                    self.num_variable += 1

    def check_constraint(self, x, y, Assigned):
        '''
        Check the constraint at board[x][y]
        First, I count the num of assigned mine and
        the block I have not assigned anything
        then I check whether the Assignment is allowed
        '''

        # count the number of mine and the number of unassigned variables
        Count_mine = 0
        Count_unassigned_neigbor = 0
        for (Nx, Ny) in Neighbor(self.BoardSize, x, y):
            if self.board[Nx][Ny] >= 0:
                continue
            if (Nx, Ny) in Assigned:
                if Assigned[(Nx, Ny)] == 1:
                    Count_mine += 1
            else:
                Count_unassigned_neigbor += 1

        # If the lower bound is larger than the hint, the constraint cannot be satisfied.
        # If the upper bound is smaller than the hint, the constraint cannot be satisfied.
        if (Count_mine > self.board[x][y] or
                Count_mine + Count_unassigned_neigbor < self.board[x][y]):
            return False
        else:
            return True

    def get_degree(self, block, Assigned):
        '''
        get the degree of board[x][y]
        degree means the number of variables which will be affected 
        after I assigned value 
        '''
        constraint_set = {(block.x, block.y)}
        degree = 0
        for (Nx, Ny) in Neighbor(self.BoardSize, block.x, block.y):
            if self.board[Nx][Ny] >= 0:
                for (N2x, N2y) in Neighbor(self.BoardSize, Nx, Ny):
                    if self.board[N2x][N2y] < 0:
                        if (N2x, N2y) not in constraint_set and (N2x, N2y) not in Assigned:
                            degree += 1
                            constraint_set.add((N2x, N2y))

        return degree

    def get_domain(self, Block, Assigned):
        '''
        It is a function to get the domain of a block. Because
        the domain can only become smaller and smaller,so I just
        have to check whether the original domain is still assignable.
        '''
        if len(Block.domain) == 0:
            return set()

        ans = set()

        for v in Block.domain:
            # assign (x, y) -> v and see whether it is allowed
            # I don't check num_mines here because if I check it when I
            # expand the Node, I will be more efficient
            Assigned[(Block.x, Block.y)] = v

            ADD = True
            for (Nx, Ny) in Neighbor(self.BoardSize, Block.x, Block.y):
                if self.board[Nx][Ny] < 0:
                    continue
                if self.check_constraint(Nx, Ny, Assigned) is False:
                    ADD = False
                    break
            if ADD:
                ans.add(v)

        # pop out the (x, y) I push in just now
        Assigned.pop((Block.x, Block.y))

        return ans

    def generate_nodes(self, value, idx, Unassigned, Assigned, forward_checking=False, Deep_Copy=True):
        '''
        when expanding a node, we have to generate the child nodes
        In this function, I have to generate a Node whose variable of
        Unassigned[idx] be assigned value 'value'
        if the assignment is not allowed, return None

        To make my function run faster, I might have to do some
        shallow copy sometimes.
        '''
        # try to assign because we have to check the full board num_mine
        # if we can't Assigned the value to the block, return None
        total_assign = Assigned['assigned_mines'] + value
        if (total_assign > self.num_mines or
                total_assign + self.num_variable - len(Assigned) < self.num_mines):
            return None

        if Deep_Copy:
            # make new assigned list
            new_assigned = Assigned.copy()
            new_assigned[(Unassigned[idx].x, Unassigned[idx].y)] = value
            new_assigned['assigned_mines'] += value

            if forward_checking:
                # make new Unassegined list
                new_Unassigned = []

                for block in Unassigned[:idx] + Unassigned[idx+1:]:
                    if Neighbor2((block.x, block.y), (Unassigned[idx].x, Unassigned[idx].y)):
                        # we only have to update the value that might change,
                        # which are the blocks in current block's (+-2, +-2)
                        new_domain = self.get_domain(block, new_assigned)
                        if len(new_domain) == 0:
                            # do forward checking
                            return None
                        new_Unassigned.append(block.new(domain=new_domain))
                    else:
                        new_Unassigned.append(block.new())

                return NODE(new_Unassigned, new_assigned)
            else:
                # if don't use forward checking, simply make the new list
                new_Unassigned = []
                for block in Unassigned[:idx] + Unassigned[idx+1:]:
                    new_Unassigned.append(block.new())

                return NODE(new_Unassigned, new_assigned)
        else:
            # just assigned value to (x, y) and pop out (x, y) from Unassigned
            Assigned[(Unassigned[idx].x, Unassigned[idx].y)] = value
            Assigned['assigned_mines'] += value

            pos = (Unassigned[idx].x, Unassigned[idx].y)
            Unassigned.pop(idx)

            if forward_checking:
                # do forward checking
                for block in Unassigned:
                    if Neighbor2((block.x, block.y), pos):
                        # we only have to update the value that might change,
                        # which are the blocks in current block's (+-2, +-2)
                        block.domain = self.get_domain(block, Assigned)
                        if len(block.domain) == 0:
                            return None

                return NODE(Unassigned, Assigned)
            else:
                return NODE(Unassigned, Assigned)

    def solve(self, forward_checking=False, MRV=False, Degree_heuristic=False, LCV=False, show=True):
        '''
        The solve function to the board in this class
        I have some optional heuristics for this funtion
        - forward_checking: check if any variables domain became empty set.
                    we must use it if we want to use the heuristic function below.
        - MRV: expand variable with domain size == 1 first.
        - Degree_heuristic: when two variable have domain size == 1,
                            the one with larger degree expand first.
        - LCV: when all variable have domain size == 2,  try both values using the consistency
                checks mentioned above to see how they affect the domains of the other variables.
        '''

        # if using heuristics, we must use forward checking
        if MRV or Degree_heuristic or LCV:
            forward_checking = True

        # if there's a hint that we can never make the neighboring mine's
        # number equals to the constraint, return No answer
        for i in range(self.BoardSize[0]):
            for j in range(self.BoardSize[1]):
                if self.board[i][j] > 0:
                    Count = 0
                    for (Nx, Ny) in Neighbor(self.BoardSize, i, j):
                        if self.board[Nx][Ny] < 0:
                            Count += 1
                    if Count < self.board[i][j]:
                        if show:
                            print('No answer.')
                        return 'No answer.', 0

        # initialize assigned list(dict), unassigned list stack
        Assigned = {'assigned_mines': 0}
        Unassigned = []
        STACK = []

        # if board[i][j] is not constraint, put into the Unassigned list
        for i in range(self.BoardSize[0]):
            for j in range(self.BoardSize[1]):
                if self.board[i][j] < 0:
                    Unassigned.append(UnassignedBlock(i, j))

        # initialize domains if we need to do forward checking
        if forward_checking:
            for block in Unassigned:
                block.domain = self.get_domain(block, Assigned)

                # if some domains are empty set, No answer
                if block.domain == {}:
                    if show:
                        print('No answer.')
                    return 'No answer.', 0

        # put Node into Stack and initialize expanded_node
        # which count how many nodes I expand
        STACK.append(NODE(Unassigned, Assigned))
        expanded_node = 0

        while len(STACK) > 0:
            expanded_node += 1

            Unassigned = STACK[-1].Unassigned
            Assigned = STACK[-1].Assigned
            STACK.pop(-1)

            # if len(Unassigned) == 0, all variable has been
            # assigned, return answer MAP and expanded_node
            if len(Unassigned) == 0:
                MAP = get_answer_map(self.BoardSize, self.board, Assigned)
                # print the map if we want
                if show:
                    print_2dboard(self.BoardSize, MAP)

                return MAP, expanded_node

            # variable being assigned's default index
            idx = 0

            if MRV and Degree_heuristic:
                # if using MRV and Degree_heuristic, assign the one
                # with domain size == 1 and larger degree first.
                # if there's no variable with domain size == 1,
                # choose the one with larger degree
                domain_size1 = []
                for i in range(len(Unassigned)):
                    if len(Unassigned[i].domain) == 1:
                        domain_size1.append(i)

                largest_degree = 0
                if len(domain_size1):
                    for i in domain_size1:
                        degree = self.get_degree(Unassigned[i], Assigned)
                        if degree > largest_degree:
                            idx = i
                            largest_degree = degree
                else:
                    for i in range(len(Unassigned)):
                        degree = self.get_degree(Unassigned[i], Assigned)
                        if degree > largest_degree:
                            idx = i
                            largest_degree = degree
            elif MRV:
                # if using MRV assign the one with domain size == 1 first.
                for i in range(len(Unassigned)):
                    if len(Unassigned[i].domain) == 1:
                        idx = i
                        break
            elif Degree_heuristic:
                # if using degree heuristic only, assigned the variable
                # with largest degree first.
                largest_degree = 0
                for i in range(len(Unassigned)):
                    degree = self.get_degree(Unassigned[i], Assigned)
                    if degree > largest_degree:
                        idx = i
                        largest_degree = degree

            # when we use no heuristic and forward cheching, we need to check
            # the domain of the variable before we assign value.
            if forward_checking is False:
                Unassigned[idx].domain = self.get_domain(
                    Unassigned[idx], Assigned)

            node_0, node_1 = None, None

            # assign value with the way of copy that makes it correctly and faster
            if Unassigned[idx].domain == {0}:
                node_0 = self.generate_nodes(0, idx, Unassigned, Assigned,
                                             forward_checking=forward_checking, Deep_Copy=False)
            elif Unassigned[idx].domain == {1}:
                node_1 = self.generate_nodes(1, idx, Unassigned, Assigned,
                                             forward_checking=forward_checking, Deep_Copy=False)
            elif Unassigned[idx].domain == {0, 1}:
                node_0 = self.generate_nodes(0, idx, Unassigned, Assigned,
                                             forward_checking=forward_checking)
                node_1 = self.generate_nodes(1, idx, Unassigned, Assigned,
                                             forward_checking=forward_checking, Deep_Copy=False)

            # if number of append node smaller than 1,
            # simply ignore it or append it
            if node_0 == None and node_1 == None:
                continue
            elif node_0 == None:
                STACK.append(node_1)
                continue
            elif node_1 == None:
                STACK.append(node_0)
                continue

            # if number of append node is 2, check if using LCV
            if LCV:
                # since the next node must have the same number of
                # variable, and we have check no domain is empty set
                # -> domain size is either 1 or 2, so we should make
                # the one with more domain size is 2 to be popped first
                Count0 = 0
                for uad in node_0.Unassigned:
                    if len(uad.domain) == 2:
                        Count0 += 1
                Count1 = 0
                for uad in node_1.Unassigned:
                    if len(uad.domain) == 2:
                        Count1 += 1

                # if Count0 > Coumt1, node0 have bigger domain
                if Count0 > Count1:
                    STACK.append(node_1)
                    STACK.append(node_0)
                else:
                    STACK.append(node_0)
                    STACK.append(node_1)
            else:
                # simply append it
                STACK.append(node_0)
                STACK.append(node_1)

        # if after expanded all node there stille have no answer,
        # return 'No answer.'
        if show:
            print('No answer.')
        return 'No answer.', expanded_node
