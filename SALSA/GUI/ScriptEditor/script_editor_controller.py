from typing import Union, Dict, Tuple

from GUI.ScriptEditor.script_editor_view import ScriptEditorView
from GUI.widgets import CustomTree2
from Project.project_facade import SCTProjectFacade


tree_children = {
    '': 'script',
    'script': 'section',
    'section': 'instruction',
    'instruction': 'detail'
}

tree_parents = {v: k for k, v in tree_children.items()}


class ScriptEditorController:
    log_name = 'Script Editor Controller'

    def __init__(self, view: ScriptEditorView, facade: SCTProjectFacade):
        self.view: ScriptEditorView = view
        self.project: SCTProjectFacade = facade
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

        self.settings = {
            'group_insts': True,
            'group_sects': True
        }

        self.project.set_callback(key='update_scripts', callback=lambda: self.update_tree('script', self.project.get_tree(self.view.get_headers('script'))))

        self.trees['script'].add_callback('select', self.on_select_tree_entry)
        self.trees['section'].add_callback('select', self.on_select_tree_entry)
        self.trees['instruction'].add_callback('select', self.on_select_tree_entry)

        self.style = 'grouped'

    def update_setting(self, setting, value):
        if setting not in self.settings.keys():
            print(f"{self.log_name}: {setting} not in settings, wasn't set")
            return
        self.settings['setting'] = value

    def load_project(self):
        for key in list(self.current.keys()):
            self.current[key] = None
        for tree in self.trees.values():
            tree.clear_all_entries()
        self.update_tree('script', self.project.get_tree(self.view.get_headers('script')))

    def on_select_tree_entry(self, tree_key, entry):
        if tree_key == 'instruction':
            return self.on_select_instruction(entry)
        kwargs = {'style': self.style}
        self.current[tree_key] = entry
        cur_key = tree_key
        while True:
            kwargs[cur_key] = self.current[cur_key]
            cur_key = tree_parents[cur_key]
            if cur_key == '':
                break
        kwargs['headers'] = self.view.get_headers(tree_key=tree_key)
        tree_list = self.project.get_tree(**kwargs)
        child_tree = tree_children[tree_key]
        self.update_tree(child_tree, tree_list)

    def on_select_instruction(self, instructID):
        self.current['instruction'] = instructID
        details = self.project.get_instruction_details(**self.current)
        self.set_instruction_details(details)

    def update_tree(self, tree, tree_dict: Union[dict, None]):
        self.trees[tree].clear_all_entries()
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
            kwargs = {'parent': parent_list[-1], 'index': 'end', 'text': ''}
            values = []
            for col in headers:
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

    def show_variables(self):
        pass

    def show_strings(self):
        pass

    def show_right_click_menu(self):
        pass
