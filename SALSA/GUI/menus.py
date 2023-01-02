import tkinter as tk


class MainMenu(tk.Menu):
    """The application's main menu"""

    def __init__(self, parent, callbacks, **kwargs):
        super().__init__(parent, **kwargs)

        self.parent = parent
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='New Project', command=callbacks['file->new_prj'])
        file_menu.add_command(label='Save Project', command=callbacks['file->save_prj'])
        file_menu.add_command(label='Load Project', command=callbacks['file->load_prj'])
        file_menu.add_command(label='Quit', command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=file_menu)

        self.project_menu = tk.Menu(self, tearoff=False)
        self.project_menu.add_command(label='Add SCT File', command=callbacks['prj->add_script'])
        self.add_cascade(label='Project', menu=self.project_menu)

        settings_menu = tk.Menu(self, tearoff=False)
        settings_menu.add_command(label='Select Script Directory', command=callbacks['set->script_dir'])
        self.add_cascade(label='Settings', menu=settings_menu)

        analysis_menu = tk.Menu(self, tearoff=False)
        analysis_menu.add_command(label='Export Data', command=callbacks['analysis->export'])

        self.view_menu = tk.Menu(self, tearoff=False)
        self.view_menu.add_command(label='Instruction editor', command=callbacks['view->inst'])
        self.view_menu.add_command(label='Variable editor', command=callbacks['view->variable'])
        self.view_menu.add_command(label='String editor', command=callbacks['view->string'])
        file_menu.add_command(label='Export Data', command=callbacks['file->export_data'])
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
        self.project_menu.entryconfig('Add SCT File', state='disabled')

