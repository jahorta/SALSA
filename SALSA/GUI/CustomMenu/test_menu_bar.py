import tkinter as tk
from tkinter import ttk

from GUI.CustomMenu.menu_widgets import SALSAMenuBar, SALSAMenu


class TestMenuBar(ttk.Frame):

    def __init__(self, master, is_darkmode, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.menu = SALSAMenuBar(self)
        self.menu.grid(row=0, column=0, sticky=tk.W)

        self.filemenu = SALSAMenu(self.menu, is_darkmode=is_darkmode)
        self.filemenu.add_command('Hi', command=lambda: self.test_print('Hi'))
        self.filemenu.add_command('Bye', command=lambda: self.test_print('Bye'))
        self.menu.add_cascade('File', self.filemenu)

        self.viewmenu = SALSAMenu(self.menu, is_darkmode=is_darkmode)
        self.disable_var = tk.IntVar
        self.viewmenu.add_checkbutton('Disable File', variable=self.disable_var, command=self.disable_file_toggle, onvalue=1, offvalue=0)
        self.menu.add_cascade('View', self.viewmenu)

    def disable_file_toggle(self):
        new_state = 'disabled' if self.disable_var.get == 1 else 'normal'
        self.filemenu.entryconfig('Hi', state=new_state)
        self.filemenu.entryconfig('Bye', state=new_state)
        self.menu.entryconfig('File', state=new_state)

    def change_theme(self, dark_mode):
        self.filemenu.change_theme(dark_mode=dark_mode)
        self.viewmenu.change_theme(dark_mode=dark_mode)

    def test_print(self, text):
        print(text)
