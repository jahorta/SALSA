import os.path
import tkinter as tk
from tkinter import filedialog, ttk

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

    def __init__(self, parent, callbacks, name, selected, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.name = name
        self.callbacks = callbacks
        self.selected = selected
        self.script_ids = {}

        if self.log_key not in settings:
            settings[self.log_key] = {}

        for s, v in self.option_settings.items():
            if s not in settings[self.log_key]:
                settings[self.log_key][s] = v['default']

        self.columnconfigure(0, weight=1)

        directory_frame = tk.LabelFrame(self, text='Select a directory for export')
        directory_frame.grid(row=0, column=0, sticky='NSEW', padx=5)
        directory_frame.columnconfigure(0, weight=1)

        self.directory_var = tk.StringVar()
        directory_entry = tk.Entry(directory_frame, textvariable=self.directory_var, width=30)
        directory_entry.grid(row=0, column=0, sticky='NSEW')

        directory_button = tk.Button(directory_frame, text='...', command=self.get_directory)
        directory_button.grid(row=0, column=1, sticky=tk.W, padx=2)

        script_tree_frame = tk.LabelFrame(self, text='Select script(s) to export')
        script_tree_frame.grid(row=1, column=0, sticky='NSEW', padx=5)
        script_tree_frame.columnconfigure(0, weight=1)
        script_tree_frame.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.scripts = ttk.Treeview(script_tree_frame, name='script', columns=[])
        self.scripts.grid(row=0, column=0, sticky='NSEW')
        self.scripts.heading('#0', text='Script')
        script_tree_scrollbar = tk.Scrollbar(script_tree_frame, orient='vertical', command=self.scripts.yview)
        script_tree_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.scripts.config(yscrollcommand=script_tree_scrollbar.set)
        self.scripts.config(show='tree')

        options_frame = tk.LabelFrame(self, text='Options')
        options_frame.grid(row=2, column=0, sticky='NSEW', padx=5)

        self.option_vars = {}
        row = 0
        for o_name, o_settings in self.option_settings.items():
            self.option_vars[o_name] = tk.StringVar()
            garbage = tk.Checkbutton(options_frame, text=o_settings['text'], variable=self.option_vars[o_name],
                                     onvalue='True', offvalue='False', command=lambda x=o_name: self.change_setting(x))
            garbage.grid(row=row, column=0, sticky=tk.W)
            self.option_vars[o_name].set(settings[self.log_key][o_name])
            row += 1

        button_frame = tk.Frame(self)
        button_frame.grid(row=3, column=0, sticky=tk.E+tk.S, padx=5, pady=2)

        self.export = tk.Button(button_frame, text='Export', command=self.export)
        self.export.grid(row=0, column=0)

        self.quit = tk.Button(button_frame, text='Cancel', command=self.close)
        self.quit.grid(row=0, column=1)

        self.title(self.t)
        self.resizable(width=False, height=False)
        self.geometry()

        posX = self.parent.winfo_x() + (self.parent.winfo_width() - self.w)//2
        posY = self.parent.winfo_y() + (self.parent.winfo_height() - self.h)//2
        pos = f'{self.w}x{self.h}+{posX}+{posY}'
        self.geometry(pos)

        self._populate_script_tree()

    def _populate_script_tree(self):
        all_scripts = self.callbacks['get_tree']()
        iid = 0
        for script in all_scripts:
            self.scripts.insert(parent='', iid=iid, text=script['Name'], values=[], index='end')
            self.script_ids[iid] = script['Name']
            iid += 1

    def get_directory(self):
        kwargs = {}
        cur_dir = self.directory_var.get()
        if os.path.exists(cur_dir):
            if os.path.isdir(cur_dir):
                kwargs['initialdir'] = cur_dir
        new_dir = filedialog.askdirectory(**kwargs)
        if new_dir == '':
            return
        self.directory_var.set(new_dir)
        self.tkraise()

    def change_setting(self, setting):
        settings[self.log_key][setting] = self.option_vars[setting].get()

    def export(self):
        directory = self.directory_var.get()
        if not os.path.exists(directory):
            return
        options = {
            'use_garbage': self.option_vars['use_garbage'].get() == 'True',
            'combine_footer_links': self.option_vars['combine_footer'].get() == 'True',
            'add_spurious_refresh': self.option_vars['all_refresh'].get() == 'True',
            'compress_aklz': self.option_vars['compress_aklz'].get() == 'True'
        }
        self.callbacks['export'](directory=directory,
                                 scripts=[self.script_ids[int(s)] for s in self.scripts.selection()],
                                 options=options)
        self.close()

    def close(self):
        self.callbacks['close'](self.name, self)
