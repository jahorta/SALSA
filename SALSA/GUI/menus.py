import tkinter as tk


class MainMenu(tk.Menu):
    """The application's main menu"""

    def __init__(self, parent, callbacks, recent_files, **kwargs):
        super().__init__(parent, **kwargs)

        self.recent_files = recent_files
        self.no_recents = True if len(self.recent_files) == 0 else False
        self.recent_files = ['No Recent Files'] if len(self.recent_files) == 0 else recent_files

        self.callbacks = callbacks

        self.parent = parent
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(label='New Project', command=callbacks['file->new_prj'])
        self.file_menu.add_command(label='Save Project', command=callbacks['file->save_prj'])
        self.file_menu.add_command(label='Load Project', command=callbacks['file->load_prj'])

        self.recent_menu = tk.Menu(self.file_menu, tearoff=False)
        for i, file in enumerate(self.recent_files):
            self.recent_menu.add_command(label=file, command=lambda x=i: self.callbacks['file->load_recent'](x))
        if self.no_recents:
            self.recent_menu.entryconfig('No Recent Projects', state='disabled')
        self.file_menu.add_cascade(label='Recent Projects...', menu=self.recent_menu)

        self.file_menu.add_command(label='Quit', command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=self.file_menu)

        self.project_menu = tk.Menu(self, tearoff=False)
        self.project_menu.add_command(label='Import SCT file(s)', command=callbacks['prj->add_script'])
        self.project_menu.add_command(label='Export SCT file(s)', command=callbacks['prj->export_script'])
        self.project_menu.add_separator()
        self.project_menu.add_command(label='Variable alias editor', command=callbacks['prj->variable'])
        self.project_menu.add_command(label='String editor', command=callbacks['prj->string'])
        self.add_cascade(label='Project', menu=self.project_menu)

        analysis_menu = tk.Menu(self, tearoff=False)
        analysis_menu.add_command(label='Export Data', command=callbacks['analysis->export'])
        self.add_cascade(label='Analysis', menu=analysis_menu)

        self.view_menu = tk.Menu(self, tearoff=False)
        self.view_menu.add_command(label='Instruction editor', command=callbacks['view->inst'])
        self.add_cascade(label='View', menu=self.view_menu)

        help_menu = tk.Menu(self, tearoff=False)
        # help_menu.add_command(label='Print debug to console', command=callbacks['help->debug'])
        help_menu.add_command(label='Help', command=callbacks['help->help'])
        help_menu.add_command(label='About', command=callbacks['help->about'])
        self.add_cascade(label='Help', menu=help_menu)

    def disable_script_commands(self):
        self.project_menu.entryconfig('Variable alias editor', state='disabled')
        self.project_menu.entryconfig('String editor', state='disabled')
        self.project_menu.entryconfig('Import SCT file(s)', state='disabled')
        self.project_menu.entryconfig('Export SCT file(s)', state='disabled')
        self.file_menu.entryconfig('Save Project', state='disabled')

    def enable_script_commands(self):
        self.project_menu.entryconfig('Variable alias editor', state='normal')
        self.project_menu.entryconfig('String editor', state='normal')
        self.project_menu.entryconfig('Import SCT file(s)', state='normal')
        self.project_menu.entryconfig('Export SCT file(s)', state='normal')
        self.file_menu.entryconfig('Save Project', state='normal')

    def update_recents(self, recent_files):
        self.no_recents = True if len(self.recent_files) == 0 else False
        self.recent_files = ['No Recent Files'] if len(self.recent_files) == 0 else recent_files

        self.recent_menu.delete(0, 'end')
        for i, file in enumerate(self.recent_files):
            self.recent_menu.add_command(label=file, command=lambda x=i: self.callbacks['file->load_recent'](x))
        if self.no_recents:
            self.recent_menu.entryconfig('No Recent Files', state='disabled')
