from typing import List
import json
from SALSA.InstructionClasses.instruct_defaults import inst_defaults


class Parameter2:

    def __init__(self, param_id, param_dict, default_name):

        self.locked_fields = [k for k in param_dict.keys()]
        self.paramID = param_id
        self.name = param_dict.get('Name', default_name)
        self.type = param_dict['Type']
        self.default_value = param_dict.get('Default', None)
        self.mask = param_dict.get('Mask', None)
        self.isSigned = param_dict.get('Signed', None)

        # # Use for finding unused keys in instruct defaults
        # for key in param_dict.keys():
        #     if key not in ['Name', 'Type', 'Default', 'Mask', 'Signed']:
        #         print('Extra parameter field present...')

    def set_parameter_details(self, param_details):

        if 'Name' not in self.locked_fields:
            self.name = param_details.get('Name', self.name)
        if 'Mask' not in self.locked_fields:
            if 'Mask Value' in param_details.keys():
                self.mask = param_details.get('Mask Value')
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


class Instruct2:

    def __init__(self, inst_id, inst_values):

        self.locked_fields = [k for k in inst_values.keys() if k != 'Parameters']
        self.instID = inst_id
        self.name = inst_values.get('Name', f'Inst{inst_id}')
        self.description = inst_values.get('Description', '\n')
        self.location = inst_values['Location']
        self.no_new_frame = inst_values['Skip Frame Refresh']
        if self.no_new_frame == 0:
            self.forced_new_frame = inst_values['Force Frame Refresh']
        self.param2 = inst_values['Hard parameter two']
        self.notes = inst_values.get('Notes', '\n')
        self.parameters = {}
        for key, param in inst_values['Parameters'].items():
            self.parameters[key] = Parameter2(key, param, f'Unknown{key}')

        self.link = inst_values.get('Link', None)
        self.link_type = inst_values.get('Link Type', None)

        self.loop = inst_values.get('Loop', None)
        self.loop_iter = inst_values.get('Loop Iterations', None)
        self.loop_cond = inst_values.get('Loop Condition', None)

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


class InstLib:
    """Takes in a dictionary containing instruction information and produces an object containing
        the necessary information to decode *.sct files"""

    def __init__(self):
        self.insts = [Instruct2(k, v) for k, v in inst_defaults.items()]

    def get_inst(self, inst_id) -> Instruct2:
        return self.insts[inst_id]

    def get_inst_details(self):
        return {k: v.get_inst_details() for k, v in enumerate(self.insts)}

    def set_inst_fields(self, inst_dict):
        for inst_id, inst_settings in inst_dict.items():
            if isinstance(inst_id, str):
                inst_id = int(inst_id)
            self.insts[inst_id].set_inst_details(inst_settings)


if __name__ == '__main__':
    inst_lib = InstLib()
    insts: List[Instruct2] = inst_lib.insts
    for i in range(len(insts)):
        if insts[i].instID != i:
            print(f'inst at position {i} is {insts[i].instID}')

    with open('./../../Lib/Instructions.json', 'r') as fh:
        file = fh.read()
        file_json = json.loads(file)

    inst_lib.set_inst_fields(file_json)

    inst_deets = inst_lib.get_inst_details()
    print('loaded')
