import os
import re

from SALSA.AKLZ.aklz import Aklz
from SALSA.Common.byte_array_utils import getString, getWord, deriveStringLength, word2Float, applyHexMask, padded_hex, \
    word2SignedInt, toInt
from SALSA.Common.constants import FieldTypes as FT
from SALSA.Scripts.script_decoder import SCTDecoder


class SCTModel:
    """Creates an object which can read in and decode *.sct files based on an instruction object"""
    path = './scripts/'

    sct_keys = {
        'Name',
        'Header',
        'Index',
        'Stats',
        'Positions',
        'Sections',
        'Footer',
        'Implemented Instructions',
        'Errors'
    }

    header_fields = {
        'misc1': {'req': True, 'type': FT.string},
        'misc2': {'req': True, 'type': FT.string},
        'Index Num': {'req': True, 'type': FT.string}
    }

    index_fields = {
        'name': {'req': True, 'type': FT.string},
        'pos': {'req': True, 'type': FT.integer},
        'length': {'req': True, 'type': FT.integer}
    }

    stats_fields = {
        'index num': {'req': True, 'type': FT.integer},
        'start pos': {'req': True, 'type': FT.integer}
    }

    position_fields = {
        'name': {'req': True, 'type': FT.string}
    }

    section_fields = {
        'type': {'req': True, 'type': FT.string_list, 'values': {'string', 'instructions'}},
        'string': {'req': True, 'type': FT.string},
        'data': {'req': True, 'type': FT.long_string}
    }

    instruction_fields = {
        'decoded': {'req': True, 'type': FT.boolean},
        'instruction': {'req': False, 'type': FT.string},
        'start location': {'req': False, 'type': FT.integer},
        'param num': {'req': False, 'type': FT.integer},
    }

    parameter_types = ['int', 'int-signed', 'int-masked', 'int-signed-masked', 'SCPT', 'override-SCPT', 'switch']

    parameter_fields = {
        'id': {'req': True, 'type': FT.integer},
        'name': {'req': True, 'type': FT.string},
        'type': {'req': True, 'type': FT.string_list, 'values': parameter_types},
        'result': {'req': True, 'type': FT.result}
    }

    error_fields = {
        'Errors': {'req': True, 'Type': FT.long_string}
    }

    indexNum = 0

    def __init__(self, path=None):
        if path is not None:
            self.path = path

    def load_sct(self, insts, file: str):
        out = self._read_sct_file(file)
        if out is None:
            return None
        name = out[0]
        sct_raw = out[1]
        sct_out = SCTDecoder.decode_sct_from_file(name=name, sct=sct_raw, inst_lib=insts)
        return name, sct_out

    def _read_sct_file(self, filepath: str):
        if '/' not in filepath:
            filename = filepath.split('.')[0]
            filepath = os.path.join(self.path, filepath)
        else:
            filename = filepath.split('/')[-1].split('.')[0]
        if os.path.exists(filepath):
            with open(filepath, 'rb') as fh:
                ba = bytearray(fh.read())
        else:
            raise FileExistsError(
                'This sct file does not exist: {}\nMay need to select the active script folder..'.format(filename))

        if Aklz.is_compressed(ba):
            ba = Aklz().decompress(ba)

        return [filename, ba]
