from typing import List, Dict
import re
import copy

from SALSA.instruction_class import Instruct
from SALSA.script_class import SCTAnalysis
from SALSA.constants import FieldTypes as FT

import importlib.util
import sys
import subprocess

module = 'colorama'
if module in sys.modules:
    print(f"{module!r} already in sys.modules")
elif (spec := importlib.util.find_spec(module)) is not None:
    # If you choose to perform the actual import ...
    import colorama as col

    print(f"{module!r} has been imported")
    col.init()
else:
    print(f"can't find the {module!r} module")
    if input(f'Would you like to install the {module!r} module?'):
        # implement pip as a subprocess:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install',
                               'colorama'])
        # process output with an API in the subprocess module:
        reqs = subprocess.check_output([sys.executable, '-m', 'pip',
                                        'freeze'])
        installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        print(installed_packages)
        import colorama as col

        col.init()


class SCTExporter:
    export_option_fields = {'types': {'req': True, 'type': FT.string_list, 'values': []}}

    def __init__(self, loc=None, verbose=True):
        self.verbose_out = verbose
        self.dir = loc
        self.script_list: List[SCTAnalysis] = []
        self.instruction_list: Dict[str, Instruct] = {}
        self.export_type = ''
        self.export_args = {}

        self.export_functions = {
            'Ship battle turn data': self._ship_battle_turn_parameters,
            'Ship battle turnID decisions': self._ship_battle_turnID_decisions
        }

        self.export_options = {
            'Ship battle turn data': {
                'scripts': '^me501.+sct$',
                'instructions': {
                    165: {
                        'turn bonus': [
                            9, 10, 11, 12
                        ],
                        'lost turns': [
                            13, 14, 15, 16
                        ]
                    }
                },
                'headers': [
                    'turn bonus', 'lost turns'
                ],
                'function': self._get_script_parameters_by_group
            },
            'Ship battle turnID decisions': {
                'scripts': '^me547.+sct$',
                'subscripts': ['_TURN_CHK'],
                'function': self._get_script_flows,
                'instructions': {174: 'scene'},
                'headers': 'ScriptID,*ID*\n\n*Inst*Starting Value,Subscript:Position, Branches'
            }
        }

        self.script_performer = ScriptPerformer()

    def get_export_fields(self):
        types = list(self.export_options.keys())
        self.export_option_fields['types']['values'] = types
        return self.export_option_fields

    def get_export_scripts(self, export_type):
        return self.export_options[export_type]['scripts']

    def export(self, sct_list, instruction_list, export_type, export_args=None):
        if export_args is None:
            export_args = {}
        self.script_list = sct_list
        self.instruction_list = instruction_list
        self.export_type = export_type
        self.export_args = export_args
        return self.export_functions[export_type]()

    def _get_script_parameters_by_group(self):
        script_info_list = {'headers': {}}

        for inst, groups in self.export_options[self.export_type]['instructions'].items():
            for group_name, group in groups.items():
                script_info_list['headers'][group_name] = self.instruction_list[str(inst)].get_param_names(group)

        for i, sct in enumerate(self.script_list):
            # print(f'Getting information for {sct.Name}: {i+1}/{len(self.script_list)}')
            script_info_out = sct.get_params_by_group(self.export_options[self.export_type]['instructions'])
            script_info_list[sct.Name] = script_info_out

        return script_info_list

    def _ship_battle_turn_parameters(self):
        info_list = self.export_options[self.export_type]['function']()
        combine = self.export_args.get('combine', False)

        groups = [i for i in self.export_options['Ship battle turn data']['headers']]
        header_dict = info_list.pop('headers')
        scripts = info_list
        data_sets = 2
        curr_group = ''
        if combine:
            data_sets = 1
            curr_group = 'all'
        max_turns = -1
        for sct in scripts.values():
            for group in sct.values():
                max_turns = max(max_turns, len(group))
        print('check whats here')

        outs = {}
        for data_set in range(0, data_sets):
            if not combine:
                curr_group = groups[data_set]
            header_rows: List[str] = [',', 'Turn,Phase']
            rows: List[str] = []
            for i in range(0, max_turns):
                for j in range(0, 4):
                    rows.append(f'{i},{j}')

            for script_name, sct in scripts.items():
                header_rows[0] += f',{script_name},,,'
                if combine:
                    header_rows[0] += ',,,,'
                for group_name, group in header_dict.items():
                    if not combine:
                        if not group_name == curr_group:
                            continue
                    for param_id, param_name in group.items():
                        cur_row = 0
                        header_rows[1] += f',{param_name}'
                        for turn in sct[group_name].values():
                            for phase in range(0, 4):
                                value = turn.get(phase, '---')
                                if not value == '---':
                                    value = int(value[param_id])
                                rows[cur_row] += f',{value}'
                                cur_row += 1
                        for row in range(cur_row, len(rows)):
                            rows[row] += ','

            for row in range(0, len(header_rows)):
                header_rows[row] += '\n'

            for row in range(0, len(rows)):
                rows[row] += '\n'
            data = [*header_rows, *rows]
            outs[curr_group] = ''.join(data)

        return outs

    def _get_script_flows(self):
        script_info_list = {'headers': self.export_options[self.export_type]['headers']}

        for i, sct in enumerate(self.script_list):
            # print(f'Getting information for {sct.Name}: {i+1}/{len(self.script_list)}')
            script_info_out = sct.get_export_script_tree(self.export_options[self.export_type]['subscripts'],
                                                         list(self.export_options[self.export_type][
                                                                  'instructions'].keys()))
            script_info_list[sct.Name] = script_info_out

        return script_info_list

    def _ship_battle_turnID_decisions(self):
        verbose = self.verbose_out
        info_dict = self.export_options[self.export_type]['function']()
        headers = info_dict.pop('headers')
        script_runs = {}
        for script_name, script in info_dict.items():
            script_runs[script_name] = self.script_performer.run(script,
                                                                 self.export_options[self.export_type]['instructions'])

        # TODO - implement formatting of decision flow
        temp_outs = {}
        for script, result in script_runs.items():
            if '.' in script:
                key = script.split('.')[0]
            else:
                key = script
            script_num = key[2:5]
            csv = headers
            csv = csv.replace('*ID*', script_num)

            diff_string = ''
            inst_num = len(result['summary'])
            csv = csv.replace('*Inst*', 'Inst,' if inst_num > 1 else '')
            level = 0
            for inst, values in result['summary'].items():
                diff_string += '\n'
                if inst_num > 1:
                    prefix = ',' * level
                    diff_string += f'{prefix}{inst}'
                    level += 1
                for value, subscripts in values.items():
                    commas = ',' * level
                    value_prefix = f'\n{commas}{value}'
                    level += 1
                    for subscript, positions in subscripts.items():
                        sub_prefix = f'{value_prefix},({subscript}'
                        for position, diff_dict in positions.items():
                            pos_prefix = f'{sub_prefix}:{position})'
                            if diff_dict['has_diff']:
                                if verbose:
                                    body_diff = diff_dict['stratified']
                                else:
                                    body_diff = diff_dict['condensed']
                            else:
                                body_diff = diff_dict['out']
                            body = self._format_diff_tree(body_diff, level)
                            diff_string += f'\n{pos_prefix}{body}'
                    level -= 1
                if inst_num > 1:
                    level -= 1

            csv += diff_string
            csv = self._fill_out_commas(csv)
            temp_outs[key] = csv

        return temp_outs

    def _format_diff_tree(self, diff_dict, level) -> str:
        level += 1
        output = ''
        if 'inst' not in diff_dict:
            body = f'-> {diff_dict["value"]} ({diff_dict["subscript"]}:{diff_dict["pos"]}) '
            return f',{body}'
        inst = diff_dict['inst']
        commas = ',' * level
        if inst == 'out':
            out_values = diff_dict['out']
            body = f'-> {out_values["value"]} ({out_values["subscript"]}:{out_values["pos"]}) '
            output = f',{body}\n'
        elif inst == 'choice':
            question = diff_dict['question']
            responses = {f'{commas}{k}': v for k, v in diff_dict['options'].items()}
            output += f',{question}'
            for key, option in responses.items():
                output += f'\n{key}'
                option_result = self._format_diff_tree(option, level)
                output += option_result
        elif inst == 'jumpif':
            condition = diff_dict['condition']
            responses = {f'{commas}{k}': v for k, v in diff_dict['options'].items()}
            output += f',{condition}'
            for key, option in responses.items():
                output += f'\n{key}'
                option_result = self._format_diff_tree(option, level)
                output += option_result
        elif inst == 'switch':
            switch = f'switch-{diff_dict["condition"]}'
            responses = {f'{commas}{k}': v for k, v in diff_dict['options'].items()}
            output += f',{switch}'
            for key, option in responses.items():
                output += f'\n{key}'
                option_result = self._format_diff_tree(option, level)
                output += option_result
        else:
            print('Add another segment?')

        level -= 1
        return output

    @staticmethod
    def _fill_out_commas(csv):
        csv_lines = csv.splitlines()
        max_comma_num = 0
        for line in csv_lines:
            cur_commas = line.count(',')
            max_comma_num = max(cur_commas, max_comma_num)

        new_lines = []
        for line in csv_lines:
            cur_commas = line.count(',')
            rem_commas = ',' * (max_comma_num - cur_commas)
            new_lines.append(f'{line}{rem_commas}')

        out = f'\n'.join(new_lines)
        return out


