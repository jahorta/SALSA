import os
from typing import Union

from Project.jsonize_project import jsonize_project
from Project.project_container import SCTProject
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade


class SCTProjectFacade:

    project: Union[SCTProject, None]

    def __init__(self):
        self.project = None
        self.callbacks = None

    def set_project(self, project):
        pass

    def create_new_project(self):
        self.project = SCTProject()

    def get_tree(self, script=None, section=None, style='grouped'):
        if self.project is None:
            return
        if script is None:
            return list(self.project.scripts.keys())
        elif section is None:
            if style == 'grouped':
                return self.project.scripts[script].grouped_section_names
            else:
                return list(self.project.scripts[script].sections.keys())
        else:
            base_insts: BaseInstLibFacade = self.callbacks['base_insts']()
            instructions = self.project.scripts[script].sections[section].instructions
            instruction_names = [f'{i}: {inst.inst_id} - {base_insts.get_inst(i).name}'
                                 for i, inst in enumerate(instructions)]
            if style == 'grouped':
                instruction_grouping = self.project.scripts[script].sections[section].instructions_grouped
                return {'names': instruction_names, 'groups': instruction_grouping}
            else:
                return {'names': instruction_names}

    def get_instruction_details(self, script, section, instruction):
        base_insts: BaseInstLibFacade = self.callbacks['base_insts']()
        instruction = self.project.scripts[script].sections[section].instructions[instruction]
        instruction_details = {}
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

    def get_cur_project_json(self):
        project = jsonize_project(self.project)
        return project

    def add_script_to_project(self, script_name, script):
        self.project.scripts[script_name] = script
