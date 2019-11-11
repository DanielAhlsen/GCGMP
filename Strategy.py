##############
# STRATEGIES #
##############

class MixedStrategy:
    """
    MixedStrategy

    Represents a mixed strategy as a n-dimensional ndarray with non-negative
    entries that sum to 1.
    """
    def __init__(self, dist):
        self.dist = np.array(dist)

        for v in self.dist:
            if v < 0:
                raise ValueError("Entries must be non-negative.")

        self.cumm = np.zeros(len(self.dist)+1)
        for index in range(len(self.cumm)-1):
            self.cumm[index+1] = self.cumm[index]+self.dist[index]
        self.cumm[-1] = 1.0

    def __call__(self):
        """Returns an outcome from the mixed strategy"""

        t = np.random.random()
        return np.searchsorted(self.cumm, t)-1

    def __str__(self):
        return str(self.dist)

    def __len__(self):
        return len(self.dist)

    def __getitem__(self,key):
        return self.dist[key]

class StateBasedStrategy:

    def __init__(self, transitions):
        self.transitions = np.array(transitions,dtype='int16')

        for v in self.transitions:
            if v < 0:
                raise ValueError("Strategy must point to states.")

    def __getitem__(self,key):
        return self.transitions[key]

class MixedStateBasedStrategy:
    def __init__(self,strategies):
        if any(type(s) != MixedStrategy for s in strategies):
            raise TypeError()

        self.strategies = strategies
        self.states = len(strategies)
        self.cstate = 0

    def __getitem__(self,key):
        return self.strategies[key]

    def __iter__(self):
        return self

    def __next__(self):
        self.cstate += 1
        if self.cstate <= self.states:
            return self.strategies[self.cstate-1]
        else:
            self.cstate = 0
            raise StopIteration

#############
# FUNCTIONS #
#############

def expected_outcome(profile):
    """Calculates the outcome probability, given a mixed strategy profile."""
    shape = list(map(lambda x : len(x), profile))
    outcome = profile[0].dist

    for i in range(len(shape)-1):
        outcome = outcome.reshape(shape[0:i+1]+[1])
        outcome = outcome*profile[i+1].dist

    return outcome
