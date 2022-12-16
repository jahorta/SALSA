import json
from typing import List

from BaseInstructions.base_instruction_container import BaseInstLib, BaseInst


class BaseInstLibFacade:

    def __init__(self):
        self.lib = BaseInstLib()

    def set_inst_all_fields(self, inst_dict):
        for inst_id, inst_settings in inst_dict.items():
            if isinstance(inst_id, str):
                inst_id = int(inst_id)
            self.lib.insts[inst_id].set_inst_details(inst_settings)

    def get_inst(self, inst_id) -> BaseInst:
        return self.lib.insts[inst_id]

    def get_inst_details(self):
        return {k: v.get_inst_details() for k, v in enumerate(self.lib.insts)}


if __name__ == '__main__':

    base_insts = BaseInstLibFacade()
    insts: List[BaseInst] = base_insts.insts
    for i in range(len(insts)):
        if insts[i].instID != i:
            print(f'inst at position {i} is {insts[i].instID}')

    with open('./../../Lib/Instructions.json', 'r') as fh:
        file = fh.read()
        file_json = json.loads(file)

    base_insts.set_inst_all_fields(file_json)

    inst_deets = base_insts.get_inst_details()
    print('loaded')
