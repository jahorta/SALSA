import tkinter as tk


class MainMenu(tk.Menu):
    """The application's main menu"""

    def __init__(self, parent, callbacks, recent_files, **kwargs):
        super().__init__(parent, **kwargs)

        self.recent_files = recent_files
        if len(self.recent_files) == 0:
            self.no_recents = True
            self.recent_files = ['No Recent Files']

        self.parent = parent
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='New Project', command=callbacks['file->new_prj'])
        file_menu.add_command(label='Save Project', command=callbacks['file->save_prj'])
        file_menu.add_command(label='Load Project', command=callbacks['file->load_prj'])

        self.recent_menu = tk.Menu(file_menu, tearoff=False)
        for file in self.recent_files:
            self.recent_menu.add_command(label=file, command=lambda x=file: self.load_recent_project(x))
        if self.no_recents:
            self.recent_menu.entryconfig('No Recent Files', state='disabled')
        file_menu.add_cascade(label='Load Recent File', menu=self.recent_menu)

        file_menu.add_command(label='Quit', command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=file_menu)

        self.project_menu = tk.Menu(self, tearoff=False)
        self.project_menu.add_command(label='Add SCT File', command=callbacks['prj->add_script'])
        self.add_cascade(label='Project', menu=self.project_menu)

        analysis_menu = tk.Menu(self, tearoff=False)
        analysis_menu.add_command(label='Export Data', command=callbacks['analysis->export'])

        self.view_menu = tk.Menu(self, tearoff=False)
        self.view_menu.add_command(label='Instruction editor', command=callbacks['view->inst'])
        self.view_menu.add_separator()
        self.view_menu.add_command(label='Variable editor', command=callbacks['view->variable'])
        self.view_menu.add_command(label='String editor', command=callbacks['view->string'])
        self.add_cascade(label='View', menu=self.view_menu)

        help_menu = tk.Menu(self, tearoff=False)
        # help_menu.add_command(label='Print debug to console', command=callbacks['help->debug'])
        help_menu.add_command(label='Help', command=callbacks['help->help'])
        help_menu.add_command(label='About', command=callbacks['help->about'])
        self.add_cascade(label='Help', menu=help_menu)

    def disable_script_commands(self):
        self.view_menu.entryconfig('Variable editor', state='disabled')
        self.view_menu.entryconfig('String editor', state='disabled')
        self.project_menu.entryconfig('Add SCT File', state='disabled')

    def enable_script_commands(self):
        self.view_menu.entryconfig('Variable editor', state='normal')
        self.view_menu.entryconfig('String editor', state='normal')
        self.project_menu.entryconfig('Add SCT File', state='normal')

    def load_recent_project(self, file):
        pass

    def update_recents(self, recent_files):
        for file in self.recent_files:
            self.recent_menu.deletecommand(file)

        self.recent_files = recent_files
        if len(self.recent_files) == 0:
            self.no_recents = True
            self.recent_files = ['No Recent Files']

        for file in self.recent_files:
            self.recent_menu.add_command(label=file, command=lambda x=file: self.load_recent_project(x))
        if self.no_recents:
            self.recent_menu.entryconfig('No Recent Files', state='disabled')
