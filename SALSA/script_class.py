import copy
import re

from SALSA.byte_array_utils import getTypeFromString, toInt, asStringOfType, toFloat


class SCTAnalysis:
    start_pos = None

    special_addresses = {
        'bit': '0x80310bc',
        'byte': '0x80310a1c'
    }

    def __init__(self, sct_dict):
        self.Name = sct_dict['Name']
        self.Header = list(sct_dict['Header'].values())
        self.Index = sct_dict['Index']
        self.Stats = sct_dict['Stats']
        self.Positions = sct_dict['Positions']
        self.BodyLength = sct_dict['Body Length']
        self.FooterLength = sct_dict['Footer Length']
        self.TotalLength = self.BodyLength + self.FooterLength
        self.Sections = {}
        sectCount = 0
        for name, sect in sct_dict['Sections'].items():
            # print('Analyzing section {}'.format(sectCount))
            length = int(self.Index[name]['length'], 16)
            position = int(self.Index[name]['pos'], 16)
            self.Sections[name] = SCTSection(sect, name, length, position)
            sectCount += 1
        self.Footer = list(sct_dict['Footer'].values())
        self.IndexedInstructions = list(sct_dict['Implemented Instructions'])
        self.ErrorSections = sct_dict['Errors']
        self.Details = sct_dict['Details']
        # Provides a dictionary for linking segments. Key is position of requester, Value is position of requested
        self.Links = {}
        self.generate_links()

    def get_script_tree(self):
        """Request info from sections for either all or error"""
        script_tree = {}
        for key, value in self.Sections.items():
            current = {'Type': value.type, 'Length': value.length}
            script_tree[key] = current
        return script_tree

    def get_instruction_tree(self, scriptID):
        script = self.Sections[scriptID]
        inst_tree = script.get_instruction_tree(self.start_pos)
        return inst_tree

    def get_sct_info(self):
        sct_info = {'Filename': self.Name, 'Footer': "{}".format('\n'.join(self.Footer)),
                    'Errors': "{}".format('\n'.join(self.ErrorSections)),
                    'Script num': int(self.Header[2], 16), 'Insts': self.Details['Instructions Used']}
        return sct_info

    def get_instruction_details(self, sctID, instID):
        script = self.Sections[sctID]
        inst_details = script.get_instruction_details(instID)
        return inst_details

    def generate_links(self):
        section_links = {}
        for key, section in self.Sections.items():
            tempLinks = section.get_links()
            if not len(tempLinks) == 0:
                section_links[key] = tempLinks
        link_results = {}
        for sect_key, sect_link in section_links.items():
            for inst_key, inst_link in sect_link.items():
                for key, link in inst_link.items():
                    target_sect = ''
                    target_pos = toInt(link['start']) + toInt(link['target offset'])
                    prev_sect = ''
                    for pos, label in self.Positions.items():
                        if target_pos < int(pos):
                            break
                        prev_sect = label
                    target_sect = prev_sect
                    # if target_sect == 'Footer44':
                    # print('stop here')
                    if target_pos > self.TotalLength:
                        target_inst_link_info = 'Unable to find link target: target beyond file size'
                    elif target_sect[:6] == "Footer":
                        footer_index = target_sect[6:]
                        target_inst_link_info = 'Links to {0}: {1}'.format(target_sect, self.Footer[int(footer_index)])
                    else:
                        target_inst_link_info = self.Sections[target_sect].get_instruction_link_info_by_position(
                            target_pos)
                    if sect_key not in link_results.keys():
                        link_results[sect_key] = {}
                    if inst_key not in link_results[sect_key].keys():
                        link_results[sect_key][inst_key] = {}
                    link_results[sect_key][inst_key][key] = target_inst_link_info
        self.Links = link_results
        for key, value in link_results.items():
            self.Sections[key].set_links(value)

    def set_inst_start(self, start):
        self.start_pos = start

    def get_params_by_group(self, requested_group_list: dict):
        groups = {}
        requested_insts = []
        for inst, group_dict in requested_group_list.items():
            requested_insts.append(inst)
            for group_name, param_list in group_dict.items():
                if group_name not in groups.keys():
                    groups[group_name] = {}

        for sct in self.Sections.values():
            i = 0
            for inst in sct.instructions.values():
                if not re.search('^0x[a-f,0-9]+$', inst.ID):
                    continue
                if int(inst.ID, 16) in requested_insts:
                    for group_name, group in groups.items():
                        group_params = inst.get_params(requested_group_list[int(inst.ID, 16)][group_name])
                        if sct.name not in group.keys():
                            group[sct.name] = {}
                        group[sct.name][i] = group_params
                    i += 1

        return groups

    def get_export_script_tree(self, requested_subscripts, important_instructions):
        # Generate subscript trees
        all_subscript_addresses = {}
        subscript_roots = []
        assessed_children = []
        all_subscript_groups = {}
        important_subscripts = []
        for subscript in self.Sections.values():
            name = subscript.name
            if name in assessed_children:
                continue
            else:
                subscript_roots.append(name)
                result = self._generate_subscript_group(name, important_instructions)
                all_subscript_groups[name] = copy.deepcopy(result['tree'])
                all_subscript_addresses[name] = copy.deepcopy(result['addr'])
                for child in result['tree'].keys():
                    if self._has_instructions_any(important_instructions, self.Sections[child]):
                        if name not in important_subscripts:
                            important_subscripts.append(name)
                result['tree'].pop(name)
                assessed_children = [*assessed_children, *list(result['tree'].keys())]

        # removes groups whose parent was called by another subscript
        for name in subscript_roots:
            if name in assessed_children:
                all_subscript_groups.pop(name)

        # Prune trees to those which contain the desired subscript
        trees_to_keep = ['init', 'loop']
        for subscript in [*requested_subscripts, *important_subscripts]:
            if subscript not in trees_to_keep:
                trees_to_keep.append(subscript)

        for tree in list(all_subscript_groups.keys()):
            if tree not in trees_to_keep:
                all_subscript_groups.pop(tree)

        addresses = {}
        for tree in all_subscript_groups.keys():
            addresses = {**addresses, **all_subscript_addresses[tree]}

        return {'addresses': addresses, 'subscript_groups': all_subscript_groups}

    @staticmethod
    def _has_instructions_any(instructions, script):
        for inst in script.instructions.values():
            if inst.ID == 'Skip 2':
                continue
            ID = int(inst.ID, 16)
            if ID in instructions:
                return True
        return False

    def _generate_subscript_group(self, name, important_instructions):
        scripts_to_decode = []
        decoded_scripts = []
        inst_IDs_to_skip = ['Skip 2']
        current_subscript = self.Sections[name]
        if current_subscript.hasString:
            return {'string': current_subscript.string}
        tree = {}
        done = False
        important_addresses = {}
        while not done:
            decoded_scripts.append(name)
            sub = {}
            return_hit = False
            for pos, inst in current_subscript.instructions.items():
                pos = int(pos)
                if inst.ID in inst_IDs_to_skip:
                    continue
                ID = int(inst.ID, 16)
                if ID == 12:
                    return_hit = True
                elif ID in current_subscript.change_script_insts:
                    if ID == 238:
                        next_script = 'me099a.sct'
                    else:
                        offset_param_id = inst.get_param_id_by_name('offset')
                        if offset_param_id is None:
                            print('offset parameter is named incorrectly..')
                            continue
                        link_string = self.Links[name][str(pos)][list(self.Links[name][str(pos)].keys())[0]]
                        next_script = link_string.split(': ')[1].rstrip()
                    sub[pos] = {'end': {'inst': ID, 'script': next_script}}
                elif ID in current_subscript.change_subscript_insts:  # This is the instruction to load a subscript
                    # if current_name == 'loop':
                    #     print('pause here')
                    desc = inst.description
                    desc_parts = desc.split('Link to Section: ')
                    if not 1 < len(desc_parts) < 3:
                        continue
                    link_target_parts = desc_parts[1].split(', ')
                    next_location = 0
                    if re.search('choice', desc_parts[0]):
                        next_script = link_target_parts[0].split('\n')[0]
                    else:
                        next_script = link_target_parts[0]
                        if not re.search('Start of Section', link_target_parts[1]):
                            next_location = int(link_target_parts[1].split(' ')[1])

                    if ID == 11:
                        sub[pos] = {'subscript_load': {'next': next_script, 'location': next_location}}
                        if next_script not in [*decoded_scripts, *scripts_to_decode]:
                            scripts_to_decode.append(next_script)

                    elif ID == 0:
                        test = self._format_desc_fxn_dict(inst)
                        if not name == next_script:
                            sub[pos] = {
                                'subscript_jumpif': {'next': next_script, 'condition': test, 'location': next_location}}
                            if next_script not in [*decoded_scripts, *scripts_to_decode]:
                                scripts_to_decode.append(next_script)
                        else:
                            sub[pos] = {'jumpif': {'location': next_location, 'condition': test}}

                    elif ID == 10:
                        if name == next_script:
                            if next_location <= int(pos):
                                sub[pos] = {'loop': next_location}
                            else:
                                sub[pos] = {'goto': next_location}
                        else:
                            sub[pos] = {'goto': {'position': pos, 'next': next_script, 'location': next_location}}
                            if next_script not in [*decoded_scripts, *scripts_to_decode]:
                                scripts_to_decode.append(next_script)

                elif ID is current_subscript.choice_inst:
                    description = inst.description
                    choice_num = description.count('[')
                    if '《' in description:
                        question = description.split('《')[1].split('》')[0]
                        desc_choices = description.split('「')[1:]
                        choices = []
                        for choice in desc_choices:
                            choices.append(choice.split('」')[0])
                    else:
                        question = description.split('<<')[1].split('>>')[0]
                        desc_choices = description.split('[')[1:]
                        choices = []
                        for choice in desc_choices:
                            choices.append(choice.split(']')[0])
                    sub[pos] = {'choice': {'choice num': choice_num, 'question': question, 'choices': choices}}

                elif ID is current_subscript.switch_inst:
                    switch_iter = inst.parameters['1'].result
                    switch_description = inst.description
                    desc_lines = switch_description.splitlines()
                    condition = desc_lines.pop(0).split(': ')[1]
                    condition_byte = condition.split(' ')[0]
                    switch_entries = {}
                    for line in desc_lines:
                        line_parts = line.split(': ')
                        key = toInt(line_parts[0])
                        next_location = toInt(line_parts[-1].rstrip())
                        switch_entries[key] = next_location

                    sub[pos] = {'switch': {'iterations': switch_iter, 'condition': condition_byte, 'entries': switch_entries}}

                elif ID in current_subscript.set_addr_insts:

                    if ID == 5:
                        base_address = '0x80310a1c'
                        offset = inst.parameters['0'].result
                        address = hex(int(base_address, 16) + int(offset))
                        value_string = inst.resolveDescriptionFuncs(inst.parameters['1'].result)
                        value = value_string
                        if isinstance(value_string, str):
                            if re.search(': ', value_string):
                                value = value_string.split(': ')[1]
                            else:
                                value = toInt(value_string)
                        sub[pos] = {'set': {'type': 'byte', 'addr': address, 'value': value}}
                        if address not in important_addresses.keys():
                            important_addresses[address] = {'size': 'byte'}

                    if ID == 6:
                        base_address = '0x8030e514'
                        offset = inst.parameters['0'].result
                        address = hex(int(base_address, 16) + (4 * int(offset)))
                        value_string = inst.resolveDescriptionFuncs(inst.parameters['1'].result)
                        value = value_string
                        if isinstance(value_string, str):
                            if re.search(': ', value_string):
                                value = value_string.split(': ')[1]
                            else:
                                value = toInt(value_string)
                        sub[pos] = {'set': {'type': 'word', 'addr': address, 'value': value}}
                        if address not in important_addresses.keys():
                            important_addresses[address] = {'size': 'word'}

                    if ID == 7:
                        base_address = '0x8030e514'
                        offset = inst.parameters['0'].result
                        address = hex(int(base_address, 16) + (4 * int(offset)))
                        value_string = inst.resolveDescriptionFuncs(inst.parameters['1'].result)
                        value = value_string
                        if isinstance(value_string, str):
                            if re.search(': ', value_string):
                                value = value_string.split(': ')[1]
                            else:
                                value = toFloat(value_string)
                        sub[pos] = {'set': {'type': 'float', 'addr': address, 'value': value}}
                        if address not in important_addresses.keys():
                            important_addresses[address] = {'size': 'float'}

                    if ID == 17:
                        address = inst.parameters['0'].result
                        sub[pos] = {'set': {'type': 'bit', 'addr': address, 'action': 'set'}}
                        if address not in important_addresses.keys():
                            important_addresses[address] = {'size': 'bit'}

                    if ID == 18:
                        address = inst.parameters['0'].result
                        sub[pos] = {'set': {'type': 'bit', 'addr': address, 'action': 'unset'}}
                        if address not in important_addresses.keys():
                            important_addresses[address] = {'size': 'bit'}

                    if ID == 19:
                        address = inst.parameters['0'].result
                        sub[pos] = {'set': {'type': 'bit', 'addr': address, 'action': 'invert'}}
                        if address not in important_addresses.keys():
                            important_addresses[address] = {'size': 'bit'}

                elif ID in important_instructions:
                    parameter_tree = {}
                    if len(inst.parameters) > 0:
                        parameter_tree['parameter names'] = {
                            x: y.name for x, y in inst.parameters.items()
                        }
                        parameter_tree['parameter values temp'] = {
                            y.name: y.result for y in inst.parameters.values()
                        }

                    parameter_tree['parameter values'] = {}
                    for key, value in parameter_tree['parameter values temp'].items():
                        new_value = inst.resolveDescriptionFuncs(value)
                        parameter_tree['parameter values'][key] = new_value
                    parameter_tree.pop('parameter values temp')

                    sub[pos] = {'requested': {'name': inst.name, 'instruction': ID, **parameter_tree}}

            sorted_keys = sorted(list(sub.keys()))
            sub = {k: sub[k] for k in sorted_keys}
            sub['pos_list'] = sorted_keys

            if not return_hit:
                script_found = False
                for script_name in self.Index.keys():
                    if script_found:
                        next_script = script_name
                        sub['fallthroughs'] = {'next': next_script}
                        if next_script not in [*decoded_scripts, *scripts_to_decode]:
                            scripts_to_decode.append(next_script)
                        break
                    if script_name == name:
                        script_found = True

            tree[name] = sub

            if len(scripts_to_decode) > 0:
                name = scripts_to_decode.pop()
                current_subscript = self.Sections[name]
            else:
                done = True

        return {'addr': important_addresses, 'tree': tree}

    def _get_roots(self, subscript, parents, subscript_parents):
        roots = []
        if len(parents) > 1:
            for parent in subscript_parents[subscript]:
                roots = [*roots, *self._get_roots(parent, subscript_parents[parent], subscript_parents)]
        else:
            if parents[0] == 'external':
                roots.append(subscript)
                return roots
            roots = [*roots, *self._get_roots(parents[0], subscript_parents[parents[0]], subscript_parents)]
        return roots

    def _format_desc_fxn_dict(self, inst, test=None):
        if test is None:
            actions = inst.parameters['0'].scptActions
            test_action = None
            max_size = 0
            for key, action in actions.items():
                dict_size = self._get_dict_depth(action)
                if dict_size > max_size:
                    test_action = key
                    max_size = dict_size
            test = actions[test_action]
        out = {}
        for key, value in test.items():
            if isinstance(value, dict):
                out_value = self._format_desc_fxn_dict(inst, value)
            elif isinstance(value, str):
                out_value = inst.resolveDescriptionFuncs(value)
            else:
                out_value = value
            out[key] = out_value
        return out

    def _get_dict_depth(self, inp, size=0):
        size += 1
        if isinstance(inp, dict):
            for value in inp.values():
                size = max(self._get_dict_depth(value, size), size)
        return size

    def _flatten_tree(self, tree, name, flat_dict=None) -> dict:
        if flat_dict is None:
            flat_dict = {}
        cur_flat_dict = copy.deepcopy(flat_dict)

        if '-' in name:
            out_name = name.split('-')[0]
        else:
            out_name = name

        if 'children' in tree.keys():
            for child_name, child in tree['children'].items():
                temp_flat_dict = self._flatten_tree(child, child_name, cur_flat_dict)
                for key, value in temp_flat_dict.items():
                    if name in cur_flat_dict.keys():
                        new_pos_length = len(value['pos_list'])
                        cur_pos_length = len(temp_flat_dict[key]['pos_list'])
                        if cur_pos_length < new_pos_length:
                            cur_flat_dict[key] = value
                    else:
                        cur_flat_dict[key] = value
            new_tree = copy.deepcopy(tree)
            new_tree.pop('children')
        else:
            new_tree = tree

        replace_tree = False
        if out_name in cur_flat_dict.keys():
            new_pos_length = len(tree['pos_list'])
            cur_pos_length = len(cur_flat_dict[out_name]['pos_list'])
            if cur_pos_length < new_pos_length:
                cur_flat_dict[out_name] = new_tree
        else:
            cur_flat_dict[out_name] = new_tree

        return cur_flat_dict

    @staticmethod
    def _sterilize_subscript_names(in_dict):
        for subscript in in_dict.values():
            for key in subscript:
                if key == 'pos_list':
                    continue
                elif key == 'fallthrough':
                    subscript[key] = subscript[key].split('-')[0]
                elif isinstance(subscript[key], dict):
                    for k, v in subscript[key].items():
                        if k in ('subscript_load', 'subscript_jumpif'):
                            v['next'] = v['next'].split('-')[0]
                else:
                    print('what are you?')

        return in_dict


