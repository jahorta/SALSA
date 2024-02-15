import os.path
import tkinter as tk
from tkinter import ttk

from SALSA.Common.constants import alt_sep
from SALSA.GUI.Widgets.data_treeview import DataTreeview

header_settings = {
    'results': {
        'link': {'label': 'Script', 'width': 300, 'stretch': False}
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
        self.rowconfigure(1, weight=1)

        self.search_icon = tk.BitmapImage(file=os.path.join(os.path.dirname(__file__), "search_icon_20x20.xbm"),
                                          foreground=theme['TButton']['configure']['foreground'],
                                          background=theme['TButton']['configure']['background'])
        self.filter_icon = tk.BitmapImage(file=os.path.join(os.path.dirname(__file__), "filtering_icon_20x20.xbm"),
                                          foreground=theme['TButton']['configure']['foreground'],
                                          background=theme['TButton']['configure']['background'])

        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky='NSEW')
        search_frame.columnconfigure(0, weight=1)

        if search_string is None:
            search_string = ""
        self.search_string = tk.StringVar(search_frame, search_string)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_string)
        self.search_entry.grid(row=0, column=0, sticky='NSEW')

        self.search_button = ttk.Button(search_frame, image=self.search_icon, command=self.search)
        self.search_button.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E)

        self.filter_button = ttk.Button(search_frame, image=self.filter_icon, command=self.open_filters)
        self.filter_button.grid(row=0, column=2, sticky=tk.N + tk.S + tk.E)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky='NSEW')
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        columns = list(header_settings['results'].keys())[1:]
        self.result_tree = DataTreeview(tree_frame, name='results', columns=columns, can_open=True, can_move=False,
                                        callbacks={'select': self.on_result_select})
        self.result_tree.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in header_settings['results'].items():
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
        close_button.grid(row=2, column=0, sticky=tk.E)

        self.protocol('WM_DELETE_WINDOW', self.close)

    def open_filters(self):
        pass

    def search(self):
        # refresh errors in each script
        self.result_tree.clear_all_entries()
        results = self.callbacks['search'](self.search_string.get())

        if results is None:
            return

        for loc, scts in results.items():
            g_id = self.result_tree.insert_entry(parent='', index='end', text=loc, values=[], row_data=None)
            for sct, results in scts.items():
                s_id = self.result_tree.insert_entry(parent=g_id, index='end', text=sct, values=[], row_data=None)
                for r in results:
                    l = alt_sep.join(r)
                    self.result_tree.insert_entry(parent=s_id, index='end', text=l, values=[], row_data=l)

    def on_result_select(self, name, row_data):
        if row_data is None:
            return
        sel_iid = self.result_tree.focus()
        script_entry = self.result_tree.parent(sel_iid)
        script = self.result_tree.item(script_entry)['text']
        location = self.result_tree.item(self.result_tree.parent(script_entry))['text']
        if location == 'dialog':
            group, s_id = row_data.split(alt_sep)
            self.callbacks['goto_dialog'](script, group, s_id)
            return
        pts = row_data.split(alt_sep)
        section = pts[0]
        inst = pts[1]
        if len(pts) > 2:
            param = pts[3]
        else:
            param = None
        self.callbacks['goto_result'](script=script, sect=section, inst=inst, param=param)

    def close(self):
        self.callbacks['close'](self.name, self)

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
        self.search_icon.configure(foreground=theme['TButton']['configure']['foreground'],
                                   background=theme['TButton']['configure']['background'])
        self.filter_icon.configure(foreground=theme['TButton']['configure']['foreground'],
                                   background=theme['TButton']['configure']['background'])
