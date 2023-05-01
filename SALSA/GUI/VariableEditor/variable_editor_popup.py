import tkinter as tk
from math import floor
from tkinter import filedialog, ttk
from typing import Tuple, List

from SALSA.Common.setting_class import settings
from SALSA.GUI import widgets as w


class VariablePopup(tk.Toplevel):
    t = 'Variable Editor'
    log_key = 'VarEditPopup'
    w = 250
    h = 400

    option_settings = {}
    canvas_names = ['Bit', 'Byte', 'Int', 'Float']

    def __init__(self, parent, callbacks, name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = callbacks
        self.name = name
        self.script_ids = {}

        if self.log_key not in settings:
            settings[self.log_key] = {}

        for s, v in self.option_settings.items():
            if s not in settings[self.log_key]:
                settings[self.log_key][s] = v['default']

        script_frame = tk.LabelFrame(self, text='Scripts')
        script_frame.grid(row=0, column=0, sticky='NSEW')

        tree_callbacks = {'select': self.script_select}

        self.script_tree = w.DataTreeview(script_frame, 'script', tree_callbacks)
        anchor = tk.CENTER
        self.script_tree.heading('#0', text='Script', anchor=anchor)
        self.script_tree.column('#0', anchor=anchor, minwidth=10, width=100, stretch=True)
        self.script_tree.grid(row=0, column=0, sticky='NSEW')
        script_tree_scroll = tk.Scrollbar(script_frame, orient='vertical', command=self.script_tree.yview)
        script_tree_scroll.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.script_tree.config(yscrollcommand=script_tree_scroll.set)
        self.script_tree.config(show='tree')

        self.cur_script = None

        variable_frame = tk.LabelFrame(self, text='Variables')
        variable_frame.grid(row=0, column=1, sticky='NSEW')
        variable_frame.columnconfigure(0, weight=1)
        variable_frame.rowconfigure(0, weight=1)

        self.variable_notebook = ttk.Notebook(variable_frame)
        self.variable_notebook.grid(row=0, column=0, sticky='NSEW')
        self.variable_notebook.columnconfigure(0, weight=1)

        self.canvases = {}
        for name in self.canvas_names:
            self.canvases[name] = w.ScrollLabelFrame(self.variable_notebook)
            self.canvases[name].grid(row=0, column=0, sticky='NSEW')
            self.canvases[name].scroll_frame.columnconfigure(1, weight=1)
            label = name + 's'
            self.variable_notebook.add(self.canvases[name], text=label)

        self.cur_var_dict = None
        self.cur_row = -1

        self.cur_var_aliases = []
        self.alias_entry_var = tk.StringVar()
        self.alias_entry: tk.Entry = None
        self.alias_labels = {k: [] for k in self.canvas_names}

        variable_usage_frame = tk.LabelFrame(self, text='Variable Usage')
        variable_usage_frame.grid(row=0, column=2, sticky='NSEW')
        variable_usage_frame.columnconfigure(0, weight=1)
        variable_usage_frame.rowconfigure(0, weight=1)

        self.variable_usage = w.ScrollLabelFrame(variable_usage_frame)
        self.variable_usage.grid(row=0, column=0, sticky='NSEW')

        self.status_label = tk.Label(self, text='')
        self.status_label.grid(row=1, column=0, columnspan=3)

        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=5)
        self.rowconfigure(0, weight=1)

        self._populate_script_tree()

    def _populate_script_tree(self):
        all_scripts = self.callbacks['get_scripts']()
        for script in all_scripts:
            self.script_tree.insert_entry(parent='', text=script['name'], values=[], index='end',
                                          row_data=script['name'])

    def script_select(self, tree, script_name):
        self.cur_script = script_name
        var_dict = self.callbacks['get_variables'](script_name)
        self.populate_variables(var_dict)

    def populate_variables(self, var_dict):
        for canvas in self.canvases.values():
            for item in canvas.scroll_frame.winfo_children():
                item.destroy()
            header_label_1 = tk.Label(canvas.scroll_frame, text='ID   ')
            header_label_1.grid(row=0, column=0)
            header_label_2 = tk.Label(canvas.scroll_frame, text='Alias')
            header_label_2.grid(row=0, column=1)

        self.cur_var_dict = var_dict
        self.cur_var_aliases = []
        self.alias_labels = {k: [] for k in self.canvas_names}
        for var_type, var_list in var_dict.items():
            canv_key = var_type[:-3]
            cur_row = 1
            for v_id, v_alias in var_list.items():
                next_id_label = tk.Label(self.canvases[canv_key].scroll_frame, text=v_id)
                next_id_label.grid(row=cur_row, column=0)
                next_id_label.bind("<Double-ButtonPress-1>", lambda event, r=cur_row: self.get_usages(row=r))
                next_id_label.bind("<Button-3>", lambda event, r=cur_row: self.var_right_click(row=r, event=event))

                if v_alias in self.cur_var_aliases:
                    # Throw error on this one? Mark it incomplete due to duplicate?
                    print("duplicate alias present")
                elif v_alias == '':
                    pass
                else:
                    self.cur_var_aliases.append(v_alias)
                next_alias_label = tk.Label(self.canvases[canv_key].scroll_frame, text=v_alias)
                next_alias_label.grid(row=cur_row, column=1, sticky='NSEW')
                next_alias_label.bind("<Double-ButtonPress-1>", lambda event, r=cur_row: self.edit_alias(row=r))
                next_alias_label.bind("<Button-3>", lambda event, r=cur_row: self.var_right_click(row=r, event=event))
                self.alias_labels[canv_key].append(next_alias_label)
                cur_row += 1

    def var_right_click(self, row, event):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label='Change variable alias', command=lambda: self.edit_alias(row))
        # m.add_command(label='Copy alias to another script', command=lambda: self.copy_alias(row))
        m.add_command(label='Find variable usages', command=lambda: self.get_usages(row))
        m.bind('<Leave>', m.destroy)
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    def edit_alias(self, row):
        var_type = self.determine_tab()
        row_id = list(self.cur_var_dict[f'{var_type}Var'].keys())[row - 1]
        self.alias_entry_var.set(self.cur_var_dict[f'{var_type}Var'][row_id])
        self.alias_entry = tk.Entry(self.canvases[var_type].scroll_frame, textvariable=self.alias_entry_var)
        self.alias_entry.grid(row=row, column=1)
        self.alias_entry.bind("<Return>", lambda event: self.attempt_create_alias(var_type, row))
        self.alias_entry.focus()

    def attempt_create_alias(self, var_type, row):
        # Check for unique alias
        new_alias = self.alias_entry_var.get()
        row_id = list(self.cur_var_dict[f'{var_type}Var'].keys())[row - 1]
        cur_alias = self.cur_var_dict[f'{var_type}Var'][row_id]
        if new_alias == cur_alias:
            self.alias_entry.destroy()
            return
        if new_alias in self.cur_var_aliases:
            # Turn entry red
            self.alias_entry.config(foreground='red')
            # Add error to status bar
            self.status_label.config(text='Warning: Unable to set alias, this alias is already in use')
            return
        if new_alias == '':
            self.cur_var_aliases.pop(self.cur_var_aliases.index(cur_alias))
            self.cur_var_dict[f'{var_type}Var'][row_id] = ''
            self.alias_labels[var_type][row - 1].config(text=new_alias)
            self.alias_entry.destroy()
            return
        self.cur_var_aliases.append(new_alias)
        self.status_label.config(text='')

        # Set alias via callback
        self.cur_var_dict[f'{var_type}Var'][row_id] = new_alias
        self.callbacks['set_alias'](self.cur_script, f'{var_type}Var', row_id, new_alias)
        # Set
        self.alias_labels[var_type][row - 1].config(text=new_alias)
        self.alias_entry.destroy()

    def copy_alias(self, row):
        # Popup to select scripts to copy to?
        pass

    def get_usages(self, row):
        # Get variable usages from the active script for the variable selected
        var_type = self.determine_tab()
        row_id = list(self.cur_var_dict[f'{var_type}Var'].keys())[row - 1]
        self.populate_usages(self.callbacks['get_var_usage'](self.cur_script, f'{var_type}Var', row_id))

    def populate_usages(self, usage_list: List[Tuple[str, int, str]]):
        for child in self.variable_usage.scroll_frame.winfo_children():
            child.destroy()

        cur_row = 0
        for usage in usage_list:
            u_label = tk.Label(self.variable_usage.scroll_frame, text=' - '.join(usage))
            u_label.grid(row=cur_row, column=0, sticky='NSEW')
            cur_row += 1

    def determine_tab(self):
        tab = self.variable_notebook.index('current')
        var_type = self.canvas_names[tab]
        return var_type
