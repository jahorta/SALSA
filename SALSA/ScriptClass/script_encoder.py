

class ScriptEncoder:
    compare_codes = {
        '0x00000000': '(1)<(2)',
        '0x00000001': '(1)<=(2)',
        '0x00000002': '(1)>(2)',
        '0x00000003': '(1)>=(2)',
        '0x00000004': '(1)==(2)',
        '0x00000005': '(1)==(2)[5]',
        '0x00000006': '(1)&(2)',
        '0x00000007': '(1)|(2)',
        '0x00000008': '(1)!=0 and (2)!=0',
        '0x00000009': '(1)!=0 or (2)!=0',
        '0x0000000a': 'overwrites (1) with (2)',
    }

    arithmetic_codes = {
        '0x0000000b': '(1)*(2)',
        '0x0000000c': '(1)/(2)',
        '0x0000000d': '(1)%(2)',
        '0x0000000e': '(1)+(2)',
        '0x0000000f': '(1)-(2)',
    }

    noLoop = [
        # Special: returns first value, doesn't enter scpt loop
        '0x7f7fffff',
        '0x00800000',
        '0x7fffffff'
    ]

    input_cutoffs = {
        '0x50000000': 'Word: *add[0x8030e3e4,',
        '0x40000000': 'Word: *add[0x803e514,',
        '0x20000000': 'starting from 80310b3c, Bit: ',
        '0x10000000': 'Byte: *add[0x80310a1c,',
        '0x08000000': 'decimal: ',
        '0x04000000': 'float: ',
    }

    """Specific secondary code checks: code <= 0x07, code < 0x21, code == 0x4a"""
    secondary_codes = {
        '0x00000000': 'gold amt',
        '0x00000001': 'Reputation',
        '0x00000002': 'Vyse.curHP',
        '0x00000003': 'Aika.curHP',
        '0x00000004': 'Fina.curHP',
        '0x00000005': 'Drachma.curHP',
        '0x00000006': 'Enrique.curHP',
        '0x00000007': 'Gilder.curHP',
        '0x0000004a': 'Vyse.lvl'
    }

    @classmethod
    def construct_param(cls, param_type, param_dict):
        out = bytearray(b'')
        return out