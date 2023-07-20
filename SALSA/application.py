import os
import queue
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Union

from SALSA.Project.RepairTools.texbox_disappear_repair import TBStringToParamRepair
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Common.setting_class import settings
from SALSA.FileModels.project_model import ProjectModel
from SALSA.FileModels.sct_model import SCTModel
from SALSA.GUI.ProjectEditor.project_editor_controller import ProjectEditorController
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.gui_controller import GUIController
from SALSA.GUI import menus
from SALSA.GUI.themes import themes, theme_non_color_maps
from SALSA.Project.project_facade import SCTProjectFacade

default_style = 'clam'


default_settings = {
    'darkmode': 'False'
}

icons = [
    ('./SALSA/GUI/Icons/icon-1.png', './SALSA/GUI/Icons/icon-1-16.png'),
    ('./SALSA/GUI/Icons/icon-2.png', './SALSA/GUI/Icons/icon-2-16.png'),
    ('./SALSA/GUI/Icons/icon-3.png', './SALSA/GUI/Icons/icon-3-16.png')
]


class Application(tk.Tk):
    """Controls the links between the data models and views"""
    test = True
    title_text = "Skies of Arcadia Legends Script Assistant"
    log_key = 'app'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.log_key not in settings:
            settings[self.log_key] = {}

        for s in default_settings:
            if settings[self.log_key].get(s, None) is None:
                settings.set_single(self.log_key, s, default_settings[s])

        # Load base instructions
        self.base_insts = BaseInstLibFacade()

        # Setup window parameters
        self.title(self.title_text)
        self.resizable(width=True, height=True)
        self.protocol('WM_DELETE_WINDOW', self.on_quit)

        icon_ind = random.randint(0, 2)
        large_icon = tk.PhotoImage(file=icons[icon_ind][0])
        small_icon = tk.PhotoImage(file=icons[icon_ind][1])
        self.iconphoto(True, large_icon, small_icon)

        self.is_darkmode = True if settings[self.log_key]['darkmode'] == 'True' else False
        self.style = ttk.Style()
        for theme, theme_settings in themes.items():
            self.style.theme_create(theme, parent=default_style, settings=theme_settings)

        for key, maps in theme_non_color_maps.items():
            for mk, mv in maps.items():
                self.style.map(key, **{mk: mv})

        theme_name = list(themes.keys())[0] if self.is_darkmode else list(themes.keys())[1]
        self.style.theme_use(theme_name)

        # maps dynamic style attributes for the current theme
        self.map_current_theme(themes[theme_name])

        # Setup project details
        self.project = SCTProjectFacade(self.base_insts)
        self.project_filepath = ''

        # Setup script editor view and controller
        self.project_edit_view = ProjectEditorView(self, is_darkmode=self.is_darkmode)
        self.project_edit_view.grid(row=0, column=0, sticky='NSEW', pady=5, padx=5)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        project_controller_callbacks = {'save_project': self.on_save_project}
        self.project_edit_controller = ProjectEditorController(self, self.project_edit_view, self.project,
                                                               callbacks=project_controller_callbacks,
                                                               is_darkmode=self.is_darkmode)

        self.gui = GUIController(parent=self, scpt_editor_view=self.project_edit_view,
                                 project_facade=self.project, inst_lib_facade=self.base_insts)

        self.project_edit_controller.add_callback('toggle_frame_state', self.gui.toggle_frame_state)

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
            'prj->repair->textbox': self.repair_text_box_fade,
            'analysis->export': self.gui.show_analysis_view,
            'view->inst': self.gui.show_instruction_view,
            'view->theme': self.change_theme,
            'help->help': self.gui.show_help,
            'help->about': self.gui.show_about,
        }

        # Implement Menu
        self.menu = menus.MainMenu(parent=self, callbacks=self.menu_callbacks, recent_files=recent_files, dark_mode=self.is_darkmode)
        self.config(menu=self.menu)

        # Connect recent files in proj_model to menu
        self.proj_model.add_callback('menu->update_recents', self.menu.update_recents)

        def return_darkmode():
            return self.is_darkmode

        # Set menu options available only when in script mode
        self.gui.add_callbacks({
            'script': self.menu.enable_script_commands,
            'no_script': self.menu.disable_script_commands,
            'export_sct': self.on_export_scts,
            'is_darkmode': return_darkmode,
        })

        self.gui.disable_script_view()

        # self.bind('<<ChangeTheme>>', self.propagate_change_theme)
        self.change_theme(self.is_darkmode)

    def on_new_project(self):
        self.project.create_new_project()
        self.gui.enable_script_view()
        self.gui.toggle_frame_state(self.project_edit_view.inst_frame, 'disabled')
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
        success = self.project.load_project(prj)
        if not success:
            self.gui.show_status_popup(title='Loading Project', msg=f'Project load failed :(')
            self.gui.scpt_view.after(1000, self.gui.stop_status_popup)
            return
        self.menu.update_recents(self.proj_model.get_recent_filenames())
        self.project_edit_controller.load_project()
        self.gui.stop_status_popup()
        self.gui.enable_script_view()
        self.gui.toggle_frame_state(self.project_edit_view.inst_frame, 'disabled')

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
        self.sct_model.set_default_directory(os.path.dirname(script_paths[0]))

        self.gui.show_status_popup('Adding Script(s)', 'tempMSG')

        script_decode_queue = queue.Queue()
        script_thread = threading.Thread(target=self._threaded_script_decoder,
                                         args=(list(script_paths), script_decode_queue, self.gui.status_queue))
        script_thread.start()
        self._script_add_listener(script_decode_queue)

    def _script_add_listener(self, decode_queue, scripts: Union[None, dict] = None):
        if scripts is None:
            scripts = {}
        if not decode_queue.empty():
            item = decode_queue.get()
            decode_queue.task_done()
            if isinstance(item, str):
                if item == 'stop':
                    return self.finish_add_script(scripts)
            else:
                scripts |= item
        self.after(20, self._script_add_listener, decode_queue, scripts)

    def _threaded_script_decoder(self, script_paths, script_decode_out_queue: queue.Queue, status_queue: queue.SimpleQueue):
        for filepath in script_paths:
            name, script = self.sct_model.load_sct(self.base_insts, file=filepath, status=status_queue)
            script_decode_out_queue.put({name: script})
        script_decode_out_queue.put('stop')

    def finish_add_script(self, scripts):
        self.project.add_scripts_to_project(scripts)
        self.gui.stop_status_popup()

    def on_quit(self):
        if self.project_edit_controller.has_changes:
            # dialog to save changes or not
            save = tk.messagebox.askyesno(title='Unsaved Changes',
                                          message='There are unsaved changes remaining.\nWould you like to save them?')
            if save:
                self.on_save_project()
        self.destroy()

    def on_export_scts(self, directory, scripts, options):
        compress = options['compress_aklz']
        options.pop('compress_aklz')

        script_paths = []
        for script in scripts:
            script_file = script
            if script_file[-4:] != '.sct':
                script_file += '.sct'
            filepath = os.path.join(directory, script_file)
            script_paths.append(filepath)

        self._notify_export_sct(script_paths, scripts, options, compress)

    def _notify_export_sct(self, script_paths, script_names, options, compress):
        filepath = script_paths[0]
        self.gui.show_status_popup(title='Exporting Script', msg=f'Exporting Script ({os.path.basename(filepath)})')
        self.after(10, self._continue_export_sct, script_paths, script_names, options, compress)

    def _continue_export_sct(self, script_paths, script_names, options, compress):
        script = self.project.get_project_script_by_name(script_names.pop(0))
        filepath = script_paths.pop(0)
        self.sct_model.export_script_as_sct(filepath=filepath, script=script, base_insts=self.base_insts,
                                            options=options, compress=compress)
        if len(script_paths) > 0:
            self._notify_export_sct(script_paths, script_names, options, compress)
        else:
            self.gui.stop_status_popup()

    def change_theme(self, dark_mode=True):
        self.is_darkmode = dark_mode
        settings.set_single(self.log_key, 'darkmode', str(dark_mode))
        theme_name = list(themes.keys())[0] if dark_mode else list(themes.keys())[1]
        theme = themes[theme_name]

        self.style.theme_use(theme_name)

        self.map_current_theme(theme)

        self.configure(bg=theme['.']['configure']['background'])

        self.project_edit_view.change_theme(dark_mode)
        self.gui.change_theme(dark_mode)

    def map_current_theme(self, theme):
        for item_key, arg_dict in theme.items():
            if 'map' not in arg_dict:
                continue
            self.style.map(item_key, **arg_dict['map'])

    def repair_text_box_fade(self):
        project = TBStringToParamRepair.repair_project(project=self.project.project, inst_lib=self.base_insts, sct_model=self.sct_model)
        if project is None:
            return
        self.project.project = project
