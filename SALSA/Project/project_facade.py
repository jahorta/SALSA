from typing import Union, Tuple

from Project.dictize_project import dictize_project
from Project.project_container import SCTProject, SCTSection
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from Common.setting_class import settings


class SCTProjectFacade:

    project: Union[SCTProject, None]
    log_key = 'PrjFacade'

    def __init__(self, base_insts: BaseInstLibFacade):
        self.project = None
        self.callbacks = {}
        self.base_insts = base_insts
        if self.log_key not in settings.keys():
            settings[self.log_key] = {}

    def load_project(self, prj, pickled=False):
        if pickled:
            self.project = prj
            return
        self.project = SCTProject.from_dict(prj)

    def create_new_project(self):
        self.project = SCTProject()

    def set_filepath(self, filepath):
        if filepath == '' or filepath is None:
            return
        self.project.filepath = filepath

    def get_filepath(self):
        return self.project.filepath

    def get_tree(self, headers: Tuple[str], script=None, section=None, style='grouped'):
        if self.project is None:
            return
        if script is None:
            scripts = self.project.scripts
            tree_list = self._create_tree(group=scripts, key_list=list(scripts.keys()), headers=headers)
        elif section is None:
            section_list = self.project.scripts[script].get_sect_list(style)
            sections = self.project.scripts[script].sections
            tree_list = self._create_tree(group=sections, key_list=section_list, headers=headers)
        else:
            inst_list = self.project.scripts[script].sections[section].get_inst_list(style)
            instructions = self.project.scripts[script].sections[section].instructions
            tree_list = self._create_tree(group=instructions, key_list=inst_list, headers=headers, base=self.base_insts.get_all_insts(), base_key='instruction_id')

        return tree_list

    def _create_tree(self, group, key_list, headers, base=None, base_key=None, key_only=False):
        tree_list = []
        for key in key_list:
            if isinstance(key, dict):
                for ele_key, ele_value in key.items():
                    if '-' not in ele_key:
                        tree_list.extend(self._create_tree(group=group, key_list=[ele_key], headers=headers, base=base, base_key=base_key, key_only=True))
                        tree_list[-1]['group_type'] = 'element'
                    else:
                        ele_key = ele_key.split('-')
                        tree_list.extend(self._create_tree(group=group, key_list=[ele_key[0]], headers=headers, base=base, base_key=base_key))
                        tree_list[-1]['group_type'] = ele_key[1]
                    tree_list.append('group')
                    ele_value = [ele_value] if not isinstance(ele_value, list) else ele_value
                    tree_list.extend(self._create_tree(group=group, key_list=ele_value, headers=headers, base=base, base_key=base_key))
                    tree_list.append('ungroup')
                continue

            if key_only:
                values = {'row_data': key}
                first = True
                for header in headers:
                    if first:
                        values[header] = key
                        first = False
                        continue
                    values[header] = ''
                tree_list.append(values)

            else:
                element = group[key]
                if isinstance(element, SCTSection):
                    if element.type == 'String':
                        continue
                element_dict = element.__dict__
                values = {'row_data': key}
                for header_key in headers:
                    value_dict = element_dict
                    if header_key not in element_dict:
                        if base is None or base_key is None:
                            raise KeyError(f'PrjFacade: {header_key} not in {element}, no base_element_group or base_key given')
                        base_inst_key = element_dict[base_key]
                        base_dict = base[base_inst_key].__dict__
                        if header_key not in base_dict:
                            raise KeyError(f'PrjFacade: {header_key} not in {element} or {base[base_key]}')
                        value_dict = base_dict
                    values[header_key] = value_dict[header_key] if isinstance(value_dict[header_key], str) else str(value_dict[header_key])
                tree_list.append(values)
        return tree_list

    def get_instruction_details(self, script, section, instruction, **kwargs):
        try:
            instruction = self.project.scripts[script].sections[section].instructions[instruction]
        except KeyError as e:
            print(self.log_key, e)
            return None
        instruction_details = self.base_insts.get_inst(instruction.instruction_id).__dict__
        instruction_details['base_parameters'] = instruction_details['parameters']
        for key, value in instruction.__dict__.items():
            instruction_details[key] = value
        # format description
        return instruction_details

    def get_parameter_details(self, script, section, instruction, parameter):
        try:
            if '-' in parameter:
                loop = int(parameter.split('-')[0])
                param = int(parameter.split('-')[1])
                parameter = self.project.scripts[script].sections[section].instructions[instruction].loop_parameters[loop][param]
            else:
                parameter = self.project.scripts[script].sections[section].instructions[instruction].parameters[int(parameter)]

        except KeyError as e:
            print(self.log_key, e)
            return None

    def get_link_details(self, link):
        pass

    def remove_element_from_group(self, script, element, group, section=None):
        if section is None:
            pass
        else:
            pass

    def add_element_to_group(self, script, element, group, section=None):
        if section is None:
            pass
        else:
            pass

    def rearrange_list(self, script, order_list, section=None):
        if section is None:
            pass
        else:
            pass

    def get_cur_project_dict(self):
        project = dictize_project(self.project)
        return project

    def add_script_to_project(self, script_name, script):
        self.project.scripts[script_name] = script
        script_keys = sorted(list(self.project.scripts.keys()), key=str.casefold)
        self.project.scripts = {k: self.project.scripts[k] for k in script_keys}
        if 'update_scripts' not in self.callbacks:
            return
        self.callbacks['update_scripts']()

    def set_callback(self, key, callback):
        self.callbacks[key] = callback

    def get_project_script_by_index(self, index):
        if index >= len(self.project.scripts.keys()):
            print(f'{self.log_key}: Script index out of range: {index} : {len(self.project.scripts.keys())-1}')
            return None
        name = list(self.project.scripts.keys())[index]
        return name, self.project.scripts[name]

    def get_project_script_by_name(self, name):
        if name not in self.project.scripts.keys():
            print(f'{self.log_key}: No script loaded with the name: {name}')
            return None
        return self.project.scripts[name]

    def get_script_variables_with_aliases(self, script):
        var_dict = {}
        for var_type, var_list in self.project.scripts[script].variables.items():
            var_dict[var_type] = {}
            var_order = sorted(list(var_list.keys()))
            for key in var_order:
                var_dict[var_type][key] = var_list[key]['alias']
        return var_dict

    def set_variable_alias(self, script, var_type, var_id, alias):
        self.project.scripts[script].variables[var_type][var_id]['alias'] = alias

    def get_variable_usages(self, script, var_type, var_id):
        return self.project.scripts[script].variables[var_type][var_id]['usage']
