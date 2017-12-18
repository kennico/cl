from itertools import chain
from collections import defaultdict

import re
import debug


class Symbol(object):

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.string)

    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.string == other.string
        else:
            return False

    def __hash__(self):
        return hash(self.string)

    def __ne__(self, other):
        return not self.__eq__(other)


class Terminal(Symbol):
    pass


class Production(object):
    """
    For the production deriving an epsilon notation (e.g. S->e),
    self.body is set to be an empty tuple.
    """

    def __init__(self, head, *symbols):
        self.head = head
        self.body = symbols

    def __str__(self):
        return '%s->%s' % (str(self.head), ''.join([str(s) for s in self]))

    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.__str__())

    def __getitem__(self, index):
        """
        Return the i-th symbolize of the production body, making a production object iterable
        """

        return self.body[index]

    def __len__(self):
        return self.body.__len__()

    def __eq__(self, other):
        if isinstance(other, Production):
            return (self.head == other.head) and (self.body == other.body)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class NTerminal(Symbol):
    """
    Non-terminal class.
    """

    def __init__(self, s):
        super(NTerminal, self).__init__(s)
        self.productions = []

    def create_production(self, *symbols):
        """
        Create a production using the given symbols.
        If no symbol is passed, a production with an empty list is created.
        That means the non-terminal derives epsilon.
        """

        p = Production(self, *symbols)
        self.productions.append(p)
        return p


class Grammar(object):
    """
    The endmarker is treated as a terminal while EPSILON is NOT treated as a grammar symbol.
    """

    NT = None
    T = None
    START = None
    END = None

    def nterminals(self):
        """Return non-terminals"""

        return self.NT.values()

    def terminals(self):
        """Return all the terminals."""

        return self.T.values()

    def productions(self):
        # TODO Remove list()

        return list(chain(*[sym.productions for sym in self.NT.values()]))


class GrammarBuilder(object):
    """
    Given the filename, start in string as keyword arguments:

    >>> g = GrammarBuilder(filename=test-input.txt', start='START').build()

    If start is not specified then the left of the first production will be considered as the start symbol.
    """

    def __init__(self, *prods, **kwargs):
        self.raw_start = kwargs.pop('start', 'S')
        self.raw_endmarker = kwargs.pop('endmarker', '#')

        if not prods:
            try:
                filename = kwargs.pop('filename')
            except KeyError:
                raise ValueError('No productions or filename found.')
            with open(filename) as f:
                self.raw_lines = f.read().splitlines()
        else:
            self.raw_lines = [line.strip() for line in prods]

    def preprocess(self):
        # TODO Make it support the yacc format

        raw_productions = defaultdict(list)

        i = 0
        while i < len(self.raw_lines):
            prods = ''

            while True:
                prods += self.raw_lines[i]
                i += 1
                if prods.endswith(';'):
                    break

            nts, bodys = re.split(r'\s*:\s*', prods.strip('; '))

            if not raw_productions:
                self.raw_start = nts

            for p in re.split(r'\s*\|\s*', bodys):
                raw_productions[nts].append(p.split())

        self.raw_productions = raw_productions

    def is_NT_string(self, s):
        """Check if the given string is a non-terminal"""

        return s in self.raw_productions

    def symbolize(self, s):
        """Convert a string into a grammar symbolize recursively"""

        if s not in self.tempd:
            if self.is_NT_string(s):
                sym = self.tempd[s] = NTerminal(s)
                for raw_prod in self.raw_productions[s]:
                    sym.create_production(*[self.symbolize(c) for c in raw_prod])
            else:
                self.tempd[s] = Terminal(s)
        return self.tempd[s]

    @debug.log_attr(names=['START', 'END', 'NT', 'T'], msg='Build Grammar')
    def build(self):
        """Begin to build a grammar object which consists of symbolize objects"""

        self.tempd = {}
        self.preprocess()

        g = Grammar()

        g.START = self.symbolize(self.raw_start)
        g.END = self.symbolize(self.raw_endmarker)

        g.NT = {s:obj for s, obj in self.tempd.items() if self.is_NT_string(s)}
        g.T = {s:obj for s, obj in self.tempd.items() if not self.is_NT_string(s)}

        return g


def main():

    g = GrammarBuilder(filename='test-input/test-LR0-input_1', start='S').build()


if __name__ == '__main__':
    main()
