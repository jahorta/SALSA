from typing import List

from SALSA.instruction_class import Instruct
from script_class import SCTAnalysis

class SCTExporter:

    export_options = {
        'Ship battle turn data': {
            'scripts': '^me5.+.sct$',
            'instructions': {
                165: {
                    'turn bonus': [
                        9, 10, 11, 12
                    ],
                    'lost turns': [
                        13, 14, 15, 16
                    ]
                }
            }
        }
    }

    def __init__(self, loc):
        self.dir = loc
        self.script_list: List[SCTAnalysis] = []
        self.instruction_list: List[Instruct] = []

        self.export_functions = {
            'Ship battle turn data': self._ship_battle_data
        }

    def get_export_scripts(self):
        return self.export_functions['scripts']

    def export(self, sct_list, instruction_list, export_type, export_args: dict):
        self.script_list = sct_list
        self.instruction_list = instruction_list
        script_info_list = {'headers': {}}
        for inst, groups in self.export_options[export_type]['instructions'].items():
            for group_name, group in groups.items():
                script_info_list['headers'][group_name] = self.instruction_list[inst].get_param_names(group)

        for sct in self.script_list:
            script_info_out = sct.get_info_by_group(self.export_options[export_type]['instructions'])
            script_info_list[sct.Name] = script_info_out

        self.export_functions[export_type](info_list=script_info_list, **export_args)

    def _ship_battle_data(self, info_list, **args):
        print('check whats here')


