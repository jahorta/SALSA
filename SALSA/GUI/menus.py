import tkinter as tk


class MainMenu(tk.Menu):
    """The application's main menu"""

    def __init__(self, parent, callbacks, **kwargs):
        super().__init__(parent, **kwargs)

        self.parent = parent
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='Select Script Directory', command=callbacks['file->script_dir'])
        file_menu.add_command(label='Select SCT File', command=callbacks['file->select'])
        file_menu.add_command(label='Export Data', command=callbacks['file->export_data'])
        file_menu.add_command(label='Quit', command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=file_menu)

        view_menu = tk.Menu(self, tearoff=False)
        view_menu.add_command(label='SCT decoder mode', command=callbacks['view->sct'])
        view_menu.add_command(label='Instruction edit mode', command=callbacks['view->inst'])
        self.add_cascade(label='View', menu=view_menu)

        help_menu = tk.Menu(self, tearoff=False)
        # help_menu.add_command(label='Print debug to console', command=callbacks['help->debug'])
        help_menu.add_command(label='Help', command=callbacks['help->help'])
        help_menu.add_command(label='About', command=callbacks['help->about'])
        self.add_cascade(label='Help', menu=help_menu)

