import tkinter as tk
from tkinter import ttk
from typing import Tuple, List

from SALSA.GUI.Widgets.data_treeview import DataTreeview
from SALSA.GUI.themes import dark_theme, light_theme
from SALSA.Common.setting_class import settings
from SALSA.GUI.Widgets import widgets as w

no_alias = '               '

global_tag = 'global'

headers = ['id', 'alias']

header_settings = {
    'id': {'label': 'ID', 'width': 90, 'stretch': True},
    'alias': {'label': 'Alias', 'width': 150, 'stretch': True}
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class VariablePopup(tk.Toplevel):
    t = 'Variable Editor'
    log_key = 'VarEditPopup'
    width = 800
    height = 1000

    option_settings = {}
    tree_names = ['Bit', 'Byte', 'Int', 'Float']

    def __init__(self, parent, callbacks, name, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = callbacks
        self.name = name
        self.script_ids = {}
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.configure(**theme['Ttoplevel']['configure'])

        if self.log_key not in settings:
            settings[self.log_key] = {}

        for s, v in self.option_settings.items():
            if s not in settings[self.log_key]:
                settings[self.log_key][s] = v['default']

        script_frame = ttk.LabelFrame(self, text='Scripts')
        script_frame.grid(row=0, column=0, sticky='NSEW')
        script_frame.rowconfigure(0, weight=1)

        tree_callbacks = {'select': self.script_select}

        self.script_tree = DataTreeview(script_frame, name='script', callbacks=tree_callbacks, return_none=True)
        anchor = tk.CENTER
        self.script_tree.heading('#0', text='Script', anchor=anchor)
        self.script_tree.column('#0', anchor=anchor, minwidth=10, width=100, stretch=True)
        self.script_tree.grid(row=0, column=0, sticky='NSEW')
        script_tree_scroll = ttk.Scrollbar(script_frame, orient='vertical', command=self.script_tree.yview)
        script_tree_scroll.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.script_tree.config(yscrollcommand=script_tree_scroll.set)
        self.script_tree.config(show='tree')

        self.cur_script = None
        self.cur_var_aliases = []

        variable_frame = ttk.LabelFrame(self, text='Variables')
        variable_frame.grid(row=0, column=1, sticky='NSEW')
        variable_frame.columnconfigure(0, weight=1)
        variable_frame.rowconfigure(0, weight=1)

        self.variable_notebook = ttk.Notebook(variable_frame)
        self.variable_notebook.grid(row=0, column=0, sticky='NSEW')
        self.variable_notebook.columnconfigure(0, weight=1)

        self.var_trees = {}
        for tree_name in self.tree_names:
            tree_frame = tk.Frame(self.variable_notebook)
            tree_frame.grid(row=0, column=0, sticky='NSEW')
            tree_frame.rowconfigure(0, weight=1)
            tree_frame.columnconfigure(0, weight=1)
            columns = list(header_settings.keys())[1:]
            self.var_trees[tree_name] = DataTreeview(tree_frame, name=tree_name, columns=columns, can_open=False,
                                                       selectmode='extended')
            self.var_trees[tree_name].grid(row=0, column=0, sticky='NSEW')
            first = True
            for name, d in header_settings.items():
                label = d.get('label', default_tree_label)
                anchor = d.get('anchor', default_tree_anchor)
                minwidth = d.get('minwidth', default_tree_minwidth)
                width = d.get('width', default_tree_width)
                stretch = d.get('stretch', default_tree_stretch)
                if first:
                    name = '#0'
                    first = False
                self.var_trees[tree_name].heading(name, text=label, anchor=anchor)
                self.var_trees[tree_name].column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
            script_tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.var_trees[tree_name].yview)
            script_tree_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
            self.var_trees[tree_name].config(yscrollcommand=script_tree_scrollbar.set)
            self.var_trees[tree_name].bind("<Double-ButtonPress-1>", self.var_double_click)
            self.var_trees[tree_name].bind("<Button-3>", self.var_right_click)

            label = tree_name + 's'
            self.variable_notebook.add(tree_frame, text=label)

        variable_usage_frame = ttk.LabelFrame(self, text='Variable Usage')
        variable_usage_frame.grid(row=0, column=2, sticky='NSEW')
        variable_usage_frame.columnconfigure(0, weight=1)
        variable_usage_frame.rowconfigure(0, weight=1)

        self.variable_usage = w.ScrollLabelFrame(variable_usage_frame, theme=theme)
        self.variable_usage.grid(row=0, column=0, sticky='NSEW')

        self.status_label = ttk.Label(self, text='')
        self.status_label.grid(row=1, column=0, columnspan=3)

        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=5)
        self.rowconfigure(0, weight=1)

        self._populate_script_tree()

        self.alias_widgets = {}
        self.cur_alias_id = 0
        self.bind('<Configure>', lambda event: self.adjust_edit_alias_entries())

    def _populate_script_tree(self):
        self.script_tree.insert_entry(parent='', text='global', values=[], index='end', row_data=None)
        all_scripts = self.callbacks['get_scripts']()
        for script in all_scripts:
            self.script_tree.insert_entry(parent='', text=script['name'], values=[], index='end', row_data=script['name'])

    def script_select(self, name, script_name):
        self.cur_script = script_name
        var_dict = self.callbacks['get_variables'](script_name)
        self.populate_variables(var_dict, script_name is None)

    def populate_variables(self, var_dict, is_global):
        for tree in self.var_trees.values():
            tree.clear_all_entries()

        for var_type, v_dict in var_dict.items():
            tree_key = var_type[:-3]
            for v_id, v_entry in v_dict.items():
                kwargs = {'parent': '', 'index': 'end', 'text': v_id}
                values = []
                for col in headers[1:]:
                    values.append(v_entry[col])
                    v_entry.pop(col)
                if values != ['']:
                    self.cur_var_aliases += values
                kwargs['values'] = values
                kwargs = {**kwargs}
                if v_entry['is_global'] and not is_global:
                    kwargs['tags'] = [global_tag]
                self.var_trees[tree_key].insert_entry(**kwargs)

    def var_right_click(self, e):
        if e.widget.identify('region', e.x, e.y) == 'heading':
            return
        sel_iid = e.widget.identify_row(e.y)
        cur_selection = e.widget.selection()
        if len(cur_selection) == 0:
            e.widget.selection_set(sel_iid)
            e.widget.focus(sel_iid)

        m = tk.Menu(self, tearoff=0)
        var_type = self.determine_tab()
        can_change = global_tag not in e.widget.item(sel_iid)['tags']
        if len(cur_selection) == 1 and can_change:
            m.add_command(label='Change variable alias', command=lambda: self.edit_alias(var_type, sel_iid, '#1'))

        if len(cur_selection) == 1:
            m.add_command(label='Find variable usages', command=lambda: self.get_usages(var_type, sel_iid))

        if can_change:
            m.add_command(label='Set Global', command=lambda: self.set_global(var_type, cur_selection))
        else:
            m.entryconfig('Change variable alias', state='disabled')
            m.add_command(label='Remove Global', command=lambda: self.remove_global(var_type, cur_selection))

        m.bind('<Leave>', m.destroy)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def var_double_click(self, e):
        # Find the region clicked, only edit if region is a cell
        if e.widget.identify_region(e.x, e.y) != 'cell':
            return

        sel_iid = e.widget.identify_row(e.y)
        tree_key = self.determine_tab()

        # get column that was clicked
        column = e.widget.identify_column(e.x)
        if column == '#0':
            return self.get_usages(tree_key=tree_key, sel_iid=sel_iid)

        if global_tag not in e.widget.item(sel_iid)['tags']:
            self.edit_alias(tree_key=tree_key, sel_iid=sel_iid, column=column)

    def edit_alias(self, tree_key, sel_iid, column):
        cur_alias = self.var_trees[tree_key].item(sel_iid)['values'][0]
        cell_bbox = self.var_trees[tree_key].bbox(sel_iid, column)

        alias_entry = tk.Entry(self.var_trees[tree_key])
        alias_entry.insert(0, cur_alias)
        alias_entry.cur_alias = cur_alias
        alias_entry.place(x=cell_bbox[0]+2, y=cell_bbox[1], w=cell_bbox[2]-4, h=cell_bbox[3])
        alias_entry.bind("<Return>", lambda event: self.attempt_create_alias(tree_key, sel_iid, event))
        alias_entry.bind("<Escape>", lambda event: self.delete_alias_entry(event))
        alias_entry.my_id = self.cur_alias_id
        self.alias_widgets[self.cur_alias_id] = {'tree': tree_key, 'sel_iid': sel_iid, 'column': column, 'widget': alias_entry}
        self.cur_alias_id += 1
        alias_entry.focus()

    def adjust_edit_alias_entries(self):
        for v in self.alias_widgets.values():
            cell_bbox = self.var_trees[v['tree']].bbox(v['sel_iid'], v['column'])
            v['widget'].place_configure(x=cell_bbox[0]+2, y=cell_bbox[1], width=cell_bbox[2]-4, height=cell_bbox[3])

    def delete_alias_entry(self, e):
        self.alias_widgets.pop(e.widget.my_id)
        e.widget.destroy()

    def attempt_create_alias(self, tree_key, sel_iid, e):
        # Check for unique alias
        new_alias = e.widget.get()
        if new_alias == e.widget.cur_alias:
            self.delete_alias_entry(e)
            return
        row_id = self.var_trees[tree_key].item(sel_iid)['text']
        if new_alias in self.cur_var_aliases:
            # Turn entry red
            e.widget.config(foreground='red')
            # Add error to status bar
            self.status_label.config(text=f'Warning: Unable to set alias, this ({new_alias}) is already in use')
            return
        if e.widget.cur_alias != '':
            self.cur_var_aliases.remove(e.widget.cur_alias)
        self.delete_alias_entry(e)
        self.unbind()
        if new_alias == '':
            return
        self.cur_var_aliases.append(new_alias)
        self.status_label.config(text='')

        # Set alias via callback
        self.callbacks['set_alias'](self.cur_script, f'{tree_key}Var', row_id, new_alias)
        self.var_trees[tree_key].item(sel_iid, values=[new_alias])

    def copy_alias(self, row):
        # Popup to select scripts to copy to?
        pass

    def get_usages(self, tree_key, sel_iid):
        # Get variable usages from the active script for the variable selected
        row_id = int(self.var_trees[tree_key].item(sel_iid)['text'])
        self.populate_usages(self.callbacks['get_var_usage'](self.cur_script, f'{tree_key}Var', row_id))

    def populate_usages(self, usage_list: List[Tuple[str, int, str]]):
        for child in self.variable_usage.scroll_frame.winfo_children():
            child.destroy()

        cur_row = 0
        for usage in usage_list:
            u_label = ttk.Label(self.variable_usage.scroll_frame, text=' - '.join(usage), style='canvas.TLabel')
            u_label.grid(row=cur_row, column=0, sticky='NSEW')
            cur_row += 1

    def determine_tab(self):
        tab = self.variable_notebook.index('current')
        var_type = self.tree_names[tab]
        return var_type

    def set_global(self, tree_key, selection):
        for sel_iid in selection:
            sel_item = self.var_trees[tree_key].item(sel_iid)
            self.callbacks['set_alias'](None, f'{tree_key}Var', sel_item['text'], sel_item['values'][0])

    def remove_global(self, tree_key, selection):
        for sel_iid in selection:
            sel_item = self.var_trees[tree_key].item(sel_iid)
            self.callbacks['remove_global'](f'{tree_key}Var', sel_item['text'])

    def on_close(self):
        self.callbacks['close'](self.name, self)

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
        self.variable_usage.change_theme(theme)
