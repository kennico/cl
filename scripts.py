import itertools


class Symbol(object):
    def __init__(self, s):
        self.string = s

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.string


class Terminal(Symbol):
    pass


class Production(object):
    def __init__(self, head, *body):
        self.head = head
        self.body = body

    def __str__(self):
        return '%s->%s' % (str(self.head), ''.join([str(s) for s in self]))

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        '''Return the i-th symbol of the production body'''
        return self.body[index]


class NTerminal(Symbol):
    def __init__(self, s):
        super(NTerminal, self).__init__(s)
        self.productions = []

    def add_production(self, *body):
        self.productions.append(Production(self, *body))


class Grammar(object):
    def __init__(self):
        self.NT = None
        self.T = None
        self.START = None
        self.EPSILON = None


class GrammarBuilder(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.raw_lines = [line.strip() for line in f]

    def pre_process(self):
        raw_productions = {}

        for l in self.raw_lines[2:]:
            nts, *prods = l.split()
            if nts not in raw_productions:
                raw_productions[nts] = []
            raw_productions[nts] += prods

        self.raw_productions = raw_productions

    def is_NT(self, s):
        return s in self.raw_productions

    def handle(self, s):
        if s not in self.tempd:
            if self.is_NT(s):
                nt = self.tempd[s] = NTerminal(s)
                for prods in self.raw_productions[s]:
                    nt.add_production(*[self.handle(c) for c in prods])
            else:
                self.tempd[s] = Terminal(s)
        return self.tempd[s]

    def symbolize(self):
        self.tempd = {}
        starts, epsilons = self.raw_lines[:2]
        self.EPSILON = self.handle(epsilons)
        self.START = self.handle(starts)

    def symbols(self):
        return self.tempd.values()

    def productions(self):
        return itertools.chain(*[sym.productions for sym in self.symbols() if self.is_NT(str(sym))])

    def build(self):

        self.pre_process()
        self.symbolize()

        firstd = {}

        def derive_epsilon(sym):
            return self.EPSILON in firstd[str(sym)]

        def calculate_first(sym):
            '''Calculate the first set of sym and set firstd[str(sym)]'''
            result = firstd.setdefault(str(sym), set())
            if not result:
                if self.is_NT(str(sym)):
                    for prod in sym.productions:
                        for subsym in prod:
                            result |= calculate_first(subsym)
                            if derive_epsilon(subsym):
                                break
                else:
                    result |= {sym}
            return result
        # Calculate first set for each non-terminal
        for sym in self.symbols():
            if self.is_NT(str(sym)):
                calculate_first(sym)

        print("FIRST SET:",firstd)
        print("PRODUCTIONS LIST:", list(self.productions()))

        depend = {s:[] for s in self.tempd}
        # TODO CALCULATE FOLLOW SET
        for prod in self.productions():
            pass


        g = Grammar()
        g.START = self.START
        g.EPSILON = self.EPSILON
        g.NT = {s:obj for s, obj in self.tempd.items() if self.is_NT(s)}
        g.T = {s:obj for s, obj in self.tempd.items() if not self.is_NT(s)}
        return g



def main():
    g = GrammarBuilder('grammar.txt').build()
    print('START:',g.START)
    print('EPSILON:',g.EPSILON)
    print('TERMINALS:',g.T)
    print('NTERMINALS:',g.NT)
    #print(g.first())



if __name__ == '__main__':
    main()
