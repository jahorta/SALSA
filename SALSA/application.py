import json
import threading
import tkinter as tk
from tkinter import filedialog

from FileModels.project_model import ProjectModel
from FileModels.sct_model import SCTModel
from GUI.ProjectEditor.project_editor_controller import ProjectEditorController
from GUI.ProjectEditor.project_editor_view import ProjectEditorView
from GUI.gui_controller import GUIController
from BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.GUI import menus
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

        # Setup window parameters
        self.title(self.title_text)
        self.resizable(width=True, height=True)

        # Setup project details
        self.project = SCTProjectFacade(self.base_insts)
        self.project_filepath = ''

        # Setup script editor view and controller
        self.script_edit_view = ProjectEditorView(self)
        self.script_edit_view.grid(row=0, column=0, sticky='NSEW', pady=5)
        self.script_edit_controller = ProjectEditorController(self.script_edit_view, self.project)

        self.gui = GUIController(parent=self, scpt_editor_view=self.script_edit_view,
                                 project_facade=self.project, inst_lib_facade=self.base_insts)

        # Create Models
        self.proj_model = ProjectModel()
        self.sct_model = SCTModel()
        recent_files = self.proj_model.get_recent_filenames()

        self.menu_callbacks = {
            'file->new_prj': self.on_new_project,
            'file->save_prj': self.on_save_project,
            'file->save_as_prj': self.on_save_as_project,
            'file->load_prj': self.on_load_project,
            'file->load_recent': self.on_load_recent_project,
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
        self.menu = menus.MainMenu(parent=self, callbacks=self.menu_callbacks, recent_files=recent_files)
        self.config(menu=self.menu)

        # Connect recent files in proj_model to menu
        self.proj_model.add_callback('menu->update_recents', self.menu.update_recents)

        # Set menu options available only when in script mode
        self.gui.add_callbacks({
            'script': self.menu.enable_script_commands,
            'no_script': self.menu.disable_script_commands
        })

        self.gui.disable_script_view()

    def on_new_project(self):
        self.project.create_new_project()
        self.gui.enable_script_view()

    def on_save_as_project(self):
        filepath = filedialog.asksaveasfilename(filetypes=(('Project File', '*.prj'),), title='Save a project file')
        if filepath == '' or filepath is None:
            return
        if filepath[-4:] != '.prj':
            filepath += '.prj'
        self.project.set_filepath(filepath=filepath)
        self.on_save_project()

    def on_save_project(self):
        filepath = self.project.get_filepath()
        if filepath == '' or filepath is None:
            self.on_save_as_project()
            return
        project_dict = self.project.project
        self.proj_model.save_project(proj=project_dict, filepath=filepath, indent=True, pickled=True)
        self.proj_model.add_recent_file(filepath=filepath)

    def on_load_project(self, filepath=''):
        if filepath == '' or filepath is None:
            default_dir = self.proj_model.get_project_directory()
            kwargs = {'filetypes': (('Project File', '*.prj'),), 'title': 'Open a project file'}
            if default_dir is not None:
                kwargs['initialdir'] = default_dir
            filepath = filedialog.askopenfilename(**kwargs)
            if filepath == '' or filepath is None:
                print('no file selected')
                return

        prj = self.proj_model.load_project(filepath=filepath, pickled=True)
        self.project.load_project(prj, pickled=True)
        self.gui.enable_script_view()

    def on_load_recent_project(self, index):
        self.on_load_project(self.proj_model.get_recent_filepath(index=index))

    def on_print_debug(self):
        print(f'\nWindow Dimensions:\nHeight: {self.winfo_height()}\nWidth: {self.winfo_width()}')

    def add_script(self):
        kwargs = {'filetypes': (('Script File', '*.sct'),), 'title': 'Select script(s) to add to the current project'}
        base_dir = self.sct_model.get_default_directory()
        if base_dir != '':
            kwargs['initialdir'] = base_dir
        script_paths = filedialog.askopenfilenames(**kwargs)
        if script_paths == '' or script_paths is None:
            return
        for script in script_paths:
            name, script = self.sct_model.load_sct(self.base_insts, file=script)
            self.project.add_script_to_project(name, script)

    def set_script_dir(self):
        script_dir = filedialog.askdirectory()
        if script_dir == '':
            return
        self.settings.set_script_dir(script_dir)

    def on_quit(self):
        pass
