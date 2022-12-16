import json
import os

from SALSA.Tools.constants import FieldTypes as FT
from SALSA.Tools.constants import OverrideTypes as OT


class InstructionModel:
    fields = {
        'Instruction ID': {'req': True, 'type': FT.integer, 'min': 0, 'max': 270},
        'Name': {'req': True, 'type': FT.string},
        'Location': {'req': True, 'type': FT.hex, 'pattern': '^0x80[0-9,a-f]{6}$'},
        'Hard parameter one': {'req': True, 'type': FT.hex},
        'Hard parameter two': {'req': True, 'type': FT.hex},
        'Description': {'req': False, 'type': FT.long_string},
        'Parameter num': {'req': True, 'type': FT.integer, 'min': 0, 'max': 1000},
        'Parameters': {'req': False, 'type': FT.parameter},
        'Implement': {'req': True, 'type': FT.boolean},
        'Notes': {'req': True, 'type': FT.long_string}
    }

    def __init__(self):

        self.filename = "./Lib/Instructions.json"
        self.parameter_model = ParameterModel()
        self.instructions = self.load_instructions()

    def load_instructions(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as fh:
                inst = {}
                for i in range(0, 266):
                    inst[str(i)] = {'Instruction ID': str(i), 'Name': 'no name', 'Location': '0x80xxxxxx',
                                    'Hard parameter one': '0x00000000', 'Hard parameter two': '0x00000000',
                                    'Parameter num': 0, 'Parameters': {}, 'Implement': False, 'Notes': ''}
                fh.write(json.dumps(inst))

        with open(self.filename, 'r') as fh:
            instructions = json.loads(fh.read())

        return instructions

    def save_instructions(self, inst_dict):
        """Function to save instructions to file"""
        print("saving to file")

        with open(self.filename, 'w') as fh:
            fh.write(json.dumps(inst_dict, indent=2))


class ParameterModel:

    parameterTypes = {
        FT.integer: 'int',
        FT.scptByte: 'scpt-byte',
        FT.scptShort: 'scpt-short',
        FT.scptInt: 'scpt-int',
        FT.scptFloat: 'scpt-float',
        FT.scptSkip: 'scpt-skip',
        FT.switch: 'switch',
        FT.string: 'string'
    }

    overrideConditions = {
        OT.compare_value: 'compare-value-current',
        OT.compare_value_offset: 'compare-value-offset'
    }

    base_fields = {
        'paramID': {'req': True, 'type': FT.integer},
        'Name': {'req': False, 'type': FT.string},
        'Parameter type': {'req': True, 'type': FT.string_list, 'values': list(parameterTypes.values())},
    }

    value_fields = {
        'Mask': {'req': True, 'type': FT.hex},
        'Signed': {'req': True, 'type': FT.boolean}
    }