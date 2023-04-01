from typing import Union, Dict
import tkinter as tk

from GUI.ProjectEditor.ParamEditorPopups.param_editor_controller import ParamEditController
from SALSA.Common.setting_class import settings
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.widgets import DataTreeview
from SALSA.Project.project_facade import SCTProjectFacade
from SALSA.Project.project_container import SCTLink

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

        view_callbacks = {
            'update_field': self.update_field,
            'edit_param': self.on_edit_parameter,
            'show_header_selection_menu': self.show_header_selection_menu
        }
        self.view.add_and_bind_callbacks(view_callbacks)

        self.project: SCTProjectFacade = facade
        self.callbacks = callbacks

        self.param_editor = ParamEditController(self.view, callbacks={'get_var_alias': self.get_var_alias})

        if self.log_name not in settings:
            settings[self.log_name] = {}

        for s, v in self.default_settings.items():
            if s not in settings[self.log_name]:
                settings[self.log_name][s] = v

        self.current: Dict[str, Union[str, None]] = {
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

    def load_project(self):
        for key in list(self.current.keys()):
            self.current[key] = None
        for tree in self.trees.values():
            tree.clear_all_entries()
        self.update_tree('script', self.project.get_tree(self.view.get_headers('script')))

    def on_select_tree_entry(self, tree_key, entry):
        self.clear_inst_details()
        if tree_key == 'instruction':
            return self.on_select_instruction(entry)
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
        tree_list = self.adjust_tree_entries(tree_list, child_tree)
        self.update_tree(child_tree, tree_list)

    def adjust_tree_entries(self, entries, key):
        if key == 'instruction':
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                entry['frame_delay_param'] = '*' if entry['frame_delay_param'] != 'None' else ''
                entry['skip_refresh'] = '*' if entry['skip_refresh'] == 'True' else ''

        return entries

    def on_select_instruction(self, instructID):
        self.current['instruction'] = instructID
        self.current['parameter'] = None
        details = self.project.get_instruction_details(**self.current)
        if details is None:
            return
        details['parameter_tree'] = self.project.get_parameter_tree(headings=self.view.get_headers('parameter'), **self.current)
        self.set_instruction_details(details)

    def on_edit_parameter(self, paramID):
        paramID = str(paramID)
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

        self.update_tree('parameter', details['parameter_tree'])

        self.view.skip_ckeck_var.set(int(details['skip_refresh']))
        if details['no_new_frame']:
            self.view.skip_error_label.config(text='This instruction never skips')
        elif details['forced_new_frame']:
            self.view.skip_error_label.config(text='This instruction always skips')
        else:
            self.view.skip_error_label.config(text='')

        for i, link in enumerate(details['links_out']):
            link: SCTLink
            if link.target_trace is None:
                continue
            tgt_sect = link.target_trace[0]
            tgt_section = tk.Label(self.view.link_out.scroll_frame, text=tgt_sect)
            tgt_section.grid(row=i, column=0)

            tgt_inst = self.project.get_inst_ind(script=self.current['script'], section=tgt_sect, inst=link.target_trace[1])
            tgt_instruction = tk.Label(self.view.link_out.scroll_frame, text=tgt_inst)
            tgt_instruction.grid(row=i, column=1)

        for i, link in enumerate(details['links_in']):
            link: SCTLink
            if link.origin_trace is None:
                continue
            ori_sect = link.origin_trace[0]
            ori_section = tk.Label(self.view.link_in.scroll_frame, text=ori_sect)
            ori_section.grid(row=i, column=0)

            ori_inst = self.project.get_inst_ind(script=self.current['script'], section=ori_sect, inst=link.origin_trace[1])
            ori_instruction = tk.Label(self.view.link_in.scroll_frame, text=ori_inst)
            ori_instruction.grid(row=i, column=1)

    def clear_inst_details(self):
        self.view.inst_label.config(text='ID - Name')
        self.view.inst_description.config(text='')

        for child in self.view.link_out.scroll_frame.winfo_children():
            child.destroy()

        for child in self.view.link_in.scroll_frame.winfo_children():
            child.destroy()

    def on_script_display_change(self, mode):
        pass

    def on_instruction_display_change(self, scriptID, mode):
        pass

    def on_set_inst_start(self, start, newID):
        pass

    def show_right_click_menu(self):
        pass