class SCTSection:
    decision_instruction_IDs = (
        0, 3, 5, 6, 7, 10, 11, 12, 17, 18, 19, 43, 144, 155
    )

    flow_control_insts = (0, 3, 10)
    change_script_insts = (43, 238, 257)
    change_subscript_insts = (0, 10, 11)
    choice_inst = 155
    switch_inst = 3
    set_addr_insts = (5, 6, 7, 17, 18, 19)

    def __init__(self, sect_dict, name, length, pos):
        self.name = name
        # if name == '_LOSE':
        #     print('stop here')
        self.length = length
        self.startPos = pos
        self.type = sect_dict['type']
        self.hasString = False
        if not sect_dict['string'] == '':
            self.hasString = True
            self.string = sect_dict['string']
            self.location = pos

        self.instructions = {}
        instCount = 0
        for key, value in sect_dict['data'].items():
            if key == 'errors':
                continue
            if key == 'final':
                break
            self.instructions[key] = SCTInstruct(self.startPos, value)
            instCount += 1

        self.hasError = False
        if 'errors' in sect_dict.keys():
            self.hasError = True

    def get_instruction_tree(self, start):
        instruction_tree = {}
        for key, value in self.instructions.items():
            current = {}
            code = value.ID
            if code == 'SCPT Parameter':
                current['Code'] = 'SCPT Par'
            elif code == 'Skip 2':
                current['Code'] = 'Skip 2'
            elif -1 < int(code, 16) < 265:
                if value.isDecoded:
                    current['Code'] = value.name
                else:
                    current['Code'] = '{0} ({1})'.format(int(code, 16), code)
                if int(code, 16) in self.decision_instruction_IDs:
                    current['Decision'] = True
                else:
                    current['Decision'] = False
            else:
                current['Code'] = value.ID
            current['Decoded'] = value.isDecoded
            if value.hasError:
                current['Error'] = value.get_error_types()
            else:
                current['Error'] = 'None'
            if start is not None:
                pos = int(key) * 4
                pos += self.startPos
                pos = hex(int(start, 16) + pos)
                current['pos'] = pos
            if 'Decision' not in current.keys():
                current['Decision'] = False
            instruction_tree[key] = current
        if self.hasString:
            next = {
                'Code': f'{self.string}',
                'Decoded': True,
                'Error': 'None'
            }
            instruction_tree['16'] = next

        return instruction_tree

    def get_instruction_details(self, instID):
        if self.hasString and instID == '16':
            inst_details = {
                'Decoded': 'This String is Decoded',
                'Code': 'String',
                'Name': self.name,
                'Errors': {},
                'Param Tree': {},
                'Description': self.string,
                'Location': self.location
            }
        else:
            inst = self.instructions[instID]
            inst_details = inst.get_details()
        return inst_details

    def get_links(self):
        inst_links = {}
        for key, inst in self.instructions.items():
            tempLinks = inst.get_links()
            if tempLinks is not None:
                inst_links[key] = tempLinks
        return inst_links

    def get_instruction_link_info_by_position(self, pos):
        inst_pos = toInt(pos) - self.startPos
        if not inst_pos % 4 == 0:
            return 'Unable to establish link: position should be divisible by 4 to be at start of an instruction:' \
                   '\nScript: {0}, Instruction: {1}'.format(self.name, inst_pos)
        target_inst = inst_pos / 4
        link_info = 'Link to Section: {0}'.format(self.name)
        if not isinstance(target_inst, int):
            target_inst = int(target_inst)
        if target_inst == 0:
            if self.hasString:
                return link_info + '\nString:\n{}'.format(self.string)
            else:
                return link_info + ', Start of Section'
        if not str(target_inst) in self.instructions.keys():
            return 'Unable to establish link: given position does not correspond to an available instruction:' \
                   '\nScript: {0}, Instruction: {1}'.format(self.name, target_inst)
        return link_info + ', Instruction: {0}'.format(target_inst)

    def set_links(self, link_dict):
        for key, value in link_dict.items():
            self.instructions[key].set_link(value)