class ScriptPerformer:
    current_subscript = ''
    current_index = 0
    index_stack = []
    addrs = {}
    out = {}
    switches = {}
    open_branch_segments = []
    all_init_ram_conditions = []
    all_outs = []
    all_starts = []
    requested_hit = False
    false_branches = []
    false_switch_entries = []
    debug_verbose = False

    def __init__(self):

        self.scpt_codes = {
            '(1)<(2)': self._is_lt,
            '(1)<=(2)': self._is_leq,
            '(1)>(2)': self._is_gt,
            '(1)>=(2)': self._is_geq,
            '(1)==(2)': self._is_eq,
            '(1)==(2)[5]': self._is_eq,
            '(1)&(2)': self._anded,
            '(1)|(2)': self._ored,
            '(1)!=0 and (2)!=0': self._both_true,
            '(1)!=0 or (2)!=0': self._either_true,
            'overwrites (1) with (2)': self._return_two,
            '(1)*(2)': self._multiply,
            '(1)/(2)': self._divide,
            '(1)%(2)': self._mod,
            '(1)+(2)': self._add,
            '(1)-(2)': self._subtract,
        }

    def run(self, input_dict, inst_details):
        self.addrs = {}
        if len(input_dict['addresses']) > 1:
            self.addrs = input_dict['addresses']

        self.open_branch_segments = []
        self.all_outs = []
        init_script = input_dict['flat'].pop('init')
        init_ram = self._get_defined_ram()
        self._run_subscript_branch(name='init', subscripts=init_script, ram=init_ram)

        for i in reversed(list(set(self.false_branches))):
            if i >= len(self.open_branch_segments):
                print(f'branch_remove_error: index {i} out of range')
                continue
            self.open_branch_segments.pop(i)
        self.false_branches = []

        for name, sub_tree in input_dict['flat'].items():
            done = False
            if len(self.open_branch_segments) == 0:
                initial_ram = self._get_defined_ram()
                branch_index = None
            else:
                branch_index = 0
                initial_ram = self.open_branch_segments[branch_index]['cur_ram']

            iteration = 0
            with_mid = True
            remove_old = False
            remove_false_branches = False
            new_run_limit = 1
            while not done:
                iteration += 1

                if branch_index is not None:
                    current_branch_init = self.open_branch_segments[branch_index]['init_value']
                    if 'parameter values' in current_branch_init:
                        value_out = current_branch_init["parameter values"]["scene"]
                        if isinstance(value_out, str):
                            value_out = current_branch_init["address_values"][value_out]
                    else:
                        value_out = 'None'
                else:
                    value_out = 'None'

                print(f'\nSubscript: {name}: Iteration {iteration}: Init Value:{value_out}')

                if iteration == 2:
                    remove_old = True
                    remove_false_branches = True

                pre_num = len(self.open_branch_segments)
                if self.debug_verbose:
                    print('Starting branch run:')
                self._run_subscript_branch(name=name, subscripts=sub_tree,
                                           ram=initial_ram, branch_index=branch_index)
                current_open_branch_num = len(self.open_branch_segments)
                change_open_branch_num = current_open_branch_num - pre_num

                false_branch_num = len(self.false_branches)

                desired_stats = {'init_value': 3.0, 'init_subscript': '_SET_PATH'}
                interesting_branches = []
                for i, branch in enumerate(self.open_branch_segments):
                    subscript = branch['init_value']['subscript']
                    if 'parameter values' in branch:
                        value_out = branch["parameter values"]["scene"]
                        if isinstance(value_out, str):
                            value_out = branch["address_values"][value_out]
                    if value_out == desired_stats['init_value'] and subscript == desired_stats['init_subscript']:
                        interesting_branches.append(i)

                sorted_false_branches = sorted(list(set(self.false_branches)))

                branches_to_remove = []
                false_branch_copy = [*self.false_branches]
                self.false_branches = []
                if remove_false_branches:
                    branches_to_remove = [*branches_to_remove, *false_branch_copy]

                # If before the remove false branches step, test for the lowest child dict depth with different
                # init_value and cur_ram
                else:
                    checked = []
                    for i, branch1 in enumerate(self.open_branch_segments):
                        checked.append(i)
                        if i in branches_to_remove:
                            continue
                        len_1 = self._get_dict_depth(branch1['children'])
                        for j, branch2 in enumerate(self.open_branch_segments):
                            if j in checked:
                                continue
                            if j in branches_to_remove:
                                continue
                            same_cur = self._variables_are_equal_recursive(branch1['cur_ram'], branch2['cur_ram'])
                            same_init = self._variables_are_equal_recursive(branch1['init_value'],
                                                                            branch2['init_value'])
                            if same_cur and same_init:
                                len_2 = self._get_dict_depth(branch2)
                                if len_1 <= len_2:
                                    branches_to_remove.append(j)
                                if len_1 > len_2:
                                    branches_to_remove.append(i)

                # flag for removal completed branches
                printProgressBar(prefix='Flagging Completed Branches', total=current_open_branch_num, iteration=0)
                for i, branch in enumerate(self.open_branch_segments):
                    if i % 500 == 0:
                        printProgressBar(prefix='Flagging Completed Branches', total=current_open_branch_num, iteration=i)
                    if 'out_value' in branch.keys():
                        branches_to_remove.append(i)
                    elif 'new_run' in branch.keys() and remove_old:
                        if branch['new_run']['value'] > (new_run_limit - 1):
                            branches_to_remove.append(i)
                printProgressBar(prefix='Flagging completed branches', total=current_open_branch_num,
                                 iteration=len(self.open_branch_segments), printEnd='\r\n')

                # flag for removal identical open branches
                branches_to_remove = sorted(list(set(branches_to_remove)))
                checked_branches = []
                printProgressBar(prefix='Flagging identical open branches', total=current_open_branch_num, iteration=0)
                for i, open1 in enumerate(self.open_branch_segments):
                    if i % 500 == 0:
                        printProgressBar(prefix='Flagging identical open branches', total=current_open_branch_num,
                                         iteration=i)
                    checked_branches.append(i)
                    for j, open2 in enumerate(self.open_branch_segments):
                        if j in branches_to_remove:
                            continue
                        if j in checked_branches:
                            continue
                        elif self._variables_are_equal_recursive(open1, open2):
                            branches_to_remove.append(j)
                printProgressBar(prefix='Flagging identical open branches', total=current_open_branch_num,
                                 iteration=current_open_branch_num, printEnd='\r\n')

                # flag for removal open branches with the same initial conditions as an out branch
                branches_to_remove = sorted(list(set(branches_to_remove)))
                repeats = []
                printProgressBar(prefix='Removing open branches which mirror closed branches', total=len(self.all_outs), iteration=0)
                for i, out_branch in enumerate(self.all_outs):
                    if i % 500 == 0:
                        printProgressBar(prefix='Removing open branches which mirror closed branches', total=len(self.all_outs),
                                         iteration=i)
                    for j, open_branch in enumerate(self.open_branch_segments):
                        if j in branches_to_remove:
                            continue
                        elif self._branch_has_same_conditions(out_branch=out_branch, open_branch=open_branch,
                                                              with_req=True, with_mid=with_mid):
                            branches_to_remove.append(j)
                            repeats.append(j)
                printProgressBar(prefix='Removing open branches which mirror closed branches', total=len(self.all_outs),
                                 iteration=len(self.all_outs), printEnd='\r\n')

                # Remove flagged branches
                branches_to_remove = sorted(list(set(branches_to_remove)))
                for i in reversed(branches_to_remove):
                    if i >= len(self.open_branch_segments):
                        print(f'branch_remove_error: index {i} out of range')
                        continue
                    self.open_branch_segments.pop(i)

                print(
                    f'{change_open_branch_num} branches opened - {false_branch_num} false branches detected '
                    f'(removed?{remove_false_branches}) - {len(branches_to_remove)} branches pruned '
                    f'- {len(self.open_branch_segments)} open branches remaining - {len(self.all_outs)} closed branches: ')

                if len(self.open_branch_segments) == 0:
                    done = True
                else:
                    branch_index = 0
                    initial_ram = self.open_branch_segments[branch_index]['cur_ram']
                    if iteration > 1:
                        updated_branch = copy.deepcopy(self.open_branch_segments[0])
                        mid_ram = copy.deepcopy(initial_ram)
                        if 'new_run' in updated_branch.keys():
                            new_run_dict = updated_branch['new_run']
                            new_run_dict['value'] = new_run_dict['value'] + 1
                            new_run_dict['mid_ram'].append(mid_ram)
                        else:
                            new_run_dict = {'value': 1, 'mid_ram': [mid_ram]}
                        updated_branch['new_run'] = new_run_dict
                        self.open_branch_segments[0] = updated_branch

            # Remove duplicates and any branch which goes past the out value, and any branch which contains a choice without modification
            outs_to_remove = sorted(list(set(self._flag_outs_for_removal(remove_no_mod=True))))
            print(f'removing {len(outs_to_remove)} branches with identical children')
            for i in reversed(outs_to_remove):
                if i >= len(self.all_outs):
                    print(f'Unable to pop all_outs at index {i} ({len(self.all_outs)} entries)')
                self.all_outs.pop(i)
            print(f'{len(self.all_outs)} branches remaining')

            # Identify branches which do not exit the subscript
            internal = []
            for i in reversed(range(len(self.all_outs))):
                if 'new_run' not in self.all_outs[i].keys():
                    internal.append(i)
            print(f'Found {len(internal)} branches which were created without exiting the subscript')

        tree_difference_summary = self._make_all_out_summary(inst_details=inst_details)
        print('Done with tree summary')

        # Sort summaries by value and add start to the beginning

        start_branch = self.all_starts[0]
        start_inst = start_branch['out_value']['instruction']
        out_value = start_branch['out_value']['parameter values'][inst_details[start_inst]]
        if isinstance(out_value, str):
            addr = out_value
            out_value = start_branch['out_value']['address_values'][addr]
        out_dict = {'value': out_value, 'subscript': start_branch['out_value']['subscript'],
                    'pos': start_branch['out_value']['pos']}

        sorted_summary = {}
        for inst, values in tree_difference_summary.items():
            if inst == start_inst:
                sorted_summary[inst] = {'Start': {'init': {0: {'has_diff': False, 'out': out_dict}}}}
            sorted_summary[inst] = {**sorted_summary[inst], **{k: values[k] for k in sorted(list(values))}}

        return {'trees_detail': self.all_outs, 'ram_stats': self.addrs, 'summary': sorted_summary}

    def _run_subscript_branch(self, name, subscripts, ram=None, branch_index=None,
                              ptrs=None, traceback=None, depth=0) -> bool:

        if depth > 30:
            print('Lots of recursion...')

        if traceback is None:
            traceback: List[Dict] = []
        if ptrs is None:
            ptrs: List[Dict] = []

        traceback.append({'name': name, 'ptr': 0})

        if len(traceback) > 10:
            print('recursion...')

        hit_requested = False
        if len(ptrs) > 0:
            my_ptr = ptrs.pop(0)
            name = my_ptr['name']
            traceback[-1] = copy.deepcopy(my_ptr)
            if len(ptrs) > 0:
                next_name = ptrs[0]['name']
                hit_requested = self._run_subscript_branch(name=next_name, subscripts=subscripts, ram=ram,
                                                           branch_index=branch_index, ptrs=copy.deepcopy(ptrs),
                                                           traceback=copy.deepcopy(traceback), depth=depth + 1)
            if 'ptr' not in my_ptr:
                print('pause here')
            current_pointer = my_ptr['ptr']
        else:
            current_pointer = 0

        if current_pointer is None:
            return False
        elif current_pointer >= len(subscripts[name]['pos_list']):
            return hit_requested

        traceback[-1]['ptr'] = current_pointer

        tabs = '\t' * len(traceback)
        spaces = ' ' * depth
        current_sub = subscripts[name]
        if len(current_sub['pos_list']) == 0:
            if self.debug_verbose:
                print(f'{tabs}{name}: no actions')
            return False
        else:
            if self.debug_verbose:
                print(f'{tabs}{name}')

        cur_ram = ram
        if current_pointer >= len(current_sub['pos_list']):
            print('error: current pointer outside position list length')
        inst_pos = current_sub['pos_list'][current_pointer]
        inst = current_sub[inst_pos]
        fallthrough_done = False
        done = False
        force_branch = False
        force_jump = False
        increment_pointer = True
        modify = False
        back_log = []
        while not done:
            cur_trace_id = len(traceback) - 1
            # print(f'{spaces}depth: {depth} current position: {name}:{current_pointer}')
            if 'set' in inst:
                cur_ram = self._set_memory_pos(inst['set'], cur_ram)
                self.open_branch_segments[branch_index]['cur_ram'] = cur_ram

            elif 'loop' in inst:
                force_jump = True
                inst_pos = inst['loop']
                current_pointer = self._get_ptr(pos=inst_pos, pos_list=current_sub['pos_list'])
                increment_pointer = False

            elif 'goto' in inst:
                inst_pos = inst['goto']
                current_pointer = self._get_ptr(pos=inst_pos, pos_list=current_sub['pos_list'])
                increment_pointer = False

            elif 'jumpif' in inst or 'subscript_jumpif' in inst:
                inst_name = list(inst.keys())[0]
                if branch_index is None:
                    self.all_starts.append({'end_ram': copy.deepcopy(cur_ram),
                                            'init_value': {'inst': 'jumpif', 'subscript': name, 'pos': 'Start'}})
                    self.open_branch_segments.append({'init_value': None, 'init_ram': copy.deepcopy(cur_ram),
                                                      'cur_ram': copy.deepcopy(cur_ram)})
                    branch_index = 0

                if 'subscript' in inst_name:
                    jump_condition = inst['subscript_jumpif']['condition']
                    next_name = inst['subscript_jumpif']['next']
                    inst_pos = inst['subscript_jumpif']['location']
                    jump_dict = {'children': {}, 'subscript': next_name, 'pos': inst_pos}
                    inst_ptr = self._get_ptr(inst_pos, subscripts[next_name]['pos_list'])
                else:
                    jump_condition = inst['jumpif']['condition']
                    next_name = name
                    inst_pos = inst['jumpif']['location']
                    jump_dict = {'children': {}, 'subscript': name, 'pos': inst_pos}
                    inst_ptr = self._get_ptr(inst_pos, subscripts[next_name]['pos_list'])

                jump_dict['condition'] = jump_condition
                jump_dict['traceback'] = copy.deepcopy(traceback)

                can_jump = self._can_jump(jump_condition, copy.deepcopy(cur_ram))

                jump = False
                make_branch = False
                if not force_branch:
                    if can_jump:
                        should_jump = self._should_not_jump(compare=jump_condition, ram=cur_ram, isBase=True)
                        if should_jump:
                            jump = True
                            make_branch = False
                    else:
                        make_branch = True
                else:
                    make_branch = True

                if force_jump:
                    make_branch = False
                    jump = True

                if make_branch:
                    traceback[cur_trace_id]['ptr'] += 1
                    ptrs = copy.deepcopy(traceback)
                    ptrs.pop()
                    ptrs.append({'name': next_name, 'ptr': inst_ptr})
                    new_branch_index = len(self.open_branch_segments)
                    jump_dict['jumped'] = True
                    new_branch = self._branch_append_node(
                        branch=copy.deepcopy(self.open_branch_segments[branch_index]),
                        node_key='jumpif', node_value=copy.deepcopy(jump_dict),
                        modify=modify)
                    self.open_branch_segments.append(new_branch)
                    pre_ram = copy.deepcopy(cur_ram)

                    sub_hit_requested = self._run_subscript_branch(name=next_name, subscripts=subscripts,
                                                                   ram=pre_ram, ptrs=copy.deepcopy(ptrs),
                                                                   branch_index=new_branch_index, depth=depth + 1)
                    new_branch_ram = copy.deepcopy(self.open_branch_segments[new_branch_index]['cur_ram'])

                    if not sub_hit_requested:
                        if self._variables_are_equal_recursive(pre_ram, new_branch_ram):
                            self.false_branches.append(new_branch_index)

                if jump:
                    current_pointer = inst_ptr
                    increment_pointer = False
                    if 'subscript' in inst_name:
                        next_name = inst['subscript']['next']
                        next_inst_pos = inst['subscript']['location']
                        next_inst_ptr = self._get_ptr(pos=next_inst_pos, pos_list=subscripts[next_name]['pos_list'])
                        traceback[-1]['ptr'] = current_pointer + 1
                        traceback.append({'name': next_name, 'ptr': next_inst_ptr})
                        name = next_name
                        current_sub = subscripts[next_name]
                        current_pointer = next_inst_ptr

                jump_dict['jumped'] = jump
                updated_branch = self._branch_append_node(
                    branch=copy.deepcopy(self.open_branch_segments[branch_index]),
                    node_key='jumpif', node_value=copy.deepcopy(jump_dict),
                    modify=modify)
                self.open_branch_segments[branch_index] = updated_branch
                force_branch = False
                force_jump = False
                modify = False

            elif 'requested' in inst:
                if inst_pos == 185:
                    print('pause here')
                hit_requested = True
                req_dict = copy.deepcopy(inst['requested'])
                params = req_dict['parameter values']
                param_address_values = {}
                for value in params.values():
                    if not isinstance(value, str):
                        value = str(value)
                    elif 'Bit: ' in value:
                        addr = value.split(' ')[1]
                        param_address_values[value] = cur_ram[addr]
                    if ': 0x8' in value:
                        if ' ' in value:
                            addr = value.split(' ')[1]
                        else:
                            addr = value
                        param_address_values[value] = self._get_memory_pos(addr, cur_ram, 'important')

                req_dict = {**req_dict, 'address_values': param_address_values, 'subscript': name,
                            'traceback': copy.deepcopy(traceback), 'pos': inst_pos}

                if branch_index is not None:
                    out_branch = self._branch_append_node(branch=self.open_branch_segments[branch_index],
                                                          node_key='out_value', node_value=req_dict)
                    out_branch['out_value'] = req_dict
                    out_branch['end_ram'] = copy.deepcopy(cur_ram)
                    self.open_branch_segments[branch_index] = out_branch
                    self.all_outs.append(out_branch)
                    prev_req_dict = self.open_branch_segments[branch_index]['init_value']
                    closing_branch = f'{branch_index}:{prev_req_dict["parameter values"]}-' \
                                     f'{prev_req_dict["address_values"]}'
                else:
                    out_branch = {'out_value': req_dict, 'end_ram': copy.deepcopy(cur_ram),
                                  'init_value': {'subscript': name, 'pos': 'Start'}}
                    self.all_starts.append(out_branch)
                    closing_branch = 'None'

                # start new branch, update branch_index with new branch ID
                new_branch_index = len(self.open_branch_segments)

                if self.debug_verbose:
                    print(f'\tDepth: {depth}, Closing Branch: {closing_branch}, Opening Branch: '
                          f'{new_branch_index}{req_dict["parameter values"]}-{req_dict["address_values"]}')
                self.open_branch_segments.append(
                    {'init_value': copy.deepcopy(req_dict), 'init_ram': copy.deepcopy(cur_ram),
                     'cur_ram': copy.deepcopy(cur_ram), 'children': {}})
                branch_index = new_branch_index

            elif 'switch' in inst:
                if branch_index is None:
                    self.all_starts.append({'end_ram': copy.deepcopy(cur_ram),
                                            'init_value': {'inst': 'jumpif', 'subscript': name, 'pos': 'Start'}})
                    self.open_branch_segments.append({'init_value': None, 'init_ram': copy.deepcopy(cur_ram),
                                                      'cur_ram': copy.deepcopy(cur_ram)})
                    branch_index = 0
                switch_all = False
                if force_branch:
                    switch_all = True

                # if memory addr has numerical value follow switch, add option: 'internal'
                switch_addr = inst['switch']['condition']
                switch_entries = inst['switch']['entries']
                can_switch = self._can_switch(addr=switch_addr, ram=cur_ram)
                if not can_switch:
                    switch_all = True

                # check for switch in list of switches, add switch to list if not present
                switch_ID = f'{name}-{inst_pos}'
                if switch_ID not in self.switches.keys():
                    self.switches[switch_ID] = inst['switch']

                # If entry cannot be selected, produce a branch for each entry

                if switch_all:
                    prev_branch = copy.deepcopy(self.open_branch_segments[branch_index])
                    traceback[cur_trace_id]['ptr'] += 1
                    ptrs = copy.deepcopy(traceback)
                    # if name == 'select_tactics':
                    #     print('pause here')
                    first = True
                    for key, offset in switch_entries.items():
                        if first:
                            first = False
                            continue
                        inst_pos = offset
                        inst_ptr = self._get_ptr(pos=offset, pos_list=current_sub['pos_list'])
                        ptrs[cur_trace_id]['ptr'] = inst_ptr
                        switch_dict = {'branched_all': switch_all, 'entries': switch_entries, 'condition': switch_addr,
                                       'selected_entry': key, 'next_inst_ptr': inst_ptr,
                                       'next_inst_pos': current_sub['pos_list'][inst_ptr], 'children': {}}
                        new_branch = self._branch_append_node(branch=copy.deepcopy(prev_branch), node_key='switch',
                                                              node_value=switch_dict, modify=modify)
                        new_branch_index = len(self.open_branch_segments)
                        self.open_branch_segments.append(new_branch)
                        pre_ram = cur_ram
                        sub_hit_requested = self._run_subscript_branch(name=name, subscripts=subscripts,
                                                                       ram=copy.deepcopy(pre_ram),
                                                                       branch_index=new_branch_index,
                                                                       ptrs=copy.deepcopy(ptrs), depth=depth + 1)

                        new_branch_ram = copy.deepcopy(self.open_branch_segments[new_branch_index]['cur_ram'])
                        if not sub_hit_requested:
                            if self._variables_are_equal_recursive(pre_ram, new_branch_ram):
                                self.false_branches.append(new_branch_index)
                        # if self.debug_verbose:
                        #     if 'colorama' in sys.modules:
                        #         suffix = f'{col.Fore.LIGHTBLACK_EX}requested:{hit_requested}{col.Fore.RESET}'
                        #     else:
                        #         suffix = f'req:{hit_requested}'
                        #     print(f'{tabs}\t<-- {suffix}')
                    switch_addr_value = list(switch_entries.keys())[0]
                else:
                    switch_addr_value = self._get_memory_pos(switch_addr, ram, 'control')

                increment_pointer = False
                if switch_addr_value in switch_entries:
                    entry = switch_entries[switch_addr_value]
                else:
                    entry = switch_entries[-1]
                inst_ptr = self._get_ptr(pos=entry, pos_list=current_sub['pos_list'])
                switch_dict = {'branched_all': switch_all, 'entries': switch_entries, 'condition': switch_addr,
                               'selected_entry': switch_addr_value, 'next_inst_ptr': inst_ptr,
                               'next_inst_pos': current_sub['pos_list'][inst_ptr], 'children': {}}
                new_branch = self._branch_append_node(branch=self.open_branch_segments[branch_index],
                                                      node_key='switch', modify=modify
                                                      , node_value=copy.deepcopy(switch_dict))
                self.open_branch_segments[branch_index] = new_branch
                current_pointer = inst_ptr

                # if self.debug_verbose:
                #     if 'colorama' in sys.modules:
                #         suffix = f'{col.Fore.LIGHTBLACK_EX}requested:{hit_requested}{col.Fore.RESET}'
                #     else:
                #         suffix = f'req:{hit_requested}'
                #     print(f'{tabs}\t<-- {suffix}')

            elif 'choice' in inst:
                if branch_index is None:
                    self.all_starts.append({'end_ram': copy.deepcopy(cur_ram),
                                            'init_value': {'inst': 'jumpif', 'subscript': name, 'pos': 'Start'}})
                    self.open_branch_segments.append({'init_value': None, 'init_ram': copy.deepcopy(cur_ram),
                                                      'cur_ram': copy.deepcopy(cur_ram)})
                    branch_index = 0
                force_branch = True
                modify = True
                choice_dict = {'details': inst['choice'], 'children': {}}
                new_branch = self._branch_append_node(branch=copy.deepcopy(self.open_branch_segments[branch_index]),
                                                      node_key='choice', node_value=copy.deepcopy(choice_dict))
                self.open_branch_segments[branch_index] = new_branch

            elif 'subscript_load' in inst:
                back_log.append({'name': name, 'ptr': current_pointer + 1})
                next_name = inst['subscript_load']['next']
                next_inst_pos = inst['subscript_load']['location']
                next_inst_ptr = self._get_ptr(pos=next_inst_pos, pos_list=subscripts[next_name]['pos_list'])
                traceback[-1]['ptr'] = current_pointer + 1
                traceback.append({'name': next_name, 'ptr': next_inst_ptr})
                name = next_name
                current_sub = subscripts[next_name]
                current_pointer = next_inst_ptr
                increment_pointer = False
                # if branch_index is not None:
                #     new_branch = self._branch_append_node(branch=self.open_branch_segments[branch_index],
                #                                           node_key='subscript', node_value=copy.deepcopy(sub_dict))
                #     self.open_branch_segments[branch_index] = new_branch
                # if self.debug_verbose:
                #     if 'colorama' in sys.modules:
                #         suffix = f'{col.Fore.LIGHTBLACK_EX}requested:{hit_requested}{col.Fore.RESET}'
                #     else:
                #         suffix = f'req:{hit_requested}'
                #     print(f'{tabs}\t<-- {suffix}')
                lis = 1

            if increment_pointer:
                current_pointer += 1
                traceback[cur_trace_id]['ptr'] = current_pointer
            else:
                increment_pointer = True

            if done:
                done = True
            elif current_pointer is None:
                done = True
            elif current_pointer < len(current_sub['pos_list']):
                inst_pos = current_sub['pos_list'][current_pointer]
                inst = current_sub[inst_pos]
            else:
                if len(back_log) > 0:
                    backtrack_successful = False
                    while not backtrack_successful:
                        traceback.pop()
                        checkpoint = back_log.pop()
                        new_name = checkpoint['name']
                        new_ptr = checkpoint['ptr']
                        name = new_name
                        current_pointer = new_ptr
                        current_sub = subscripts[new_name]
                        if current_pointer < len(current_sub['pos_list']):
                            inst_pos = current_sub['pos_list'][current_pointer]
                            inst = current_sub[inst_pos]
                            backtrack_successful = True
                        elif len(back_log) == 0:
                            done = True
                            backtrack_successful = True
                elif not fallthrough_done:
                    fallthrough_done = True
                    if 'fallthrough' in current_sub.keys():
                        next_subscript_name = current_sub['fallthrough']
                        hit_requested = self._run_subscript_branch(name=next_subscript_name,
                                                                   subscripts=subscripts, ram=copy.deepcopy(cur_ram),
                                                                   branch_index=branch_index, depth=depth + 1)
                        # if self.debug_verbose:
                        #     if 'colorama' in sys.modules:
                        #         suffix = f'{col.Fore.LIGHTBLACK_EX}requested:{hit_requested}{col.Fore.RESET}'
                        #     else:
                        #         suffix = f'req:{hit_requested}'
                        #     print(f'{tabs}\t<-- {suffix}')
                    done = True
                else:
                    done = True

        if branch_index is not None:
            self.open_branch_segments[branch_index]['cur_ram'] = cur_ram
        return hit_requested

    @staticmethod
    def _get_ptr(pos, pos_list):
        ptr = 0
        if pos == 0:
            return ptr
        if pos in pos_list:
            return int(pos_list.index(pos))
        else:
            if pos > pos_list[-1]:
                return None
            else:
                for i, p in enumerate(pos_list):
                    if p > pos:
                        return i

    def _make_all_out_summary(self, inst_details) -> dict:
        all_branches = self.all_outs

        # Group branches by: Inst, Inst_value, Subscript, Position
        grouped_branches = {}
        for branch in all_branches:

            inst = branch['init_value']['instruction']
            if inst not in grouped_branches.keys():
                grouped_branches[inst] = {}

            value = branch['init_value']['parameter values'][inst_details[inst]]
            if isinstance(value, str):
                addr = value
                value = branch['init_value']['address_values'][addr]
            if value not in grouped_branches[inst].keys():
                grouped_branches[inst][value] = {}

            subscript = branch['init_value']['subscript']
            if subscript not in grouped_branches[inst][value].keys():
                grouped_branches[inst][value][subscript] = {}

            cur_position = branch['init_value']['pos']
            if cur_position not in grouped_branches[inst][value][subscript].keys():
                grouped_branches[inst][value][subscript][cur_position] = []

            grouped_branches[inst][value][subscript][cur_position].append(branch)

        print('\nLooking for branch differences')
        all_differences = {}
        all_outs = {}
        all_levels = {}
        all_internals = {}
        for inst, subscripts in grouped_branches.items():
            all_differences[inst] = {}
            all_outs[inst] = {}
            all_levels[inst] = {}
            all_internals[inst] = {}
            for value, positions in subscripts.items():
                all_differences[inst][value] = {}
                all_outs[inst][value] = {}
                all_levels[inst][value] = {}
                all_internals[inst][value] = {}
                for subscript, values in positions.items():
                    all_differences[inst][value][subscript] = {}
                    all_outs[inst][value][subscript] = {}
                    all_levels[inst][value][subscript] = {}
                    all_internals[inst][value][subscript] = []
                    for position, branches in values.items():
                        print(f'\tGetting first differences from {inst}:{value}:{subscript}:{position}')
                        all_differences[inst][value][subscript][position] = []
                        all_levels[inst][value][subscript][position] = []

                        # Determine whether this position is internal and get outs for each branch
                        is_internal = True
                        branch_outs = []
                        for branch in branches:
                            if subscript == 'init' or 'new_run' in branch.keys():
                                is_internal = False

                            out_value = branch['out_value']['parameter values'][inst_details[inst]]
                            if isinstance(out_value, str):
                                addr = out_value
                                out_value = branch['out_value']['address_values'][addr]
                            out_sub = branch['out_value']['subscript']
                            out_pos = branch['out_value']['pos']
                            branch_outs.append({'value': out_value, 'subscript': out_sub, 'pos': out_pos})
                        all_outs[inst][value][subscript][position] = branch_outs

                        if is_internal:
                            all_internals[inst][value][subscript].append(position)

                        if len(branches) > 1:
                            checked_branches = []
                            for i, branch1 in enumerate(branches):
                                checked_branches.append(i)
                                for j, branch2 in enumerate(branches):
                                    if j in checked_branches:
                                        continue
                                    if self.debug_verbose:
                                        print(f'\tGetting first difference between {i} and {j}')

                                    temp_difference = self._get_first_difference(copy.deepcopy(branch1),
                                                                                 copy.deepcopy(branch2),
                                                                                 top_level=True)
                                    if len(temp_difference) == 0:
                                        continue
                                    diff_level = temp_difference.pop('level')
                                    deets = temp_difference.pop('diff_deets')
                                    difference = {'branches': [i, j], 'level': diff_level, 'diff': temp_difference,
                                                  'diff_details': deets}
                                    all_differences[inst][value][subscript][position].append(difference)

                            diff_levels = []
                            for diff in all_differences[inst][value][subscript][position]:
                                diff_levels.append(diff['level'])
                            diff_levels = sorted(list(set(diff_levels)))
                            all_levels[inst][value][subscript][position] = diff_levels

        # debug use only [inst, value, subscript, position]
        pause_at = {
            'inst': 174,
            'value': 8.0,
            'sub': '_SET_PATH',
            'pos': 4
        }
        print('Making Summary...')
        summary = {}
        for inst, values in grouped_branches.items():
            summary[inst] = {}
            pause_inst = inst == pause_at['inst']
            if pause_inst:
                pass
            for value, subscripts in values.items():
                summary[inst][value] = {}
                pause_value = value == pause_at['value']
                if pause_value:
                    pass
                for subscript, positions in subscripts.items():
                    summary[inst][value][subscript] = {}
                    pause_sub = subscript == pause_at['sub']
                    if pause_sub:
                        pass
                    for position, branches in positions.items():
                        pause_pos = position == pause_at['pos']
                        if pause_pos:
                            pass
                        if pause_pos and pause_sub and pause_value and pause_inst:
                            # print('pause here')
                            pass
                        differences = all_differences[inst][value][subscript][position]
                        branch_outs = all_outs[inst][value][subscript][position]
                        if len(branches) > 1:
                            if len(differences) > 0:
                                diff_levels = all_levels[inst][value][subscript][position]
                                stratified_diff_summary = self._get_stratified_differences(
                                    diffs=copy.deepcopy(differences),
                                    outs=copy.deepcopy(branch_outs),
                                    levels=copy.deepcopy(diff_levels))

                                condensed_diff_summary = self._condense_stratified_differences(
                                    copy.deepcopy(stratified_diff_summary))

                                temp_summary = {
                                    'has_diff': True,
                                    'stratified': stratified_diff_summary,
                                    'condensed': condensed_diff_summary
                                }
                            else:
                                out = branch_outs[0]
                                temp_summary = {'has_diff': False, 'out': out, 'unused_trees': True}
                        else:
                            out = branch_outs[0]
                            temp_summary = {'has_diff': False, 'out': out}

                        summary[inst][value][subscript][position] = temp_summary

        # Remove internal summaries and append them to external summaries
        appended_summary = {}
        first = True
        for int_inst, int_values in all_internals.items():
            for int_value, int_subscripts in int_values.items():
                for int_subscript, int_positions in int_subscripts.items():
                    for int_position in int_positions:
                        int_summary = summary[int_inst][int_value][int_subscript][int_position]
                        if first:
                            temp_summary = summary
                            first = False
                        else:
                            temp_summary = appended_summary
                        appended_summary = {}
                        for sum_inst, sum_values in temp_summary.items():
                            for sum_value, sum_subscripts in sum_values.items():
                                for sum_subscript, sum_positions in sum_subscripts.items():
                                    for sum_position, cur_summary in sum_positions.items():
                                        same_val = int_value == sum_value
                                        same_sub = int_subscript == sum_subscript
                                        same_pos = int_position == sum_position
                                        if same_pos and same_sub and same_val:
                                            continue

                                        int_identifier = {'inst': int_inst, 'val': int_value,
                                                          'sub': int_subscript, 'pos': int_position}
                                        keys = ('stratified', 'condensed')
                                        new_sum = {k: v for k, v in cur_summary.items() if k not in keys}
                                        for key in keys:

                                            if 'out' in int_summary.keys():
                                                int_sum = copy.deepcopy(int_summary['out'])
                                            else:
                                                int_sum = copy.deepcopy(int_summary[key])

                                            if 'out' in cur_summary.keys():
                                                cur_sum = copy.deepcopy(cur_summary['out'])
                                            else:
                                                cur_sum = copy.deepcopy(cur_summary[key])

                                            temp_sum = self._append_int_summary_to_externals(int_sum, cur_sum,
                                                                                             int_identifier)
                                            new_sum[key] = temp_sum

                                        if sum_inst not in appended_summary.keys():
                                            appended_summary[sum_inst] = {}
                                        if sum_value not in appended_summary[sum_inst].keys():
                                            appended_summary[sum_inst][sum_value] = {}
                                        if sum_subscript not in appended_summary[sum_inst][sum_value].keys():
                                            appended_summary[sum_inst][sum_value][sum_subscript] = {}
                                        if sum_position not in appended_summary[sum_inst][sum_value][
                                            sum_subscript].keys():
                                            appended_summary[sum_inst][sum_value][sum_subscript][sum_position] = {}

                                        appended_summary[sum_inst][sum_value][sum_subscript][sum_position] = new_sum

        if len(appended_summary) == 0:
            appended_summary = summary
        return appended_summary

    def _get_first_difference(self, branch1, branch2, top_level=False, level=0) -> dict:
        if 'children' not in branch1.keys() or 'children' not in branch2.keys():
            if self.debug_verbose:
                print('\t\tNo children or difference present...')
            return {}

        children1 = branch1.pop('children')
        children2 = branch2.pop('children')
        ch1_keys = list(children1.keys())
        ch2_keys = list(children2.keys())
        if top_level:
            rest_same = True
        else:
            rest_same = self._variables_are_equal_recursive(branch1, branch2)
            if rest_same:
                rest_same = self._variables_are_equal_recursive(ch1_keys, ch2_keys)

        if rest_same:
            next_branch1 = children1[ch2_keys[0]]
            next_branch2 = children2[ch2_keys[0]]
            temp_diff = self._get_first_difference(next_branch1, next_branch2, level=(level + 1))

            if 'insert_key' in temp_diff.keys():
                temp_diff.pop('insert_key')
                level = temp_diff.pop('level')
                deets = temp_diff.pop('diff_deets')
                difference = {ch2_keys[0]: temp_diff, 'level': level, 'diff_deets': deets}
            else:
                difference = temp_diff

        else:
            difference = self._get_difference_details(branch1, branch2)
            difference['level'] = level
            difference['diff_deets'] = [copy.deepcopy(branch1), copy.deepcopy(branch2)]
            difference['insert_key'] = True

        return difference

    def _get_difference_details(self, var1, var2):
        diff = {}
        if not type(var1) == type(var2):
            type1 = type(var1)
            type2 = type(var2)
            diff = {'var1': copy.deepcopy(var1), 'var2': copy.deepcopy(var2), 'var1_type': copy.deepcopy(type1),
                    'var2_type': copy.deepcopy(type2)}

        elif isinstance(var1, dict):
            for key in var1:
                if key not in var2.keys():
                    return {'var1': copy.deepcopy(var1), 'var2': copy.deepcopy(var2), 'key': copy.deepcopy(key)}
            for key, var1_value in var1.items():
                var2_value = var2[key]
                sub_diff = self._get_difference_details(var1_value, var2_value)
                if not len(sub_diff) == 0:
                    diff[key] = sub_diff

        elif isinstance(var1, list):
            if not len(var1) == len(var2):
                diff = [var1, var2]
            else:
                for i in range(len(var1)):
                    var1_value = var1[i]
                    var2_value = var2[i]
                    sub_diff = self._get_difference_details(var1_value, var2_value)
                    if not len(sub_diff) == 0:
                        diff[i] = sub_diff

        else:
            if not var1 == var2:
                return {'var1': copy.deepcopy(var1), 'var2': copy.deepcopy(var2)}
            else:
                return {}

        return diff

    def _get_stratified_differences(self, diffs, outs, levels, valid_ids=None) -> dict:
        strat_diff = {}
        rem_levels = levels[1:]
        level = levels[0]
        child_ids = {}
        for diff in diffs:
            if diff['level'] == level:
                b_keys = diff['branches']
                invalid_id_detected = False
                if valid_ids is not None:
                    for key in b_keys:
                        if key not in valid_ids:
                            invalid_id_detected = True

                if len(b_keys) < 2:
                    print('Stratification Error: Invalid number of branches to form a difference')
                    continue
                if invalid_id_detected:
                    continue

                diff_inst = list(diff['diff'].keys())[0]
                diff_dict = diff['diff'][diff_inst]

                if diff_inst == 'choice':
                    if 'jumpif' in diff_dict['modification']:
                        b_diff_value_dict = diff_dict['modification']['jumpif']['jumped']
                    if 'switch' in diff_dict['modification']:
                        b_diff_value_dict = diff_dict['modification']['switch']['selected_entry']

                    b_diff_values = [b_diff_value_dict['var1'], b_diff_value_dict['var2']]

                    choice_details = diff['diff_details'][0]['details']
                    options = choice_details['choices']
                    strat_diff['inst'] = 'choice'
                    strat_diff['question'] = choice_details['question']
                    for i, value in enumerate(b_diff_values):
                        if isinstance(value, bool):
                            if value:
                                entry = 0
                            else:
                                entry = 1
                        else:
                            entry = int(value)
                        if not options[entry] in child_ids.keys():
                            child_ids[options[entry]] = []
                        b_id = b_keys[i]
                        if b_id not in child_ids[options[entry]]:
                            child_ids[options[entry]].append(b_id)

                elif diff_inst == 'jumpif':
                    details = diff['diff_details'][0]
                    b_diff_value_dict = diff_dict['jumped']
                    found_values = True
                    for ind in ('var1', 'var2'):
                        if ind not in b_diff_value_dict.keys():
                            found_values = False

                    b_diff_values = []
                    if not found_values:
                        continue
                    else:
                        b_diff_values.append(b_diff_value_dict['var1'])
                        b_diff_values.append(b_diff_value_dict['var2'])

                    if 'jumped' in details.keys():
                        details.pop('jumped')
                    options = [True, False]
                    strat_diff['inst'] = 'jumpif'
                    strat_diff['results'] = options
                    condition_key = list(diff['diff_details'][0]['condition'].keys())[0]
                    condition = self._generate_condition_string(
                        cond_in=diff['diff_details'][0]['condition'][condition_key])
                    strat_diff['condition'] = condition
                    for i, value in enumerate(b_diff_values):
                        if isinstance(value, bool):
                            if value:
                                entry = 0
                            else:
                                entry = 1
                        else:
                            print('\t\tjump w/o a boolean???')
                            entry = int(value)
                        if not options[entry] in child_ids.keys():
                            child_ids[options[entry]] = []
                        b_id = b_keys[i]
                        if b_id not in child_ids[options[entry]]:
                            child_ids[options[entry]].append(b_id)
                    for child_list in child_ids.values():
                        if len(child_list) == 0:
                            print('error')
                elif diff_inst == 'switch':
                    details = diff['diff_details'][0]
                    b_diff_value_dict = diff_dict['selected_entry']
                    found_values = True
                    for ind in ('var1', 'var2'):
                        if ind not in b_diff_value_dict.keys():
                            found_values = False

                    b_diff_values = []
                    if not found_values:
                        continue
                    else:
                        b_diff_values.append(b_diff_value_dict['var1'])
                        b_diff_values.append(b_diff_value_dict['var2'])

                    strat_diff['inst'] = 'switch'
                    condition = details['condition']
                    strat_diff['condition'] = condition
                    for i, value in enumerate(b_diff_values):
                        if isinstance(value, bool):
                            if value:
                                entry = 0
                            else:
                                entry = 1
                            print('\t\tswitch w/ a boolean???')
                        else:
                            entry = int(value)
                        if entry not in child_ids.keys():
                            child_ids[entry] = []
                        b_id = b_keys[i]
                        if b_id not in child_ids[entry]:
                            child_ids[entry].append(b_id)
                    for child_list in child_ids.values():
                        if len(child_list) == 0:
                            print('error')
                else:
                    print(f'make new category: {diff_inst}')

        temp_children = child_ids
        if len(temp_children) == 0:
            if len(rem_levels) > 0:
                return self._get_stratified_differences(diffs=diffs, outs=outs, levels=rem_levels,
                                                        valid_ids=valid_ids)
            else:
                cur_outs = []
                for id in valid_ids:
                    cur_outs.append(outs[id])
                output = cur_outs[0]
                out_dict = {'inst': 'out', 'out': output, 'multiple_outs': True}
                print('no children here?')
                return out_dict

        for key, option_list in child_ids.items():
            if not len(option_list) == 1:
                if len(rem_levels) > 0:
                    out_dict = self._get_stratified_differences(diffs=diffs, outs=outs, levels=rem_levels,
                                                                valid_ids=option_list)
                else:
                    cur_outs = []
                    for option in option_list:
                        cur_outs.append(outs[option])
                    output = cur_outs[0]
                    out_dict = {'inst': 'out', 'out': output, 'multiple_outs': True}
            else:
                if len(option_list) < 1 or len(outs) < option_list[0]:
                    print('stop here')
                output = outs[option_list[0]]
                out_dict = {'inst': 'out', 'out': output}

            if out_dict is None:
                print('out dict wasnt made??')
            temp_children[key] = out_dict
            if len(out_dict) == 0:
                print('out_dict is empty?')

        strat_diff['options'] = temp_children

        return strat_diff

    def _generate_condition_string(self, cond_in, top_level=True):
        string = ''
        for cond, cond_dict in cond_in.items():
            temp_cond = cond
            values = {}
            for id, value in cond_dict.items():
                if isinstance(value, dict):
                    substring = self._generate_condition_string(cond_in=value, top_level=False)
                    values[id] = substring
                else:
                    values[id] = value

            for key, value in values.items():
                if isinstance(value, str):
                    if ': ' in value:
                        cond_value = value.split(': ')[1].rstrip()
                    else:
                        cond_value = value
                else:
                    cond_value = str(value)
                replace_key = f'({key})'
                temp_cond = temp_cond.replace(replace_key, cond_value)

            string += f'{temp_cond}'
            if not top_level:
                string = f'({string})'

        return string

    def _condense_stratified_differences(self, diffs) -> dict:
        current_diffs = copy.deepcopy(diffs)
        if 'options' in diffs.keys():
            options = {}
            for selection, result in diffs['options'].items():
                if 'inst' not in result.keys():
                    print('condense_error - no inst in result')
                if not result['inst'] == 'out':
                    next_level = self._condense_stratified_differences(result)
                    options[selection] = next_level
                else:
                    if len(result) == 0:
                        print('condense_error - empty result')
                    options[selection] = result

            if len(options) == 0:
                print('condense_error - options is empty')

            last_option = None
            all_options_same = True
            for key, out in options.items():
                cur_option = out
                if all_options_same:
                    if last_option is not None:
                        if not self._variables_are_equal_recursive(cur_option, last_option):
                            all_options_same = False
                last_option = cur_option

            if all_options_same:
                option_key = list(options.keys())[0]
                condensed_dict = options[option_key]
            else:
                current_diffs.pop('options')
                condensed_dict = {**current_diffs, 'options': options}

        else:
            condensed_dict = current_diffs

        return condensed_dict

    def _append_int_summary_to_externals(self, int_sum, cur_sum, int_id):

        if not cur_sum['inst'] == 'out':
            if 'options' not in cur_sum.keys():
                print('append_error - no options available, cannot continue')
                return cur_sum
            new_sum = {k: v for k, v in cur_sum.items() if not k == 'options'}
            options = {}
            for option, tree in cur_sum['options'].items():
                new_option = self._append_int_summary_to_externals(int_sum, tree, int_id)
                options[option] = new_option
            new_sum['options'] = options

        else:
            if len(cur_sum) == 0:
                print('append_error - end is empty')
            same_val = int_id['val'] == cur_sum['out']['value']
            same_sub = int_id['sub'] == cur_sum['out']['subscript']
            same_pos = int_id['pos'] == cur_sum['out']['pos']
            if same_pos and same_sub and same_val:
                new_sum = copy.deepcopy(int_sum)
            else:
                new_sum = cur_sum

        return new_sum

    # ----------------------------- #
    # Branch manipulation functions #
    # ----------------------------- #

    def _branch_append_node(self, branch, node_key, node_value, modify=False):
        if isinstance(branch, str):
            print('Branch is a string?')
            return branch
        if 'children' not in branch.keys():
            # print('No children entry, adding entry')
            old_children = {}
        else:
            old_children = branch.pop('children')
        new_branch = branch
        if len(old_children) > 0:
            next_level_key = list(old_children.keys())[0]
            next_level = old_children[next_level_key]
            new_children = {next_level_key: self._branch_append_node(branch=next_level, node_key=node_key,
                                                                     node_value=node_value, modify=modify)}
        elif modify:
            new_branch['modification'] = {node_key: node_value}
            new_children = old_children
        else:
            new_children = {node_key: node_value}
        new_branch['children'] = new_children
        return new_branch

    def _flag_outs_for_removal(self, remove_no_mod=False):
        outs = copy.deepcopy(self.all_outs)
        outs_to_remove = []
        for i, out in enumerate(outs):
            if self._goes_past_out(out):
                outs_to_remove.append(i)

        no_mod = []
        for i, out in enumerate(outs):
            if i in outs_to_remove:
                continue
            elif self._choice_with_no_mod(out):
                no_mod.append(i)
        print(f'({len(no_mod)}) branches found with a choice but no modifier')
        if remove_no_mod:
            outs_to_remove = [*outs_to_remove, *no_mod]
            print('removed...')

        duplicates = []
        checked_outs = []
        for i, out1 in enumerate(outs):
            checked_outs.append(i)
            for j, out2 in enumerate(outs):
                if j in checked_outs:
                    continue
                if self._variables_are_equal_recursive(var1=out1, var2=out2):
                    duplicates.append(j)
        outs_to_remove = [*outs_to_remove, *duplicates]
        print(f'({len(duplicates)}) duplicate branches found')

        return outs_to_remove

    def _goes_past_out(self, out):
        goes_past_out = False
        out_children = out['children']
        if len(out_children) == 0:
            return False
        elif 'out_value' in out_children.keys():
            if 'children' in out_children['out_value'].keys():
                return True

        for child1 in out_children.values():
            for key in child1.keys():
                if goes_past_out:
                    break
                if key == 'children':
                    goes_past_out = self._goes_past_out(out=child1)

        return goes_past_out

    def _choice_with_no_mod(self, out):
        has_no_mod = False
        out_children = out['children']
        if len(out_children) == 0:
            has_no_mod = False
        elif 'choice' in out_children.keys():
            if 'modification' not in out_children['choice'].keys():
                has_no_mod = True

        for child1 in out_children.values():
            for key in child1.keys():
                if has_no_mod:
                    break
                if key == 'children':
                    has_no_mod = self._choice_with_no_mod(out=child1)

        return has_no_mod

    def _branch_has_same_conditions(self, out_branch, open_branch, with_req=False, with_mid=False):
        is_same = True

        # Compare initial ram state
        same_init_ram = self._variables_are_equal_recursive(open_branch['init_ram'], out_branch['init_ram'])
        if not same_init_ram:
            is_same = False

        # Compare requested instruction at start of branch
        if with_req and is_same:
            same_req = self._variables_are_equal_recursive(open_branch['init_value'], out_branch['init_value'])
            if not same_req:
                is_same = False

        if with_mid and is_same:
            open_mid = open_branch['cur_ram']
            if 'new_run' in out_branch.keys():
                out_mid = out_branch['new_run']['mid_ram'][0]
                same_mid_ram = self._variables_are_equal_recursive(open_mid, out_mid)
                if not same_mid_ram:
                    is_same = False
            else:
                out_mid = out_branch['cur_ram']
                same_mid_ram = self._variables_are_equal_recursive(open_mid, out_mid)
                if not same_mid_ram:
                    is_same = False

        return is_same

    def _variables_are_equal_recursive(self, var1, var2):
        if not type(var1) == type(var2):
            return False
        if isinstance(var1, dict):
            for key in var1:
                if key not in var2.keys():
                    return False
            for key, var1_value in var1.items():
                var2_value = var2[key]
                if not self._variables_are_equal_recursive(var1_value, var2_value):
                    return False
        elif isinstance(var1, list):
            if not len(var1) == len(var2):
                return False
            for i in range(len(var1)):
                var1_value = var1[i]
                var2_value = var2[i]
                if not self._variables_are_equal_recursive(var1_value, var2_value):
                    return False
        else:
            if not var1 == var2:
                return False

        return True

    # ---------------------- #
    # Memory state functions #
    # ---------------------- #

    def _set_memory_pos(self, details: dict, ram):
        addr_type = details['type']
        addr = details['addr']
        if addr not in ram.keys():
            if addr not in self.addrs.keys():
                self.addrs[addr] = {'addr_not_init': True, 'size': addr_type}
                self.addrs[addr]['addr_not_init'] = True
            if 'init_loc' not in self.addrs[addr].keys():
                self.addrs[addr]['init_loc'] = 'internal'
            ram[addr] = self.addrs[addr]
        cur_value = self.addrs[addr].get('value', None)
        if addr_type == 'bit':
            if details['action'] == 'set':
                ram[addr]['value'] = 1
            elif details['action'] == 'unset':
                ram[addr]['value'] = 0
            elif details['action'] == 'invert':
                if cur_value is None:
                    cur_value = 0
                ram[addr]['value'] = 1 - cur_value
        else:
            ram[addr]['value'] = details['value']
        return ram

    def _get_memory_pos(self, addr, ram, addr_type):
        if addr not in ram.keys():
            if addr not in self.addrs.keys():
                self.addrs[addr] = {'addr_not_init': True, 'types': addr_type}
            self.addrs[addr]['init_loc'] = 'external'
            cur_value = None
        else:
            cur_value = ram[addr]['value']

        if 'types' not in self.addrs[addr].keys():
            self.addrs[addr]['types'] = addr_type
        else:
            cur_type = self.addrs[addr]['types']
            if addr_type not in cur_type:
                cur_type += f'-{addr_type}'

        return cur_value

    def _get_defined_ram(self, branch=None):
        ram = {}
        if branch is None:
            for addr, addr_dict in self.addrs.items():
                if 'value' in addr_dict.keys():
                    if addr_dict['value'] is not None:
                        ram[addr] = addr_dict
        else:
            ram = branch['current ram']
        return ram

    # ------------ #
    # Jump testing #
    # ------------ #

    def _should_not_jump(self, compare, ram, isBase=False):
        params = []
        comparison = ''
        for value in compare.values():
            for comp, param_list in value.items():
                comparison = comp
                for param in param_list.values():
                    if isinstance(param, dict):
                        params.append(self._should_not_jump(param, ram))
                    else:
                        params.append(param)

        if not len(params) == 2:
            if isBase:
                return False
            else:
                return 1

        param_values = []
        for param in params:
            if isinstance(param, str):
                addr = param.split(': ')[1].rstrip()
                value = self._get_memory_pos(addr, ram, 'control')
                param_values.append(value)
            else:
                param_values.append(param)

        result = self.scpt_codes[comparison](param_values[0], param_values[1])
        if isBase:
            if result == 1:
                return True
            else:
                return False
        return result

    def _can_jump(self, compare, ram):
        for value in compare.values():
            if isinstance(value, dict):
                if not self._can_jump(value, ram):
                    return False
            else:
                if re.search(': ', value):
                    addr = value.split(': ')[1].rstrip()
                    value = self._get_memory_pos(addr, ram, 'control')
                    if value is not None:
                        return True
                    else:
                        return False
        return True

    def _can_switch(self, addr, ram):
        value = self._get_memory_pos(addr, ram, 'control')
        if value is not None:
            return True
        return False

    # ------------------------------- #
    # SCPT Analyze Comparison Methods #
    # ------------------------------- #
    # True returns 1, False returns 0

    @staticmethod
    def _is_lt(in_1, in_2):
        result = in_1 < in_2
        if result:
            return 1
        return 0

    @staticmethod
    def _is_leq(in_1, in_2):
        result = in_1 <= in_2
        if result:
            return 1
        return 0

    @staticmethod
    def _is_gt(in_1, in_2):
        result = in_1 > in_2
        if result:
            return 1
        return 0

    @staticmethod
    def _is_geq(in_1, in_2):
        result = in_1 > in_2
        if result:
            return 1
        return 0

    @staticmethod
    def _is_eq(in_1, in_2):
        result = in_1 == in_2
        if result:
            return 1
        return 0

    @staticmethod
    def _anded(in_1, in_2):
        result = in_1 & in_2
        return result

    @staticmethod
    def _ored(in_1, in_2):
        result = in_1 | in_2
        return result

    @staticmethod
    def _both_true(in_1, in_2):
        if not in_1 == 0 and not in_2 == 0:
            return 1
        return 0

    @staticmethod
    def _either_true(in_1, in_2):
        if not in_1 == 0 or not in_2 == 0:
            return 1
        return 0

    @staticmethod
    def _return_two(in_1, in_2):
        return in_2

    # ------------------------------- #
    # SCPT Analyze Arithmetic Methods #
    # ------------------------------- #

    @staticmethod
    def _multiply(in_1, in_2):
        return in_1 * in_2

    @staticmethod
    def _divide(in_1, in_2):
        return in_1 / in_2

    @staticmethod
    def _mod(in_1, in_2):
        return in_1 % in_2

    @staticmethod
    def _add(in_1, in_2):
        return in_1 + in_2

    @staticmethod
    def _subtract(in_1, in_2):
        return in_1 - in_2

    def _get_dict_depth(self, inp, size=0):
        size += 1
        if isinstance(inp, dict):
            for value in inp.values():
                size = max(self._get_dict_depth(value, size), size)
        return size


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='*', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()