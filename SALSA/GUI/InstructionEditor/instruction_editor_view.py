import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import json

from SALSA.GUI.widgets import ScrollLabelFrame
from SALSA.Common.setting_class import settings
from SALSA.Common.constants import sep

default_headers = {
    'instruction': ['inst_ID', 'name'],
    'parameter': ['param_ID', 'name', 'type', 'mask', 'is_signed']
}

header_settings = {
    'instruction': {
        'inst_ID': {'label': 'ID', 'width': 40, 'stretch': False},
        'name': {'label': 'Name', 'width': 250, 'stretch': False}
    },
    'parameter': {
        'param_ID': {'label': 'ID', 'width': 40, 'stretch': False},
        'name': {'label': 'Name', 'width': 150, 'stretch': True},
        'type': {'label': 'Type', 'width': 100, 'stretch': True},
        'mask': {'label': 'Mask', 'width': 100, 'stretch': True},
        'is_signed': {'label': 'Is Signed', 'width': 50, 'stretch': True},
        'default_value': {'label': 'Default Value', 'width': 100, 'stretch': True}
    }
}

param_edit_fields = {
    'name': {'widget': tk.Entry, 'args': {}, 'kwargs': {}},
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class InstructionEditorView(tk.Toplevel):

    log_name = 'InstEditorView'

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks

        if self.log_name not in settings.keys():
            settings[self.log_name] = {}

        # if 'headers' not in settings[self.log_name].keys():
        settings.set_single(self.log_name, 'headers', json.dumps(default_headers))

        self.visible_headers = json.loads(settings[self.log_name]['headers'])

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.protocol('WM_DELETE_WINDOW', self.on_close)

        # Save, undo, redo buttons

        self.save = tk.Button(self, text='Save', command=self.on_save)
        self.save.grid(row=0, column=0, sticky=tk.W+tk.N, padx=2, pady=2)

        inst_tree_frame = tk.Frame(self)
        inst_tree_frame.grid(row=1, column=0, sticky='NSEW', padx=2, pady='0 2')
        inst_tree_frame.rowconfigure(0, weight=1)

        columns = list(header_settings['instruction'].keys())[1:]
        self.inst_list_tree = ttk.Treeview(inst_tree_frame, name='instruction', columns=columns)
        self.inst_list_tree.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in header_settings['instruction'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.inst_list_tree.heading(name, text=label, anchor=anchor)
            self.inst_list_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        self.inst_list_tree['displaycolumns'] = self.visible_headers['instruction'][1:]
        inst_tree_scrollbar = tk.Scrollbar(inst_tree_frame, orient='vertical', command=self.inst_list_tree.yview)
        inst_tree_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.inst_list_tree.config(yscrollcommand=inst_tree_scrollbar.set)
        self.inst_list_tree.bind('<<TreeviewSelect>>', self.on_select_instruction)

        self.inst_details_frame = tk.Frame(self)
        self.inst_details_frame.grid(row=1, column=1, sticky='NSEW')
        self.inst_details_frame.columnconfigure(0, weight=1)
        self.inst_details_frame.rowconfigure(0, weight=1)
        self.inst_details_frame.rowconfigure(1, weight=1)

        top_details_frame = tk.Frame(self.inst_details_frame)
        top_details_frame.grid(row=0, column=0, sticky='NSEW')
        top_details_frame.columnconfigure(0, weight=1)
        top_details_frame.columnconfigure(1, weight=1)
        top_details_frame.rowconfigure(6, weight=1)

        # Instruction details - Hardcoded

        id_frame = tk.Frame(top_details_frame)
        id_frame.grid(row=0, column=0, sticky=tk.W)
        id_label_label = tk.Label(id_frame, text=f'Instruction ID: ')
        id_label_label.grid(row=0, column=0)
        self.id_label = tk.Label(id_frame, text='')
        self.id_label.grid(row=0, column=1)

        skip_frame = tk.Frame(top_details_frame)
        skip_frame.grid(row=0, column=1, sticky=tk.W)
        skip_label_label = tk.Label(skip_frame, text=f'Frame Refresh: ')
        skip_label_label.grid(row=0, column=0)
        self.skip_label = tk.Label(skip_frame, text='')
        self.skip_label.grid(row=0, column=1)

        param2_frame = tk.Frame(top_details_frame)
        param2_frame.grid(row=1, column=0, sticky=tk.W)
        param2_label_label = tk.Label(param2_frame, text=f'FxnParameter2: ')
        param2_label_label.grid(row=0, column=0)
        self.param2_label = tk.Label(param2_frame, text='')
        self.param2_label.grid(row=0, column=1)

        location_frame = tk.Frame(top_details_frame)
        location_frame.grid(row=1, column=1, sticky=tk.W)
        location_label_label = tk.Label(location_frame, text=f'Function Location: ')
        location_label_label.grid(row=0, column=0)
        self.location_label = tk.Label(location_frame, text='')
        self.location_label.grid(row=0, column=1)

        link_frame = tk.Frame(top_details_frame)
        link_frame.grid(row=2, column=0, sticky=tk.W)
        link_label_label = tk.Label(link_frame, text=f'Link Type: ')
        link_label_label.grid(row=0, column=0)
        self.link_label = tk.Label(link_frame, text='')
        self.link_label.grid(row=0, column=1)

        loop_params_frame = tk.Frame(top_details_frame)
        loop_params_frame.grid(row=3, column=0, sticky=tk.W)
        loop_params_label_label = tk.Label(loop_params_frame, text=f'Loop Params: ')
        loop_params_label_label.grid(row=0, column=0)
        self.loop_params_label = tk.Label(loop_params_frame, text='')
        self.loop_params_label.grid(row=0, column=1)

        self.warning_frame = tk.Frame(top_details_frame)
        self.warning_frame.grid(row=4, column=0, sticky=tk.W)
        warning_label_label = tk.Label(self.warning_frame, text=f'Warning: ')
        warning_label_label.grid(row=0, column=0)
        self.warning_label = tk.Label(self.warning_frame, text='')
        self.warning_label.grid(row=0, column=1)
        self.no_warning = tk.Label(top_details_frame, text=' ')
        self.no_warning.grid(row=4, column=0, columnspan=2, sticky='NSEW')

        # Instruction details - Editable

        name_frame = tk.Frame(top_details_frame)
        name_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E)
        name_label_label = tk.Label(name_frame, text='Name:')
        name_label_label.grid(row=0, column=0)
        self.details_name_entry = tk.Entry(name_frame, text='')
        self.details_name_entry.grid(row=0, column=1, sticky='nsew')
        self.details_name_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.details_name_entry.bind('<FocusOut>', lambda e, k='name': self.on_entry_focus_out(k, e))
        self.details_name_label = tk.Label(name_frame, text='', anchor=tk.W)
        self.details_name_label.grid(row=0, column=1, sticky='nsew')

        desc_frame = tk.LabelFrame(top_details_frame, text='Description')
        desc_frame.grid(row=6, column=0, sticky='NSEW', columnspan=2)
        desc_frame.columnconfigure(0, weight=1)
        desc_frame.rowconfigure(0, weight=1)
        self.details_desc_text = tk.scrolledtext.ScrolledText(desc_frame, wrap=tk.WORD, height=15)
        self.details_desc_text.grid(row=0, column=1, sticky='NSEW')
        self.details_desc_text.bind('<FocusIn>', self.on_text_focus_in)
        self.details_desc_text.bind('<FocusOut>', lambda e, k='name': self.on_text_focus_out(k, e))

        # Instruction parameter setup frame
        self.parameters_frame = tk.LabelFrame(self.inst_details_frame, text='Parameters')
        self.parameters_frame.grid(row=1, column=0, sticky='NSEW')
        self.parameters_frame.columnconfigure(0, weight=1)
        self.parameters_frame.rowconfigure(0, weight=1)

        columns = list(header_settings['parameter'].keys())[1:]
        self.param_list_tree = ttk.Treeview(self.parameters_frame, name='parameter', columns=columns)
        self.param_list_tree.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in header_settings['parameter'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.param_list_tree.heading(name, text=label, anchor=anchor)
            self.param_list_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        self.param_list_tree['displaycolumns'] = self.visible_headers['parameter'][1:]
        param_tree_scrollbar = tk.Scrollbar(self.parameters_frame, orient='vertical', command=self.param_list_tree.yview)
        param_tree_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.param_list_tree.config(yscrollcommand=param_tree_scrollbar.set)

        self.param_list_tree.bind('<Double-1>', self.on_param_double_click)

    # ------------------------------------------------------------ #
    # Methods to generate or use the instruction or parameter tree #
    # ------------------------------------------------------------ #

    def get_headers(self, tree_key):
        if tree_key is None:
            return {k: list(header_settings[k].keys()) for k in header_settings.keys()}
        return list(header_settings[tree_key].keys())

    def on_select_instruction(self, e):
        print(self.details_desc_text.winfo_width())
        if self.inst_list_tree.identify_region(e.x, e.y) == 'heading':
            return
        selected_iid = self.inst_list_tree.focus()
        inst_id = self.inst_list_tree.item(selected_iid).get('text')
        self.callbacks['on_select_instruction'](inst_id)

    # -------------------------------------------------- #
    # Methods to detect and change entry and text fields #
    # -------------------------------------------------- #

    def on_entry_focus_in(self, e):
        self.details_name_entry.cur_value = self.details_name_entry.get()

    def on_entry_focus_out(self, key, e):
        if e.widget.get() == e.widget.cur_value:
            print('same value')
            return
        self.callbacks['set_change'](key=key, value=e.widget.get())

    def on_text_focus_in(self, e):
        self.details_desc_text.cur_value = self.details_desc_text.get(1.0, tk.END)

    def on_text_focus_out(self, key, e):
        if e.widget.get(1.0, tk.END) == e.widget.cur_value:
            print('same text')
            return
        self.callbacks['set_change'](key=key, value=e.widget.get(1.0, tk.END))

    # -------------------------------------------------- #
    # Methods to detect and change parameter tree values #
    # -------------------------------------------------- #

    def on_param_double_click(self, e):
        # Find the region clicked, only edit if region is a cell
        if self.param_list_tree.identify_region(e.x, e.y) != 'cell':
            return

        # get column that was clicked
        column = self.param_list_tree.identify_column(e.x)
        column_id = int(column[1:])
        column_name = self.visible_headers['parameter'][column_id]

        # get item id and values associated with the item
        selected_iid = self.param_list_tree.focus()
        selected_values = self.param_list_tree.item(selected_iid)
        current_value = selected_values.get('values')[column_id-1]
        param_id = selected_values.get('text')

        if self.callbacks['check_locked']([param_id, column_name]):
            print('This field is locked for editing')
            # Add dialog box to indicate that the selected field is not editable
            return

        if column_name not in param_edit_fields:
            print('This column is not available for editing')
            return

        widget_details = param_edit_fields[column_name]

        # get cell bounding box
        cell_bbox = self.param_list_tree.bbox(selected_iid, column)

        edit_widget = widget_details['widget'](self.parameters_frame, *widget_details['args'], **widget_details['kwargs'])
        edit_widget.place(x=cell_bbox[0], y=cell_bbox[1], w=cell_bbox[2], h=cell_bbox[3])

        edit_widget.editing_column_index = column_id
        edit_widget.editing_item_iid = selected_iid
        edit_widget.editing_column_name = column_name
        edit_widget.default_value = current_value
        if isinstance(edit_widget, tk.Entry):
            edit_widget.insert(0, current_value)
            edit_widget.select_range(0, tk.END)

        edit_widget.focus()

        edit_widget.bind('<FocusOut>', lambda event: event.widget.destroy())
        edit_widget.bind('<Return>', self.on_param_enter_pressed)

    def on_param_enter_pressed(self, e):
        new_text = e.widget.get()
        if new_text == e.widget.default_text:
            return

        selected_iid = e.widget.editing_item_iid
        column_index = e.widget.editing_column_index
        column_name = e.widget.editing_column_name

        current_values = self.param_list_tree.item(selected_iid).get('values')
        current_values[column_index] = new_text

        self.param_list_tree.item(selected_iid, values=current_values)

        param_id = self.param_list_tree.item(selected_iid).get('text')
        self.callbacks['set_change'](f'{param_id}{sep}{column_name}')

        e.widget.destroy()

    def on_close(self):
        self.focus()
        self.after(10, func=self.callbacks['on_close'])

    def on_save(self):
        self.callbacks['save']()
