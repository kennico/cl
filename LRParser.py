import debug
import grammar

from collections import deque


class AugmentedGrammarBuilder(grammar.GrammarBuilder):

    @debug.log_attr(names=['START_PROD'], msg='Build Augmented Grammar')
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
        self.goto = {}
        self.action = {}
        self.startset = self.construct(aug_gram)

    def setaction(self, state, sym, func, *args):
        """
        Set action on (state, sym). If conflict found, an error will be raised.

        :param state:
        :param sym:
        :param func:
        :param args:
        :return:
        """

        k = (state, sym)
        v = (func, args)

        found = self.action.get(k, None)

        if found and found != v:
            raise ParseError('Conflict found', -1)

        self.action[k] = v

    def setgoto(self, state, sym, next):
        """
        Set action on (state, sym). If conflict found, an error will be raised.

        :param state:
        :param sym:
        :param next:
        :return:
        """
        k = (state, sym)

        found = self.goto.get(k, None)

        if found and found != next:
            raise ParseError('Conflict found', -1)

        self.goto[k] = next

    def construct(self, aug_gram):
        """
        Construct the LR analysis tables.

        :param aug_gram:
        :return:
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
        self.stack = stack      # Remember to assign self.stack stack

    @debug.log_param(msg='PARSE BEGIN')
    def parse(self, symbols):
        """
        Should be fed a symbols sequence terminated with an endmarker.

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
                method(*action[1])
            except KeyError as e:
                raise ParseError('No such action.', -1)
            except (ParseError, ParseFinish) as e:
                return e

