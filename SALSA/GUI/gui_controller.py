import tkinter as tk
from typing import Union, TypedDict, Literal

from GUI.AnalysisPopup.analysis_controller import AnalysisController
from GUI.HelpPopup.help_controller import HelpController
from GUI.InstructionEditor.instruction_editor_controller import InstructionEditorController
from GUI.other_popups import AboutView
from BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.GUI.AnalysisPopup.analysis_view import AnalysisView
from SALSA.GUI.HelpPopup.help_view import HelpView
from SALSA.GUI.InstructionEditor.instruction_editor_view import InstructionEditorView
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from GUI.SCTExport.sct_export_popup import SCTExportPopup
from GUI.VariableEditor.variable_editor_popup import VariablePopup
from GUI.StringEditor.string_editor_popup import StringPopup
from Project.project_facade import SCTProjectFacade
from Common.containers import Vector2


class PopupTypes(TypedDict):
    inst: Union[None, InstructionEditorController]
    analysis: Union[None, AnalysisController]
    help: Union[None, HelpController]
    about: Union[None, AboutView]
    variable: Union[None, VariablePopup]
    string: Union[None, StringPopup]
    export: Union[None, SCTExportPopup]


class GUIController:
    parent: tk.Tk
    scpt_view: ProjectEditorView

    def __init__(self, parent, scpt_editor_view: ProjectEditorView, project_facade: SCTProjectFacade,
                 inst_lib_facade: BaseInstLibFacade):

        self.parent = parent
        self.scpt_view = scpt_editor_view
        self.project = project_facade
        self.base_lib = inst_lib_facade

        self.popups: PopupTypes = {'inst': None, 'analysis': None, 'help': None, 'about': None,
                                   'variable': None, 'string': None, 'export': None}

        self.callbacks = {}

        self.status_popup: Union[None, tk.Toplevel] = None

    # ------------------------------------------------------------- #
    # Functions to inactivate script view when no project is loaded #
    # ------------------------------------------------------------- #

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
                    or 'datatreeview' in r \
                    or 'scrollbar' in r \
                    or 'separator' in r \
                    or 'message' in r \
                    or 'menu' in r \
                    or 'panedwindow' in r:
                self.recursive_toggle(child, state)
            else:
                child.configure(state=state)

    # ------------------------ #
    # Functions to show popups #
    # ------------------------ #

    def show_instruction_view(self):
        if self.popups['inst'] is not None:
            self.popups['inst'].view.tkraise()
            return

        callbacks = {
            'close': self.close_popup
        }
        self.popups['inst'] = InstructionEditorController(parent=self.parent, callbacks=callbacks,
                                                          inst_lib_facade=self.base_lib, name='inst')

    def show_analysis_view(self):
        # self.popups['analysis'] = AnalysisController()
        pass

    def show_about(self):
        position = Vector2(x=self.parent.winfo_x(), y=self.parent.winfo_y())
        self.popups['about'] = AboutView(parent=self.parent, position=position, callback=self.close_popup)

    def show_help(self):
        pass
        # self.help_view = HelpView(self.parent, callbacks={'close': self.close_popup}, )
        # self.help_controller = HelpController(self.help_view)

    def show_settings(self):
        pass

    def show_variables_popup(self):
        if self.popups['variable'] is not None:
            self.popups['variable'].tkraise()
            return
        callbacks = {
            'get_scripts': lambda: self.project.get_tree(self.scpt_view.get_headers('script')),
            'get_variables': self.project.get_script_variables_with_aliases,
            'set_alias': self.project.set_variable_alias,
            'get_var_usage': self.project.get_variable_usages,
            'close': self.close_popup
        }
        self.popups['variable'] = VariablePopup(self.parent, callbacks=callbacks, name='variable')

    def show_strings_popup(self):
        pass

    def show_sct_export_popup(self, selected=None):
        if self.popups['export'] is not None:
            self.popups['export'].tkraise()
            return
        callbacks = {
            'export': self.callbacks['export_sct'], 'close': self.close_popup,
            'get_tree': lambda: self.project.get_tree(self.scpt_view.get_headers('script')),
        }
        self.popups['export'] = SCTExportPopup(self.parent, callbacks=callbacks, name='export', selected=selected)

    # ----------------------- #
    # Popup cleanup functions #
    # ----------------------- #

    def close_popup(self, name: Literal['inst', 'analysis', 'help', 'about', 'variable', 'string', 'export'],
                    popup: Union[InstructionEditorView, AnalysisView, HelpView, AboutView, SCTExportPopup, VariablePopup, StringPopup]):
        popup.destroy()
        self.popups[name] = None

    def add_callbacks(self, callbacks):
        self.callbacks = {**self.callbacks, **callbacks}

    # ---------------------- #
    # Status popup functions #
    # ---------------------- #

    def show_status_popup(self, title, msg):
        height = 50
        width = 300
        self.status_popup = tk.Toplevel(self.scpt_view)
        self.status_popup.title = title
        self.status_popup.overrideredirect(True)
        self.status_popup.columnconfigure(0, weight=1)
        self.status_popup.rowconfigure(0, weight=1)
        msg_lbl = tk.Label(self.status_popup, text=msg, anchor=tk.CENTER)
        msg_lbl.grid(row=0, column=0)

        cur_geom = (self.scpt_view.winfo_width(), self.scpt_view.winfo_height(), self.scpt_view.winfo_rootx(), self.scpt_view.winfo_rooty())
        x = cur_geom[2] + cur_geom[0] // 2 - width // 2
        y = cur_geom[3] + cur_geom[1] // 2 - height // 2
        new_geom = f'{width}x{height}+{x}+{y}'
        self.status_popup.geometry(new_geom)

    def stop_status_popup(self):
        self.status_popup.destroy()
        self.status_popup = None


