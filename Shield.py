def evaluate(operand, a, b):
    if operand:
        return a
    else:
        return b

def inv_evaluate(operand, a, b):
    if operand:
        return not a
    else:
        return not b 


class Shield(object):
    def __init__(self):
        self.s0 = False;
        self.s1 = False;
        self.s2 = False;
        self.s3 = False;
        self.s4 = False;
        self.s5 = False;
        self.s6 = False;
        self.s7 = False;
        self.s8 = False;
        self.s9 = False;
    def move(self,h, u1, l1, l2, l3, l4):
        l1__1 = False;

        l2__1 = False;

        l3__1 = False;

        l4__1 = False;

        self.s9 = False;

        self.s8 = False;

        self.s7 = False;

        self.s6 = False;

        self.s5 = False;

        self.s4 = False;

        self.s3 = False;

        self.s2 = False;

        self.s1 = False;

        self.s0 = False;

        return (l1__1, l2__1, l3__1, l4__1)