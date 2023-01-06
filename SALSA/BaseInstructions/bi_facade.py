import json
import os.path
from typing import List

from BaseInstructions.bi_container import BaseInstLib, BaseInst

from FileModels.instruction_model import InstructionModel


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
        return {k: v.get_inst_details() for k, v in enumerate(self.lib.insts)}

    def get_all_insts(self):
        return self.lib.insts

    def set_inst_detail(self, inst_id, details: dict):
        self.lib.insts[inst_id].set_inst_details(details)

    def save_user_insts(self):
        self.inst_model.save_instructions()


if __name__ == '__main__':

    base_insts = BaseInstLibFacade()
    insts: List[BaseInst] = base_insts.insts
    for i in range(len(insts)):
        if insts[i].instruction_id != i:
            print(f'inst at position {i} is {insts[i].instruction_id}')

    with open('../../UserSettings/DefaultInstructions.json', 'r') as fh:
        file = fh.read()
        file_json = json.loads(file)

    base_insts.set_inst_all_fields(file_json)

    inst_deets = base_insts.get_inst_details()
    print('loaded')
