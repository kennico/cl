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
        return '%s->%s' % (str(self.head), ''.join([str(s) for s in self.body]))

    def __repr__(self):
        return self.__str__()


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

    def __contains__(self, s):
        return s in self.T or s in self.NT

    def get_productions(self, s):
        if s not in self.NT:
            raise ValueError('"%s" is not a non-terminal.')
        return self.NT[s].productions

    def first(self):
        result = {s:{t} for s, t in self.T.items()}

        def recur(s):
            if s in result:
                return result[s]

            result[s] = set()
            for prod in self.NT[s].productions:
                for sym in prod.body:
                    sub = recur(str(sym))
                    result[s] |= sub
                    if self.EPSILON not in sub:
                        break
            return result[s]

        for s, nt in self.NT.items():
            recur(s)

        return result

    def follow(self):
        pass

    def nterminals(self):
        return self.NT.values()

    def terminals(self):
        return self.T.values()

    def productions(self):
        return itertools.chain(*[nt.productions for nt in self.nterminals()])


class GrammarBuilder(object):
    def build(self, filename):
        raw_productions = {}
        with open(filename) as f:
            start = f.readline().strip()
            epsilon = f.readline().strip()
            for l in f:
                nts, *prods = l.split()
                if nts not in raw_productions:
                    raw_productions[nts] = []
                raw_productions[nts] += prods

        self.raw_productions = raw_productions
        self.tempd = {}
        start = self.handle(start)

        g = Grammar()
        g.START = start
        g.EPSILON = epsilon
        g.NT = {s:obj for s, obj in self.tempd.items() if s in self.raw_productions}
        g.T = {s:obj for s, obj in self.tempd.items() if s not in self.raw_productions}
        return g

    def handle(self, s):
        if s not in self.tempd:
            if s in self.raw_productions:
                nt = self.tempd[s] = NTerminal(s)
                for prods in self.raw_productions[s]:
                    nt.add_production(*[self.handle(c) for c in prods])
            else:
                self.tempd[s] = Terminal(s)
        return self.tempd[s]


def main():
    g = GrammarBuilder().build('grammar.txt')
    print(g.START)
    print(g.terminals())
    print(g.nterminals())
    print(g.T)
    print(g.NT)
    print(g.EPSILON)
    print(list(g.productions()))
    print(g.first())



if __name__ == '__main__':
    main()
