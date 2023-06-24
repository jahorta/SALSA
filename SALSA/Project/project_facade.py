import copy
from typing import Union, Tuple

from Common.script_string_utils import SAstr_to_head_and_body
from SALSA.Project.description_formatting import format_description
from SALSA.Project.project_container import SCTProject, SCTSection, SCTParameter, SCTInstruction, SCTLink
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Common.setting_class import settings
from SALSA.Common.constants import sep, alt_sep, alt_alt_sep, uuid_sep
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

    # ---------------------- #
    # Project Editor Methods #
    # ---------------------- #

    def set_callback(self, key, callback):
        self.callbacks[key] = callback

    # Tree methods

    def get_tree(self, headers: Tuple[str], script=None, section=None, style='grouped', **kwargs):
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
            link_type = inst.parameters[param].link.type
            if link_type == 'Footer':
                tree[param]['type'] = 'Footer Entry'
                tree[param]['value'] = inst.parameters[param].linked_string
            elif link_type in ('Jump', 'Subscript'):
                tree[param]['type'] = 'Jump'
                tgt_sect = inst.parameters[param].link.target_trace[0]
                tgt_inst = inst.parameters[param].link.target_trace[1]
                target_inst = self.project.scripts[script].sections[tgt_sect].instructions[tgt_inst]
                tgt_name = self.base_insts.get_inst(target_inst.instruction_id).name
                tree[param]['value'] = f'{tgt_sect} - {target_inst.ungrouped_position} {tgt_name}'
            elif link_type == 'String':
                tree[param]['type'] = 'String'
                tree[param]['value'] = inst.parameters[param].linked_string

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

    def add_script_to_project(self, script_name, script):
        self.project.scripts[script_name] = script
        script_keys = sorted(list(self.project.scripts.keys()), key=str.casefold)
        self.project.scripts = {k: self.project.scripts[k] for k in script_keys}
        if 'update_scripts' not in self.callbacks:
            return
        self.callbacks['update_scripts']()

    def get_project_script_by_name(self, name):
        if name not in self.project.scripts.keys():
            print(f'{self.log_key}: No script loaded with the name: {name}')
            return None
        return self.project.scripts[name]

    def add_delay_parameter(self, script, section, instruction, **kwargs):
        param = SCTParameter(_id=-1, _type='scpt-int')
        self.project.scripts[script].sections[section].instructions[instruction].frame_delay_param = param
        return param

    def update_inst_field(self, field, value, script, section, instruction, **kwargs):
        inst = self.project.scripts[script].sections[section].instructions[instruction]
        inst.__setattr__(field, value)

    # def get_project_script_by_index(self, index):
    #     if index >= len(self.project.scripts.keys()):
    #         print(f'{self.log_key}: Script index out of range: {index} : {len(self.project.scripts.keys()) - 1}')
    #         return None
    #     name = list(self.project.scripts.keys())[index]
    #     return name, self.project.scripts[name]

    # ---------------------------- #
    # Instruction position methods #
    # ---------------------------- #

    def get_inst_ind(self, script, section, inst):
        return self.project.scripts[script].sections[section].instruction_ids_ungrouped.index(inst)

    def _refresh_inst_positions(self, script, section):
        section = self.project.scripts[script].sections[section]
        for i, inst_id in enumerate(section.instruction_ids_ungrouped):
            section.instructions[inst_id].ungrouped_position = i

    # ----------------------- #
    # Script variable methods #
    # ----------------------- #

    def get_script_variables_with_aliases(self, script):
        var_dict = {}
        for var_type, var_list in self.project.scripts[script].variables.items():
            var_dict[var_type] = {}
            var_order = sorted(list(var_list.keys()))
            for key in var_order:
                var_dict[var_type][key] = var_list[key]['alias']
        return var_dict

    def get_var_alias(self, script, var_type, var_id):
        if var_id not in self.project.scripts[script].variables[var_type]:
            return 'No Alias'
        return self.project.scripts[script].variables[var_type][var_id]['alias']

    def set_variable_alias(self, script, var_type, var_id, alias):
        self.project.scripts[script].variables[var_type][var_id]['alias'] = alias

    def get_variable_usages(self, script, var_type, var_id):
        return self.project.scripts[script].variables[var_type][var_id]['usage']

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

    # ------------------------------ #
    # String Editor Callback Methods #
    # ------------------------------ #

    def get_string_tree(self, script, headers):
        string_groups = self.project.scripts[script].string_groups
        strings = self.project.scripts[script].strings
        string_tree = []
        for key, group in string_groups.items():
            string_tree.append({headers[0]: key, headers[1]: '', 'row_data': None})
            string_tree.append('group')
            for string_id in group:
                str_head, str_body = SAstr_to_head_and_body(strings[string_id])
                if '\n' in str_body:
                    str_body = str_body.split('\n')[0]
                    str_body += '...'
                string_tree.append({headers[0]: string_id, headers[1]: f'{str_head}: {str_body}', 'row_data': string_id})
            string_tree.append('ungroup')

        return string_tree

    def get_string_to_edit(self, script, string_id):
        return SAstr_to_head_and_body(self.project.scripts[script].strings[string_id])

    def edit_strings(self, change_dict):
        pass

    # ----------------------------- #
    # Param Editor Callback Methods #
    # ----------------------------- #

    def get_section_list(self, script):
        return list(self.project.scripts[script].sections.keys())

    def get_inst_list(self, script, section, goto_uuid=None):
        cur_sect = self.project.scripts[script].sections[section]
        inst_list = cur_sect.instruction_ids_ungrouped
        if goto_uuid is not None:
            first_blocked = 0
            master_uuid = None
            if len(cur_sect.instructions[goto_uuid].my_master_uuids) < 0:
                master_uuid = cur_sect.instructions[goto_uuid].my_master_uuids[0]
                first_blocked = inst_list.index(master_uuid)
            last_blocked = cur_sect.instruction_ids_ungrouped.index(goto_uuid)
            if master_uuid is not None:
                if cur_sect.instructions[master_uuid].instruction_id == 3:
                    last_blocked = max(*[cur_sect.instruction_ids_ungrouped.index(i) for i in
                                         cur_sect.instructions[master_uuid].my_goto_uuids], last_blocked)
            inst_list = cur_sect.instruction_ids_ungrouped[:first_blocked] + cur_sect.instruction_ids_ungrouped[
                                                                             last_blocked + 1:]

        return [f'{cur_sect.instructions[i].ungrouped_position}: '
                f'{self.base_insts.get_inst(cur_sect.instructions[i].instruction_id).name}'
                f'{sep}{cur_sect.instructions[i].ID}' for i in inst_list]

    # ------------------------------------------ #
    # Instruction and parameter analysis methods #
    # ------------------------------------------ #

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

    def get_inst_is_removable(self, script, section, instruction, **kwargs):
        cur_sect = self.project.scripts[script].sections[section]
        inst_ind = cur_sect.instruction_ids_ungrouped.index(instruction)

        # Checks for initial label and return of a function
        if inst_ind == 0 or inst_ind + 1 == len(cur_sect.instruction_ids_ungrouped):
            return False

        # Checks if the instruction is a goto with a master
        if len(cur_sect.instructions[instruction].my_master_uuids) > 0:
            return False

        return True

    # ---------------------------------------------- #
    # Instruction and parameter manipulation methods #
    # ---------------------------------------------- #

    def remove_inst(self, script, section, inst, custom_link_tgt=None):
        self.remove_inst_links(script, section, inst, custom_tgt=custom_link_tgt)
        # This will handle inst group children, remove any inst links in the group
        # and remove the inst from the grouped representation of insts
        self.change_inst(script, section, inst)
        cur_sect = self.project.scripts[script].sections[section]
        cur_sect.instructions.pop(inst)
        if inst in cur_sect.instruction_ids_ungrouped:
            cur_sect.instruction_ids_ungrouped.remove(inst)
            self._refresh_inst_positions(script, section)

    def add_inst(self, script, section, ref_inst_uuid, case=None, direction='below'):
        new_inst = SCTInstruction()
        inst_sect = self.project.scripts[script].sections[section]
        inst_sect.instructions[new_inst.ID] = new_inst

        inst_parents, index = self.get_inst_grouped_parents_and_index(ref_inst_uuid, inst_sect.instruction_ids_grouped)

        cur_group = inst_sect.instruction_ids_grouped
        for key in inst_parents:
            cur_group = cur_group[key]

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

    def change_inst(self, script, section, inst, new_id=None):
        # not entering a new_id will remove the instruction
        cur_section = self.project.scripts[script].sections[section]
        cur_inst = cur_section.instructions[inst]
        if new_id is not None:
            if cur_inst.instruction_id == new_id:
                return True

        saved_children = {}
        changes = []
        if cur_inst.instruction_id in self.base_insts.group_inst_list:
            inst_group = self.get_inst_group(script, section, inst)
            if cur_inst.instruction_id == 3:
                inst_group = inst_group[f'{inst}{sep}switch']
            new_id = None if new_id is None else int(new_id)
            change_type = self.callbacks['confirm_remove_inst_group'](new_id=new_id, children=inst_group)
            if 'cancel' in change_type:
                return False

            custom_link_tgt = self.get_next_grouped_uuid(script, section, inst)
            for goto in cur_inst.my_goto_uuids:
                if goto in cur_section.instructions:
                    self.remove_inst(script, section, goto, custom_link_tgt=custom_link_tgt)

            changes: list = change_type.split(alt_alt_sep)
            changes.reverse()

            finished_change_indexes = []
            for i, change in enumerate(changes):
                change_parts = change.split(alt_sep)
                cur_group = None
                for key, group in inst_group.items():
                    if key == change_parts[0]:
                        cur_group = group
                        break
                if cur_group is None:
                    print(f'{self.log_key}: Unable to find group for processing: {change_parts[0]}')

                if 'Move' in change or 'Delete' in change:
                    self.perform_group_change(script, section, inst, cur_group, change)
                    finished_change_indexes.append(i)
                elif 'Insert' in change:
                    self.perform_group_change(script, section, inst, cur_group, change)
                    saved_children[change_parts[0]] = cur_group[:-1]
                else:
                    print(f'{self.log_key}: Unknown group change instruction: {change}')

            for i in reversed(finished_change_indexes):
                changes.pop(i)

            self.remove_inst_links(script, section, inst, custom_tgt=custom_link_tgt)

        parent_list, index = self.get_inst_grouped_parents_and_index(inst, cur_section.instruction_ids_grouped)

        if index is None:
            return

        cur_group = cur_section.instruction_ids_grouped
        for parent in parent_list:
            cur_group = cur_group[parent]

        if new_id is None:
            cur_group.pop(index)
            return

        if cur_inst.instruction_id in self.base_insts.group_inst_list:
            cur_group[index] = inst

        # Change inst id
        cur_inst.set_inst_id(int(new_id))

        # Remove any current parameters and loop parameters
        self.remove_inst_parameters(script, section, inst)

        # Add in default parameter values with no loops
        base_inst = self.base_insts.get_inst(int(new_id))

        for i in [*base_inst.params_before, *base_inst.params_after]:
            base_param = base_inst.parameters[i]
            new_param = SCTParameter(base_param.param_ID, base_param.type)
            if base_param.default_value == 'override':
                new_param.set_value('override', get_scpt_override(base_param.type))
            else:
                new_param.set_value(base_param.default_value)
            cur_inst.parameters[i] = new_param

        if int(new_id) in self.base_insts.group_inst_list:
            self.setup_group_type_inst(script, section, inst, cur_inst, parent_list, index)

            # add necessary groups to insert insts into
            for change in changes:
                if 'If' in change:
                    continue
                sub_group = change.split(' ')[-1].lower()
                self.add_inst_sub_group(script, section, inst, parent_list, index, sub_group)

            # Insert insts into groups
            for change in changes:
                # insert inst list into appropriate place in ungrouped
                temp_cur_group = cur_group
                if 'If' in change:
                    ungrouped_index = cur_section.instruction_ids_ungrouped.index(inst) + 1
                    temp_cur_group = temp_cur_group[index][f'{inst}{sep}if']
                elif 'Else' in change:
                    goto_inst = cur_section.instructions[cur_inst.my_goto_uuids[0]]
                    ungrouped_index = cur_section.instruction_ids_ungrouped.index(goto_inst.ID) + 1
                    temp_cur_group = temp_cur_group[index + 1][f'{inst}{sep}else']
                else:
                    sub_group = change.split(' ')[-1]
                    temp_cur_group = temp_cur_group[index][f'{inst}{sep}switch'][sub_group]
                    first_uuid, _ = self.get_inst_group_bounds(cur_group)
                    ungrouped_index = cur_section.instruction_ids_ungrouped.index(first_uuid)

                inst_list = self.extract_inst_uuids_from_group(saved_children[change.split(alt_sep)[0]])
                for uuid in reversed(inst_list):
                    cur_section.instruction_ids_ungrouped.insert(ungrouped_index, uuid)

                # insert saved_group into appropriate place in grouped
                for item in reversed(saved_children[change.split(alt_sep)[0]]):
                    temp_cur_group.insert(0, item)

                # Adjust if or switch for new linked inst values
                if 'If' in change:
                    pass
                elif 'Else' in change:
                    prev_tgt_uuid = cur_inst.parameters[0].link.target_trace[1]
                    prev_tgt_inst = cur_section.instructions[prev_tgt_uuid]
                    prev_tgt_inst.links_in.remove(cur_inst.parameters[0].link)
                    cur_inst.parameters[0].link.target_trace[1] = inst_list[0]
                    new_tgt_inst = cur_section.instructions[inst_list[0]]
                    new_tgt_inst.links_in.append(cur_inst.parameters[0].link)
                else:
                    case_param = None
                    for loop in cur_inst.loop_parameters:
                        if loop[0].value == int(sub_group):
                            case_param = loop[1]
                            break
                    if case_param is None:
                        print(f'{self.log_key}: Unable to find switch case for link change')
                    prev_tgt_inst = cur_section.instructions[case_param.link.target_trace[1]]
                    prev_tgt_inst.links_in.remove(case_param.link)
                    case_param.link.target_trace[1] = inst_list[0]
                    new_tgt_inst = cur_section.instructions[inst_list[0]]
                    new_tgt_inst.links_in.append(cur_inst.parameters[0].link)

        self._refresh_inst_positions(script, section)

        return True

    def remove_inst_parameters(self, script, section, inst, loop=True):
        cur_inst = self.project.scripts[script].sections[section].instructions[inst]
        cur_inst.parameters = {}
        if not loop:
            return
        cur_inst.loop_parameters = []

    # ------------------------------- #
    # Inst group manipulation methods #
    # ------------------------------- #

    def setup_group_type_inst(self, script, section, inst_id, inst, parent_list, index):

        inst_sect = self.project.scripts[script].sections[section]

        cur_group = inst_sect.instruction_ids_grouped
        for key in parent_list:
            cur_group = cur_group[key]

        if inst.instruction_id == 0:
            target_inst_UUID_index = inst_sect.instruction_ids_ungrouped.index(inst_id) + 1
            target_inst_UUID = inst_sect.instruction_ids_ungrouped[target_inst_UUID_index]

            inst_link = SCTLink(origin=-1, origin_trace=[section, inst.ID, 1], type='Jump',
                                target=-1, target_trace=[section, target_inst_UUID])
            inst.parameters[1].link = inst_link
            inst.links_out.append(inst_link)
            inst_sect.instructions[target_inst_UUID].links_in.append(inst_link)

            goto_inst = SCTInstruction()
            goto_inst.set_inst_id(10)
            goto_param = SCTParameter(0, 'int|jump')
            goto_inst.add_parameter(0, goto_param)
            goto_link = SCTLink(origin=-1, origin_trace=[section, goto_inst.ID, 0], type='Jump',
                                target=-1, target_trace=[section, target_inst_UUID])
            goto_param.link = goto_link
            inst_sect.instructions[target_inst_UUID].links_in.append(goto_link)
            goto_inst.links_out.append(goto_link)

            inst.my_goto_uuids = [goto_inst.ID]
            goto_inst.my_master_uuids = [inst.ID]

            inst_sect.instructions[goto_inst.ID] = goto_inst

            inst_sect.instruction_ids_ungrouped.insert(target_inst_UUID_index, goto_inst.ID)

            grouped_insertion = {f'{inst_id}{sep}if': [goto_inst.ID]}

        elif inst.instruction_id == 3:
            grouped_insertion = {f'{inst_id}{sep}switch': {}}
            inst.my_goto_uuids = []
        else:
            print(
                f'{self.log_key}: Setup Group Type Inst: Unknown group type inst ({inst.instruction_id}). Group not made.')
            grouped_insertion = inst_id

        cur_group.pop(index)
        cur_group.insert(index, grouped_insertion)

    def perform_group_change(self, script, section, inst, cur_group, change):
        # Handles Move Above, Move Below, Delete
        cur_sect = self.project.scripts[script].sections[section]

        start_inst_key, end_inst_key = self.get_inst_group_bounds(cur_group)

        # Remove Instructions from current place in ungrouped in new temp ungrouped
        start_inst_uuid = start_inst_key if sep not in start_inst_key else start_inst_key.split(sep)[0]
        end_inst_uuid = end_inst_key if sep not in end_inst_key else end_inst_key.split(sep)[0]
        start_ind = cur_sect.instruction_ids_ungrouped.index(start_inst_uuid)
        end_ind = cur_sect.instruction_ids_ungrouped.index(end_inst_uuid)
        group_insts = cur_sect.instruction_ids_ungrouped[start_ind: end_ind + 1]
        temp_ungrouped = []
        temp_ungrouped += cur_sect.instruction_ids_ungrouped[:start_ind] if start_ind > 0 else []
        temp_ungrouped += cur_sect.instruction_ids_ungrouped[end_ind + 1:] if end_ind < len(
            cur_sect.instruction_ids_ungrouped) - 1 else []

        # Remove instructions from current place in grouped in new temp grouped
        parents, grouped_ind = self.get_inst_grouped_parents_and_index(inst, cur_sect.instruction_ids_grouped)

        cur_temp_group = cur_sect.instruction_ids_grouped
        for parent in parents:
            cur_temp_group = cur_temp_group[parent]

        if "Delete" in change:
            for del_inst in reversed(group_insts):
                links_removed = False
                if len(cur_sect.instructions[del_inst].links_in) > 0:
                    for link in cur_sect.instructions[del_inst].links_in:
                        if link.origin_trace is None:
                            continue
                        if link.origin_trace[1] in temp_ungrouped:
                            links_removed = True
                            self.remove_inst_links(script, section, del_inst)
                if not links_removed and len(cur_sect.instructions[del_inst].links_out) > 0:
                    for link in cur_sect.instructions[del_inst].links_out:
                        if link.target_trace is None:
                            continue
                        if link.target_trace[1] in temp_ungrouped:
                            self.remove_inst_links(script, section, del_inst)
            new_insts = {k: cur_sect.instructions[k] for k in cur_sect.instructions if k not in group_insts}
            cur_sect.instructions = new_insts
            new_ungrouped = temp_ungrouped

        elif 'Move' in change:
            grouped_insert_loc = grouped_ind

            if 'Below' in change:
                grouped_insert_loc += 1

            ungroup_ref_inst_uuid = self.get_inst_uuid_from_group_entry(cur_temp_group[grouped_insert_loc])
            ungrouped_insert_ind = temp_ungrouped.index(ungroup_ref_inst_uuid)

            ungrouped_before = temp_ungrouped[:ungrouped_insert_ind]
            ungrouped_after = temp_ungrouped[ungrouped_insert_ind:]

            new_ungrouped = ungrouped_before + group_insts + ungrouped_after
            for entry in reversed(cur_group):
                cur_temp_group.insert(grouped_insert_loc, entry)

        elif 'Insert' in change:
            new_ungrouped = temp_ungrouped

        else:
            print(f'{self.log_key}: Unknown change request: {change}')
            return

        cur_sect.instruction_ids_ungrouped = new_ungrouped

    def add_inst_sub_group(self, script, section, inst, parent_list, index, sub_group):
        cur_sect = self.project.scripts[script].sections[section]
        cur_group = cur_sect.instruction_ids_grouped
        cur_inst = cur_sect.instructions[inst]
        for parent in parent_list:
            cur_group = cur_group[parent]

        test_group = cur_group
        if cur_inst.instruction_id == 3:
            test_group = test_group[index]
            test_group = test_group[list(test_group.keys())[0]]

        if cur_inst.instruction_id == 0:
            sub_group = f'{inst}{sep}{sub_group}'

        if self._inst_sub_group_present(test_group, sub_group):
            return

        if 'else' in sub_group:
            cur_group.insert(index + 1, {sub_group: []})
            return

        goto_target_ind = cur_sect.instruction_ids_ungrouped.index(inst) + 1
        goto_target_uuid = cur_sect.instruction_ids_ungrouped[goto_target_ind]
        loop_param_num = len(cur_inst.loop_parameters)
        if loop_param_num > 0:
            for uuid in cur_inst.my_goto_uuids:
                cur_tgt_uuid = cur_sect.instructions[uuid].parameters[0].link.target_trace[1]
                cur_tgt_ind = cur_sect.instruction_ids_ungrouped.index(cur_tgt_uuid)
                if cur_tgt_ind > goto_target_ind:
                    goto_target_ind = cur_tgt_uuid
                    goto_target_uuid = cur_tgt_uuid

        case_goto = SCTInstruction()
        case_goto.set_inst_id(10)
        case_goto.parameters[0] = SCTParameter(0, 'int|jump')
        case_goto.parameters[0].link = SCTLink('Jump', origin=-1, origin_trace=[section, case_goto.ID, 0],
                                               target=-1, target_trace=[section, goto_target_uuid])

        switch_loop_params = {2: SCTParameter(2, 'int'), 3: SCTParameter(3, 'int|jump')}
        switch_loop_params[2].value = int(sub_group)
        switch_loop_params[3].link = SCTLink('Jump', origin=-1, origin_trace=[section, inst, f'{loop_param_num}{sep}3'],
                                             target=-1, target_trace=[section, case_goto.ID])
        cur_inst.loop_parameters.append(switch_loop_params)

        cur_inst.links_out.append(switch_loop_params[3].link)
        case_goto.links_in.append(switch_loop_params[3].link)
        case_goto.links_out.append(case_goto.parameters[0].link)
        cur_sect.instructions[goto_target_uuid].links_in.append(case_goto.parameters[0].link)

        cur_sect.instruction_ids_ungrouped.insert(goto_target_ind, case_goto.ID)
        test_group[sub_group] = [case_goto.ID]

    # --------------------------- #
    # Inst group analysis methods #
    # --------------------------- #

    def get_inst_group(self, script, section, inst_uuid) -> Union[None, dict]:
        cur_sect = self.project.scripts[script].sections[section]
        parents, index = self.get_inst_grouped_parents_and_index(inst_uuid, cur_sect.instruction_ids_grouped)

        cur_level = cur_sect.instruction_ids_grouped
        for parent in parents:
            cur_level = cur_level[parent]

        group = cur_level[index]

        if not isinstance(group, dict):
            return None

        next_element = cur_level[index + 1]
        if isinstance(next_element, dict):
            if inst_uuid in list(next_element.keys())[0]:
                group |= next_element

        return group

    def get_inst_grouped_parents_and_index(self, inst, grouped_region, parents=None) -> (list, int):
        if parents is None:
            parents = []

        if inst in grouped_region:
            return parents, grouped_region.index(inst)

        if isinstance(grouped_region, dict):
            for key, value in grouped_region.items():
                out_parents, index = self.get_inst_grouped_parents_and_index(inst, value, parents=parents + [key])
                if out_parents is not None:
                    return out_parents, index
        else:
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

    def get_inst_group_bounds(self, cur_group) -> (str, str):
        first = self.get_inst_uuid_from_group_entry(cur_group[0])
        last = self.get_inst_uuid_from_group_entry(cur_group[-1], last=True)
        return first, last

    @staticmethod
    def _inst_sub_group_present(cur_group: Union[list, dict], sub_group: str):
        if 'else' in sub_group:
            for item in cur_group:
                if not isinstance(item, dict):
                    continue
                if list(item.keys())[0] == sub_group:
                    return True
        else:
            if sub_group in cur_group:
                return True
        return False

    def extract_inst_uuids_from_group(self, cur_group, uuids: Union[list, None] = None):
        if uuids is None:
            uuids = []

        for item in cur_group:
            item_uuid = self.get_inst_uuid_from_group_entry(item)
            if isinstance(item_uuid, str):
                if item_uuid not in uuids:
                    uuids.append(item_uuid)

            if not isinstance(item, dict):
                continue

            if item_uuid not in uuids:
                uuids.append(item_uuid)

            item_key = list(item.keys())[0]
            next_group = item[item_key]
            if isinstance(next_group, dict):
                for value in next_group.values():
                    uuids = self.extract_inst_uuids_from_group(value, uuids)
            else:
                uuids = self.extract_inst_uuids_from_group(next_group, uuids)

        return uuids

    def get_inst_uuid_from_group_entry(self, entry, last=False):
        if isinstance(entry, dict):
            if not last:
                item_key = list(entry.keys())[0]
                item_uuid = item_key.split(sep)[0]
            else:
                item_key = list(entry.keys())[-1]
                item_uuid = self.get_inst_uuid_from_group_entry(entry[item_key], last)
        elif isinstance(entry, list):
            if last:
                item_uuid = self.get_inst_uuid_from_group_entry(entry[-1], last)
            else:
                item_uuid = self.get_inst_uuid_from_group_entry(entry[0], last)
        else:
            return entry
        return item_uuid

    def get_next_grouped_uuid(self, script, section, inst):
        cur_sect = self.project.scripts[script].sections[section]
        cur_inst = cur_sect.instructions[inst]
        parents, index = self.get_inst_grouped_parents_and_index(inst, cur_sect.instruction_ids_grouped)
        cur_group = cur_sect.instruction_ids_grouped
        for parent in parents:
            cur_group = cur_group[parent]

        if index + 1 < len(cur_group):
            # if cur_inst is an if/else/while
            if cur_inst.instruction_id == 0:
                new_tgt_inst_uuid = cur_sect.instructions[cur_inst.my_goto_uuids[0]].links_out[0].target_trace[1]
            # if cur_inst is a switch
            elif cur_inst.instruction_id == 3:
                max_goto_tgt_uuid = ''
                max_goto_tgt_pos = 0
                for goto in cur_inst.my_goto_uuids:
                    cur_goto_tgt_uuid = cur_sect.instructions[goto].links_out[0].target_trace[1]
                    cur_goto_tgt_pos = cur_sect.instruction_ids_ungrouped.index(cur_goto_tgt_uuid)
                    if cur_goto_tgt_pos > max_goto_tgt_pos:
                        max_goto_tgt_pos = cur_goto_tgt_pos
                        max_goto_tgt_uuid = cur_goto_tgt_uuid
                new_tgt_inst_uuid = max_goto_tgt_uuid
            else:
                new_tgt_inst_uuid = self.get_inst_uuid_from_group_entry(cur_group[index + 1])
        else:
            if len(parents) == 0:
                return None
            next_inst = parents[-1]
            if uuid_sep not in next_inst:
                if len(parents) == 1:
                    return None
                next_inst = parents[-2]
            next_inst = next_inst.split(sep)[0]
            new_tgt_inst_uuid = self.get_next_grouped_uuid(script, section, next_inst)

        return new_tgt_inst_uuid

    # ----------------- #
    # Inst link methods #
    # ----------------- #

    def remove_inst_links(self, script, section, inst):
        cur_sect = self.project.scripts[script].sections[section]
        cur_inst = cur_sect.instructions[inst]
        if len(cur_inst.links_in) == 0 and len(cur_inst.links_out) == 0:
            return
        parents, index = self.get_inst_grouped_parents_and_index(inst, cur_sect.instruction_ids_grouped)
        cur_group = cur_sect.instruction_ids_grouped
        for parent in parents:
            cur_group = cur_group[parent]

        new_tgt_inst_uuid = self.get_next_grouped_uuid(script, section, inst)
        for link in cur_inst.links_in:
            ori_sect = link.origin_trace[0]
            ori_inst_uuid = link.origin_trace[1]
            ori_inst = self.project.scripts[script].sections[ori_sect].instructions[ori_inst_uuid]
            link_ind = ori_inst.links_out.index(link)
            if new_tgt_inst_uuid is None:
                ori_inst.links_out.pop(link_ind)
            else:
                ori_inst.links_out[link_ind].target_trace[1] = new_tgt_inst_uuid
                cur_sect.instructions[new_tgt_inst_uuid].links_in.append(link)
        for link in cur_inst.links_out:
            tgt_sect = link.target_trace[0]
            tgt_inst_uuid = link.target_trace[1]
            self.project.scripts[script].sections[tgt_sect].instructions[tgt_inst_uuid].links_in.remove(link)



