class FieldTypes:
    string = 1
    string_list = 2
    long_string = 3
    decimal = 4
    integer = 5
    boolean = 6
    double = 7
    parameter = 8
    scpt = 9
    hex = 10
    result = 11
    switch = 12
    signed_integer = 13
    scptByte = 14
    scptShort = 15
    scptInt = 16
    scptFloat = 17
    loopStart = 18
    loopEnd = 19
    loopCondition = 20


class OverrideTypes:
    compare_value = 1
    compare_value_offset = 2


class KnownMemAddresses:
    Script_types = {'^me5.+.sct$': 'Ship_battles'}
    Ship_Battles = {'0x80310b21': 'Player HP (%)',
                    '0x80310b22': 'Enemy HP (%)',
                    '0x80310a9d': 'Battle State Control,Is 1 during turn setup',
                    '0x80310b1d': 'Battle State Control,Is 1 during attacks',
                    '0x8030e424': 'Rand(0-9999)',
                    '0x8030e4ac': 'Ship Stat'
                    }
