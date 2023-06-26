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

note_font = {}
no_head_warning = 'Removing the header will allow for 5 lines of body text instead of 4.\nWARNING: Clicking this check box will delete the current header.'
body_note = 'NOTE:"[" and "]" are used for open and close quotes respectively. Using " or \' will only give the close quote.'


class StringPopup(tk.Toplevel):
    t = 'SALSA - String Editor'
    log_key = 'StrEditPopup'
    w = 600
    h = 500

    option_settings = {}

    def __init__(self, parent, callbacks, name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = callbacks
        self.name = name

        # if self.log_key not in settings:
        #     settings.add_group(self.log_key)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        save_frame = tk.Frame(self)
        save_frame.grid(row=0, column=0, sticky='NSEW')

        self.save_button = tk.Button(save_frame, text='Save', command=self.save, state='disabled')
        self.save_button.grid(row=0, column=0, sticky=tk.W)

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
        lower_frame.grid(row=2, column=0, sticky='NSEW', padx=5)
        lower_frame.columnconfigure(0, weight=1)

        no_head_frame = tk.Frame(lower_frame)
        no_head_frame.grid(row=0, column=0, sticky=tk.W)

        self.no_head_var = tk.IntVar()
        self.no_head = tk.Checkbutton(no_head_frame, text='Remove Header', variable=self.no_head_var, onvalue=1, offvalue=0,
                                      command=lambda: self.set_change('no_head', self.no_head_var.get() == 1), state='disabled')
        self.no_head.grid(row=0, column=0, sticky=tk.W)
        no_head_warning_label = tk.Label(no_head_frame, text=no_head_warning, anchor='w', justify=tk.LEFT)
        no_head_warning_label.grid(row=1, column=0)

        head_frame = tk.Frame(lower_frame)
        head_frame.grid(row=1, column=0, sticky=tk.W)

        head_label = tk.Label(head_frame, text='Textbox Header')
        head_label.grid(row=0, column=0, sticky=tk.W)
        self.head_entry = tk.Entry(head_frame, state='disabled', width=70)
        self.head_entry.grid(row=1, column=0, sticky=tk.W)
        self.head_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.head_entry.bind('<FocusOut>', lambda e, k='head': self.on_entry_focus_out(k, e))
        self.head_add_quote = tk.Button(head_frame, text='add《》to header', command=self.add_quotes_to_head)
        self.head_add_quote.grid(row=1, column=1, sticky=tk.W)

        body_label = tk.Label(lower_frame, text='Textbox Body')
        body_label.grid(row=2, column=0, sticky=tk.W)
        self.body_entry = tk.Text(lower_frame, wrap=tk.WORD, height=5)
        self.body_entry.grid(row=3, column=0, sticky=tk.W + tk.E)
        self.body_entry.bind('<FocusIn>', self.on_text_focus_in)
        self.body_entry.bind('<FocusOut>', lambda e, k='body': self.on_text_focus_out(k, e))
        body_note_label = tk.Label(lower_frame, text=body_note, anchor='w', justify=tk.LEFT)
        body_note_label.grid(row=4, column=0, sticky=tk.W)

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

    def update_scripts(self):
        self._clear_editor_fields()
        self._change_editor_state('disabled')
        self.strings.clear_all_entries()
        script_tree = self.callbacks['get_scripts']()
        for entry in script_tree:
            self.scripts.insert_entry(parent='', index='end', text=entry['name'], values=[], row_data=entry['row_data'])

    def _change_editor_state(self, state):
        self.no_head.configure(state=state)
        self.head_entry.configure(state=state)
        self.head_add_quote.configure(state=state)

    def _clear_editor_fields(self):
        self.no_head_var.set(0)
        self.head_entry.delete(0, tk.END)
        self.body_entry.delete(1.0, tk.END)

    def on_script_select(self, name, script):
        self.cur_script = script
        self._clear_editor_fields()
        self._change_editor_state('disabled')
        self._update_string_tree(script)

    def _update_string_tree(self, script):
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
        if len(self.string_changes) > 0:
            self.save()

        self._change_editor_state('normal')
        self._clear_editor_fields()

        self.cur_string_id = string_id
        no_head, head, body = self.callbacks['get_string_to_edit'](string_id, self.cur_script)
        no_head = 1 if no_head else 0
        self.no_head_var.set(no_head)
        self.head_entry.insert(0, head)
        self.body_entry.insert(tk.INSERT, body)

    def add_quotes_to_head(self):
        self.head_entry.insert(0, '《')
        self.head_entry.insert(tk.END, '》')
        self.set_change('head', self.head_entry.get())

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
        if self.cur_script not in self.string_changes:
            self.string_changes[self.cur_script] = {self.cur_string_id: {key: value}}
        elif self.cur_string_id not in self.string_changes[self.cur_script]:
            self.string_changes[self.cur_script][self.cur_string_id] = {key: value}
        elif key not in self.string_changes[self.cur_script][self.cur_string_id]:
            self.string_changes[self.cur_script][self.cur_string_id][key] = value
        elif self.string_changes[self.cur_script][self.cur_string_id][key] != value:
            self.string_changes[self.cur_script][self.cur_string_id][key] = value
        else:
            return
        self.save_button.configure(state='normal')

    def save_and_close(self):
        self.save()
        self.callbacks['close'](self.name, self)

    def save(self):
        for script, strings in self.string_changes.items():
            for string_id, string_changes in strings.items():
                self.callbacks['save'](script, string_id, string_changes)
        self.string_changes = {}

    def close(self):
        self.focus()
        self.after(10, self.save_and_close)


