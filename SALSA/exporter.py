from typing import List

from SALSA.instruction_class import Instruct
from SALSA.script_class import SCTAnalysis
from SALSA.constants import FieldTypes as FT

class SCTExporter:

    export_options = {
        'Ship battle turn data': {
            'scripts': '^me50.+sct$',
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
            ]
        }
    }

    export_option_fields = {'types': {'req': True, 'type': FT.string_list, 'values': []}}

    def __init__(self, loc=None):
        self.dir = loc
        self.script_list: List[SCTAnalysis] = []
        self.instruction_list: List[Instruct] = []

        self.export_functions = {
            'Ship battle turn data': self._ship_battle_data
        }

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
        script_info_list = {'headers': {}}
        for inst, groups in self.export_options[export_type]['instructions'].items():
            for group_name, group in groups.items():
                script_info_list['headers'][group_name] = self.instruction_list[str(inst)].get_param_names(group)

        for i, sct in enumerate(self.script_list):
            print(f'Getting information for {sct.Name}: {i+1}/{len(self.script_list)}')
            script_info_out = sct.get_info_by_group(self.export_options[export_type]['instructions'])
            script_info_list[sct.Name] = script_info_out

        return self.export_functions[export_type](info_list=script_info_list, **export_args)

    def _ship_battle_data(self, info_list, combine=False):
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

            for name, sct in scripts.items():
                header_rows[0] += f',{name},,,'
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
            print('pause here')

        return outs






