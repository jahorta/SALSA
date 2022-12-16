import tkinter as tk

from GUI.widgets import CustomTree, RequiredEntry, ScrollFrame, ScrollCanvas


class InstructionEditorView(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Save, undo, redo buttons

        self.save = tk.Button(self, text='Save', command=None)
        self.save.grid(row=0, column=0)

        self.inst_list_tree = CustomTree(self)
        self.inst_list_tree.grid(row=1, column=0)

        self.inst_details_frame = tk.Frame(self)
        self.inst_details_frame.grid(row=1, column=1)

        top_details_frame = tk.Frame(self.inst_details_frame)
        top_details_frame.grid(row=0, column=0)

        # Instruction details - Hardcoded

        id_frame = tk.Frame(top_details_frame)
        id_frame.grid(row=0, column=1, sticky=tk.E)
        id_label_label = tk.Label(id_frame, text='InstID:')
        id_label_label.grid(row=0, column=0)
        self.id_label = tk.Label(id_frame, text='')
        self.id_label.grid(row=0, column=1)

        skip_frame = tk.Frame(top_details_frame)
        skip_frame.grid(row=1, column=1, sticky=tk.E)
        skip_label_label = tk.Label(skip_frame, text='Frame Refresh:')
        skip_label_label.grid(row=0, column=0)
        self.skip_label = tk.Label(skip_frame, text='')
        self.skip_label.grid(row=0, column=1)

        param2_frame = tk.Frame(top_details_frame)
        param2_frame.grid(row=2, column=1, sticky=tk.E)
        force_label_label = tk.Label(param2_frame, text='Skip Frame Refresh:')
        force_label_label.grid(row=0, column=0)
        self.force_label = tk.Label(param2_frame, text='')
        self.force_label.grid(row=0, column=1)

        location_frame = tk.Frame(top_details_frame)
        location_frame.grid(row=1, column=1, sticky=tk.E)
        location_label_label = tk.Label(location_frame, text='Frame Refresh:')
        location_label_label.grid(row=0, column=0)
        self.location_label = tk.Label(location_frame, text='')
        self.location_label.grid(row=0, column=1)

        # Instruction details - Editable

        name_frame = tk.Frame(top_details_frame)
        name_frame.grid(row=1, column=0, sticky=tk.E)
        name_label_label = tk.Label(name_frame, text='Name:')
        name_label_label.grid(row=0, column=0)
        self.details_name_label = tk.Label(name_frame, text='')
        self.details_name_label.grid(row=0, column=1)
        self.details_name_variable = tk.StringVar()
        self.details_name_variable.set('')
        self.details_name_entry = RequiredEntry(name_frame)
        self.details_name_entry.grid(row=0, column=1)

        desc_frame = tk.LabelFrame(top_details_frame, text='Description')
        desc_frame.grid(row=1, column=0, sticky=tk.E, columnspan=2)
        scroll_frame = ScrollFrame(desc_frame)
        scroll_frame.grid(row=0, column=1)
        self.details_desc_label = tk.Label(scroll_frame.viewport, text='')
        self.details_desc_label.grid(row=0, column=0)
        self.details_desc_variable = tk.StringVar()
        self.details_desc_variable.set('')
        self.details_desc_entry = tk.Text(desc_frame, textvariable=self.details_desc_variable, wrap=tk.WORD)
        self.details_desc_entry.grid(row=0, column=1)

        # Insruction parameter field

        parameters_frame = tk.LabelFrame(self.inst_details_frame, text='Parameters')
        parameters_frame.grid(row=5, column=1, columnspan=2)
        param_list_frame = ScrollCanvas(parameters_frame, )
        param_list_frame.grid(row=0, column=0)