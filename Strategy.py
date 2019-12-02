import numpy as np
import networkx as nx
import intervals as I

##############
# STRATEGIES #
##############

class StateStrategy:

    def __init__(self, transitions):
        self.transitions = np.array(transitions,dtype='int16')

        for v in self.transitions:
            if v < 0:
                raise ValueError("Strategy must point to states.")

    def __getitem__(self,key):
        return self.transitions[key]

class Segmentation:
    """A segmentation is a finite collection of disjoint intervals which cover
    the real line. It is specified by a sorted list of distinct real numbers,
    and a list of delimiters which specifies the open and closedness of
    intervals.

    TODO: Make it possible for a Segmentation to be empty.

    Parameters
    ----------
    points : array
        Points of the segmentation.
    delimiters : array
        Delimiters determine whether the point number i is included in the left or
        the right segment, relative to the point. 0 means left, 1 means right.
    """
    def __init__(self,points,delimiters):
        """Initializes a Segmentation. Checks that

        Parameters
        ----------
        points : array
            Points of the segmentation.
        delimiters : array
            Delimiters determine whether the point number i is included in the left or
            the right segment, relative to the point. 0 means left, 1 means right.

        Returns
        -------
        type
            None

        """
        if len(delimiters) != len(points):
            raise ValueError("Numbers of delimiters equal the number of points.")
        for i in range(len(points)-1):
            if points[i+1] <= points[i]:
                raise ValueError("Array must be sorted and points distinct.")
            if delimiters[i] not in {0,1}:
                raise ValueError("Delimiters must be 0 or 1.")

        if delimiters[-1] not in {0,1}:
                raise ValueError("Delimiters must be 0 or 1.")

        self.points = points
        self.delimiters = delimiters

    def __call__(self,x):
        i = 0
        while i < len(self.delimiters):
            if self.delimiters[i] == 0 and not self.points[i] < x:
                return i
            elif self.delimiters[i] == 1 and not self.points[i] <= x:
                return i
            else:
                i += 1

        return i

    def __len__(self):
        return len(self.points)+1

    def __str__(self):
        string = '(-inf,'
        for i in range(len(self.delimiters)):
            string += str(self.points[i])
            if self.delimiters[i] == 0:
                string += ']('
            else:
                string += ')['
            string += str(self.points[i]) + ','
        string += 'inf)'
        return string

class SegmentationStrategy(Segmentation):
    """A SegmentationStrategy extends Segmentations by assigning each segment
    in a Segmentation an action.

    TODO: Make it possible to enter segmentation directly, without creating
    the Segmentation object.

    Parameters
    ----------
    segmentation : Segmentation
        a segmentation that
    actions : array
        An array of actions. May contain anything, but the length must match
        the length of the Segmentation.

    Attributes
    ----------
    actions : array
        the action for each segment in the segmentation.

    """


    def __init__(self,segmentation,actions):
        if type(segmentation) is not Segmentation:
            raise ValueError("First argument is not a Segmentation.")
        if len(segmentation) != len(actions):
            raise ValueError("Number of actions must match number of segments.")

        super().__init__(segmentation.points,segmentation.delimiters)
        self.actions = actions

    def __call__(self,x):
        return self.actions[super().__call__(x)]

class StateSegmentationStrategy:

    def __init__(self,states,strategies):

        if states != len(strategies):
            raise ValueError("Number of strategies must match the number of states.")
        if any( [ type(s) is not SegmentationStrategy for s in strategies ] ):
            raise ValueError("Strategies must be SegmentationStrategy.")

        self.strategies = strategies

    def __call__(self,state,x):
        return self.strategies[state](x)
