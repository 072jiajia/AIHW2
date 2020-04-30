

class UnassignedBlock:
    '''
    This is A class to store the message about an unassigned block.
    '''

    def __init__(self, x, y, domain={0, 1}):
        self.x = x
        self.y = y
        self.domain = domain

    def new(self, x=None, y=None, domain=None, degree=None):
        '''
        deep copy a block
        '''
        x = self.x if x is None else x
        y = self.y if y is None else y
        domain = self.domain if domain is None else domain

        return UnassignedBlock(x, y, set(domain))
