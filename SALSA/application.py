import datetime
import os
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import Union

from GUI.ScriptEditor.script_editor_controller import ScriptEditorController
from GUI.ScriptEditor.script_editor_view import ScriptEditorView
from GUI.gui_controller import GUIController
from BaseInstructions.base_instruction_container import BaseInstLib
from BaseInstructions.base_instruction_facade import BaseInstLibFacade
from SALSA.GUI import menus
from SALSA.Scripts.script_container import SCTScript, SCTProject
from SALSA.FileModels.sct_model import SctModel
from SALSA.Settings.settings import Settings
from Scripts.script_decoder import SCTDecoder
from Scripts.script_facade import SCTProjectFacade


class Application(tk.Tk):
    """Controls the links between the data models and views"""
    test = True
    title_text = "Skies of Arcadia Legends - Script Assistant"
    default_sct_file = 'me002a.sct'
    export_thread: threading.Thread

    active_project: Union[None, SCTProject] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load settings
        self.settings = Settings()
        if self.settings.get_sct_file() == '':
            self.settings.set_sct_file(self.default_sct_file)
        else:
            self.default_sct_file = self.settings.get_sct_file()
            self.file_select_last_selected = self.default_sct_file
        self.script_dir = self.settings.get_script_dir()

        # Load a script file facade
        self.active_project = None
        self.script_facade = SCTProjectFacade(self.active_project)

        self.base_insts = BaseInstLibFacade()

        # TODO - Prep an sct model, only for read/write of the encoded file

        # TODO - Read in and set up the initial instructions

        # Define callbacks for the different views
        # self.instruction_callbacks = {
        #     'on_inst_lib_save': self.save_inst_lib,
        #     'on_select_instruction': self.on_select_instruction,
        #     'on_instruction_commit': self.on_instruction_commit,
        #     'on_select_parameter': self.on_select_parameter,
        #     'on_parameter_num_change': self.on_param_num_change
        # }
        #
        # self.script_callbacks = {
        #     'on_script_display_change': self.on_script_display_change,
        #     'on_instruction_display_change': self.on_instruction_display_change,
        #     'on_select_script': self.on_select_script,
        #     'on_select_script_instruction': self.on_select_script_instruction,
        #     'on_set_inst_start': self.on_set_inst_start,
        #     'create_breakpoint': self.on_create_breakpoints
        # }
        #

        #
        # self.exporter_callbacks = {
        #     'on_export': self.on_data_export,
        #     'on_close': self.about_window_close,
        #     'on_write_to_csv': self.export_as_csv
        # }

        # Initialize popup window variables

        # Setup window parameters
        self.title(self.title_text)
        self.resizable(width=True, height=True)

        # Setup script editor view and controller
        self.script_edit_view = ScriptEditorView(self)
        self.script_edit_view.grid(row=0, column=0, sticky='NSEW', pady=5)
        self.script_edit_controller = ScriptEditorController(self.script_edit_view)

        self.gui = GUIController(parent=self, scpt_editor_view=self.script_edit_view,
                                 script_facade=self.script_facade, inst_lib_facade=self.base_insts)

        self.menu_callbacks = {
            'file->script_dir': self.settings.set_script_dir,
            'file->select': self.on_file_select,
            'file->quit': self.on_quit,
            'file->export_data': self.gui.show_analysis_view,
            'view->inst': self.gui.show_instruction_view,
            'view->variable': self.script_edit_controller.show_variables,
            'view->string': self.script_edit_controller.show_strings,
            'help->help': self.gui.show_help,
            'help->about': self.gui.show_about,
        }

        # Implement Menu
        self.menu = menus.MainMenu(self, self.menu_callbacks)
        self.config(menu=self.menu)

        # Set menu options available only when in script mode
        self.gui.add_callbacks({
            'script': self.menu.enable_script_commands,
            'no_script': self.menu.disable_script_commands
        })

        self.gui.disable_script_view()
        self.gui.update_script_view()

    def on_file_select(self):
        default_dir = self.settings.get_script_dir()
        prev_file = self.settings.get_sct_file()
        script = filedialog.askopenfilename(initialdir=default_dir, initialfile=prev_file,
                                            filetypes=(('script file', '*.sct'),), title='Open a script file')
        if script == '':
            print('no file selected')
            return

        new_file_name = os.path.basename(script)
        self.settings.set_sct_file(new_file_name)
        with open(os.path.join(default_dir, new_file_name), 'rb') as fh:
            sct = fh.read()

        self.active_project = SCTProject()
        self.active_project.add_script(new_file_name, SCTDecoder.decode_sct_from_file(name=script, sct=sct,
                                                                                      inst_lib=self.base_insts))
        self.script_facade.project = self.active_project
        self.gui.enable_script_view()
        self.gui.update_script_view()

    def on_print_debug(self):
        print(f'\nWindow Dimensions:\nHeight: {self.winfo_height()}\nWidth: {self.winfo_width()}')

    def set_script_dir(self):
        script_dir = filedialog.askdirectory()
        if script_dir == '':
            return
        self.settings.set_script_dir(script_dir)

    def on_quit(self):
        pass
