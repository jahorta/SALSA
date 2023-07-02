import os.path
import tkinter as tk
from tkinter import ttk
from typing import Union, TypedDict, Literal
import webbrowser

from SALSA.GUI.themes import light_theme, dark_theme
from SALSA.GUI import widgets as w
from SALSA.GUI.AnalysisPopup.analysis_controller import AnalysisController
from SALSA.GUI.InstructionEditor.instruction_editor_controller import InstructionEditorController
from SALSA.GUI.other_popups import AboutView
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.GUI.AnalysisPopup.analysis_view import AnalysisView
from SALSA.GUI.InstructionEditor.instruction_editor_view import InstructionEditorView
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.SCTExport.sct_export_popup import SCTExportPopup
from SALSA.GUI.VariableEditor.variable_editor_popup import VariablePopup
from SALSA.GUI.StringEditor.string_editor_popup import StringPopup
from SALSA.Project.project_facade import SCTProjectFacade
from SALSA.Common.containers import Vector2


class PopupTypes(TypedDict):
    inst: Union[None, InstructionEditorController]
    analysis: Union[None, AnalysisController]
    about: Union[None, AboutView]
    variable: Union[None, VariablePopup]
    string: Union[None, StringPopup]
    export: Union[None, SCTExportPopup]


class GUIController:
    parent: tk.Tk
    scpt_view: ProjectEditorView

    def __init__(self, parent, scpt_editor_view: ProjectEditorView, project_facade: SCTProjectFacade,
                 inst_lib_facade: BaseInstLibFacade):

        self.help_path = os.path.abspath('./SALSA/Help/Skies of Arcadia Legends Script Assistant.html')
        self.parent = parent
        self.scpt_view = scpt_editor_view
        self.project = project_facade
        self.base_lib = inst_lib_facade

        self.popups: PopupTypes = {'inst': None, 'analysis': None, 'about': None,
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

    def toggle_frame_state(self, frame, state: Literal['normal', 'disabled']):
        self.recursive_toggle(frame, state)

    def recursive_toggle(self, parent, state):
        for child in parent.winfo_children():
            r = child.__repr__().split('.')[-1]

            # capture the children of the scroll frame
            if isinstance(child, w.ScrollLabelFrame) or isinstance(child, w.ScrollFrame):
                self.recursive_toggle(child.scroll_frame, state)

            child_type = type(child)
            # ttk containers do both
            if child_type in (ttk.PanedWindow, ttk.Frame, ttk.LabelFrame):
                ttk_state = state
                ttk_state = ttk_state if ttk_state != 'normal' else '!disabled'
                child.state([ttk_state])
                self.recursive_toggle(child, state)

            # tk containers and tk fields with no state
            elif child_type in (
            tk.Frame, tk.LabelFrame, tk.Message, tk.Menu, tk.Menubutton, w.ScrollFrame, w.ScrollLabelFrame):
                self.recursive_toggle(child, state)

            # ttk widgets
            elif type(child) in (
            ttk.Button, ttk.Checkbutton, w.DataTreeview, ttk.Treeview, ttk.Scrollbar, ttk.Label, ttk.Separator):
                ttk_state = state
                ttk_state = ttk_state if ttk_state != 'normal' else '!disabled'
                child.state([ttk_state])
            # tk widgets
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
                                                          inst_lib_facade=self.base_lib, name='inst',
                                                          is_darkmode=self.callbacks['is_darkmode']())

    def show_analysis_view(self):
        # self.popups['analysis'] = AnalysisController()
        pass

    def show_about(self):
        position = Vector2(x=self.parent.winfo_x(), y=self.parent.winfo_y())
        self.popups['about'] = AboutView(parent=self.parent, position=position, callback=self.close_popup)

    def show_help(self):
        webbrowser.open(url='file://' + self.help_path)

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
            'remove_global': self.project.remove_global,
            'get_var_usage': self.project.get_variable_usages,
            'close': self.close_popup
        }
        self.popups['variable'] = VariablePopup(self.parent, callbacks=callbacks, name='variable',
                                                is_darkmode=self.callbacks['is_darkmode']())

    def show_strings_popup(self):
        if self.popups['string'] is not None:
            self.popups['string'].tkraise()
            return
        callbacks = {
            'save': self.project.edit_string, 'close': self.close_popup,
            'get_scripts': lambda: self.project.get_tree(self.scpt_view.get_headers('script')),
            'get_string_tree': self.project.get_string_tree, 'get_string_to_edit': self.project.get_string_to_edit
        }
        self.popups['string'] = StringPopup(self.parent, callbacks=callbacks, name='string',
                                            is_darkmode=self.callbacks['is_darkmode']())

    def show_sct_export_popup(self, selected=None):
        if self.popups['export'] is not None:
            self.popups['export'].tkraise()
            return
        callbacks = {
            'export': self.callbacks['export_sct'], 'close': self.close_popup,
            'get_tree': lambda: self.project.get_tree(self.scpt_view.get_headers('script')),
        }
        self.popups['export'] = SCTExportPopup(self.parent, callbacks=callbacks, name='export', selected=selected,
                                                is_darkmode=self.callbacks['is_darkmode']())

    # ----------------------- #
    # Popup cleanup functions #
    # ----------------------- #

    def close_popup(self, name: Literal['inst', 'analysis', 'about', 'variable', 'string', 'export'],
                    popup: Union[
                        InstructionEditorView, AnalysisView, AboutView, SCTExportPopup, VariablePopup, StringPopup]):
        popup.destroy()
        self.popups[name] = None

    def add_callbacks(self, callbacks):
        self.callbacks = {**self.callbacks, **callbacks}

    # ---------------------- #
    # Status popup functions #
    # ---------------------- #

    def show_status_popup(self, title, msg):
        if self.status_popup is not None:
            self.stop_status_popup()
        height = 50
        width = 300
        theme = dark_theme if self.callbacks['is_darkmode']() else light_theme
        bg = theme['TLabelframe']['configure']['highlightbackground']
        fg = theme['.']['configure']['foreground']
        self.status_popup = tk.Toplevel(self.scpt_view, background=bg)
        self.status_popup.title = title
        self.status_popup.overrideredirect(True)
        self.status_popup.columnconfigure(0, weight=1)
        self.status_popup.rowconfigure(0, weight=1)

        msg_lbl = tk.Label(self.status_popup, text=msg, anchor=tk.CENTER, background=bg, foreground=fg)
        msg_lbl.grid(row=0, column=0)

        cur_geom = (self.scpt_view.winfo_width(), self.scpt_view.winfo_height(), self.scpt_view.winfo_rootx(),
                    self.scpt_view.winfo_rooty())
        x = cur_geom[2] + cur_geom[0] // 2 - width // 2
        y = cur_geom[3] + cur_geom[1] // 2 - height // 2
        new_geom = f'{width}x{height}+{x}+{y}'
        self.status_popup.geometry(new_geom)

    def stop_status_popup(self):
        self.status_popup.destroy()
        self.status_popup = None

    def change_theme(self, dark_mode):
        for popup in self.popups.values():
            if popup is not None:
                popup.change_theme(dark_mode)
