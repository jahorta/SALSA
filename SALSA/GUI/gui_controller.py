import tkinter as tk
from typing import Union

from GUI.AnalysisPopup.analysis_controller import AnalysisController
from GUI.HelpPopup.help_controller import HelpController
from GUI.InstructionEditor.instruction_editor_controller import InstructionEditorController
from GUI.other_popups import AboutView
from BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.GUI.AnalysisPopup.analysis_view import AnalysisView
from SALSA.GUI.HelpPopup.help_view import HelpView
from SALSA.GUI.InstructionEditor.instruction_editor_view import InstructionEditorView
from SALSA.GUI.ScriptEditor.script_editor_view import ScriptEditorView
from Project.project_facade import SCTProjectFacade
from Common.containers import Vector2


class GUIController:

    parent: tk.Tk
    instruction_view: Union[None, InstructionEditorView]
    instruction_controller: Union[None, InstructionEditorController]
    scpt_view: ScriptEditorView
    analysis_view: Union[None, AnalysisView]
    analysis_controller: Union[None, AnalysisController]
    help_view: Union[None, HelpView]
    help_controller: Union[None, HelpController]
    about_view: Union[None, AboutView]

    def __init__(self, parent, scpt_editor_view: ScriptEditorView, project_facade: SCTProjectFacade,
                 inst_lib_facade: BaseInstLibFacade):

        self.parent = parent
        self.scpt_view = scpt_editor_view
        self.project = project_facade
        self.base_lib = inst_lib_facade

        self.popup_cleanup = {
            InstructionEditorView: self._inst_view_cleanup,
            AnalysisView: self._analysis_view_cleanup,
            HelpView: self._help_view_cleanup,
            AboutView: self._about_view_cleanup
        }

        self.popup_close_check = {
            InstructionEditorView: self._instruction_edit_check,
            AnalysisView: self._no_check,
            HelpView: self._no_check,
            AboutView: self._no_check
        }

        self.callbacks = {}

    def show_instruction_view(self, inst_lib, callbacks, position):
        self.instruction_view = InstructionEditorView(self.parent, inst_lib, callbacks, position)
        self.instruction_controller = InstructionEditorController(view=self.instruction_view, callbacks=callbacks,
                                                                  inst_lib_facade=inst_lib, position=position)

    def show_analysis_view(self):
        self.analysis_view = AnalysisView(self.parent)
        self.analysis_controller = AnalysisController(self.analysis_view)

    def update_all_views(self):
        self.scpt_view.refresh_views()

    def enable_script_view(self):
        self.recursive_toggle(self.scpt_view, 'normal')
        self.callbacks['script']()

    def disable_script_view(self):
        self.recursive_toggle(self.scpt_view, 'disabled')
        self.callbacks['no_script']()

    def recursive_toggle(self, parent, state):
        for child in parent.winfo_children():
            r = child.__repr__().split('.')[-1]
            if 'frame' in r \
                    or 'labelframe' in r \
                    or 'customtree' in r\
                    or 'scrollbar' in r\
                    or 'panedwindow' in r:
                self.recursive_toggle(child, state)
            else:
                child.configure(state=state)

    def show_about(self):
        position = Vector2(x=self.parent.winfo_x(), y=self.parent.winfo_y())
        self.about_view = AboutView(parent=self.parent, position=position, callback=self.close_popup)

    def show_help(self):
        pass
        # self.help_view = HelpView(self.parent, callbacks={'close': self.close_popup}, )
        # self.help_controller = HelpController(self.help_view)

    def show_settings(self):
        pass

    def _instruction_edit_check(self):
        pass

    def _no_check(self):
        pass

    def _inst_view_cleanup(self):
        self.instruction_view = None
        self.instruction_controller = None

    def _analysis_view_cleanup(self):
        self.analysis_view = None
        self.analysis_controller = None

    def _help_view_cleanup(self):
        self.help_view = None
        self.help_controller = None

    def _about_view_cleanup(self):
        self.about_view = None

    def close_popup(self, popup: Union[InstructionEditorView, AnalysisView, HelpView, AboutView]):
        p_type = type(popup)
        if not self.popup_close_check[p_type]():
            return
        popup.destroy()
        self.popup_cleanup[p_type]()

    def add_callbacks(self, callbacks):
        self.callbacks = {**self.callbacks, **callbacks}
        print('added')

