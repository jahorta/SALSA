from typing import Union, Dict
import tkinter as tk

from Common.setting_class import settings
from GUI.ProjectEditor.variable_editor_popup import VariablePopup
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.ProjectEditor.sct_export_popup import SCTExportPopup
from SALSA.GUI.widgets import DataTreeview
from SALSA.Project.project_facade import SCTProjectFacade
from SALSA.Project.project_container import SCTParameter
from SALSA.BaseInstructions.bi_container import BaseParam

tree_children = {
    '': 'script',
    'script': 'section',
    'section': 'instruction',
    'instruction': 'parameter',
    'parameter': ''
}

tree_parents = {v: k for k, v in tree_children.items()}


class ProjectEditorController:
    log_name = 'PrjEditorCtrl'

    default_settings = {
        'style': 'grouped'
    }

    def __init__(self, parent: tk.Tk, view: ProjectEditorView, facade: SCTProjectFacade, callbacks):
        self.parent: tk.Tk = parent
        self.view: ProjectEditorView = view
        self.project: SCTProjectFacade = facade
        self.callbacks = callbacks

        if self.log_name not in settings:
            settings[self.log_name] = {}

        for s, v in self.default_settings.items():
            if s not in settings[self.log_name]:
                settings[self.log_name][s] = v

        self.current: Dict[str, Union[int, None]] = {
            'script': None,
            'section': None,
            'instruction': None,
            'parameter': None
        }

        self.trees: Dict[str, DataTreeview] = {
            'script': self.view.scripts_tree,
            'section': self.view.sections_tree,
            'instruction': self.view.insts_tree,
            'parameter': self.view.param_tree
        }

        self.project.set_callback(key='update_scripts', callback=lambda: self.update_tree('script', self.project.get_tree(self.view.get_headers('script'))))

        self.trees['script'].add_callback('select', self.on_select_tree_entry)
        self.trees['section'].add_callback('select', self.on_select_tree_entry)
        self.trees['instruction'].add_callback('select', self.on_select_tree_entry)
        self.trees['parameter'].add_callback('select', self.on_select_tree_entry)

    def load_project(self):
        for key in list(self.current.keys()):
            self.current[key] = None
        for tree in self.trees.values():
            tree.clear_all_entries()
        self.update_tree('script', self.project.get_tree(self.view.get_headers('script')))

    def on_select_tree_entry(self, tree_key, entry):
        if tree_key == 'instruction':
            return self.on_select_instruction(entry)
        if tree_key == 'parameter':
            return self.on_select_parameter(entry)
        kwargs = {'style': settings[self.log_name]['style']}
        self.current[tree_key] = entry
        cur_key = tree_key
        while True:
            kwargs[cur_key] = self.current[cur_key]
            cur_key = tree_parents[cur_key]
            if cur_key == '':
                break
        child_tree = tree_children[tree_key]
        kwargs['headers'] = self.view.get_headers(tree_key=child_tree)
        tree_list = self.project.get_tree(**kwargs)
        self.update_tree(child_tree, tree_list)

    def on_select_instruction(self, instructID):
        self.current['instruction'] = instructID
        self.current['parameter'] = None
        details = self.project.get_instruction_details(**self.current)
        details['parameter_tree'] = self.project.get_parameter_tree(headings=self.view.get_headers('parameter'), **self.current)
        self.set_instruction_details(details)

    def on_select_parameter(self, paramID):
        self.current['parameter'] = paramID
        param_details = self.project.get_parameter_details(**self.current)

    def clear_tree(self, tree: str):
        if tree in self.trees.keys():
            self.trees[tree].clear_all_entries()

    def update_tree(self, tree, tree_dict: Union[dict, None]):
        if tree is None:
            for tree in self.trees.keys():
                self.clear_tree(tree)
            return

        # Clear the current tree and all child trees to prevent desync
        cur_tree = tree
        trees_to_clear = [cur_tree]
        while cur_tree != '':
            trees_to_clear.append(tree_children[cur_tree])
            cur_tree = tree_children[cur_tree]
        for t in trees_to_clear:
            self.clear_tree(t)

        if tree_dict is None:
            return

        self._add_tree_entries(tree, tree_dict)

    def _add_tree_entries(self, tree_key: str, tree_list):
        tree = self.trees[tree_key]
        if not isinstance(tree_list, list):
            return
        parent_list = ['']
        prev_iid = -1
        headers = self.view.get_headers(tree_key)
        for entry in tree_list:
            if isinstance(entry, str):
                if entry == 'group':
                    parent_list.append(prev_iid)
                elif entry == 'ungroup':
                    if len(parent_list) == 1:
                        raise RuntimeError(f'{self.log_name}: unable to lower group level, not enough groups left')
                    parent_list.pop()
                else:
                    raise ValueError(f'{self.log_name}: Unknown command in tree list sent to _add_tree_entries')
                continue
            kwargs = {'parent': parent_list[-1], 'index': 'end'}
            values = []
            first = True
            for col in headers:
                if col == 'name':
                    if 'group_type' in entry.keys():
                        entry[col] += f' ({entry["group_type"]})'
                if first:
                    kwargs['text'] = entry[col]
                    first = False
                else:
                    values.append(entry[col])
                entry.pop(col)
            kwargs['values'] = values
            kwargs = {**kwargs, **entry}
            prev_iid = tree.insert_entry(**kwargs)

    def set_instruction_details(self, details):
        if details is None:
            return
        self.view.inst_label.config(text=f'{details["instruction_id"]} - {details["name"]}')
        self.view.inst_description.config(text=details['description'])
        for i in details['params_before']:
            param: SCTParameter = details['parameters'][i]
            self._add_tree_entries('parameter', )
            self.view.param_tree.insert_entry(parent='', text=i, values=param)

        self.view.set_refresh_value(details['no_new_frame'], details['forced_new_frame'], details['skip_refresh'])

        # Guard clause to prevent adding loop parameters if there is no loop in the instruction
        if details['loop'] is None:
            return

    def on_script_display_change(self, mode):
        pass

    def on_instruction_display_change(self, scriptID, mode):
        pass

    def on_set_inst_start(self, start, newID):
        pass

    def show_right_click_menu(self):
        pass

