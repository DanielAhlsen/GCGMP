import intervals as I
import numpy as np
from Strategy import Segmentation

class Parser:

    def __init__(self,string):
        self.index = 0
        self.string = ''.join(string.split())

    ## Helper functions

    def peek(self):
        return self.string[self.index]

    def hasNext(self):
        return self.index < len(self.string)

    def isNext(self,c):
        if self.hasNext():
            return self.string[self.index] == c
        else:
            return False

    def pop(self):
        c = self.string[self.index]
        self.index += 1
        return c

    def popIfNext(self,c):
        if self.isNext(c):
            return self.pop()
        else:
            return False

class IntervalParser(Parser):

    def __init__(self,string):
        super().__init__(string)
        self.peek = super().peek
        self.hasNext = super().hasNext
        self.isNext = super().isNext
        self.pop = super().pop
        self.popIfNext = super().popIfNext
        self.interval = self.parseExpression()

    ## Parsing functions

    def parseExpression(self):
        if self.popIfNext('{'):
            interval = self.parseUnion()
            if not self.popIfNext('}'):
                raise ValueError("No closing curly bracket found.")
            elif self.popIfNext('&'):
                return interval & self.parseExpression()
            elif self.popIfNext('|'):
                return interval | self.parseExpression()
            elif not self.hasNext():
                return interval
            else:
                raise ValueError('Unexpected character encountered.')
        else:
            return self.parseUnion()

    def parseUnion(self):
        if self.peek() == '{':
            return self.parseExpression()
        else:
            interval = self.parseIntersection()
            while self.popIfNext('|'):
                interval = interval | self.parseIntersection()
            return interval

    def parseIntersection(self):
        if self.peek() == '{':
            return self.parseExpression()
        else:
            interval = self.parseInterval()
            while self.popIfNext('&'):
                if self.peek() == '{':
                    interval = interval & self.parseExpression()
                else:
                    interval = interval & self.parseInterval()
            return interval

    def parseInterval(self):
        left = self.pop()
        if left not in '[(':
            raise ValueError('Unexpected character, expected [ or (.')

        lower = self.parseFloat()

        if self.pop() != ',':
            raise ValueError('Unexpected character, expected ,.')

        upper = self.parseFloat()

        right = self.pop()
        if right not in ')]':
            raise ValueError('Unexpected character, expected ) or ].')

        if left+right == '[]':
            return I.closed(lower,upper)
        elif left+right == '[)':
            return I.closedopen(lower,upper)
        elif left+right == '(]':
            return I.openclosed(lower,upper)
        elif left+right == '()':
            return I.open(lower,upper)

    def parseFloat(self):
        num = ''
        hasDot = False
        sign = 1
        if self.popIfNext('-'):
            sign = -1
        while self.peek() in '0123456789.':
            c = self.pop()
            if c == '.':
                if not hasDot:
                    hasDot = True
                else:
                    raise ValueError('Unexpected period found in string.')
            num += c
        if num == '':
            raise ValueError('Unexpected character, expected float.')
        return sign*float(num)

class SegmentationParser(Parser):

    def __init__(self,string):
        super().__init__(string)
        self.peek = super().peek
        self.hasNext = super().hasNext
        self.isNext = super().isNext
        self.pop = super().pop
        self.popIfNext = super().popIfNext
        self.segmentation = self.parseSegmentation()

    def parseSegmentation(self):
        points = []
        delimiters = []
        while self.index < len(self.string)-1:
            if self.peek() in '])':
                if len(delimiters) == len(points):
                    raise ValueError("Unexpected delimiter found.")
                else:
                    c = self.pop()
                    if c == ']':
                        delimiters.append(0)
                    else:
                        delimiters.append(1)
            elif len(points) == len(delimiters):
                points.append(self.parseFloat())
            else:
                raise ValueError("Numbers and delimiters do not match.")

        if self.peek() in '])':
            if len(delimiters) == len(points):
                raise ValueError("Unexpected delimiter found.")
            else:
                c = self.pop()
                if c == ']':
                    delimiters.append(0)
                else:
                    delimiters.append(1)
        else:
            raise ValueError("Missing closing delimiter.")

        return Segmentation(points,delimiters)

    def parseFloat(self):
        num = ''
        hasDot = False
        sign = 1
        if self.popIfNext('-'):
            sign = -1
        while self.peek() in '0123456789.':
            c = self.pop()
            if c == '.':
                if not hasDot:
                    hasDot = True
                else:
                    raise ValueError('Unexpected period found in string.')
            num += c
        if num == '':
            raise ValueError('Unexpected character, expected float.')
        return sign*float(num)
