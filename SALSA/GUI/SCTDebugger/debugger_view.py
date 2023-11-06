import tkinter as tk
from tkinter import ttk
from typing import Literal, List, Dict

from SALSA.Common.setting_class import settings


cur_script_text = 'Current Script: '


class SCTDebuggerPopup(tk.Toplevel):
    t = 'Debug SCTs in Dolphin'
    log_key = 'SCTDebugger'
    w = 400
    h = 600

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

        self.buttons: Dict[str, ttk.Button] = {
            'attach': ttk.Button(self, text='Attach Dolphin', command=self.callbacks['attach_dolphin'])
        }
        self.buttons['attach'].grid(row=0, column=0)

        status_label = ttk.Label(self, text='Debugger Status:')
        status_label.grid(row=1, column=0)

        self.status_widgets = {
            'dolphin': ttk.Label(self, text='', style='warning.TLabel'),
            'cur_sct': ttk.Label(self, text=''),
            'update': ttk.Label(self, text='', style='warning.TLabel')
        }

        row = 2
        for w in self.status_widgets.values():
            w.grid(row=row, column=0, sticky=tk.E+tk.W)
            row += 1

        self.buttons['update'] = ttk.Button(self, text='Update Current SCT in Dolphin',
                                            command=self.callbacks['update_sct'])
        self.buttons['update'].grid(row=row, column=0, sticky=tk.E)
        self.buttons['update'].state(['disabled'])

        self.callbacks['attach_controller'](self)

    def set_status(self, stat_type: Literal['dolphin', 'update', 'cur_sct'], status, style=None):
        self.status_widgets[stat_type].configure(style=style, text=status)

    def update_button_state(self, button: Literal['attach', 'update'],
                            state: List[Literal['disabled', '!disabled']]):
        self.buttons[button].state(state)

    def close(self):
        self.callbacks['attach_controller'](None)
        self.callbacks['close'](self.name, self)

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
