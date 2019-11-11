"""
PresburgerArithmetic - A module for Presburger Arithmetic
"""

import numpy as np

class LinearConstraint():
    """
    A linear constraint
    """
    def __init__(self,A,lb,ub):
        self.A = np.array(A)
        if (lb > ub):
            raise ArgumentError("Lower bound must be smaller than upper bound.")
        self.lb = lb
        self.ub = ub

    def __call__(self,x):
        """ Evaluates the constraint at the given configuration """
        return (np.dot(self.A,x) <= self.ub) and (np.dot(self.A,x) >= self.lb)

class PAFormula():
    """
    A formula in Presburger Arithmetic (PA), i.e a Boolean combination of
    linear constraint. All linear constraints are assumed to be over the
    same variables.
    """
    def __init__(self, attr = True, children=None):

        # If input is a PAFormula, return a new PAFormula with the same
        # children and attribute
        if type(attr) == PAFormula:
            if children != None:
                raise TypeError("PAFormulas cannot be initialized with " +
                                    "subformulas.")
            else:
                self.attr = attr.attr
                self.children = attr.children
                return
        # If input is LinearConstraint, set self.attr to it and children to
        # None
        elif type(attr) == LinearConstraint:
            if children != None:
                raise TypeError("Linear constraints cannot have " +
                                    "subformulas.")
            else:
                self.attr = attr
                self.children = children
        # If input is a logical operator
        elif (attr == '&' or
            attr == '|' or
            attr == '~' or
            attr == True or
            attr == False):

            # Check that the number of children is equal to the arity
            # of the logical operator
            if (attr == '&' or attr == '|') and len(children) != 2:
                raise TypeError("Operators & and | are binary.")
            if (attr == '~') and len(children) != 1:
                raise TypeError("Operator ~ is unary.")
            if (attr is True or attr is False) and children != None:
                raise TypeError("Truth/Falsity is a constant.")

            # Store attribute
            self.attr = attr

            if children != None:
                # Check that children are PAFormulas or LinearConstraints
                if not all([(type(ch) == LinearConstraint or
                            type(ch) == PAFormula) for ch in children]):
                    raise TypeError("Subformulas must be PAFormula or " +
                        "LinearConstraint objects.")

                # convert all children to PAFormulas
                self.children = [ PAFormula(ch) for ch in children ]
            else:
                self.children = None
        else:
            raise TypeError("Attribute must be &, |, ~, Truth, Falsity," +
                                " a PAFormula object or a LinearConstraint " +
                                "object.")



    def __call__(self,x):
        if self.attr == '&':
            return self.children[0](x) and self.children[1](x)
        elif self.attr == '|':
            return self.children[0](x) or self.children[1](x)
        elif self.attr == '~':
            return not self.children[0](x)
        elif type(self.attr) == LinearConstraint:
            return self.attr(x)
        else:
            return self.attr
