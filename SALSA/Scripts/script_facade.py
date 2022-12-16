from typing import Union

from SALSA.Scripts.script_container import SCTProject


class SCTProjectFacade:

    project: Union[SCTProject, None]

    def __init__(self, project: Union[SCTProject, None]):
        self.project = project

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
            if style == 'grouped':
                return self.project.scripts[script].grouped_section_names
            else:
                return list(self.project.scripts[script].sections.keys())

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


