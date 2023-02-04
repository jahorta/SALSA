from typing import Union, Dict
import tkinter as tk

from Common.setting_class import settings
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.ProjectEditor.sct_export_popup import SCTExportPopup
from SALSA.GUI.widgets import CustomTree2
from SALSA.Project.project_facade import SCTProjectFacade


tree_children = {
    '': 'script',
    'script': 'section',
    'section': 'instruction',
    'instruction': 'detail'
}

tree_parents = {v: k for k, v in tree_children.items()}


class ProjectEditorController:
    log_name = 'PrjEditorCtrl'

    popup_names = {
        SCTExportPopup: 'SCTExport'
    }

    sct_export_popup: Union[None, SCTExportPopup] = None

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
            'instruction': None
        }

        self.trees: Dict[str, CustomTree2] = {
            'script': self.view.scripts_tree,
            'section': self.view.sections_tree,
            'instruction': self.view.insts_tree
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
        self.update_tree(child_tree, tree_list)

    def on_select_instruction(self, instructID):
        self.current['instruction'] = instructID
        details = self.project.get_instruction_details(**self.current)
        self.set_instruction_details(details)

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
        while cur_tree in tree_children.keys():
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
                        raise RuntimeError(f'SEController: unable to lower group level, not enough groups left')
                    parent_list.pop()
                else:
                    raise ValueError(f'SEController: Unknown command in tree list sent to _add_tree_entries')
                continue
            kwargs = {'parent': parent_list[-1], 'index': 'end'}
            values = []
            first = True
            for col in headers:
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
        pass

    def on_script_display_change(self, mode):
        pass

    def on_instruction_display_change(self, scriptID, mode):
        pass

    def on_set_inst_start(self, start, newID):
        pass

    # ################################ #
    # Project Editing Popup Controller #
    # ################################ #

    # ---------------------------------- #
    # Instruction Editor Popup Functions #
    # ---------------------------------- #

    def show_instructions_popup(self):
        pass

    # ------------------------------- #
    # Variable Editor Popup Functions #
    # ------------------------------- #

    def show_variables_popup(self):
        pass

    # ----------------------------- #
    # String Editor Popup Functions #
    # ----------------------------- #

    def show_strings_popup(self):
        pass

    # -------------------------- #
    # SCT Export Popup Functions #
    # -------------------------- #

    def show_sct_export_popup(self, selected=None):
        callbacks = {
            'export': self.callbacks['export_sct'], 'cancel': self.close_popup,
            'get_tree': lambda: self.project.get_tree(self.view.get_headers('script'))
            }
        self.sct_export_popup = SCTExportPopup(self.parent, callbacks=callbacks, name=self.popup_names[SCTExportPopup], selected=selected)

    # ----------------------- #
    # General popup functions #
    # ----------------------- #

    def close_popup(self, name):
        if name == self.popup_names[SCTExportPopup]:
            self.sct_export_popup.destroy()
            self.sct_export_popup = None

    def show_right_click_menu(self):
        pass

