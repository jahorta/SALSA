import os
import threading
import tkinter as tk
from tkinter import filedialog

from FileModels.project_model import ProjectModel
from FileModels.sct_model import SCTModel
from GUI.ScriptEditor.script_editor_controller import ScriptEditorController
from GUI.ScriptEditor.script_editor_view import ScriptEditorView
from GUI.gui_controller import GUIController
from BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.GUI import menus
from Project.project_container import SCTProject
from SALSA.Settings.settings import Settings, settings
from Scripts.script_decoder import SCTDecoder
from Project.project_facade import SCTProjectFacade


class Application(tk.Tk):
    """Controls the links between the data models and views"""
    test = True
    title_text = "Skies of Arcadia Legends - Script Assistant"
    default_sct_file = 'me002a.sct'
    export_thread: threading.Thread

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load base instructions
        self.base_insts = BaseInstLibFacade()

        # Define callbacks for the different views
        # self.instruction_callbacks = {
        #     'on_inst_lib_save': self.save_inst_lib,
        #     'on_select_instruction': self.on_select_instruction,
        #     'on_instruction_commit': self.on_instruction_commit,
        #     'on_select_parameter': self.on_select_parameter,
        #     'on_parameter_num_change': self.on_param_num_change
        # }

        # self.script_callbacks = {
        #     'on_save_project': self.save_project,
        # }

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

        # Setup project details
        self.project_facade = SCTProjectFacade(self.base_insts)
        self.project_filepath = ''

        # Setup script editor view and controller
        self.script_edit_view = ScriptEditorView(self)
        self.script_edit_view.grid(row=0, column=0, sticky='NSEW', pady=5)
        self.script_edit_controller = ScriptEditorController(self.script_edit_view, self.project_facade)

        self.gui = GUIController(parent=self, scpt_editor_view=self.script_edit_view,
                                 project_facade=self.project_facade, inst_lib_facade=self.base_insts)

        self.menu_callbacks = {
            'file->new_prj': self.on_new_project,
            'file->save_prj': self.on_save_project,
            'file->save_as_prj': self.on_save_as_project,
            'file->load_prj': self.on_load_project,
            'file->settings': self.gui.show_settings,
            'file->quit': self.on_quit,
            'prj->add_script': self.add_script,
            'analysis->export': self.gui.show_analysis_view,
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

        # Create Models
        self.proj_model = ProjectModel()
        self.sct_model = SCTModel()

    def on_new_project(self):
        self.project_facade.create_new_project()
        self.gui.enable_script_view()

    def on_save_as_project(self):
        filepath = filedialog.asksaveasfile(filetypes=(('Project File', '*.prj'),), title='Save a project file')
        if filepath == '':
            return
        self.project_filepath = filepath
        self.on_save_project()

    def on_save_project(self):
        if self.project_filepath == '':
            self.on_save_as_project()
            return
        project_dict = self.project_facade.get_cur_project_json()
        self.proj_model.save_project(project_dict, indent=True)

    def on_load_project(self):
        default_dir = self.proj_model.get_project_directory()

        kwargs = {'filetypes': (('Project File', '*.prj'),), 'title': 'Open a project file'}
        if default_dir is not None:
            kwargs['initialdir'] = default_dir
        project_file = filedialog.askopenfilename(**kwargs)
        if project_file == '':
            print('no file selected')
            return

        new_file_name = os.path.basename(project_file)
        self.proj_model.add_recent_file(project_file)
        with open(os.path.join(default_dir, new_file_name), 'rb') as fh:
            prj_dict = fh.read()
        self.project_facade.load_project(prj_dict)
        self.gui.enable_script_view()

    def on_print_debug(self):
        print(f'\nWindow Dimensions:\nHeight: {self.winfo_height()}\nWidth: {self.winfo_width()}')

    def add_script(self):
        script = filedialog.askopenfile()
        if script == '':
            return
        name, script = self.sct_model.load_sct(self.base_insts, file=script.name)
        self.project_facade.add_script_to_project(name, script)

    def set_script_dir(self):
        script_dir = filedialog.askdirectory()
        if script_dir == '':
            return
        self.settings.set_script_dir(script_dir)

    def on_quit(self):
        pass
