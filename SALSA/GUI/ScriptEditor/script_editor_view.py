import tkinter as tk
import tkinter.ttk as ttk

import SALSA.GUI.widgets as w

default_headers = {
    'script': ('Name',),
    'section': ('Name',),
    'instruction': ('Name', 'Condition', 'Instruction ID')
}

available_headers = {
    'script': ('Name', 'Sections'),
    'section': ('Name', 'Relative Offset', 'Offset'),
    'instruction': ('Name', 'Condition', 'Instruction ID', 'Relative Offset', 'Offset', 'Synopsis')
}


class ScriptEditorView(tk.Frame):

    def __init__(self, parent, *args, headers=None, **kwargs):
        self.headers = default_headers if headers is None else headers

        super().__init__(parent, *args, **kwargs)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky=tk.W)
        self.save_button = tk.Button(button_frame, text='Save', command=None)
        self.save_button.grid(row=0, column=0)

        self.main_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_frame.grid(row=1, column=0)

        script_tree_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        script_tree_frame.grid(row=1, column=0, sticky='NSEW')
        script_tree_label = tk.Label(script_tree_frame, text='Project Scripts')
        script_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.main_frame.add(script_tree_frame, weight=1)

        self.scripts_tree = w.CustomTree2(script_tree_frame, name='script', columns=self.headers['script'][1:])
        self.scripts_tree.grid(row=1, column=0, sticky='NSEW')
        first = True
        for header in self.headers['script']:
            header_text = header
            if first:
                header = '#0'
                first = False
            self.scripts_tree.heading(header, text=header_text)
        script_tree_frame.rowconfigure(1, weight=1)
        script_tree_frame.columnconfigure(1, weight=1)

        section_tree_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        section_tree_frame.grid(row=0, column=0, sticky='NSEW')
        section_tree_label = tk.Label(section_tree_frame, text='Sections')
        section_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.main_frame.add(section_tree_frame, weight=1)

        self.sections_tree = w.CustomTree2(section_tree_frame, name='section', columns=self.headers['section'][1:])
        self.sections_tree.grid(row=1, column=0, sticky='NSEW')
        first = True
        for header in self.headers['section']:
            header_text = header
            if first:
                header = '#0'
                first = False
            self.sections_tree.heading(header, text=header_text)
        section_tree_frame.rowconfigure(1, weight=1)
        section_tree_frame.columnconfigure(1, weight=1)

        inst_tree_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        inst_tree_frame.grid(row=0, column=0, sticky='NSEW')
        inst_tree_label = tk.Label(inst_tree_frame, text='Instructions')
        inst_tree_label.grid(row=0, column=0, sticky=tk.W)
        self.main_frame.add(inst_tree_frame, weight=1)

        self.insts_tree = w.CustomTree2(inst_tree_frame, name='instruction', columns=self.headers['instruction'][1:])
        self.insts_tree.grid(row=1, column=0, sticky='NSEW')
        first = True
        for header in self.headers['instruction']:
            header_text = header
            if first:
                header = '#0'
                first = False
            self.insts_tree.heading(header, text=header_text)
        inst_tree_frame.rowconfigure(1, weight=1)
        inst_tree_frame.columnconfigure(1, weight=1)

        inst_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        inst_frame.grid(row=0, column=0, sticky='NSEW')
        inst_frame_label = tk.Label(inst_frame, text='Instruction Details')
        inst_frame_label.grid(row=0, column=0, sticky=tk.W)
        self.main_frame.add(inst_frame, weight=3)

        self.inst_label = tk.Label(inst_frame, text='ID - Name')
        self.inst_label.grid(row=1, column=0, sticky=tk.W)

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
