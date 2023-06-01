import copy
from typing import Union, Tuple

from SALSA.Project.description_formatting import format_description
from SALSA.Project.project_container import SCTProject, SCTSection, SCTParameter, SCTInstruction, SCTLink
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Common.setting_class import settings
from SALSA.Common.constants import sep, alt_sep, alt_alt_sep
from SALSA.Scripts.scpt_param_codes import get_scpt_override


class SCTProjectFacade:
    project: Union[SCTProject, None]
    log_key = 'PrjFacade'

    def __init__(self, base_insts: BaseInstLibFacade):
        self.project = None
        self.callbacks = {}
        self.base_insts = base_insts
        if self.log_key not in settings.keys():
            settings[self.log_key] = {}

    def load_project(self, prj: SCTProject):
        new_project = SCTProject()
        if prj.version == new_project.version:
            self.project = prj
            return

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
            self._refresh_inst_positions(script=script, section=section)
            inst_list = self.project.scripts[script].sections[section].get_inst_list(style)
            instructions = self.project.scripts[script].sections[section].instructions
            tree_list = self._create_tree(group=instructions, key_list=inst_list, headers=headers,
                                          base=self.base_insts.get_all_insts(), base_key='instruction_id')

        return tree_list

    def _create_tree(self, group, key_list, headers, base=None, base_key=None, key_only=False, prev_group_type=None):
        tree_list = []
        for key in key_list:
            if isinstance(key, dict):
                for ele_key, ele_value in key.items():
                    if sep not in ele_key:
                        tree_list.extend(self._create_tree(group=group, key_list=[ele_key], headers=headers, base=base,
                                                           base_key=base_key, key_only=True))
                        if prev_group_type == 'switch':
                            cur_group_type = 'case'
                        else:
                            cur_group_type = 'element'
                        tree_list[-1]['group_type'] = cur_group_type
                    else:
                        ele_key = ele_key.split(sep)
                        tree_list.extend(
                            self._create_tree(group=group, key_list=[ele_key[0]], headers=headers, base=base,
                                              base_key=base_key, prev_group_type=ele_key[1]))
                        tree_list[-1]['group_type'] = ele_key[1]
                    tree_list.append('group')
                    ele_value = [ele_value] if not isinstance(ele_value, list) else ele_value
                    cur_group_type = ele_key[1] if len(ele_key) > 1 else ''
                    tree_list.extend(self._create_tree(group=group, key_list=ele_value, headers=headers, base=base,
                                                       base_key=base_key, prev_group_type=cur_group_type))
                    tree_list.append('ungroup')
                continue

            if key_only:
                values = {'row_data': None}
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
                            raise KeyError(
                                f'PrjFacade: {header_key} not in {element}, no base_element_group or base_key given')

                        base_inst_key = element_dict[base_key]
                        if base_inst_key is None:
                            base_dict = {header_key: '---'}
                        else:
                            base_dict = base[base_inst_key].__dict__

                        if header_key not in base_dict:
                            raise KeyError(f'PrjFacade: {header_key} not in {element} or {base[base_key]}')
                        value_dict = base_dict
                    values[header_key] = value_dict[header_key] if isinstance(value_dict[header_key], str) else str(
                        value_dict[header_key])
                tree_list.append(values)
        return tree_list

    def get_parameter_tree(self, script, section, instruction, headings, **kwargs):
        inst = self.project.scripts[script].sections[section].instructions[instruction]
        base_inst = self.base_insts.get_inst(inst.instruction_id)

        tree = self._create_tree(inst.parameters, base_inst.params_before, headings, base=base_inst.parameters,
                                 base_key='ID')

        for param in base_inst.params_before:
            if inst.parameters[param].link is None:
                continue
            link_type = inst.parameters[param].link_value[0]
            if link_type == 'Footer':
                tree[param]['type'] = 'Footer Entry'
                tree[param]['value'] = inst.parameters[param].link_result
            elif link_type == 'SCT':
                tree[param]['type'] = 'Jump'
                sect = inst.parameters[param].link_value[1].split(f'{sep}')[0]
                target_inst = self.project.scripts[script].sections[sect].instructions[
                    inst.parameters[param].link_value[1].split(f'{sep}')[1]]
                tree[param]['value'] = f'{sect} - {target_inst.ungrouped_position} ' \
                                       f'{self.base_insts.get_inst(target_inst.instruction_id).name}'
            elif link_type == 'String':
                tree[param]['type'] = 'String'
                tree[param]['value'] = inst.parameters[param].link_result

        if base_inst.loop is None:
            return tree

        for loop, params in enumerate(inst.loop_parameters):
            temp_tree = self._create_tree(params, [f'loop{loop}'], headings, key_only=True)
            temp_tree += ['group']
            loop_items = self._create_tree(params, base_inst.loop, headings, base=base_inst.parameters, base_key='ID')
            for item in loop_items:
                if 'row_data' not in item:
                    continue
                item['row_data'] = f'{loop}{sep}{item["row_data"]}'
            temp_tree += loop_items
            temp_tree += ['ungroup']
            tree += temp_tree

        tree += self._create_tree(inst.parameters, base_inst.params_after, headings, base=base_inst.parameters,
                                  base_key='ID')

        return tree

    def get_instruction_details(self, script, section, instruction, **kwargs):
        try:
            instruction = self.project.scripts[script].sections[section].instructions[instruction]
        except KeyError as e:
            print(self.log_key, e)
            return None
        if instruction.instruction_id is None:
            return None
        base_inst = self.base_insts.get_inst(instruction.instruction_id)
        instruction_details = copy.deepcopy(base_inst.__dict__)
        instruction_details['base_parameters'] = instruction_details['parameters']
        for key, value in instruction.__dict__.items():
            instruction_details[key] = value
        instruction_details['description'] = format_description(inst=instruction, base_inst=base_inst)
        return instruction_details

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
            print(f'{self.log_key}: Script index out of range: {index} : {len(self.project.scripts.keys()) - 1}')
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

    def get_inst_ind(self, script, section, inst):
        return self.project.scripts[script].sections[section].instruction_ids_ungrouped.index(inst)

    def _refresh_inst_positions(self, script, section):
        section = self.project.scripts[script].sections[section]
        for i, inst_id in enumerate(section.instruction_ids_ungrouped):
            section.instructions[inst_id].ungrouped_position = i

    def get_parameter(self, script, section, instruction, parameter):
        instruction = self.project.scripts[script].sections[section].instructions[instruction]
        if parameter == 'delay':
            return instruction.frame_delay_param
        if sep in parameter:
            param_parts = parameter.split(sep)
            return instruction.loop_parameters[int(param_parts[0])][int(param_parts[1])]
        return instruction.parameters[int(parameter)]

    def get_inst_id(self, script, section, instruction, **kwargs):
        return self.project.scripts[script].sections[section].instructions[instruction].instruction_id

    def get_inst_id_name(self, inst_id):
        return self.base_insts.get_inst(inst_id).name

    def get_base_parameter(self, inst_id, param_str):
        if param_str == 'delay':
            return self.base_insts.get_inst(129).parameters[0]
        param_parts = param_str.split(sep)
        b_param_id = param_parts[-1]
        return self.base_insts.get_inst(inst_id).parameters[int(b_param_id)]

    def add_delay_parameter(self, script, section, instruction, **kwargs):
        param = SCTParameter(_id=-1, _type='scpt-int')
        self.project.scripts[script].sections[section].instructions[instruction].frame_delay_param = param
        return param

    def get_var_alias(self, script, var_type, var_id):
        if var_id not in self.project.scripts[script].variables[var_type]:
            return 'No Alias'
        return self.project.scripts[script].variables[var_type][var_id]['alias']

    def update_var_usage(self, changes, script, section, instruction, parameter):
        trace = (section, instruction, parameter)

        for change in changes['add']:
            var_parts = change.split(': ')
            var_type = var_parts[0]
            var_key = int(var_parts[1])
            if var_key in self.project.scripts[script].variables[var_type]:
                self.project.scripts[script].variables[var_type][var_key]['usage'].append(trace)
            else:
                self.project.scripts[script].variables[var_type][var_key] = {'alias': '', 'usage': [trace]}

        for change in changes['remove']:
            var_parts = change.split(': ')
            var_type = var_parts[0]
            var_key = int(var_parts[1])
            if trace not in self.project.scripts[script].variables[var_type][var_key]['usage']:
                print(f'{self.log_key}: No variable usage to remove for {trace} in {var_type}: {var_key}')
                continue
            self.project.scripts[script].variables[var_type][var_key]['usage'].remove(trace)

    def update_inst_field(self, field, value, script, section, instruction, **kwargs):
        inst = self.project.scripts[script].sections[section].instructions[instruction]
        inst.__setattr__(field, value)

    def get_section_list(self, script):
        return list(self.project.scripts[script].sections.keys())

    def add_inst(self, script, section, ref_inst_uuid, case=None, direction='below'):
        new_inst = SCTInstruction()
        inst_sect = self.project.scripts[script].sections[section]
        inst_sect.instructions[new_inst.ID] = new_inst

        inst_parents, index = self.get_inst_grouped_parents_and_index(ref_inst_uuid, inst_sect.instructions_ids_grouped)

        cur_group = inst_sect.instructions_ids_grouped
        for key in inst_parents:
            cur_group = cur_group[key]

        clicked_inst_group_key = cur_group[index]
        if isinstance(clicked_inst_group_key, dict):
            clicked_inst_group_key = list(clicked_inst_group_key.keys())[0]

        grouped_insert_loc = index

        if direction == 'below':
            grouped_insert_loc += 1

        if direction == 'inside':
            grouped_insert_loc = 0
            cur_group = cur_group[index][list(cur_group.keys())[0]]
            if case is not None:
                cur_group = cur_group[case]

        cur_group.insert(grouped_insert_loc, new_inst.ID)

        ungroup_ref_inst_uuid = ref_inst_uuid

        if direction == 'below' and isinstance(cur_group[index], dict):
            cur_group = cur_group[index][list(cur_group.keys())[0]]

            # If it is a switch, there will be one more dict level for cases
            if isinstance(cur_group, dict):
                cur_group = cur_group[list(cur_group.keys())[-1]]

            # The ref inst for below is the last instruction of the group this should almost always be a goto
            ungroup_ref_inst_uuid = cur_group[-1]

        insert_pos = inst_sect.instruction_ids_ungrouped.index(ungroup_ref_inst_uuid)
        if direction in ('inside', 'below'):
            insert_pos += 1
        inst_sect.instruction_ids_ungrouped.insert(insert_pos, new_inst.ID)

        # if new inst is inside, and clicked is a switch case, change target of link of case to new inst
        if case is not None:
            switch = inst_sect.instructions[ref_inst_uuid]
            for loop in switch.loop_parameters:
                if loop[2].value == int(case):
                    loop[3].link.target_trace[1] = new_inst.ID
                    break

        # if new inst is below, and clicked is a switch, change targets of all links which contain the prev_below inst to cur_below inst for the switch
        if direction == 'below' and inst_sect.instructions[ref_inst_uuid].instruction_id == 3:
            switch = inst_sect.instructions[ref_inst_uuid]
            old_target = inst_sect.instruction_ids_ungrouped[insert_pos + 1]
            for loop in switch.loop_parameters:
                if loop[3].link.target_trace[1] == old_target:
                    loop[3].link.target_trace[1] = new_inst.ID

        # if new inst is below, and clicked is if, change target of goto to new inst
        if direction == 'below' and inst_sect.instructions[ref_inst_uuid].instruction_id == 0:
            if_inst = inst_sect.instructions[ref_inst_uuid]
            goto_inst = inst_sect.instructions[if_inst.my_goto_uuids[0]]
            goto_inst.parameters[0].link.target_trace[1] = new_inst.ID

        return new_inst.ID

    def get_inst_grouped_parents_and_index(self, inst, grouped_region, parents=None) -> (list, int):
        if parents is None:
            parents = []

        if inst in grouped_region:
            return parents, grouped_region.index(inst)

        for i, entry in enumerate(grouped_region):
            if not isinstance(entry, dict):
                continue

            for key, value in entry.items():
                if inst in key:
                    return parents, i

                out_parents, index = self.get_inst_grouped_parents_and_index(inst, value, parents=parents + [i] + [key])
                if out_parents is not None:
                    return out_parents, index

        return None, None

    def get_inst_group(self, script, section, inst_uuid):
        cur_sect = self.project.scripts[script].sections[section]
        parents, index = self.get_inst_grouped_parents_and_index(inst_uuid, cur_sect.instructions_ids_grouped)

        cur_level = cur_sect.instructions_ids_grouped
        for parent in parents:
            cur_level = cur_level[parent]

        group = cur_level[index]

        if not isinstance(group, dict):
            return None

        next_element = cur_level[index+1]
        if isinstance(next_element, dict):
            if inst_uuid in list(next_element.keys())[0]:
                group = [group, next_element]

        return group

    def change_inst_id(self, script, section, inst, new_id):
        # Check that the instruction requires an inst_id change
        cur_section = self.project.scripts[script].sections[section]
        cur_inst = cur_section.instructions[inst]
        if cur_inst.instruction_id == new_id:
            return True

        change_type = None
        if cur_inst.instruction_id in self.base_insts.group_inst_list:
            change_type = self.callbacks['check_remove_inst_group'](cur_inst.instruction_id, int(new_id))
            if change_type == 'cancel':
                return
            # TODO - If change_type == 'delete' confirm delete for N instructions
            # TODO - If change_type == 'pop below' move instructions out of group
            # TODO - if 'insert group' in change type save instructions for later, and add them to new group
            # TODO - else delete grouped instructions

        parent_list, index = self.get_inst_grouped_parents_and_index(inst, cur_section.instructions_ids_grouped)

        # Change inst id
        cur_inst.set_inst_id(new_id)

        # Remove any current parameters and loop parameters
        self.remove_inst_parameters(script, section, inst)

        # Add in default parameter values with no loops
        base_inst = self.base_insts.get_inst(int(new_id))

        for i in [*base_inst.params_before, *base_inst.params_after]:
            base_param = base_inst.parameters[i]
            new_param = SCTParameter(base_param.param_ID, base_param.type)
            if 'iterations' in base_param.type:
                new_param.set_value(0)
            cur_inst.parameters[i] = new_param

        if int(new_id) in self.base_insts.group_inst_list:
            self.setup_group_type_inst(script, section, inst, cur_inst, parent_list, index)
            # TODO - if 'insert group' in change_type, insert instructions in group, resolve ungrouped, etc.

        return True

    def remove_inst_parameters(self, script, section, inst, loop=True):
        cur_inst = self.project.scripts[script].sections[section].instructions[inst]
        cur_inst.parameters = {}
        if not loop:
            return
        cur_inst.loop_parameters = []

    def setup_group_type_inst(self, script, section, inst_id, inst, parent_list, index):
        print('here')
        inst_sect = self.project.scripts[script].sections[section]

        cur_group = inst_sect.instructions_ids_grouped
        for key in parent_list:
            cur_group = cur_group[key]

        if inst.instruction_id == 0:
            goto_inst = SCTInstruction()
            goto_inst.set_inst_id(10)
            goto_param = SCTParameter(0, 'int-jump')
            target_inst_UUID_index = inst_sect.instruction_ids_ungrouped.index(inst_id)+1
            target_inst_UUID = inst_sect.instruction_ids_ungrouped[target_inst_UUID_index]
            goto_link = SCTLink(origin=-1, origin_trace=[script, section, goto_inst.ID, 0], type='Jump',
                                target=-1, target_trace=[script, section, target_inst_UUID])
            goto_param.link = goto_link
            inst_sect.instructions[target_inst_UUID].links_in.append(goto_link)
            goto_inst.links_out.append(goto_link)
            goto_inst.add_parameter(0, goto_param)
            inst_sect.instructions[goto_inst.ID] = goto_inst
            inst_sect.instruction_ids_ungrouped.insert(target_inst_UUID_index, goto_inst.ID)
            grouped_insertion = {f'{inst_id}{sep}if': [goto_inst.ID]}
        elif inst.instruction_id == 3:
            grouped_insertion = {f'{inst_id}{sep}switch': {}}
        else:
            print(f'{self.log_key}: Setup Group Type Inst: Unknown group type inst ({inst.instruction_id}). Group not made.')
            grouped_insertion = inst_id

        cur_group.pop(index)
        cur_group.insert(index, grouped_insertion)
