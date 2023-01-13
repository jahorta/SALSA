compare = [
    (0x00000000, '(1)<(2)'),
    (0x00000001, '(1)<=(2)'),
    (0x00000002, '(1)>(2)'),
    (0x00000003, '(1)>=(2)'),
    (0x00000004, '(1)==(2)'),
    (0x00000005, '(1)==(2)[5]'),
    (0x00000010, '(1)&(2)'),
    (0x00000006, '(1)&(2)'),  # Same as 6
    (0x00000011, '(1)|(2)'),
    (0x00000007, '(1)|(2)'),  # Same as 7
    (0x00000008, '(1)!=0 and (2)!=0'),
    (0x00000009, '(1)!=0 or (2)!=0'),
    (0x0000000a, 'overwrites (1) with (2)'),
]

arithmetic = [
    (0x00000012, '(1)*(2)'),
    (0x0000000b, '(1)*(2)'),  # Same as 12
    (0x00000013, '(1)/(2)'),
    (0x0000000c, '(1)/(2)'),  # Same as 13
    (0x00000014, '(1)%(2)'),
    (0x0000000d, '(1)%(2)'),  # Same as 14
    (0x00000015, '(1)+(2)'),
    (0x0000000e, '(1)+(2)'),  # Same as 15
    (0x00000016, '(1)-(2)'),
    (0x0000000f, '(1)-(2)'),  # Same as 16
]

no_loop = [
    # Special: returns first value, doesn't enter scpt loop
    (0x7f7fffff, '0x7f7fffff'),
    (0x00800000, '0x00800000'),
    (0x7fffffff, '0x7fffffff')
]

input_cutoffs = [
    (0x50000000, 'IntVar: '),
    (0x40000000, 'FloatVar: '),
    (0x20000000, 'BitVar: '),
    (0x10000000, 'ByteVar: '),
    (0x08000000, 'decimal: '),
    (0x04000000, 'float: '),
]

"""Specific secondary code checks: code <= 0x07, code < 0x21, code == 0x4a"""
secondary = [
    (0x00000000, 'Gold'),
    (0x00000001, 'Reputation'),
    (0x00000002, 'Vyse.curHP'),
    (0x00000003, 'Aika.curHP'),
    (0x00000004, 'Fina.curHP'),
    (0x00000005, 'Drachma.curHP'),
    (0x00000006, 'Enrique.curHP'),
    (0x00000007, 'Gilder.curHP'),
    (0x0000004a, 'Vyse.lvl')
]


class SCPTParamCodes:

    def __init__(self, is_decoder=True):
        if is_decoder:
            self.compare = {_[0]: _[1] for _ in compare}
            self.arithmetic = {_[0]: _[1] for _ in arithmetic}
            self.input_cutoffs = {_[0]: _[1] for _ in input_cutoffs}
            self.secondary = {_[0]: _[1] for _ in secondary}
            self.cutoff_prefixes = [(_ & 0xff000000) for _ in list(self.input_cutoffs.keys())]
            self.no_loop = {_[0]: _[1] for _ in no_loop}
        else:
            self.compare = {_[1]: _[0] for _ in compare}
            self.arithmetic = {_[1]: _[0] for _ in arithmetic}
            self.input_cutoffs = {_[1]: _[0] for _ in input_cutoffs}
            self.secondary = {_[1]: _[0] for _ in secondary}
            self.no_loop = {_[1]: _[0] for _ in no_loop}
        self.primary_keys = [*list(self.compare.keys()), *list(self.arithmetic.keys())]
        self.stop_code = stop_code

