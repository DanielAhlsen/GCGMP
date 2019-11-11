class niter:
    """
    An n-dimensional iterator. Given a shape (n_1, ..., n_m), the iterator
    yields the values (0,0, ..., 0), (1,0,...,0), ... (n_1-1, ..., n_m-1).
    """
    def __init__(self,shape, fixed_indices=None, fixed_values=None):

        if fixed_values == None:
            self.fixed_values = []
        else:
            self.fixed_values = fixed_values
        if fixed_indices == None:
            self.fixed_indices = []
        else:
            self.fixed_indices = fixed_indices


        self.size = len(shape)
        self.cstate = [ 0 for x in shape ]
        self.shape = list(shape)
        for index in self.fixed_indices:
            self.shape.pop(index)
            self.cstate.pop(index)

    def __iter__(self):
        return self

    def __next__(self):
        # create output vector
        output = [ 0 for i in range(self.size)]
        counter = 0
        for index in range(self.size):
            if index in self.fixed_indices:
                output[index] = self.fixed_values[index]
                counter += 1
            else:
                output[index] = self.cstate[index-counter]

        # update counter
        i = 0
        while i < len(self.shape):
            #find smallest index that may be increased
            if(self.cstate[i]+1 < self.shape[i]):
                self.cstate[i] += 1 #increase index
                i -= 1
                while i >= 0: #set every index below that to 0
                    self.cstate[i] = 0
                    i -= 1
                return tuple(output)
            i += 1
        # fix an off-by-one error
        if self.cstate[i-1] == self.shape[i-1]-1:
            self.cstate[i-1] += 1
            return tuple(output)
        else:
            raise StopIteration
