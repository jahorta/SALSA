import tkinter as tk
from tkinter import ttk
from typing import Literal

from SALSA.Common.setting_class import settings


class SCTDebuggerPopup(tk.Toplevel):
    t = 'Debug SCTs in Dolphin'
    log_key = 'SCTDebugger'
    w = 250
    h = 400

    option_settings_check = {
        'use_garbage': {'text': 'Add garbage from original files', 'default': 'True'},
        'combine_footer': {'text': 'Combine footer entries', 'default': 'False'},
        'all_refresh': {'text': 'Add unnecessary refresh skips', 'default': 'True'},
        'compress_aklz': {'text': 'Compress file using AKLZ compression', 'default': 'False'}
    }
    option_settings_radio = {
        'system': {'label': 'Select target system:', 'entries': ['Dreamcast', 'GameCube'], 'default': 'GameCube'}
    }

    def __init__(self, parent, callbacks, name, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.name = name
        self.callbacks = callbacks

        self.protocol('WM_DELETE_WINDOW', self.close)
        self.configure(**theme['Ttoplevel']['configure'])

        self.title(self.t)
        self.resizable(width=False, height=False)

        posX = self.parent.winfo_x() + (self.parent.winfo_width() - self.w)//2
        posY = self.parent.winfo_y() + (self.parent.winfo_height() - self.h)//2
        pos = f'{self.w}x{self.h}+{posX}+{posY}'
        self.geometry(pos)

        if self.log_key not in settings:
            settings[self.log_key] = {}

        status_label = ttk.Label(self, text='Debugger Status:')
        status_label.grid(row=0, column=0)

        self.status_widgets = {
            'dolphin': ttk.Label(self, text=''),
            'export': ttk.Label(self, text=''),
            'cur_sct': ttk.Label(self, text='')
        }

        row = 1
        for w in self.status_widgets.values():
            w.grid(row=row, column=0, sticky=tk.E+tk.W)
            row += 1

        self.load_sct = ttk.Button(self, text='Update Current SCT in Dolphin', command=self.callbacks['update_sct'])
        self.load_sct.grid(row=row, column=0, sticky=tk.E)

    def set_status(self, stat_type: Literal['dolphin', 'export', 'cur_sct'], status):
        self.status_widgets[stat_type].configure(text=status)

    def close(self):
        self.callbacks['close'](self.name, self)

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
