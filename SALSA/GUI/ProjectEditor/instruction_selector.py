import json
import tkinter as tk


import SALSA.GUI.widgets as w
from Common.setting_class import settings


class SearchWidget(w.ValidatedMixin, tk.Entry):

    def __init__(self, parent, callbacks, *a, **kw):
        super().__init__(parent, *a, **kw)

        self.callbacks = callbacks

    def _key_validate(self, proposed, current, char, event, index, action):
        self.callbacks['search'](proposed)

        return True


default_headers = {
    'instruction': ['inst_ID', 'name']
}

header_settings = {
    'instruction': {
        'inst_ID': {'label': 'ID', 'width': 40, 'stretch': False},
        'name': {'label': 'Name', 'width': 250, 'stretch': False}
    }
}


default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class InstructionSelectorWidget(tk.Frame):

    log_name = 'InstSelView'
    entry_max = 10

    def __init__(self, parent, callbacks, inst_trace, x, y, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        self.inst_trace = inst_trace

        if self.log_name not in settings.keys():
            settings[self.log_name] = {}

        # if 'headers' not in settings[self.log_name].keys():
        settings.set_single(self.log_name, 'headers', json.dumps(default_headers))

        self.visible_headers = json.loads(settings[self.log_name]['headers'])

        search_label = tk.Label(self, text='Search: ')
        search_label.grid(row=0, column=0)
        self.search_var = tk.StringVar(self, '')
        self.search = SearchWidget(self, textvariable=self.search_var, callbacks={'search': self.update_search})
        self.search.grid(row=0, column=1, sticky=tk.E+tk.W)

        r_callbacks = {
            'select': self.select_inst
        }
        self.result_dropdown = w.DataTreeview(parent, name='result', callbacks=r_callbacks)
        self.result_dropdown.place(x=x, y=y, anchor='nw')
        self.result_dropdown.heading('#0', text='Relevant Instructions')
        self.result_dropdown.configure(show='tree')
        self.result_dropdown.configure(height=1)

    def update_search(self, current):
        self.update_menu(self.callbacks['get_relevant'](current))

    def update_menu(self, relevant_entries):
        self.result_dropdown.clear_all_entries()
        for entry in relevant_entries:
            entry_parts = entry.split(' - ')
            inst_id = entry_parts[0]
            self.result_dropdown.insert_entry(parent='', index='end', text=entry, values=[], row_data=inst_id)
        rows = min(self.entry_max, len(relevant_entries))
        rows = max(rows, 1)
        self.result_dropdown.configure(height=rows)

    def select_inst(self, name, new_ID):
        self.callbacks['set_inst_id'](*self.inst_trace, new_ID)
        self.destroy()
        self.result_dropdown.destroy()
        self.callbacks['update_tree']()
