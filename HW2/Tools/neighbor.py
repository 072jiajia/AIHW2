
# It makes me easier to get neighbors
neighbor = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
            (0, 1), (1, -1), (1, 0), (1, 1)]


def Neighbor(BoardSize, x, y):
    '''
    To get the list of neighbor
    '''
    Neighbor_List = []
    for (dx, dy) in neighbor:
        if (x + dx < 0 or x + dx >= BoardSize[0] or
                y + dy < 0 or y + dy >= BoardSize[1]):
            continue
        Neighbor_List.append((x+dx, y+dy))
    return Neighbor_List


def Neighbor2(A, B):
    '''
    check if A and B can or cannot have the same constraint (hint)
    '''
    if abs(A[0] - B[0]) > 2:
        return False
    if abs(A[1] - B[1]) > 2:
        return False
    return True
