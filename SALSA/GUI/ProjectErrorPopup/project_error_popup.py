import tkinter as tk
from tkinter import ttk

from SALSA.GUI.fonts_used import SALSAFont
from SALSA.GUI.Widgets import widgets as w
from SALSA.Common.setting_class import settings


class SCTExportPopup(tk.Toplevel):

    t = 'Export Script(s) as SCT file'
    log_key = 'SCTExportPopup'
    w = 250
    h = 400

    option_settings = {
        'use_garbage': {'text': 'Add garbage from original files', 'default': 'True'},
        'combine_footer': {'text': 'Combine footer entries', 'default': 'False'},
        'all_refresh': {'text': 'Add unnecessary refresh skips', 'default': 'True'},
        'compress_aklz': {'text': 'Compress file using AKLZ compression', 'default': 'False'}
    }

    def __init__(self, parent, callbacks, name, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.name = name
        self.callbacks = callbacks
        self.configure(**theme['Ttoplevel']['configure'])
        self.link_font = SALSAFont()

        self.link_in = w.ScrollFrame(self, size={'width': 100, 'height': 100})
        self.link_in.grid(row=1, column=0, sticky=tk.W + tk.E, padx='0 5')
        self.link_in.columnconfigure(0, weight=1)
        self.link_in.rowconfigure(0, weight=1)

        errors = self.callbacks['get_errors']()



    def add_string_link(self, text):
        pass

    def add_inst_link(self, sect, inst, row):
        ori_frame = tk.Frame(self.link_in.scroll_frame)
        ori_frame.grid(row=row, column=0, sticky=tk.E + tk.W, pady='5 0', padx=5)
        ori_frame.bind('<Enter>', self.handle_link_font)
        ori_frame.bind('<Leave>', self.handle_link_font)
        ori_frame.columnconfigure(0, weight=1)
        # ori_sect = link.origin_trace[0]

        ori_label = ttk.Label(ori_frame, text=f'{ori_sect}{link_sep}{ori_inst}',
                              font=self.link_font.font, style='canvas.TLabel')
        ori_label.grid(row=0, column=0, sticky=tk.E + tk.W)
        ori_label.bind('<ButtonRelease-1>', self.goto_link)

    def handle_link_font(self, e):
        font = self.link_font.font if e.type == tk.EventType.Leave else self.link_font.hover_font
        style = 'canvas.TLabel' if e.type == tk.EventType.Leave else 'link.TLabel'
        for child in e.widget.winfo_children():
            child.configure(font=font, style=style)

    def goto_link(self):
        pass

    def close(self):
        self.callbacks['close'](self.name, self)

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
        self.link_in.change_theme(theme)
