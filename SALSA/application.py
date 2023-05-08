import json
import os
import threading
import tkinter as tk
from tkinter import filedialog

from SALSA.FileModels.project_model import ProjectModel
from SALSA.FileModels.sct_model import SCTModel
from SALSA.GUI.ProjectEditor.project_editor_controller import ProjectEditorController
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.gui_controller import GUIController
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.GUI import menus
from SALSA.Project.project_facade import SCTProjectFacade


class Application(tk.Tk):
    """Controls the links between the data models and views"""
    test = True
    title_text = "Skies of Arcadia Legends Script Assistant"
    log_key = 'app'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.log_key not in settings:
            settings[self.log_key] = {}

        # Load base instructions
        self.base_insts = BaseInstLibFacade()

        # Setup window parameters
        self.title(self.title_text)
        self.resizable(width=True, height=True)

        # Setup project details
        self.project = SCTProjectFacade(self.base_insts)
        self.project_filepath = ''

        # Setup script editor view and controller
        self.project_edit_view = ProjectEditorView(self)
        self.project_edit_view.grid(row=0, column=0, sticky='NSEW', pady=5)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        project_view_callbacks = {'save_project': self.on_save_project}
        self.project_edit_controller = ProjectEditorController(self, self.project_edit_view, self.project, callbacks=project_view_callbacks)

        self.gui = GUIController(parent=self, scpt_editor_view=self.project_edit_view,
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
            'prj->export_script': self.gui.show_sct_export_popup,
            'prj->variable': self.gui.show_variables_popup,
            'prj->string': self.gui.show_strings_popup,
            'analysis->export': self.gui.show_analysis_view,
            'view->inst': self.gui.show_instruction_view,
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
            'no_script': self.menu.disable_script_commands,
            'export_sct': self.on_export_scts
        })

        self.gui.disable_script_view()

    def on_new_project(self):
        self.project.create_new_project()
        self.gui.enable_script_view()
        self.project_edit_controller.update_tree(None, None)

    def on_save_as_project(self):
        kwargs = {'filetypes': (('Project File', '*.prj'),), 'title': 'Save a project file'}
        start_dir = self.proj_model.get_project_directory()
        if start_dir != '' and start_dir is not None:
            kwargs['initialdir'] = start_dir
        filepath = filedialog.asksaveasfilename(**kwargs)
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

        self.gui.show_status_popup(title='Saving Project', msg=f'Saving Project ({os.path.basename(filepath)})')
        self.after(10, self._continue_save_project, filepath)

    def _continue_save_project(self, filepath):
        project = self.project.project
        self.proj_model.save_project(proj=project, filepath=filepath)
        self.proj_model.add_recent_file(filepath=filepath)
        self.gui.stop_status_popup()

    def on_load_recent_project(self, index):
        self.on_load_project(self.proj_model.get_recent_filepath(index=index))

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

        self.gui.show_status_popup(title='Loading Project', msg=f'Loading Project ({os.path.basename(filepath)})')
        self.after(10, self._continue_load_project, filepath)

    def _continue_load_project(self, filepath):
        prj = self.proj_model.load_project(filepath=filepath)
        self.proj_model.add_recent_file(filepath=filepath)
        self.menu.update_recents(self.proj_model.get_recent_filenames())
        self.project.load_project(prj)
        self.project_edit_controller.load_project()
        self.gui.stop_status_popup()

        self.gui.enable_script_view()

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

        self._notify_add_script(list(script_paths))

    def _notify_add_script(self, script_paths):
        filepath = script_paths.pop(0)
        self.gui.show_status_popup(title='Decoding Script', msg=f'Decoding Script ({os.path.basename(filepath)})')
        self.after(10, self._continue_add_script, filepath, script_paths)

    def _continue_add_script(self, filepath, script_paths):
        name, script = self.sct_model.load_sct(self.base_insts, file=filepath)
        self.project.add_script_to_project(name, script)
        if len(script_paths) > 0:
            self._notify_add_script(script_paths)
        else:
            self.gui.stop_status_popup()

    def set_script_dir(self):
        script_dir = filedialog.askdirectory()
        if script_dir == '':
            return
        self.settings.set_script_dir(script_dir)

    def on_quit(self):
        pass

    def on_export_scts(self, directory, scripts, options):
        compress = options['compress_aklz']
        options.pop('compress_aklz')

        for script in scripts:
            script_file = script
            if script_file[-4:] != '.sct':
                script_file += '.sct'
            script = self.project.get_project_script_by_name(script)
            filepath = os.path.join(directory, script_file)
            self.sct_model.export_script_as_sct(filepath=filepath, script=script, base_insts=self.base_insts,
                                                options=options, compress=compress)
