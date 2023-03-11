import json
import os.path
from typing import List

from SALSA.BaseInstructions.bi_container import BaseInstLib, BaseInst, locked_conversions
from SALSA.FileModels.instruction_model import InstructionModel
from SALSA.Common.constants import sep


class BaseInstLibFacade:

    def __init__(self):
        self.lib = BaseInstLib()
        self.inst_model = InstructionModel()
        self.default_inst_details = self.inst_model.load_instructions('default')
        self.set_inst_all_fields(self.default_inst_details)
        if os.path.exists('./UserSettings/user_is_default.txt'):
            self.user_inst_details = None
            self.user_identifier = 'default'
        else:
            self.user_inst_details = self.inst_model.load_instructions('user')
            self.user_identifier = 'user'
            self.set_inst_all_fields(self.user_inst_details)

    def set_inst_all_fields(self, inst_dict):
        for inst_id, inst_settings in inst_dict.items():
            if isinstance(inst_id, str):
                inst_id = int(inst_id)
            self.lib.insts[inst_id].set_inst_details(inst_settings)

    def get_inst(self, inst_id) -> BaseInst:
        return self.lib.insts[inst_id]

    def get_inst_details(self):
        return {k: v.get_user_inst_details() for k, v in enumerate(self.lib.insts)}

    def get_all_insts(self):
        return self.lib.insts

    def set_inst_detail(self, inst_id, details: dict):
        self.lib.insts[inst_id].set_inst_details(details)

    def save_user_insts(self):
        self.inst_model.save_instructions(inst_dict=self.get_inst_details(), inst_type=self.user_identifier)

    def get_tree_entries(self, headers, inst_id=None):
        if inst_id is None:
            elements = self.lib.insts
            id_key = 'inst_ID'
        else:
            elements = self.lib.insts[inst_id].parameters
            elements = [elements[k] for k in range(len(elements))]
            id_key = 'param_ID'

        tree = []
        for i, element in enumerate(elements):
            entry = {}
            element = element.__dict__
            for item in headers:
                if item == id_key:
                    entry[id_key] = i
                    continue
                if item not in element:
                    raise KeyError(f'Item not present in inst dict: {item}')
                entry[item] = element[item]
            tree.append(entry)
        return tree

    def check_locked(self, item_code: list):
        inst_id = item_code.pop(0)
        element = self.lib.insts[inst_id]
        locked_key = 'instruction'
        if len(item_code) > 1:
            param_id = item_code.pop(0)
            element = element.parameters[param_id]
            locked_key = 'parameter'
        return locked_conversions[locked_key][item_code[0]] in element.locked_fields


if __name__ == '__main__':

    base_insts = BaseInstLibFacade()
    insts: List[BaseInst] = base_insts.lib.insts
    for i in range(len(insts)):
        if insts[i].instruction_id != i:
            print(f'inst at position {i} is {insts[i].instruction_id}')

    with open('../../UserSettings/DefaultInstructions.json', 'r') as fh:
        file = fh.read()
        file_json = json.loads(file)

    base_insts.set_inst_all_fields(file_json)

    inst_deets = base_insts.get_inst_details()
    print('loaded')
