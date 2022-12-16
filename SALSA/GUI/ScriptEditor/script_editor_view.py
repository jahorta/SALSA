import tkinter as tk

import SALSA.GUI.widgets as w


class ScriptEditorView(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky=tk.W)
        self.save_button = tk.Button(button_frame, text='Save', command=None)
        self.save_button.grid(row=0, column=0)

        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=1, column=0)

        project_frame_label = tk.Label(self.main_frame, text='Project Scripts')
        project_frame_label.grid(row=0, column=0, sticky=tk.W)
        project_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        project_frame.grid(row=1, column=0, sticky='NSEW')

        self.scripts_tree = w.CustomTree(project_frame)
        self.scripts_tree.grid(row=0, column=0, sticky='NSEW')

        script_frame_label = tk.Label(self.main_frame, text='Sections')
        script_frame_label.grid(row=0, column=1, sticky=tk.W)
        script_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        script_frame.grid(row=1, column=1, sticky='NSEW')

        self.sections_tree = w.CustomTree(script_frame)
        self.sections_tree.grid(row=0, column=0, sticky='NSEW')

        section_frame_label = tk.Label(self.main_frame, text='Instructions')
        section_frame_label.grid(row=0, column=2, sticky=tk.W)
        section_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        section_frame.grid(row=1, column=2, sticky='NSEW')

        self.insts_tree = w.CustomTree(section_frame)
        self.insts_tree.grid(row=0, column=0, sticky='NSEW')

        inst_frame_label = tk.Label(self.main_frame, text='Instruction Details')
        inst_frame_label.grid(row=0, column=3, sticky=tk.W)
        inst_frame = tk.Frame(self.main_frame, highlightthickness=1, highlightbackground='#DEDEDE', width=400)
        inst_frame.grid(row=1, column=3, sticky='NSEW')

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
