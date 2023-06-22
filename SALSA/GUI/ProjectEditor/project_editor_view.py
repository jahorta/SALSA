import tkinter as tk
from tkinter import simpledialog
import tkinter.ttk as ttk
import json
from typing import List, Dict

import SALSA.GUI.widgets as w
from Common.constants import sep, alt_sep, alt_alt_sep
from SALSA.Common.setting_class import settings

default_headers = {
    'script': ['name'],
    'section': ['name'],
    'instruction': ['ungrouped_position', 'name', 'condition', 'frame_delay_param', 'skip_refresh', 'instruction_id'],
    'parameter': ['ID', 'name', 'type', 'value']
}

default_header_order = {
    'script': ['name', 'section_num'],
    'section': ['name', 'start_offset'],
    'instruction': ['ungrouped_position', 'name', 'condition', 'instruction_id', 'frame_delay_param', 'skip_refresh', 'synopsis', 'absolute_offset', 'relative_offset'],
    'parameter': ['name', 'section_num'],
}

header_settings = {
    'script': {
        'name': {'label': 'Name', 'width': 80, 'stretch': True},
        'section_num': {'label': 'Section #', 'width': 50, 'stretch': True}
    },
    'section': {
        'name': {'label': 'Name', 'width': 180, 'stretch': True},
        'start_offset': {'label': 'Start Offset', 'width': 50, 'stretch': True}
    },
    'instruction': {
        'ungrouped_position': {'label': 'Pos', 'width': 180, 'stretch': True},
        'name': {'label': 'Name', 'width': 270, 'stretch': True},
        'condition': {'label': 'Condition', 'width': 300, 'stretch': True},
        'instruction_id': {'label': 'ID', 'width': 40, 'stretch': False},
        'frame_delay_param': {'label': 'Delay', 'width': 50, 'stretch': False},
        'skip_refresh': {'label': 'SR', 'width': 50, 'stretch': False},
        'synopsis': {'label': 'Synopsis', 'width': 50, 'stretch': True},
        'absolute_offset': {'label': 'Offset', 'width': 50, 'stretch': True}
    },
    'parameter': {
        'ID': {'label': 'ID', 'width': 50, 'stretch': False},
        'name': {'label': 'Name', 'width': 80, 'stretch': True},
        'type': {'label': 'Type', 'width': 70, 'stretch': True},
        'value': {'label': 'Value', 'width': 200, 'stretch': True},
        'formatted_value': {'label': 'ID', 'width': 100, 'stretch': False}
    }
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class ProjectEditorView(tk.Frame):

    log_name = 'PrjEditorView'

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        if self.log_name not in settings.keys():
            settings[self.log_name] = {}

        self.callbacks = None

        # if 'headers' not in settings[self.log_name].keys():
        settings.set_single(self.log_name, 'headers', json.dumps(default_headers))

        self.visible_headers: Dict[str, List[str]] = json.loads(settings[self.log_name]['headers'])

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky=tk.W)
        self.save_button = tk.Button(button_frame, text='Save', command=self.on_save_button)
        self.save_button.grid(row=0, column=0)

        self.pane_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.pane_frame.grid(row=1, column=0, sticky='NSEW')

        script_tree_frame = tk.Frame(self.pane_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        script_tree_frame.grid(row=1, column=0, sticky='NSEW')
        script_tree_frame.rowconfigure(1, weight=1)
        script_tree_frame.columnconfigure(0, weight=1)

        script_tree_label = tk.Label(script_tree_frame, text='Project Scripts')
        script_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.pane_frame.add(script_tree_frame, weight=1)

        columns = list(header_settings['script'].keys())[1:]
        self.scripts_tree = w.DataTreeview(script_tree_frame, name='script', columns=columns)
        self.scripts_tree.grid(row=1, column=0, sticky='NSEW')
        first = True
        for name, d in header_settings['script'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.scripts_tree.heading(name, text=label, anchor=anchor)
            self.scripts_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        self.scripts_tree['displaycolumns'] = self.visible_headers['script'][1:]
        script_tree_scrollbar = tk.Scrollbar(script_tree_frame, orient='vertical', command=self.scripts_tree.yview)
        script_tree_scrollbar.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.scripts_tree.config(yscrollcommand=script_tree_scrollbar.set)

        section_tree_frame = tk.Frame(self.pane_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        section_tree_frame.grid(row=0, column=0, sticky='NSEW')
        section_tree_frame.rowconfigure(1, weight=1)
        section_tree_frame.columnconfigure(0, weight=1)

        section_tree_label = tk.Label(section_tree_frame, text='Sections')
        section_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.pane_frame.add(section_tree_frame, weight=1)

        columns = list(header_settings['section'].keys())[1:]
        self.sections_tree = w.DataTreeview(section_tree_frame, name='section', columns=columns)
        self.sections_tree.configure('columns')
        self.sections_tree.grid(row=1, column=0, sticky='NSEW')
        first = True
        for name, d in header_settings['section'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.sections_tree.heading(name, text=label, anchor=anchor)
            self.sections_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        self.sections_tree['displaycolumns'] = self.visible_headers['section'][1:]
        section_tree_scrollbar = tk.Scrollbar(section_tree_frame, orient='vertical', command=self.sections_tree.yview)
        section_tree_scrollbar.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.sections_tree.config(yscrollcommand=section_tree_scrollbar.set)

        self.inst_tree_frame = tk.Frame(self.pane_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        self.inst_tree_frame.grid(row=0, column=0, sticky='NSEW')
        self.inst_tree_frame.rowconfigure(1, weight=1)
        self.inst_tree_frame.columnconfigure(0, weight=1)

        inst_tree_label = tk.Label(self.inst_tree_frame, text='Instructions')
        inst_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.pane_frame.add(self.inst_tree_frame, weight=1)

        columns = list(header_settings['instruction'].keys())[1:]
        self.insts_tree = w.DataTreeview(self.inst_tree_frame, name='instruction', columns=columns)
        self.insts_tree.grid(row=1, column=0, sticky='NSEW')
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
            self.insts_tree.heading(name, text=label, anchor=anchor)
            self.insts_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        self.insts_tree['displaycolumns'] = self.visible_headers['instruction'][1:]
        inst_tree_scrollbar = tk.Scrollbar(self.inst_tree_frame, orient='vertical', command=self.insts_tree.yview)
        inst_tree_scrollbar.grid(row=1, column=1, sticky=tk.N+tk.S)
        self.insts_tree.config(yscrollcommand=inst_tree_scrollbar.set)

        # Instruction details frame setup
        inst_frame = tk.Frame(self.pane_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        inst_frame.grid(row=0, column=0, sticky='NSEW')
        inst_frame.columnconfigure(0, weight=1)
        inst_frame.rowconfigure(2, weight=5)
        inst_frame.rowconfigure(3, weight=1)
        self.pane_frame.add(inst_frame, weight=3)

        inst_frame_label = tk.Label(inst_frame, text='Instruction Details')
        inst_frame_label.grid(row=0, column=0, sticky=tk.W)

        inst_top_frame = tk.Frame(inst_frame)
        inst_top_frame.grid(row=1, column=0, sticky=tk.E+tk.W)
        inst_top_frame.columnconfigure(0, weight=1)

        self.inst_label = tk.Label(inst_top_frame, text='ID - Name')
        self.inst_label.grid(row=0, column=0, sticky=tk.W+tk.N)

        skip_frame = tk.Frame(inst_top_frame)
        skip_frame.grid(row=0, column=1, sticky=tk.E)

        self.skip_ckeck_var = tk.IntVar()
        skip_check = tk.Checkbutton(skip_frame, variable=self.skip_ckeck_var,
                                    command=lambda: self.callbacks['update_field']('skip_frame_refresh',
                                                                                   (self.skip_ckeck_var.get() == 1)))
        skip_check.grid(row=0, column=0)
        skip_label = tk.Label(skip_frame, text='Skip Frame Refresh')
        skip_label.grid(row=0, column=1)
        self.skip_error_label = tk.Label(skip_frame, text='')
        self.skip_error_label.grid(row=1, column=0, columnspan=2, sticky='NSEW')

        delay_frame = tk.LabelFrame(inst_top_frame, text='Instruction Delay')
        delay_frame.grid(row=2, column=0, columnspan=2, sticky='NSEW')

        self.delay_label = tk.Label(delay_frame, text=' ')
        self.delay_label.grid(row=0, column=0, sticky='NSEW')
        self.delay_label.bind('<Double-1>', lambda e: self.on_param_double_click('delay', e))

        self.inst_desc_frame = w.ScrollLabelFrame(inst_frame, text='Description', size={'width': 100, 'height': 100})
        self.inst_desc_frame.grid(row=2, column=0, sticky='NSEW')
        self.inst_desc_frame.columnconfigure(0, weight=1)
        self.inst_desc_frame.rowconfigure(0, weight=1)

        self.inst_description = tk.Message(self.inst_desc_frame.scroll_frame)
        self.inst_desc_frame.canvas.bind("<Configure>", lambda e: self.inst_description.configure(width=e.width - 10), add='+')
        self.inst_description.grid(row=0, column=0, sticky='NSEW')

        param_frame = tk.LabelFrame(inst_frame, text='Parameters')
        param_frame.grid(row=3, column=0, sticky='NSEW')
        param_frame.columnconfigure(0, weight=1)
        param_frame.rowconfigure(0, weight=1)

        columns = list(header_settings['parameter'].keys())[1:]
        self.param_tree = w.DataTreeview(param_frame, name='parameter', columns=columns, can_open=False)
        self.param_tree.grid(row=0, column=0, sticky='NSEW')
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
            self.param_tree.heading(name, text=label, anchor=anchor)
            self.param_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        self.param_tree['displaycolumns'] = self.visible_headers['parameter'][1:]
        param_tree_scrollbar = tk.Scrollbar(param_frame, orient='vertical', command=self.param_tree.yview)
        param_tree_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.param_tree.config(yscrollcommand=param_tree_scrollbar.set)
        self.param_tree.bind('<Double-1>', lambda e: self.on_param_double_click('param', e))

        link_frame = tk.LabelFrame(inst_frame, text='Links')
        link_frame.grid(row=4, column=0, sticky='NSEW')
        link_frame.columnconfigure(0, weight=1)
        link_frame.columnconfigure(2, weight=1)

        link_in_label = tk.Label(link_frame, text='Incoming Links')
        link_in_label.grid(row=0, column=0, sticky=tk.W)
        self.link_in = w.ScrollLabelFrame(link_frame, has_label=False, size={'width': 100, 'height': 50})
        self.link_in.grid(row=1, column=0, sticky=tk.W+tk.E)
        self.link_in.columnconfigure(0, weight=1)
        self.link_in.rowconfigure(0, weight=1)

        link_sep = ttk.Separator(link_frame, orient='vertical')
        link_sep.grid(row=0, column=1, rowspan=2, sticky=tk.N+tk.S)

        link_out_label = tk.Label(link_frame, text='Outgoing Links')
        link_out_label.grid(row=0, column=2, sticky=tk.W)
        self.link_out = w.ScrollLabelFrame(link_frame, has_label=False, size={'width': 100, 'height': 50})
        self.link_out.grid(row=1, column=2, sticky=tk.W+tk.E)
        self.link_out.columnconfigure(0, weight=1)
        self.link_out.rowconfigure(0, weight=1)

    def on_save_button(self):
        self.callbacks['save_project']()

    def get_headers(self, tree_key=None, get_all=False):
        if tree_key is None:
            if get_all:
                return {k: list(header_settings[k].keys()) for k in header_settings.keys()}
            return {k: list(header_settings[k].keys()) for k in header_settings.keys()}

        if get_all:
            return header_settings[tree_key]
        return list(header_settings[tree_key].keys())

    def update_field(self, field_name, value):
        self.callbacks['update_field'](field_name, value)

    def add_and_bind_callbacks(self, callbacks):
        self.callbacks = callbacks
        self.scripts_tree.bind('<Button-3>', self.callbacks['show_header_selection_menu'])
        self.sections_tree.bind('<Button-3>', self.callbacks['show_header_selection_menu'])
        self.insts_tree.bind('<Button-3>', self.callbacks['show_header_selection_menu'])
        self.insts_tree.bind('<Button-3>', self.callbacks['show_inst_menu'], add='+')
        self.param_tree.bind('<Button-3>', self.callbacks['show_header_selection_menu'])

    def on_param_double_click(self, param, e):
        if param != 'delay':
            # get item id and values associated with the item
            selected_iid = self.param_tree.focus()
            param = self.param_tree.row_data[selected_iid]
            if param is None:
                return
        self.callbacks['edit_param'](param)

    def sort_visible_headers(self, tree):
        self.visible_headers[tree] = [_ for _ in default_header_order[tree] if _ in self.visible_headers[tree]]

    def get_header_order(self, tree):
        return default_header_order[tree]

    def fit_headers(self, cur_tree: w.DataTreeview):
        widget_width = cur_tree.winfo_width()
        widths = {}
        first = '#0'
        width_sum = 0
        for col in self.visible_headers[cur_tree.name]:
            if first:
                col = first
                first = ''
            widths[col] = cur_tree.column(col, 'width')
            width_sum += widths[col]

        if width_sum == widget_width:
            return

        width_ratios = {}
        for k, v in widths.items():
            width_ratios[k] = v / width_sum

        for k, v in width_ratios.items():
            cur_tree.column(k, width=int(v*widget_width))

    def inst_group_handling(self, cur_inst_id, new_id, children):
        # create message to decide how to handle group entries
        children = [{k: children[k]} for k in children.keys()]
        if cur_inst_id == 0:
            labels = ['Group']
        elif cur_inst_id == 3:
            labels = ['Switch Case']
        else:
            return ''

        labels += ['Delete', 'Move Above', 'Move Below']
        if new_id == 0:
            labels += ['Insert in If', 'Insert in Else']
        elif new_id == 3:
            labels += ['Insert in Switch Case']

        radio_vars = []
        entry_vars = []
        row_labels = []

        for child in children:
            radio_vars.append(tk.IntVar(self, 1))
            row_labels.append(list(child.keys())[0])
            if new_id == 3:
                entry_vars.append(tk.IntVar(self))

        class InstGroupHandlerDialog(tk.simpledialog.Dialog):

            def body(self, master):

                cur_col = 0
                for label in labels:
                    tk.Label(master, text=label).grid(row=0, column=cur_col)
                    cur_col += 1

                for i, row_label in enumerate(row_labels):
                    cur_col = 0
                    if cur_inst_id == 0:
                        row_label = row_label.split(sep)[1]
                    tk.Label(master, text=row_label).grid(row=i+1, column=cur_col)
                    cur_col += 1
                    for label in labels[1:]:
                        tk.Radiobutton(master, text='', variable=radio_vars[i], value=cur_col).grid(row=i+1, column=cur_col)
                        cur_col += 1
                    if new_id == 3:
                        tk.Entry(master, textvariable=entry_vars[i]).grid(row=i+1, column=cur_col)

        cancel = not InstGroupHandlerDialog(self, title='Group Handling')
        if cancel:
            return 'cancel'

        response = ''
        for i, row_label in enumerate(row_labels):
            if i > 0:
                response += f'{alt_alt_sep}'
            choice = labels[radio_vars[i].get()]
            response += f'{row_label}{alt_sep}{choice}'
            if new_id == 3 and choice == 'Insert in Switch Case':
                response += f'{alt_sep}{entry_vars[i].get()}'

        return response