class SCTInstruct:
    desc_codes = ['add', 'sub', 'mul', 'lnk']

    def __init__(self, script_pos, inst_dict):

        self.isDecoded = inst_dict['decoded']
        self.hasError = False
        self.hasInstructError = False
        self.hasParamErrors = False
        self.hasSCPTerror = False
        self.errors = {}
        self.hasLink = False
        self.links = {}
        self.inst_pos = int(inst_dict['start location'])
        self.overall_pos = self.inst_pos + script_pos

        if not self.isDecoded:
            self.ID = inst_dict['data']['word']
        else:
            self.ID = hex(int(inst_dict['instruction']))
            self.Function = inst_dict['function']
            # if self.ID == '0x87':
            #     print('stop here')
            self.name = inst_dict['name']
            if self.name == 'code_error':
                self.name += ': {0}({1})'.format(int(self.ID, 16), self.ID)
            elif self.name[:2] == '??':
                self.name += f' ({int(self.ID, 16)})'
            raw_description = inst_dict['description']
            self.pos = inst_dict['start location']
            self.paramNum = inst_dict['param num']

            if 'errors' in inst_dict.keys():
                self.hasError = True
                self.errors = inst_dict['errors']
                inst_dict = inst_dict.pop('errors')

                self.hasInstructError = False
                for value in self.errors.values():
                    if 'Instruction' in value:
                        self.HasInstructError = True

            self.hasParamErrors = False
            self.parameters = {}
            for key, value in inst_dict['parameters'].items():
                self.parameters[key] = SCTParam(key, value)
                if self.parameters[key].hasError:
                    self.hasParamErrors = True
                    self.hasError = True

            # if self.name == 'Switch':
            #     print('stop here')

            temp_description = self.description_insert_param_values(raw_description)
            self.description = self.resolveDescriptionFuncs(temp_description)

        if self.ID == 'SCPT Parameter':
            self.hasError = True
            self.hasSCPTerror = True
            self.errors = inst_dict['errors']

    def description_insert_param_values(self, d):
        desc = d
        paramSets = {}
        for param in self.parameters.values():
            name = param.name
            paramSets[name] = param.result

        for key, value in paramSets.items():
            keyword = '<{}>'.format(key)
            if not isinstance(value, str):
                value = str(value)
            result = value
            desc = desc.replace(keyword, result)

        return desc

    def get_details(self):
        if self.hasSCPTerror:
            details = {
                'Code': 'SCPT-specific Code was found before an appropriate instruction',
                'Decoded': 'SCPT',
            }
            error_string = ''
            for k, e in self.errors.items():
                error_string += '{0}: {1}\n'.format(k, e)
            details['Description'] = error_string
            return details
        if self.ID == 'Skip 2':
            inst_details = {'Code': 'Skip 2',
                            'Description': 'This is a skip of 2 positions. Not sure why yet, but necessary.'}
        else:
            inst_details = {'Code': '{0} ({1})'.format(int(self.ID, 16), self.ID)}
        if not self.isDecoded:
            inst_details['Decoded'] = 'This Instruction is NOT Decoded'
            inst_details['Description'] = ''
        else:
            inst_details['Name'] = self.name
            inst_details['Decoded'] = 'This Instruction is Decoded'
            inst_details['Location'] = self.Function
            inst_details['Description'] = self.description
            inst_details['Errors'] = '{}'.format('{0}: {1}\n'.join(self.errors.keys()).join(self.errors.values()))
            paramTree = {}
            for key, param in self.parameters.items():
                paramTree[key] = param.get_param_as_tree()
            inst_details['Param Tree'] = paramTree

        return inst_details

    def get_params(self, param_list):
        params = {}
        for param in param_list:
            params[param] = self.parameters[str(param)].result

        return params

    def get_error_types(self):
        if self.hasSCPTerror:
            return 'SCPT'
        error_type = 'Inst'
        if self.hasParamErrors:
            error_type = 'Param'
            if self.hasInstructError:
                error_type = 'Both'

        return error_type

    def resolveDescriptionFuncs(self, temp_desc):

        currentSubstring = temp_desc
        if not isinstance(currentSubstring, str):
            return currentSubstring
        new_desc = ''
        while True:
            nextStarPos = currentSubstring.find('*')
            if nextStarPos == -1:
                new_desc += currentSubstring
                break
            new_desc += currentSubstring[:nextStarPos]
            currentSubstring = currentSubstring[nextStarPos:]
            currentCode = currentSubstring[1:4]
            if currentCode in self.desc_codes:
                tempCommand = currentSubstring.split(' ')[0]
                closeBrackets = tempCommand.rfind(']*')
                currentCommand = currentSubstring[:closeBrackets + 2]
                currentSubstring = currentSubstring[closeBrackets + 2:]
                result = self.run_desc_func(currentCommand)
                new_desc += '{} '.format(result)
            else:
                currentSubstring = currentSubstring[1:]
                new_desc += '*'

        return new_desc

    def run_desc_func(self, func):
        command = func[1:4]
        params = func[5:-2]
        nextStarPos = params.find('*')
        nextCommaPos = params.find(',')
        if -1 < nextStarPos < nextCommaPos:
            internal_func = params[nextStarPos:] + ']*'
            params = self.run_desc_func(internal_func)
        nextCloseParam = params.find(']')
        param1 = params[:params.find(',')]
        suffix = ''
        if nextCloseParam == -1:
            param2 = params[params.find(',') + 1:]
        else:
            param2 = params[params.find(',') + 1:nextCloseParam]
            suffix = params[nextCloseParam + 2:]

        nextStarPos = param2.find('*')
        if -1 < nextStarPos:
            internal_func = param2[nextStarPos:] + ']*'
            param2 = self.run_desc_func(internal_func)

        if command == 'add':
            result = self.add_desc_params(param1, param2)
        elif command == 'sub':
            result = self.subtract_desc_params(param1, param2)
        elif command == 'mul':
            result = self.multiply_desc_params(param1, param2)
        elif command == 'lnk':
            result = self.link_desc_params(param1, param2)
        else:
            result = ''

        return result + suffix

    def get_links(self):
        if self.hasLink:
            return self.links
        else:
            return None

    @staticmethod
    def add_desc_params(param1, param2):
        result_type = getTypeFromString(param1)
        result = toInt(param1) + toInt(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def subtract_desc_params(param1, param2):
        result_type = getTypeFromString(param1)
        result = toInt(param1) - toInt(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def multiply_desc_params(param1, param2):
        result_type = getTypeFromString(param1)
        result = toFloat(param1) * toFloat(param2)
        result = asStringOfType(result, result_type)
        return result

    def link_desc_params(self, param1, param2):
        """
        Reads in two parameters:
        [1] The name of the start point, could be the instruction start (INST), or a param name
        [2] The offset of the link target
        The function then adds this information to the link dictionary and returns a new link
        placeholder with the link index number.
        """
        startPos = -1
        if param1 == 'INST':
            startPos = self.pos
        elif len(self.parameters) > 0:
            for key, value in self.parameters.items():
                if value.name == param1:
                    startPos = value.position
            if startPos == -1:
                return 'Unable to link - invalid start position'
        else:
            return 'Unable to link - invalid start position'
        self.hasLink = True
        linkLabel = 'LINK{}'.format(len(self.links))
        self.links[linkLabel] = {'start': startPos, 'target offset': param2}
        return '<{}>'.format(linkLabel)

    def set_link(self, link_dict):
        for key, value in link_dict.items():
            replace_key = '<{}>'.format(key)
            stringList = self.description.split(replace_key)
            if len(stringList) > 1:
                self.description = stringList[0] + value + stringList[1]
            # print('')

    def get_param_id_by_name(self, name):
        param_id = None
        for key, param in self.parameters.items():
            if param.name == name:
                param_id = key
                break
        return param_id


class SCTParam:
    parameter_types = ['int',
                       'masked-int',
                       'SCPT',
                       'override-SCPT',
                       'switch',
                       'loop']

    def __init__(self, key, param_dict):
        self.ID = key
        # print(self.ID)
        self.name = param_dict['name']
        self.type = param_dict['type']

        self.position = param_dict['position']
        self.hasError = False
        if 'int' in self.type:
            self.word = param_dict['result']['original value']
            self.result = param_dict['result']['result']
            if 'masked' in self.type:
                self.mask = param_dict['result']['mask']
                self.maskValue = param_dict['result']['mask']

        elif self.type not in self.parameter_types:
            self.type = 'unknown ({})'.format(param_dict['type'])
            self.hasError = True
            self.error = 'Unknown parameter type'
            self.result = 'Unknown result'

        elif 'loop' in self.type:
            self.result = 'Loop:'
            self.loopBypass = False

            if 'Error' in param_dict['result'].keys():
                self.hasError = True
                self.error = param_dict['result']['Error']
                self.result = self.error
                self.loopEntries = {'0_0': 'Loop Error'}
                return

            if 'bypass' in param_dict['result'].keys():
                self.loopEntries = {'0_0': 'Loop Bypassed'}
                self.loopBypass = True
                self.result = 'Loop Bypassed'
                return

            self.loopEntries = {}
            self.loopIter = len(param_dict['result']['loop'])
            tempResult = param_dict['result']['loop']
            for key, item in tempResult.items():
                self.result += f'\nIteration {key}:'
                for key1, item1 in item.items():
                    tempID = f"{key}_{key1}"
                    self.loopEntries[tempID] = item1
                    if 'scpt' in item1['type']:
                        if isinstance(item1['result'], str):
                            out = item1['result']
                        elif isinstance(item1['result']['result'], str):
                            out = item1['result']['result']
                        else:
                            out = item1['result']['result']['returned value']
                    else:
                        out = item1['result']
                    self.result += f'\n\t({tempID}): {out}'

        elif self.type == 'SCPT':
            scptOut = param_dict['result']
            if 'error' in scptOut.keys():
                self.hasError = True
                self.error = scptOut['error']
                scptOut.pop('error')
            self.result = scptOut['returned value']
            self.result = self.formatSCPTResult()
            scptOut.pop('returned value')
            self.scptActions = scptOut

        elif self.type == 'override-SCPT':
            self.result = param_dict['result']

        elif self.type == 'switch':

            if 'Error' in param_dict['result'].keys():
                self.hasError = True
                self.error = param_dict['result']['Error']
                self.switchEntries = {'0': self.error}
                self.switchLimit = 0
                self.result = ''
                return
            else:
                self.switchEntries = param_dict['result']['Entries']
            self.switchLimit = param_dict['result']['Entry Limit']
            self.idx = list(self.switchEntries.keys())
            self.result = ''
            badList = False

            for i in self.idx:
                if not re.search('^[-,0-9]+$', i):
                    badList = True

            if len(self.idx) > self.switchLimit:
                badList = True
            if badList:
                self.result = '\n Bad Switch, probably a parameter instead \n '

            self.idx[-1] = self.switchLimit - 1
            resultEntries = {}

            for i in range(len(self.idx)):
                if not re.search('^[-,0-9]+$', str(list(self.switchEntries.values())[i])):
                    print("pause here")
                offset = (i + 1) * 8 + list(self.switchEntries.values())[i]
                offset -= 4
                resultEntries[list(self.switchEntries.keys())[i]] = '*lnk[Switch,{}]*'.format(offset)
            self.result += ' \n'.join('{0}: {1}'.format(key, value) for key, value in resultEntries.items())

        else:
            raise IndexError('Somehow a parameter type was not chosen')

    def get_param_as_tree(self):

        param_dict = {
            'Name': self.name
        }
        if self.hasError:
            param_dict['Error'] = self.error
        else:
            param_dict['Error'] = 'None'

        if re.search('int', self.type):
            if re.search('masked', self.type):
                desc = 'This is a masked int: result: {0}, mask: {1} ({2})'.format(self.result, self.mask, self.word)
            else:
                desc = 'This is an integer: {0} ({1})'.format(self.result, self.word)
            param_dict['Details'] = desc
        elif self.type == 'override-SCPT':
            desc = 'This overrides an SCPTAnalyze call to return: {}'.format(self.result)
            param_dict['Details'] = desc
        elif self.type == 'SCPT':
            desc = 'This is an SCPTAnalyze call:'
            param_dict['Details'] = desc
            scpts = {}
            for key, value in self.scptActions.items():
                scpts[key] = value
            param_dict['SCPT'] = scpts
        elif self.type == 'switch':
            desc = 'This is a switch with a limit of {} entries'.format(self.switchLimit)
            param_dict['Details'] = desc
            entries = {}
            for key, value in self.switchEntries.items():
                newKey = 'sw_{}'.format(key)
                entries[newKey] = value
            param_dict['switch'] = entries
        elif self.type == 'loop':
            desc = 'This is a loop with {} iterations'.format(self.loopIter)
            param_dict['Details'] = desc
            entries = {}
            for key, value in self.loopEntries.items():
                newKey = 'l_{}'.format(key)
                entries[newKey] = value
            param_dict['loop'] = entries
        else:
            desc = 'This is an unknown parameter type:'
            param_dict['Details'] = desc

        # print(param_dict)
        return param_dict

    def formatSCPTResult(self):
        if not isinstance(self.result, dict):
            return self.result
        tempResult = self.unpack_result_dict(self.result, 0)
        return tempResult

    def unpack_result_dict(self, cur_dict, level):
        returnValue = ''
        for key, value in cur_dict.items():

            if not isinstance(value, dict):
                formatedReturn = '\n'
                tabs = '  ' * level
                formatedReturn += tabs
                returnValue += '{0}{1}: {2}'.format(formatedReturn, key, value)
            else:
                nextLevel = self.unpack_result_dict(value, level + 1)
                formatedReturn = '\n'
                tabs = '  ' * level
                formatedReturn += tabs
                returnValue += '{0}{1}: {2}'.format(formatedReturn, key, nextLevel)

        return returnValue
