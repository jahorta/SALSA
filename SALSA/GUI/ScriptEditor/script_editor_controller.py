from typing import Union, Dict

from GUI.ScriptEditor.script_editor_view import ScriptEditorView
from GUI.widgets import CustomTree
from Project.project_facade import SCTProjectFacade


class ScriptEditorController:
    log_name = 'Script Editor Controller'

    def __init__(self, view: ScriptEditorView, facade: SCTProjectFacade):
        self.view: ScriptEditorView = view
        self.project: SCTProjectFacade = facade
        self.cur_script: Union[str, None] = None
        self.cur_sect: Union[str, None] = None
        self.cur_inst: Union[int, None] = None
        self.trees: Dict[str, CustomTree] = {
            'script': self.view.scripts_tree,
            'section': self.view.sections_tree,
            'instruction': self.view.insts_tree
        }

        self.settings = {
            'group_insts': True,
            'group_sects': True
        }

        # Send callbacks to the facade?

    def update_setting(self, setting, value):
        if setting not in self.settings.keys():
            print(f"{self.log_name}: {setting} not in settings, wasn't set")
            return
        self.settings['setting'] = value

    def load_project(self):
        self.cur_script: Union[str, None] = None
        self.cur_sect: Union[str, None] = None
        self.cur_inst: Union[int, None] = None
        for tree in self.trees.values():
            tree.clear_all_entries()

        scripts = self.project.get_tree()
        scripts = sorted(scripts)
        self.update_tree('script', scripts)

    def on_create_breakpoints(self, newID):
        pass

    def on_select_script(self, scriptID):
        self.cur_script = scriptID
        tree = self.project.get_tree(script=scriptID)
        self.update_tree('section', tree)

    def on_select_section(self, sectionID):
        self.cur_sect = sectionID
        tree = self.project.get_tree(script=self.cur_script, section=sectionID)
        self.update_tree('instruction', tree)

    def on_select_instruction(self, instructID):
        self.cur_inst = instructID
        details = self.project.get_instruction_details(self.cur_script, self.cur_sect, self.cur_inst)
        self.set_instruction_details(details)

    def update_tree(self, tree, tree_list: Union[list, None]):
        """
        Updates specified tree using a provided tree list. Tree list should contain either a set or dict.
        A set indicates that the entry should be a row with ('text', 'row_data'). A dict indicates the entry should
        start a new group. it should contain {'text': the text to display, text: this key is the value of text and
        it should contain a list of entries that are inside the group, 'data': row_data
        """
        self.trees[tree].clear_all_entries()
        if tree_list is None:
            return
        tree = self.trees[tree]
        self._add_tree_entries(tree, tree_list)

    def _add_tree_entries(self, tree, tree_list):
        if not isinstance(tree_list, list):
            return
        for entry in tree_list:
            if not isinstance(entry, dict):
                tree.add_row(text=entry[0], row_data=entry[1])
                continue
            text = entry['text']
            group = entry[text]
            data = entry['data']
            tree.start_group(text=text, row_data=data)
            self._add_tree_entries(tree, group)
            tree.end_group()

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
