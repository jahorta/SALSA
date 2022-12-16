import tkinter as tk
from typing import Union

from GUI.ScriptEditor.script_editor_view import ScriptEditorView
from Scripts.script_facade import SCTProjectFacade


class ScriptEditorController:

    def __init__(self, view: ScriptEditorView, facade: SCTProjectFacade):
        self.view: ScriptEditorView = view
        self.project: SCTProjectFacade = facade
        self.cur_script: Union[str, None] = None
        self.cur_sect: Union[str, None] = None
        self.cur_inst: Union[int, None] = None

    def load_project(self):
        self.cur_script: Union[str, None] = None
        self.cur_sect: Union[str, None] = None
        self.cur_inst: Union[int, None] = None
        self.view.scripts_tree.clear_all_entries()
        self.view.sections_tree.clear_all_entries()
        self.view.insts_tree.clear_all_entries()

        scripts = self.project.get_tree()
        for script in sorted(scripts):
            self.view.scripts_tree.add_row(text=script)

    def refresh_tree(self, tree: int):
        pass

    def on_create_breakpoints(self, newID):
        pass

    def on_select_script(self, newID):
        pass

    def on_select_script_instruction(self, scriptID, instructID):
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
