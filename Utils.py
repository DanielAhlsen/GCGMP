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
        self.shape = [ shape[i] for i in range(self.size) if i not in self.fixed_indices]
        self.output = [ 0 for _ in range(self.size)]
        self.moving_indices = list(range(self.size))
        counter = 0
        for i in self.fixed_indices:
            self.output[i] = self.fixed_values[counter]
            self.moving_indices.remove(i)
            counter += 1

    def __iter__(self):
        return self

    def __next__(self):

        output = self.output
        # update counter

        i = 0
        while i < len(self.shape):
            #find smallest index that may be increased
            if(self.output[self.moving_indices[i]] < self.shape[i]-1):
                self.output[self.moving_indices[i]] += 1
                i -= 1
                while i >= 0: #set every index below that to 0
                    self.output[self.moving_indices[i]] = 0
                    i -= 1
                return tuple(output)
            i += 1
        # fix an off-by-one error
        if self.output[self.moving_indices[i-1]]-1 == self.shape[i-1]:
            self.output[self.moving_indices[i-1]] += 1
            return tuple(output)
        else:
            raise StopIteration
