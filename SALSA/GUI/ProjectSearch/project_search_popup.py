import tkinter as tk
from tkinter import ttk

from SALSA.Common.constants import alt_sep
from SALSA.GUI.Widgets.data_treeview import DataTreeview

header_settings = {
    'results': {
        'script': {'label': 'Script', 'width': 80, 'stretch': False},
        'type': {'label': 'Type', 'width': 100, 'stretch': False},
        'error': {'label': 'Error', 'width': 150, 'stretch': False},
        'info': {'label': 'Information', 'width': 300, 'stretch': True}
    }
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class ProjectSearchPopup(tk.Toplevel):

    t = 'Project Search'
    log_key = 'PRJSearchPopup'
    w = 250
    h = 400

    def __init__(self, parent, callbacks, name, theme, *args, search_string=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.name = name
        self.callbacks = callbacks
        self.configure(**theme['Ttoplevel']['configure'])
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky='NSEW')

        if search_string is None:
            search_string = ""
        self.search_string = tk.StringVar(search_frame, search_string)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_string)
        self.search_entry.grid(row=0, column=0, sticky='NSEW')

        self.search_button = ttk.Button(search_frame, image="", command=self.search)
        self.search_button.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E)

        self.filter_button = ttk.Button(search_frame, image="", command=self.open_filters)
        self.filter_button.grid(row=0, column=3, sticky=tk.N + tk.S + tk.E)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky='NSEW')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = list(header_settings['results'].keys())[1:]
        self.result_tree = DataTreeview(tree_frame, name='results', columns=columns, can_open=True, can_move=False,
                                        callbacks={'select': self.on_error_select})
        self.result_tree.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in header_settings['search'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.result_tree.heading(name, text=label, anchor=anchor)
            self.result_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        error_tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.result_tree.yview)
        error_tree_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.result_tree.config(yscrollcommand=error_tree_scrollbar.set)

        close_button = ttk.Button(self, text='Close', command=self.close)
        close_button.grid(row=1, column=0, sticky=tk.E)

        self.protocol('WM_DELETE_WINDOW', self.close)

    def open_filters(self):
        pass

    def search(self):
        # refresh errors in each script
        self.result_tree.clear_all_entries()
        results = self.callbacks['search']()

        for name, results in results.items():
            for error in results:
                self.result_tree.insert_entry(parent='', index='end', text=name, values=error[1:], row_data=error[3])

    def on_error_select(self, name, row_data):
        sel_iid = self.result_tree.focus()
        script = self.result_tree.item(sel_iid)['text']
        section, inst, param = row_data.split(alt_sep)
        self.callbacks['goto_result'](script=script, sect=section, inst=inst, param=param)

    def close(self):
        self.callbacks['close'](self.name, self)

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
