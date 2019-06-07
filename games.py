"""
games - A module for calculations on games, using numpy.
"""

__version__ = '0.1'
__author__ = 'Daniel Ahlsén'

import numpy as np
import networkx as nx
from itertools import groupby

###############
# GAME MODELS #
###############

class Game:
    """Represents a game in normal form by an ndarray with shape 
    (n_1, ..., n_m, m)."""
    def __init__(self, payoffs, dtype='float64'):
        self.mat = np.array(payoffs,dtype)
        self.shape = np.shape(self.mat)
        self.players = self.mat.ndim-1
        
        if(self.mat.shape[-1] != self.players):
            raise ValueError('Matrix does not represent a strategic game.')
        
    
    def outcome(self,move):
        return self.mat[move]

    def expected_outcome(self,profile):
        dist = expected_outcome(profile)
        outcome = np.ones(self.players)
        
        for i in range(self.players):
            outcome[i] = np.sum(self.mat[...,i]*dist)
        
        return outcome
        
    def __str__(self):
        return str(self.mat)

class ConcurrentGameModel:
    """
    A Concurrent Game Model as a list of integer matrices of equal dimension.
    """
    def __init__(self, transitions, init = 0):
        """
        Initialize a Concurrent Game Model.
        
        Keyword arguments
        transitions -- a list of transition matrices
        init -- the initial state (default 0)
        """

        # Convert transition matrices to integer ndarrays
        self.transitions = np.array(transitions,dtype='int16')
        
        # Check that all dimensions match
        dims = map(lambda x : np.ndim(x), self.transitions)
        if all_equal(dims):
            raise ValueError("Dimensions of transition matrices must match.")
        
        # Check that all transitions point to other states
        for matrix in self.transitions:
            if any(n < 0 or n >= len(transitions) for n in np.nditer(matrix)):
                raise ValueError("All transitions must be to other states.")

        self.states = range(len(transitions))
        self.cstate = init
        self.transitions = transitions
        
        self.players = np.ndim(transitions[0])
        self.shistory = []
        self.mhistory = []
        
    def make_move(self, move):
        """
        Make a move and add outcome to histories
        
        Keyword arguments
        move -- move to make
        """
        
        self.shistory.append(self.cstate)
        self.cstate = self.transitions[self.cstate][move]
        self.mhistory.append(move)
    
    def __str__(self):
        txt = "Current state: " + str(self.cstate) + "\n" 
        txt += "State history: " + str(self.shistory) + "\n"
        txt += "Move history: " + str(self.mhistory) + "\n"
        return txt
        
    def reset(self, init = 0):
        self.cstate = init
        self.shistory = []
        self.mhistory = []

class GuardedConcurrentGameModelPayoffs(ConcurrentGameModel):
    """
    A Guarded Concurrent Game Model with Payoffs is a Concurrent Game Model 
    (CGM) with a strategic game in each state.
    """
    def __init__(self, transitions, payoffs, guards=[], init=0):
        
        ConcurrentGameModel.__init__(self, transitions, init)
        self.games = [ Game(mat) for mat in payoffs ]
        
        for i in range(len(payoffs)):
            if games[i].shape[:-1] != transitions[i]:
                raise ArgumentError()
            if games[i].players != transitions[i].ndim:
                raise ArgumentError()
        
        self.phistory = []
        self.guards = guards
        
    def make_move(self,move):
        self.phistory.append(games[self.cstate].outcome(move))
        ConcurrentGameModel.make_move(self,move)
        
    def reset(self,init=0):
        self.phistory = []
        ConcurrentGameModel.reset(self,init)
        
    def __str__(self):
        txt = ConcurrentGameModel.__str__(self)
        txt += "Payoff history: " + str(self.phistory) + "\n"
        return txt

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
      
def transition_matrix(cgm, profile):
    """Returns the transition matrix for a given CGM and strategy profile."""
    if cgm.players != len(profile):
        raise ValueError("Number of strategy profiles must match number of "
                + "players in CGM.")
    
    if any(cgm.states != s.states for s in profile):
        raise ValueError("Number of states in strategy profile must match "
                + "number of states in CGM.")
    
    # Extract state outcomes
    temp = []
    outcomes = []
    for state in range(cgm.states):
        for player in profile:
            temp.append(player[state])
        
        outcomes.append(expected_outcome(temp))
        temp = []
    
    
    # Calculate transition probabilities
    transition = np.zeros((cgm.states,cgm.states))
    
    for state in range(len(cgm.states)):
        for prob, end_state in np.nditer( [outcomes[state],
                cgm.transitions[state]]):
            transitions[state,end_state] += prob
    
    return transitions

def markov_chain(cgm, profile):
    """ Returns the Markov chain corresponding to a state-based mixed 
    strategy profile """
    t = transition_matrix(cgm, profile)

    G = nx.DiGraph()
    
    for i in range(x.shape[0]):
        for j in range(x.shape[1]):
            if x[i,j] > 0:
                G.add_edge(i,j)
                G[i][j]['weight']=x[i,j]
    
    return G

def expected_outcome_statebased(profile):
    """Outputs the expected value of a profile of state-based 
    mixed strategies."""
    # TODO: Find attracting, irreducible subchains
    
    # TODO: Calculate expected value 
    
def all_equal(iterable):
    """Returns True if all the elements are equal to each other"""
    g = groupby(iterable)
    return next(g, True) and not next(g, False)