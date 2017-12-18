import debug
import grammar

from collections import deque


class AugmentedGrammarBuilder(grammar.GrammarBuilder):

    @debug.log_attr(names=['START', 'END', 'NT', 'T', 'START_PROD'], msg='Build Augmented Grammar')
    def build(self):
        g = grammar.GrammarBuilder.build(self)
        g.START_PROD = g.START.productions[0]

        return g


class BaseParseException(Exception):
    def __init__(self, msg, errno):
        self.msg = msg
        self.errno = errno

    def __iter__(self):
        return iter((self.msg, self.errno))


class ParseError(BaseParseException):
    pass


class ParseFinish(BaseParseException):
    pass


class LRParser(object):
    """
    Apply to an augmented grammar which has only one production starts with the START symbol
    """

    def __init__(self, aug_gram):
        startset, action, goto = self.construct(aug_gram)

        self.startset = startset
        self.goto = goto
        self.action = action

    def construct(self, aug_gram):
        """
        Construct the LR analysis tables.

        :return: startset, action table and goto table
        """
        raise NotImplementedError

    @debug.log_param(msg='ACCEPT')
    def accept(self):
        """
        Raise a ParseFinish exception.

        :return:
        """

        raise ParseFinish('Accepted.', 0)

    @debug.log_param(msg='SHIFT')
    def shift(self, state):
        """
        Shift a symbol from self.test-input and push the state onto self.stack

        :param state:
        :return:
        """

        self.input.popleft()
        self.stack.append(state)

    @debug.log_param(names=['prod'], msg='REDUCE')
    def reduce(self, prod):
        """
        Reduce the prod.body on the top of self.stack to prod.head

        :param prod: a Production object used in the reduction
        :return:
        """

        stack = self.stack[:-len(prod)]     # Pop states and symbols from the stack
        curr = stack[-1]

        try:
            next = self.goto[(curr, prod.head)]
        except KeyError:
            raise ParseError('No such transition.', -1)

        stack.append(next)
        self.stack = stack      # Remember to assgin self.stack stack

    def parse(self, symbols):
        """
        Should be fed a sequence of symbols with an endmarker.

        :param symbols: an iterable objcect teminated with an endmarker
        :return: a string msg and an int number, 0 for success
        """
        self.input = deque(symbols)
        self.stack = [self.startset]

        while True:
            try:
                curr = self.stack[-1]
                sym = self.input[0]

                action = self.action[(curr, sym)]

                method = action[0]
                method(*action[1:])
            except (ParseError, ParseFinish) as e:
                return e
            except KeyError as e:
                print(e)
                raise ParseError('No such action.', -1)

