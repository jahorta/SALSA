import json
import tkinter as tk
from tkinter import ttk

import SALSA.GUI.Widgets.widgets as w
from SALSA.GUI.Widgets.data_treeview import DataTreeview
from SALSA.Common.setting_class import settings


class SearchWidget(w.ValidatedMixin, ttk.Entry):

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


class InstructionSelectorWidget(ttk.Frame):

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

        search_label = ttk.Label(self, text='Search: ')
        search_label.grid(row=0, column=0)
        self.search_var = tk.StringVar(self, '')
        self.search = SearchWidget(self, textvariable=self.search_var, callbacks={'search': self.update_search})
        self.search.grid(row=0, column=1, sticky=tk.E+tk.W)

        r_callbacks = {
            'select': self.select_inst
        }
        self.result_dropdown = DataTreeview(parent, name='result', callbacks=r_callbacks)
        self.result_dropdown.place(x=x, y=y, anchor='nw')
        self.result_dropdown.heading('#0', text='Relevant Instructions')
        self.result_dropdown.configure(show='tree')
        self.result_dropdown.configure(height=1)

        self.search.focus_set()

        self.search.bind('<KeyPress-Escape>', self.cancel)
        self.search.bind('<KeyPress-Return>', self.select_inst_by_enter)
        self.search.bind('<KeyPress-Down>', self.move_to_results)

        self.result_dropdown.bind('<KeyPress-Escape>', self.cancel)
        self.result_dropdown.bind('<KeyPress-Return>', self.select_inst_by_enter)
        self.result_dropdown.bind('<KeyPress-Up>', self.handle_dropdown_up_keypress)

    def update_search(self, current):
        self.update_menu(self.callbacks['get_relevant'](current, exclude_modifiers=True))

    def update_menu(self, relevant_entries):
        self.result_dropdown.clear_all_entries()
        if len(relevant_entries) == 0:
            return
        rows = min(self.entry_max, len(relevant_entries))
        rows = max(rows, 1)
        if len(relevant_entries) > rows:
            relevant_entries = relevant_entries[:rows]
        self.result_dropdown.configure(height=rows)
        for entry in relevant_entries:
            entry_parts = entry.split(' - ')
            inst_id = entry_parts[0]
            self.result_dropdown.insert_entry(parent='', index='end', text=entry, values=[], row_data=inst_id)
        self.result_dropdown.selection_set(self.result_dropdown.get_children('')[0])

    def select_inst(self, name, new_ID):
        end_callback = self.finish_select_inst
        end_kwargs = {'result': None, 'new_ID': new_ID}
        children = self.callbacks['get_children'](*self.inst_trace)
        if self.callbacks['is_group'](*self.inst_trace):
            return self.callbacks['group_inst_handler'](children=children, new_id=new_ID, end_callback=end_callback, end_kwargs=end_kwargs)
        end_callback(**end_kwargs)

    def finish_select_inst(self, result, new_ID):
        if result is not None:
            if result == 'cancel':
                return
        self.callbacks['set_inst_id'](*self.inst_trace, new_id=new_ID, change_type=result)
        self.cancel(None)
        self.callbacks['update_tree']()

    def move_to_results(self, e):
        children = self.result_dropdown.get_children('')
        if len(children) == 0:
            return
        self.result_dropdown.focus_set()
        if len(children) == 1:
            target_index = 0
        else:
            target_index = 1
        targeted_item = self.result_dropdown.get_children('')[target_index]
        self.result_dropdown.focus(targeted_item)
        self.result_dropdown.selection_set([targeted_item])

    def handle_dropdown_up_keypress(self, e):
        children = e.widget.get_children('')
        cur_item_ind = children.index(e.widget.selection()[0])
        if cur_item_ind == 0:
            self.search.focus_set()

    def select_inst_by_enter(self, e):
        if len(self.result_dropdown.get_children('')) == 0:
            return
        self.select_inst(name=None, new_ID=self.result_dropdown.row_data[self.result_dropdown.selection()[0]])

    def cancel(self, e):
        self.result_dropdown.destroy()
        self.destroy()
