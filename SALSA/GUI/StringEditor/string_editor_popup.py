import tkinter as tk
from tkinter import ttk

from SALSA.Common.setting_class import settings
from SALSA.GUI.widgets import DataTreeview

tree_settings = {
    'script': {
        'name': {'label': 'Name', 'width': 100, 'stretch': True}
    },
    'string': {
        'location': {'label': 'Name', 'width': 120, 'stretch': True},
        'string': {'label': 'Name', 'width': 200, 'stretch': True}
    }
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class StringPopup(tk.Toplevel):
    t = 'SALSA - String Editor'
    log_key = 'StrEditPopup'
    w = 600
    h = 400

    option_settings = {}

    def __init__(self, parent, callbacks, name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = callbacks
        self.name = name

        # if self.log_key not in settings:
        #     settings.add_group(self.log_key)

        self.columnconfigure(0, weight=1)

        save_frame = tk.Frame(self)
        save_frame.grid(row=0, column=0, sticky='NSEW')

        save_button = tk.Button(save_frame, text='Save', command=self.save, state='disabled')
        save_button.grid(row=0, column=0, sticky=tk.W)

        upper_frame = tk.Frame(self)
        upper_frame.grid(row=1, column=0, sticky='NSEW')
        upper_frame.columnconfigure(1, weight=1)
        upper_frame.rowconfigure(0, weight=1)

        script_tree_frame = tk.LabelFrame(upper_frame, text='Scripts')
        script_tree_frame.grid(row=0, column=0, sticky='NSEW', padx=5)
        script_tree_frame.rowconfigure(0, weight=1)

        columns = list(tree_settings['script'].keys())[1:]
        self.scripts = DataTreeview(script_tree_frame, name='script', columns=columns)
        self.scripts.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in tree_settings['script'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.scripts.heading(name, text=label, anchor=anchor)
            self.scripts.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        script_tree_scrollbar = tk.Scrollbar(script_tree_frame, orient='vertical', command=self.scripts.yview)
        script_tree_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.scripts.config(yscrollcommand=script_tree_scrollbar.set)
        self.scripts.config(show='tree')
        self.scripts.add_callback('select', self.on_script_select)

        string_tree_frame = tk.LabelFrame(upper_frame, text='Strings')
        string_tree_frame.grid(row=0, column=1, sticky='NSEW', padx=5)
        string_tree_frame.columnconfigure(0, weight=1)
        string_tree_frame.rowconfigure(0, weight=1)

        columns = list(tree_settings['string'].keys())[1:]
        self.strings = DataTreeview(string_tree_frame, name='strings', columns=columns)
        self.strings.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in tree_settings['script'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.strings.heading(name, text=label, anchor=anchor)
            self.strings.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        string_tree_scrollbar = tk.Scrollbar(string_tree_frame, orient='vertical', command=self.strings.yview)
        string_tree_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.strings.config(yscrollcommand=string_tree_scrollbar.set)
        self.strings.config(show='tree')
        self.strings.add_callback('select', self.edit_string)

        lower_frame = tk.Frame(self)
        lower_frame.grid(row=2, column=0, sticky='NSEW')
        lower_frame.columnconfigure(0, weight=1)

        head_label = tk.Label(lower_frame, text='Textbox Header')
        head_label.grid(row=0, column=0, sticky=tk.W)
        self.head_entry = tk.Entry(lower_frame, state='disabled')
        self.head_entry.grid(row=1, column=0, sticky=tk.W)
        self.head_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.head_entry.bind('<FocusOut>', lambda e, k='head': self.on_entry_focus_out(k, e))

        body_label = tk.Label(lower_frame, text='Textbox Body')
        body_label.grid(row=2, column=0, sticky=tk.W)
        self.body_entry = tk.Text(lower_frame, wrap=tk.WORD)
        self.body_entry.grid(row=3, column=0, sticky=tk.W + tk.E)
        self.body_entry.bind('<FocusIn>', self.on_text_focus_in)
        self.body_entry.bind('<FocusOut>', lambda e, k='body': self.on_text_focus_out(k, e))

        self.update_scripts()

        self.cur_script = ''
        self.cur_string_id = ''
        self.string_defaults = {}
        self.string_changes = {}

        self.title(self.t)

        posX = self.parent.winfo_x() + (self.parent.winfo_width() - self.w)//2
        posY = self.parent.winfo_y() + (self.parent.winfo_height() - self.h)//2
        pos = f'{self.w}x{self.h}+{posX}+{posY}'
        self.geometry(pos)

    def update_scripts(self, ):
        script_tree = self.callbacks['get_scripts']()
        for entry in script_tree:
            self.scripts.insert_entry(parent='', index='end', text=entry['name'], values=[], row_data=entry['row_data'])

    def on_script_select(self, name, script):
        self.cur_script = script
        self.update_string_tree(script)

    def update_string_tree(self, script):
        self.strings.clear_all_entries()
        headers = list(tree_settings['string'].keys())
        string_tree = self.callbacks['get_string_tree'](script, headers)
        parent_list = ['']
        prev_iid = -1
        for entry in string_tree:
            if isinstance(entry, str):
                if entry == 'group':
                    parent_list.append(prev_iid)
                elif entry == 'ungroup':
                    if len(parent_list) == 1:
                        raise RuntimeError(f'{self.log_key}: unable to lower group level, not enough groups left')
                    parent_list.pop()
                else:
                    raise ValueError(f'{self.log_key}: Unknown command in tree list sent to _add_tree_entries')
                continue
            kwargs = {'parent': parent_list[-1], 'index': 'end'}
            values = []
            first = True
            for col in headers:
                if col == 'name':
                    if 'group_type' in entry.keys():
                        entry[col] += f' ({entry["group_type"]})'
                if first:
                    kwargs['text'] = entry[col]
                    first = False
                else:
                    values.append(entry[col])
                entry.pop(col)
            kwargs['values'] = values
            kwargs = {**kwargs, **entry}
            prev_iid = self.strings.insert_entry(**kwargs)

    def edit_string(self, name, string_id):
        self.cur_string_id = string_id

        head, body = self.callbacks['get_string_to_edit'](self.cur_script, string_id)
        if string_id not in self.string_defaults:
            self.string_defaults[string_id] = {}
        self.string_defaults[string_id]['head'] = head
        self.string_defaults[string_id]['body'] = body

        self.head_entry.configure(state='normal')
        self.head_entry.delete(0, tk.END)
        self.head_entry.insert(0, head)
        self.body_entry.delete(1.0, tk.END)
        self.body_entry.insert(tk.INSERT, body)

    def on_entry_focus_in(self, e):
        e.widget.cur_value = e.widget.get()

    def on_entry_focus_out(self, key, e):
        if e.widget.get() == e.widget.cur_value:
            print('same value')
            return
        self.set_change(key=key, value=e.widget.get())

    def on_text_focus_in(self, e):
        e.widget.cur_value = e.widget.get(1.0, tk.END)

    def on_text_focus_out(self, key, e):
        if e.widget.get(1.0, tk.END) == e.widget.cur_value:
            print('same text')
            return
        self.set_change(key=key, value=e.widget.get(1.0, tk.END))

    def set_change(self, key, value):
        if self.cur_string_id not in self.string_changes:
            self.string_changes[self.cur_string_id] = {}
        self.string_changes[self.cur_string_id][key] = value

    def save(self):
        self.callbacks['save']()

    def close(self):
        self.callbacks['close'](self.name, self)


