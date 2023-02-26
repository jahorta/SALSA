import tkinter as tk
import tkinter.ttk as ttk
import json

import SALSA.GUI.widgets as w
from SALSA.Common.setting_class import settings

default_headers = {
    'script': ['name'],
    'section': ['name'],
    'instruction': ['name', 'condition', 'instruction_id']
}

header_settings = {
    'script': {
        'name': {'label': 'Name', 'width': 80, 'stretch': True},
        'section_num': {'label': 'Section #', 'width': 50, 'stretch': True}
    },
    'section': {
        'name': {'label': 'Name', 'width': 100, 'stretch': True},
        'start_offset': {'label': 'Start Offset', 'width': 50, 'stretch': True}
    },
    'instruction': {
        'name': {'label': 'Name', 'width': 270, 'stretch': True},
        'condition': {'label': 'Condition', 'width': 300, 'stretch': True},
        'instruction_id': {'label': 'ID', 'width': 25, 'stretch': False},
        'synopsis': {'label': 'Synopsis', 'width': 50, 'stretch': True},
        'absolute_offset': {'label': 'Offset', 'width': 50, 'stretch': True},
        'relative_offset': {'label': 'Relative Offset', 'width': 50, 'stretch': True}
    }
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.CENTER
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
        self.scripts_tree = w.CustomTree2(script_tree_frame, name='script', columns=columns)
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
        self.sections_tree = w.CustomTree2(section_tree_frame, name='section', columns=columns)
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
        self.insts_tree = w.CustomTree2(inst_tree_frame, name='instruction', columns=columns)
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

        skip_frame = tk.Frame(inst_frame)
        skip_frame.grid(row=1, column=1, sticky=tk.E, rowspan=2)

        self.skip_ckeck_var = tk.IntVar()
        skip_check = tk.Checkbutton(skip_frame, variable=self.skip_ckeck_var)
        skip_check.grid(row=0, column=0)
        skip_label = tk.Label(skip_frame, text='Skip Frame Refresh')
        skip_label.grid(row=0, column=1)
        self.skip_error_label = tk.Label(skip_frame, text='')
        self.skip_error_label.grid(row=1, column=0, columnspan=2, sticky='NSEW')

        inst_desc_label = tk.Label(inst_frame, text='Description')
        inst_desc_label.grid(row=2, column=0, sticky=tk.W)

        self.inst_description = tk.Text(inst_frame, height=20)
        self.inst_description.grid(row=3, column=0, columnspan=2, sticky='NSEW')

        param_frame = tk.LabelFrame(inst_frame, text='Parameter Values')
        param_frame.grid(row=4, column=0, columnspan=2, sticky='NSEW')
        self.param_scroll_frame = w.ScrollFrame(param_frame, size={'width': 300, 'height': 300})
        self.param_scroll_frame.grid(row=0, column=0)

        self.after(50, self.param_scroll_frame.resize)

    def get_headers(self, tree_key=None):
        if tree_key is None:
            return self.headers
        return self.headers[tree_key]
