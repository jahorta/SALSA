from typing import List
import json
from SALSA.BaseInstructions.bi_defaults import inst_defaults


class BaseParam:

    def __init__(self, param_id, param_dict, default_name, link_type=None):

        self.locked_fields = [k for k in param_dict.keys()]
        self.paramID = param_id
        self.name = param_dict.get('Name', default_name)
        self.type = param_dict['Type']
        self.default_value = param_dict.get('Default', None)
        self.mask = param_dict.get('Mask', None)
        self.isSigned = param_dict.get('Signed', None)
        self.link_type = link_type

        # # Use for finding unused keys in instruct defaults
        # for key in param_dict.keys():
        #     if key not in ['Name', 'Type', 'Default', 'Mask', 'Signed']:
        #         print('Extra parameter field present...')

    def set_parameter_details(self, param_details):

        if 'Name' not in self.locked_fields:
            self.name = param_details.get('Name', self.name)
        if 'Mask' not in self.locked_fields:
            if 'Mask' in param_details.keys():
                if isinstance(param_details['Mask'], bool):
                    if 'Mask Value' in param_details.keys() and param_details['Mask']:
                        temp_mask = param_details.get('Mask Value')
                        self.mask = int(temp_mask, 16) if isinstance(temp_mask, str) else temp_mask
                else:
                    self.mask = param_details.get('Mask', self.mask)
        if 'Signed' not in self.locked_fields:
            self.isSigned = param_details.get('Signed', self.isSigned)
        if 'Default' not in self.locked_fields and self.type != 'int':
            self.default_value = param_details.get('Default', self.default_value)

    def get_fields(self):
        fields = {}
        if 'Name' not in self.locked_fields:
            fields['Name'] = self.name
        if 'Signed' not in self.locked_fields:
            fields['Signed'] = self.isSigned
        if 'Mask' not in self.locked_fields and self.mask is not None:
            fields['Mask'] = self.mask
        if 'Default' not in self.locked_fields and self.default_value is not None:
            fields['Default'] = self.default_value
        return fields


class BaseInst:

    def __init__(self, inst_id, inst_values):

        self.locked_fields = [k for k in inst_values.keys() if k != 'Parameters']
        self.instruction_id = inst_id
        self.name = inst_values.get('Name', f'Inst{inst_id}')
        self.description = inst_values.get('Description', '\n')
        self.location = inst_values['Location']
        self.no_new_frame = inst_values['Skip Frame Refresh']
        self.forced_new_frame = inst_values['Force Frame Refresh'] if self.no_new_frame == 0 else False

        self.link = inst_values.get('Link', None)
        self.link_type = inst_values.get('Link Type', None)

        self.param2 = inst_values['Hard parameter two']
        self.notes = inst_values.get('Notes', '\n')
        self.parameters = {}
        for key, param in inst_values['Parameters'].items():
            link_type = None
            if self.link is not None:
                if self.link == key:
                    link_type = self.link_type
            self.parameters[key] = BaseParam(param_id=key, param_dict=param, default_name=f'Unknown{key}', link_type=link_type)

        self.loop = inst_values.get('Loop', None)
        self.loop_iter = inst_values.get('Loop Iterations', None)
        self.loop_cond = inst_values.get('Loop Break Condition', None)

        self.params_before = list(self.parameters.keys()) if self.loop is None else []
        self.params_after = []
        hit_loop = False
        if self.loop is not None:
            for p in list(self.parameters.keys()):
                if p in self.loop:
                    hit_loop = True
                    continue
                if hit_loop:
                    self.params_after.append(p)
                else:
                    self.params_before.append(p)

        self.warning = inst_values.get('Warning', None)

    def get_all(self):
        all_fields = {'Name': self.name, 'Description': self.description, 'Notes': self.notes}
        param = {}
        currParam = 0
        for key, value in self.parameters.items():
            param[key] = value.get_fields()
            currParam += 1

        all_fields['Parameters'] = param

        return all_fields

    def set_inst_details(self, updated_details):
        if 'Name' not in self.locked_fields:
            self.name = updated_details.get('Name', self.name)
        if 'Description' not in self.locked_fields:
            self.description = updated_details.get('Description', self.description)
        self.notes = updated_details.get('Notes', self.notes)
        if 'Parameters' in updated_details.keys():
            loop_count = 0
            for key, param_details in updated_details['Parameters'].items():
                if isinstance(key, str):
                    key = int(key)
                if 'loop' in param_details['Type']:
                    loop_count += 1
                else:
                    self.parameters[key-loop_count].set_parameter_details(param_details=param_details)

    def get_inst_details(self):
        fields = {}
        if 'Name' not in self.locked_fields:
            fields['Name'] = self.name
        if 'Description' not in self.locked_fields:
            fields['Description'] = self.description
        fields['Notes'] = self.notes
        params = {}
        for key, param in self.parameters.items():
            p_dict = param.get_fields()
            if len(p_dict) > 0:
                params[key] = p_dict
        if len(params) > 0:
            fields['Parameters'] = params
        return fields

    def get_param_names(self, param_list):
        names = {}
        for param in self.parameters.values():
            if int(param.paramID) in param_list:
                names[int(param.paramID)] = param.name
        return names

    def __repr__(self):
        return f'INST({self.instruction_id}: pos:{self.location}'


class BaseInstLib:
    """Takes in a dictionary containing instruction information and produces an object containing
        the necessary information to decode *.sct files"""

    def __init__(self):
        self.insts = [BaseInst(k, v) for k, v in inst_defaults.items()]
        insts_with_a_parameter = [_ for _ in self.insts if len(_.parameters) > 0]
        self.p1_scpt = [_.instruction_id for _ in insts_with_a_parameter if 'scpt' in _.parameters[0].type]
        self.p1_int = [_.instruction_id for _ in insts_with_a_parameter if 'int' in _.parameters[0].type]


if __name__ == '__main__':

    base_insts = BaseInstLib()
    insts: List[BaseInst] = base_insts.insts
    for i in range(len(insts)):
        if insts[i].instruction_id != i:
            print(f'inst at position {i} is {insts[i].instruction_id}')
