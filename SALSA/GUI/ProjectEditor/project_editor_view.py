import tkinter as tk
import tkinter.ttk as ttk
import json

import SALSA.GUI.widgets as w
from SALSA.Common.setting_class import settings

default_headers = {
    'script': ['name'],
    'section': ['name'],
    'instruction': ['name', 'condition', 'instruction_id'],
    'parameter': ['ID', 'name', 'type', 'value']
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
        'name': {'label': 'Name', 'width': 270, 'stretch': True},
        'condition': {'label': 'Condition', 'width': 300, 'stretch': True},
        'instruction_id': {'label': 'ID', 'width': 25, 'stretch': False},
        'synopsis': {'label': 'Synopsis', 'width': 50, 'stretch': True},
        'absolute_offset': {'label': 'Offset', 'width': 50, 'stretch': True},
        'relative_offset': {'label': 'Relative Offset', 'width': 50, 'stretch': True}
    },
    'parameter': {
        'ID': {'label': 'ID', 'width': 30, 'stretch': True},
        'name': {'label': 'Name', 'width': 150, 'stretch': True},
        'type': {'label': 'Type', 'width': 70, 'stretch': True},
        'value': {'label': 'Value', 'width': 120, 'stretch': False},
        'formatted_value': {'label': 'ID', 'width': 50, 'stretch': False}
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

        # if 'headers' not in settings[self.log_name].keys():
        settings.set_single(self.log_name, 'headers', json.dumps(default_headers))

        self.visible_headers = json.loads(settings[self.log_name]['headers'])

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky=tk.W)
        self.save_button = tk.Button(button_frame, text='Save', command=None)
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

        inst_tree_frame = tk.Frame(self.pane_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        inst_tree_frame.grid(row=0, column=0, sticky='NSEW')
        inst_tree_frame.rowconfigure(1, weight=1)
        inst_tree_frame.columnconfigure(0, weight=1)

        inst_tree_label = tk.Label(inst_tree_frame, text='Instructions')
        inst_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.pane_frame.add(inst_tree_frame, weight=1)

        columns = list(header_settings['instruction'].keys())[1:]
        self.insts_tree = w.DataTreeview(inst_tree_frame, name='instruction', columns=columns)
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
        inst_tree_scrollbar = tk.Scrollbar(inst_tree_frame, orient='vertical', command=self.insts_tree.yview)
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
        skip_check = tk.Checkbutton(skip_frame, variable=self.skip_ckeck_var)
        skip_check.grid(row=0, column=0)
        skip_label = tk.Label(skip_frame, text='Skip Frame Refresh')
        skip_label.grid(row=0, column=1)
        self.skip_error_label = tk.Label(skip_frame, text='')
        self.skip_error_label.grid(row=1, column=0, columnspan=2, sticky='NSEW')

        self.inst_desc_frame = w.ScrollLabelFrame(inst_frame, text='Description', size={'width': 100, 'height': 50})
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
        self.param_tree = w.DataTreeview(param_frame, name='parameter', columns=columns)
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

        link_frame = tk.LabelFrame(inst_frame, text='Links')
        link_frame.grid(row=4, column=0, sticky='NSEW')
        link_frame.columnconfigure(0, weight=1)

        link_out_label = tk.Label(link_frame, text='Outgoing Links')
        link_out_label.grid(row=0, column=0, sticky=tk.W)
        self.link_out = tk.Label(link_frame, text='')
        self.link_out.grid(row=1, column=0, sticky=tk.W)

        link_sep = ttk.Separator(link_frame, orient='horizontal')
        link_sep.grid(row=2, column=0, sticky=tk.W+tk.E)

        link_in_label = tk.Label(link_frame, text='Incoming Links')
        link_in_label.grid(row=3, column=0, sticky=tk.W)
        self.link_in = tk.Label(link_frame, text='')
        self.link_in.grid(row=4, column=0, sticky=tk.W)

    def get_headers(self, tree_key=None):
        if tree_key is None:
            return {k: list(header_settings[k].keys()) for k in header_settings.keys()}
        return list(header_settings[tree_key].keys())

    def set_refresh_value(self, never_refresh, always_refresh, cur_refresh_choice):
        self.skip_ckeck_var.set(int(cur_refresh_choice))
        if never_refresh:
            self.skip_error_label.config(text='This instruction never skips')
        elif always_refresh:
            self.skip_error_label.config(text='This instruction always skips')
        else:
            self.skip_error_label.config(text='')

    def add_link(self, link_type, link_text, link_callback):
        pass



