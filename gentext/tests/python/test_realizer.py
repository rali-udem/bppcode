import unittest
from gentext.realizer import JSRealBRealizer


class TestRealizer(unittest.TestCase):
    def test_single(self):
        real = JSRealBRealizer('en')
        self.assertEquals(real.realize(['S(CP(C("but"), S(NP(Pro("I").pe(1)), VP(V("be"), AdvP(Adv("not")), NP(D("a"), N("specialist")))), S(NP(Pro("I").pe(1)), VP(V("assume"), SP(C("that"), S(NP(D("my").pe(2), AP(A("previous")), N("work")), PP(P("as"), NP(N("CFO"))), VP(V("teach").perf(true), NP(Pro("I").pe(2)), AdvP(Adv("much")), PP(P("about"), NP(N("Strategic Planning"))))))))))']),
                          'I am not a specialist but I assume that your previous work as CFO has taught you much about Strategic Planning.\n')
        

    def test_with_newline(self):
        real = JSRealBRealizer('en')
        self.assertEquals(real.realize(
            ['S(CP(C("but"), S(NP(Pro("I").pe(1)), VP(V("be"), AdvP(Adv("not")), NP(D("a"), N("specialist")))), S(NP(Pro("I").pe(1)), VP(V("assume"), SP(C("that"), S(NP(D("my").pe(2), AP(A("previous")), N("work")), PP(P("as"), NP(N("CFO"))), VP(V("teach").perf(true), NP(Pro("I").pe(2)), AdvP(Adv("much")), PP(P("about"), NP(N("Strategic Planning"))))))))))',
             '#NEWLINE',
             'S(CP(C("but"), S(NP(Pro("I").pe(1)), VP(V("be"), AdvP(Adv("not")), NP(D("a"), N("specialist")))), S(NP(Pro("I").pe(1)), VP(V("assume"), SP(C("that"), S(NP(D("my").pe(2), AP(A("previous")), N("work")), PP(P("as"), NP(N("CFO"))), VP(V("teach").perf(true), NP(Pro("I").pe(2)), AdvP(Adv("much")), PP(P("about"), NP(N("Guerra"))))))))))'
             ]),
            'I am not a specialist but I assume that your previous work as CFO has taught you much about Strategic Planning.\nI am not a specialist but I assume that your previous work as CFO has taught you much about Guerra.\n')
        