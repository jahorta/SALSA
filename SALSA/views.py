import re
import tkinter as tk
from pathlib import Path
from threading import Timer
from tkinter import ttk

from . import widgets as w
from .constants import FieldTypes as FT


class MainMenu(tk.Menu):
    """The application's main menu"""

    def __init__(self, parent, callbacks, **kwargs):
        super().__init__(parent, **kwargs)

        self.parent = parent
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label='Select Script Directory', command=callbacks['file->script_dir'])
        file_menu.add_command(label='Select SCT File', command=callbacks['file->select'])
        file_menu.add_command(label='Export Data', command=callbacks['file->export_data'])
        file_menu.add_command(label='Quit', command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=file_menu)

        view_menu = tk.Menu(self, tearoff=False)
        view_menu.add_command(label='SCT decoder mode', command=callbacks['view->sct'])
        view_menu.add_command(label='Instruction edit mode', command=callbacks['view->inst'])
        self.add_cascade(label='View', menu=view_menu)

        help_menu = tk.Menu(self, tearoff=False)
        # help_menu.add_command(label='Print debug to console', command=callbacks['help->debug'])
        help_menu.add_command(label='Help', command=callbacks['help->help'])
        help_menu.add_command(label='About', command=callbacks['help->about'])
        self.add_cascade(label='Help', menu=help_menu)


class FileSelectView(tk.Toplevel):
    offset = {
        'x': 50,
        'y': 50
    }

    script_tree_headers = {
        '#0': {'label': 'Name', 'width': 200},
        'Focus': {'label': 'Sel', 'width': 50}
    }
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self, parent, last, scalebar_pos, position, filepath, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.file = last
        self.path = filepath
        self.callbacks = callbacks
        self.scalebarPos = scalebar_pos

        fileSelectlabel = tk.LabelFrame(self, text='File Select')
        columns = list(self.script_tree_headers.keys())[1:]
        self.file_select_tree = ttk.Treeview(fileSelectlabel, columns=columns, height=25)
        fileSelectlabel.columnconfigure(0, weight=1)
        fileSelectlabel.rowconfigure(1, weight=1)
        self.file_select_tree.grid(row=0, column=0, sticky='NSEW')

        for name, definition in self.script_tree_headers.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.file_select_tree.heading(name, text=label, anchor=anchor)
            self.file_select_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.file_select_tree_scroll = ttk.Scrollbar(fileSelectlabel, orient=tk.VERTICAL,
                                                     command=self.file_select_tree.yview)
        self.file_select_tree.configure(yscrollcommand=self.file_select_tree_scroll.set)
        self.file_select_tree_scroll.grid(row=0, column=1, sticky='NSEW')

        self.file_select_tree.bind('<<TreeviewSelect>>', self.on_select_script_file)
        fileSelectlabel.grid(row=0, column=0)

        buttonFrame = tk.Frame(self)
        self.load = tk.Button(buttonFrame, text='Load', command=self.on_load_script_file)
        self.load.grid(row=0, column=3)
        self.quit = tk.Button(buttonFrame, text='Cancel', command=self.callbacks['on_quit'])
        self.quit.grid(row=0, column=4)
        buttonFrame.grid(row=1, column=0, sticky=tk.E)

        self.title('File Select Menu')
        self.resizable(width=False, height=False)
        posX = position['x'] + self.offset['x']
        posY = position['y'] + self.offset['y']
        pos = '+{0}+{1}'.format(posX, posY)
        self.geometry(pos)

    def on_select_script_file(self, *args):
        self.scalebarPos = str(self.file_select_tree.yview()[0])
        self.file = self.file_select_tree.selection()[0]
        self.populate_files(self.path)

        pass

    def on_load_script_file(self, *args):
        if self.file is None:
            """message to select a file"""
        else:
            self.callbacks['on_load'](self.file, str(self.scalebarPos))
            self.callbacks['on_quit']()

    def populate_files(self, path):

        self.path = path

        for row in self.file_select_tree.get_children():
            self.file_select_tree.delete(row)

        paths = Path(path).glob('**/*')
        for path in paths:
            # Only list files with the .sct file extension
            if not path.suffix == '.sct':
                continue
            values = []
            if path.name == self.file:
                values.append('***')
            self.file_select_tree.insert('', 'end', iid=str(path.name), text=str(path.name), values=values)
        # print(paths)


class InstructionView(tk.Frame):
    """The applications instruction view container. Contains an instruction selector and instruction details"""

    def __init__(self, parent, instfields, paramfields, callbacks, instructions, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.panels = {}
        self.callbacks = callbacks
        self.instructions = instructions

        self.currentInstruction = 0

        self.panels["instruction tree"] = InstructionSelector(self, callbacks=callbacks, text='Instructions')
        self.panels['instruction tree'].grid(row=0, column=0, sticky='NSEW')

        self.panels['instruction detail'] = InstructionDetails(self, instruction=instructions['0'],
                                                               instfields=instfields, paramfields=paramfields,
                                                               callbacks=callbacks, text='Instruction Details')
        self.panels['instruction detail'].grid(row=0, column=1, sticky='NSEW')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

    def populate_instructions(self, insts):
        self.panels["instruction tree"].populate(instructions=insts)

    def get_current_inst_details(self):
        return self.panels['instruction detail'].get_inst_fields()

    def set_instruction_fields(self):
        self.panels['instruction detail'].set_inst_fields()

    def get_param_fields(self):
        return self.panels['instruction detail'].get_param_fields()

    def set_param_fields(self, paramID):
        self.panels['instruction detail'].set_param_fields(paramID)

    def update_instructions(self, instructions, instID):
        if instID == 0:
            instID = '0'
        self.panels['instruction detail'].update_instructions(instructions[instID])
        self.panels['instruction tree'].populate(instructions)

    def populate_parameters(self, num):
        self.panels['instruction detail'].param_populate(num)


class InstructionSelector(tk.LabelFrame):
    """The applications instruction definition selector. A selectable treeview displaying all available instructions"""

    column_defs = {
        '#0': {'label': 'ID', 'anchor': tk.W, 'width': 40},
        'Name': {'label': 'Name', 'width': 200, 'stretch': True, 'anchor': tk.W},
        'Pnum': {'label': 'Param #', 'width': 60, 'stretch': True},
        'Focus': {'label': 'Sel', 'width': 50, 'stretch': True}
    }
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        self.currentID = 0

        self.title = tk.Label(self, text="Select an Instruction")
        self.title.grid(row=0, column=0)

        self.treeview = ttk.Treeview(self, columns=['Name', 'Pnum', 'Focus'], height=30)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.treeview.grid(row=1, column=0, sticky='NSEW')

        for name, definition in self.column_defs.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.treeview.heading(name, text=label, anchor=anchor)
            self.treeview.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=1, sticky='NSEW')

        self.treeview.bind('<<TreeviewSelect>>', self.on_select_instruction)

        self.commit = tk.Button(self, text='Commit Changes', command=self.on_instruction_commit)
        self.commit.grid(row=2)

        self.treeview_update = True

    def populate(self, instructions):
        """Clear tree view and re-load all instructions"""

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        for key, inst in instructions.items():
            values = [inst.get_attribute('name'), inst.get_attribute('param num')]
            if key == self.currentID:
                values.append('>>>')
            self.treeview.insert('', 'end', iid=key, text=key, values=values)

    def on_select_instruction(self, *args):
        if not self.treeview_update:
            self.treeview_update = True
            return
        self.treeview_update = False
        selected_id = self.treeview.selection()[0]
        self.currentID = selected_id
        self.callbacks['on_select_instruction'](selected_id)

        child_id = self.treeview.get_children()[int(selected_id)]

        self.treeview.focus(child_id)
        self.treeview.selection_set(int(selected_id))

    def on_instruction_commit(self):
        self.callbacks["on_instruction_commit"](self.currentID)


class InstructionDetails(tk.LabelFrame):
    """The applications instruction details view"""

    paramTree_column_defs = {
        '#0': {'label': 'ID', 'width': 30},
        'Name': {'label': 'Name', 'stretch': True, 'width': 400},
        'Type': {'label': 'Type', 'width': 100, 'stretch': True}
    }
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self, parent, instruction, instfields, paramfields, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.inputs = {}
        self.param_buttons = {}
        self.param_inputs = {}
        self.callbacks = callbacks
        self.editParamsInternal = False

        detailsLeft = tk.Frame(self)
        instDetails = tk.Frame(detailsLeft)

        self.instruction = instruction
        self.currentInstructionID = self.instruction.get_attribute('id')
        start_title = 'Instruction {}:'.format(self.currentInstructionID)

        self.title = ttk.Label(instDetails, text=start_title)
        self.title.grid(row=0, column=0, sticky=tk.E)

        self.inputs['Name'] = w.LabelInput(instDetails, 'Name', field_spec=instfields['Name'])
        self.inputs['Name'].grid(row=0, column=1, sticky=tk.W)
        self.inputs['Name'].set(instruction.get_attribute('name'))

        self.inputs['Implement'] = w.LabelInput(instDetails, 'Implement Instruction',
                                                field_spec=instfields['Implement'])
        self.inputs['Implement'].grid(row=1, column=0, sticky=tk.W)
        self.inputs['Implement'].set(instruction.get_attribute('implement'))

        self.inputs['Location'] = w.LabelInput(instDetails, 'Function Location', field_spec=instfields['Location'])
        self.inputs['Location'].grid(row=1, column=1)
        self.inputs['Location'].set(instruction.get_attribute('location'))

        self.inputs['Hard parameter one'] = w.LabelInput(instDetails, 'Hardcoded Param 1',
                                                         field_spec=instfields['Hard parameter one'])
        self.inputs['Hard parameter one'].grid(row=1, column=2)
        self.inputs['Hard parameter one'].set(instruction.get_attribute('hparam1'))

        self.inputs['Hard parameter two'] = w.LabelInput(instDetails, 'Hardcoded Param 2',
                                                         field_spec=instfields['Hard parameter two'])
        self.inputs['Hard parameter two'].grid(row=1, column=3)
        self.inputs['Hard parameter two'].set(instruction.get_attribute('hparam2'))
        instDetails.grid(row=0, column=0, sticky='NSEW')
        instDetails.rowconfigure(0, weight=1)
        instDetails.rowconfigure(1, weight=1)
        instDetails.columnconfigure(0, weight=2)
        instDetails.columnconfigure(1, weight=1)
        instDetails.columnconfigure(2, weight=1)
        instDetails.columnconfigure(3, weight=1)

        description = tk.Frame(detailsLeft)
        self.inputs['Description'] = w.LabelInput(description, 'Function Description',
                                                  field_spec=instfields['Description'],
                                                  input_args={'height': 5, 'width': 40})
        self.inputs['Description'].grid(row=0, column=0, sticky='NSEW')
        self.inputs['Description'].set(instruction.get_attribute('description'))
        self.description_scroll = ttk.Scrollbar(description, orient=tk.VERTICAL,
                                                command=self.inputs['Description'].input.yview)
        self.inputs['Description'].input.configure(yscrollcommand=self.description_scroll.set)
        self.description_scroll.grid(row=0, column=1, sticky='NSEW')
        description.grid(row=1, column=0, sticky='NSEW')
        description.grid_columnconfigure(0, weight=1)

        paramSelectTop = tk.Frame(detailsLeft)
        self.paramSelectTitle = ttk.Label(paramSelectTop, text='Select a Parameter to Edit')
        self.paramSelectTitle.grid(row=1, column=0)
        self.inputs['Parameter num'] = w.LabelInput(paramSelectTop, 'Param #', field_spec=instfields['Parameter num'])
        self.inputs['Parameter num'].grid(row=0, column=0)
        self.inputs['Parameter num'].set(instruction.get_attribute('param num'))
        self.param_buttons['Add'] = tk.Button(paramSelectTop, text='Insert Param Here', command=self.addParameter)
        self.param_buttons['Add'].grid(row=0, column=1)
        self.param_buttons['Remove'] = tk.Button(paramSelectTop, text='Remove this Param', command=self.remParameter)
        self.param_buttons['Remove'].grid(row=0, column=2)
        paramSelectTop.grid(row=2, column=0, sticky=tk.N + tk.S)
        paramSelectTop.rowconfigure(0, weight=1)
        paramSelectTop.rowconfigure(1, weight=1)
        paramSelectTop.columnconfigure(0, weight=1)
        paramSelectTop.columnconfigure(1, weight=1)
        paramSelectTop.columnconfigure(2, weight=1)

        paramSelect = tk.Frame(detailsLeft)
        self.paramTreeview = ttk.Treeview(paramSelect, columns=['Name', 'Type'])
        self.paramTreeview.grid(row=0, column=0, sticky='NSEW')

        for name, definition in self.paramTree_column_defs.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.paramTreeview.heading(name, text=label, anchor=anchor)
            self.paramTreeview.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.scrollbar = ttk.Scrollbar(paramSelect, orient=tk.VERTICAL, command=self.paramTreeview.yview)
        self.paramTreeview.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky='NSEW')
        self.paramTreeview.bind('<<TreeviewSelect>>', self.open_parameter)

        self.param_Treeview_update = True

        paramSelect.grid(row=3, column=0, sticky='NSEW')
        paramSelect.rowconfigure(0, weight=1)
        paramSelect.columnconfigure(0, weight=1)

        self.currentParamID = ''
        paramDetailsFrame = tk.LabelFrame(detailsLeft, text='Parameter {} Details'.format(self.currentParamID))
        paramOptionsAll = tk.Frame(paramDetailsFrame)
        self.param_inputs['Name'] = w.LabelInput(paramOptionsAll, 'Name',
                                                 field_spec=paramfields['Name'],
                                                 input_args={'width': 30})
        self.param_inputs['Name'].grid(row=0, column=0)

        self.param_inputs['Type'] = w.LabelInput(paramOptionsAll, 'Type', field_spec=paramfields['Parameter type'])
        self.param_inputs['Type'].grid(row=0, column=1)
        paramOptionsAll.grid(row=0, column=0, sticky='NSEW')

        self.paramOptionsValue = tk.Frame(paramDetailsFrame)
        self.param_inputs['Signed'] = w.LabelInput(self.paramOptionsValue, 'Is Signed?',
                                                   field_spec=paramfields['Signed'])
        self.param_inputs['Signed'].grid(row=1, column=0)

        self.param_inputs['Mask'] = w.LabelInput(self.paramOptionsValue, 'Uses a Mask?', field_spec=paramfields['Mask'])
        self.param_inputs['Mask'].grid(row=1, column=1)

        self.param_inputs['Mask Value'] = w.LabelInput(self.paramOptionsValue, 'Mask',
                                                       field_spec=paramfields['Mask Value'])
        self.param_inputs['Mask Value'].grid(row=1, column=2)
        self.paramOptionsValue.grid(row=1, column=0, sticky='NSEW')

        self.paramOptionsLoopCondition = tk.Frame(paramDetailsFrame)
        self.param_inputs['Condition Parameter'] = w.LabelInput(self.paramOptionsLoopCondition, 'Condition Parameter',
                                                                field_spec=paramfields['Condition Parameter'])
        self.param_inputs['Condition Parameter'].grid(row=0, column=0)

        self.param_inputs['Condition Test'] = w.LabelInput(self.paramOptionsLoopCondition, '',
                                                           field_spec=paramfields['Condition Test'])
        self.param_inputs['Condition Test'].grid(row=0, column=1)

        self.param_inputs['Condition Value'] = w.LabelInput(self.paramOptionsLoopCondition, 'Condition Value',
                                                            field_spec=paramfields['Condition Value'])
        self.param_inputs['Condition Value'].grid(row=0, column=2)
        self.paramOptionsLoopCondition.grid(row=1, column=0, sticky='NSEW')

        self.paramOptionsIteration = tk.Frame(paramDetailsFrame)
        self.param_inputs['Iterations'] = w.LabelInput(self.paramOptionsIteration, 'Iteration Parameter',
                                                       field_spec=paramfields['Iteration'])
        self.param_inputs['Iterations'].grid(row=0, column=0)
        self.paramOptionsIteration.grid(row=1, column=0, sticky='NSEW')

        self.paramOptionsInt = tk.Frame(paramDetailsFrame)
        self.param_inputs['Override'] = w.LabelInput(self.paramOptionsInt, 'Has Override?',
                                                     field_spec=paramfields['Override'])
        self.param_inputs['Override'].grid(row=0, column=0)

        self.param_inputs['Override condition'] = w.LabelInput(self.paramOptionsInt, 'Override Condition',
                                                               field_spec=paramfields['Override condition'])
        self.param_inputs['Override condition'].grid(row=0, column=1)

        self.param_inputs['Override offset'] = w.LabelInput(self.paramOptionsInt, 'Override Offset (Bytes)',
                                                            field_spec=paramfields['Override offset'])
        self.param_inputs['Override offset'].grid(row=1, column=1)

        self.param_inputs['Override result'] = w.LabelInput(self.paramOptionsInt, 'Override Result',
                                                            field_spec=paramfields['Override result'])
        self.param_inputs['Override result'].grid(row=1, column=2)

        self.param_inputs['Override compare'] = w.LabelInput(self.paramOptionsInt, 'Override Compare',
                                                             field_spec=paramfields['Override compare'])
        self.param_inputs['Override compare'].grid(row=1, column=0)
        self.paramOptionsInt.grid(row=2, column=0, sticky='NSEW')

        self.paramOptionsNoneUpper = tk.Frame(paramDetailsFrame)
        self.paramOptionsNoneUpper.grid(row=1, column=0, sticky='NSEW')

        self.paramOptionsNoneLower = tk.Frame(paramDetailsFrame)
        self.paramOptionsNoneLower.grid(row=2, column=0, sticky='NSEW')

        self.param_inputs['Type'].set_trace(self.change_param_fields)

        paramDetailsFrame.grid(row=4, column=0, sticky='NSEW')

        self.param_populate(int(self.inputs['Parameter num'].get()))
        self.param_fields_active = False
        self.set_param_fields_inactive()

        self.inputs['Parameter num'].set_trace(self.on_param_num_change)
        detailsLeft.grid(row=0, column=0, sticky='NSEW')
        detailsLeft.rowconfigure(0, weight=1)
        detailsLeft.rowconfigure(1, weight=2)
        detailsLeft.rowconfigure(2, weight=1)
        detailsLeft.rowconfigure(3, weight=4)
        detailsLeft.rowconfigure(4, weight=1)
        detailsLeft.columnconfigure(0, weight=1)

        self.inputs['Notes'] = w.LabelInput(self, 'Instruction Notes', field_spec=instfields['Notes'],
                                            input_args={'width': 50, 'height': 40})
        self.inputs['Notes'].grid(row=0, column=1, sticky='NSEW')
        self.description_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                                command=self.inputs['Notes'].input.yview)
        self.inputs['Notes'].input.configure(yscrollcommand=self.description_scroll.set)
        self.inputs['Notes'].set(instruction.get_attribute('notes'))
        self.description_scroll.grid(row=0, column=2, sticky='NSEW')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def change_param_fields(self, *args):
        paramType = self.param_inputs['Type'].get()
        # print(f'switching to {paramType}')
        if 'scpt' in paramType:
            if paramType == 'scpt':
                self.paramOptionsValue.tkraise()
                self.paramOptionsInt.tkraise()
            else:
                self.paramOptionsNoneUpper.tkraise()
                self.paramOptionsNoneLower.tkraise()

        elif 'loop' in paramType:
            self.paramOptionsNoneLower.tkraise()
            if 'start' in paramType:
                self.paramOptionsIteration.tkraise()
                self.populate_parameters_choices('Iterations')
            elif 'condition' in paramType:
                self.paramOptionsLoopCondition.tkraise()
                self.populate_parameters_choices('Condition Parameter')
            else:
                self.paramOptionsNoneUpper.tkraise()

        elif 'switch' == paramType:
            self.paramOptionsIteration.tkraise()
            self.paramOptionsNoneLower.tkraise()
            self.populate_parameters_choices('Iterations')

        elif 'int' == paramType:
            self.paramOptionsValue.tkraise()
            self.paramOptionsInt.tkraise()

        else:
            self.paramOptionsNoneUpper.tkraise()
            self.paramOptionsNoneLower.tkraise()

    def param_populate(self, num):
        for row in self.paramTreeview.get_children():
            self.paramTreeview.delete(row)

        if num == -1:
            num = self.inputs['Parameter num'].get()
        params = self.instruction.get_attribute('params')
        if len(params) > 0:
            for key, value in params.items():
                if int(key) > num - 1:
                    break
                ID = key
                text = key
                values = [value.get_attribute('name'), value.get_attribute('type')]
                self.paramTreeview.insert('', 'end', iid=ID, text=text, values=values)

    def open_parameter(self, *args):
        """Tell app to load new parameter"""
        if not self.param_Treeview_update:
            self.param_Treeview_update = True
            return
        self.param_Treeview_update = False
        selected_id = self.paramTreeview.selection()[0]
        self.set_param_fields_active()
        self.callbacks['on_select_parameter'](self.currentInstructionID, self.currentParamID, selected_id)

        child_id = self.paramTreeview.get_children()[int(selected_id)]
        self.paramTreeview.focus(child_id)
        self.paramTreeview.selection_set(int(selected_id))

    def get_inst_fields(self):
        fields = {'Instruction ID': self.currentInstructionID,
                  'Parameter num': self.inputs['Parameter num']}
        for key, value in self.inputs.items():
            fields[key] = value.get()
            if key in ('Description', 'Notes'):
                fields[key] = fields[key].rstrip()
        return fields

    def set_inst_fields(self):
        inst_dict = self.instruction.get_all()

        # Set title
        self.currentInstructionID = inst_dict['Instruction ID']
        title = 'Instruction {}:'.format(self.currentInstructionID)
        self.title.config(text=title)

        # Populate parameters
        self.param_populate(-1)

        # set all other fields
        inst_dict.pop('Instruction ID')
        inst_dict.pop('Parameters')
        for key, value in inst_dict.items():
            self.inputs[key].set(value)

        self.currentParamID = ''
        self.clear_param_fields()
        self.set_param_fields_inactive()

        self.reset_scroll_bars()

    def get_param_fields(self):
        if self.param_fields_active:
            param_fields = {'ID': self.currentParamID}
            for key, value in self.param_inputs.items():
                param_fields[key] = value.get()

            return param_fields
        else:
            return {'inactive': True}

    def set_param_fields(self, paramID):
        try:
            param_details = self.instruction.get_attribute('params')[paramID]
        except IndexError:
            tk.Message(text='there is no such parameter available')
        else:
            param_dict = param_details.get_fields()
            self.currentParamID = param_dict['ID']
            param_dict.pop('ID')
            for key, value in param_dict.items():
                self.param_inputs[key].set(value)

    def set_param_fields_active(self):
        self.param_fields_active = True
        for key in self.param_inputs.keys():
            self.param_inputs[key].config({'state': 'normal'})
        for key in self.param_buttons.keys():
            self.param_buttons[key].config({'state': 'normal'})

    def set_param_fields_inactive(self):
        self.param_fields_active = False
        for key in self.param_inputs.keys():
            self.param_inputs[key].config({'state': 'disabled'})
        for key in self.param_buttons.keys():
            self.param_buttons[key].config({'state': 'disabled'})

    def clear_param_fields(self):
        for key in self.param_inputs.keys():
            if key in ('Mask', 'Override'):
                self.param_inputs[key].set(False)
            else:
                self.param_inputs[key].set('')

    def update_instructions(self, instruction):
        self.instruction = instruction

    def on_param_num_change(self, *args):
        instID = self.currentInstructionID
        newParamNum = self.inputs['Parameter num'].get()
        # print("param num change activated")
        if self.editParamsInternal:
            self.callbacks['on_parameter_num_change'](instID, newParamNum, int(self.currentParamID))
        else:
            self.callbacks['on_parameter_num_change'](instID, newParamNum)
        self.editParamsInternal = False
        self.currentParamID = ''
        self.clear_param_fields()
        self.set_param_fields_inactive()

    def reset_scroll_bars(self):
        self.inputs['Description'].input.yview_moveto('0.00')
        self.inputs['Notes'].input.yview_moveto('0.00')
        self.paramTreeview.yview_moveto('0.00')

    def populate_parameters_choices(self, field):
        paramList = []
        params = self.instruction.get_attribute('params')
        for i in range(int(self.currentParamID)):
            value = f'{str(i)}-'
            value += params[str(i)].get_attribute('name')
            paramList.append(value)
        self.param_inputs[field].input['values'] = paramList

    def addParameter(self):
        self.editParamsInternal = True
        self.inputs['Parameter num'].set(self.inputs['Parameter num'].get() + 1)

    def remParameter(self):
        self.editParamsInternal = True
        self.inputs['Parameter num'].set(self.inputs['Parameter num'].get() - 1)


class ScriptView(tk.Frame):
    """The application's script decoding view"""

    hideDefault = True

    script_tree_headers = {
        '#0': {'label': 'Name', 'width': 110},
        'Type': {'label': 'Type', 'stretch': True, 'width': 35},
        'Length': {'label': 'Length', 'width': 50, 'stretch': True},
        'Focus': {'label': 'Sel', 'width': 30, 'stretch': True}
    }

    instruction_tree_headers = {
        '#0': {'label': 'Position', 'width': 50, 'stretch': True},
        'Addr': {'label': 'Address', 'stretch': True, 'width': 120, 'anchor': tk.W},
        'Code': {'label': 'Code', 'stretch': True, 'width': 200, 'anchor': tk.W},
        'Decoded': {'label': 'Impl', 'width': 40, 'stretch': True},
        'Error': {'label': 'Err', 'width': 40, 'stretch': True},
        'Focus': {'label': 'Sel', 'width': 30, 'stretch': True}
    }

    parameter_tree_headers = {
        '#0': {'label': 'Position', 'width': 50},
        'Name': {'label': 'Code', 'width': 50},
        'Details': {'label': 'Decoded', 'stretch': True, 'width': 400},
        'Error': {'label': 'Error', 'width': 50, 'stretch': True}
    }

    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    script_display_select_options = {
        'All Scripts': 'all',
        'Only Scripts with Errors': 'errors'
    }

    instruction_display_select_options = {
        'All Instructions': 'all',
        'Only Implemented Instructions': 'implemented',
        'Only Instructions with errors': 'errors',
        'Exclude Implemented': 'unimplemented',
        'Set and Decisions only': 'set'
    }

    details_canvas_padding = {'x': 5, 'y': 5}

    script_start_field = {'req': False, 'type': FT.hex, 'pattern': '^0x8[0-9,a-f]{7}$'}

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.inst_text_width = 50
        self.callbacks = callbacks
        self.error_list = None

        scriptDisplayTop = tk.Frame(self)
        self.script_file_title = tk.Label(scriptDisplayTop, text='Script File Details')
        self.script_file_title.grid(row=0, column=0)

        self.script_file_script_num = tk.Label(scriptDisplayTop, text='Number of scripts')
        self.script_file_script_num.grid(row=1, column=0)

        self.script_file_start = w.LabelInput(scriptDisplayTop, 'Script File Position (value at 0x8030CEA0)',
                                              field_spec=self.script_start_field)
        self.script_file_start.grid(row=1, column=1, padx=(10, 10))

        self.script_file_start_set = tk.Button(scriptDisplayTop, text='Set Position', command=self.set_script_start)
        self.script_file_start_set.grid(row=1, column=2)

        scriptDisplayTop.grid(row=0, column=0, sticky=tk.W)
        scriptDisplayTop.columnconfigure(1, weight=1)

        scriptDisplayBot = tk.Frame(self)

        # Frame which holds the error display and footer
        scriptDisplayBotLeft = tk.Frame(scriptDisplayBot)

        # Frame to hold the error display and scrollbar
        self.details_text_objects = []
        detailsDisplay = tk.LabelFrame(scriptDisplayBotLeft, text='Script Parsing Details')
        self.details_display = tk.Canvas(detailsDisplay, width=18, height=20)
        self.details_display.grid(row=0, column=0, sticky='NSEW')
        self.details_display_scroll = ttk.Scrollbar(detailsDisplay, orient=tk.VERTICAL,
                                                    command=self.details_display.yview)
        self.details_display.configure(yscrollcommand=self.details_display_scroll.set, bg='white')
        self.details_display_scroll.grid(row=0, column=1, sticky='NSEW')
        self.details_display.tag_bind('inst', '<Button-1>', func=self.highlight_detail)
        detailsDisplay.grid(row=0, column=0, sticky='NSEW')
        detailsDisplay.rowconfigure(0, weight=1)
        detailsDisplay.columnconfigure(0, weight=1)
        self.cur_highlight_obj_id = None
        self.highlighted_detail = None
        self.highlights_lists = None

        # Frame to hold the footer display and scrollbar
        footer = tk.LabelFrame(scriptDisplayBotLeft, text='Footer')
        self.footer_text = tk.Text(footer, height=17, width=15)
        self.footer_text.grid(row=0, column=0, sticky='NSEW')
        self.footer_display_scroll = ttk.Scrollbar(footer, orient=tk.VERTICAL,
                                                   command=self.footer_text.yview)
        self.footer_text.configure(yscrollcommand=self.footer_display_scroll.set)
        self.footer_display_scroll.grid(row=0, column=1, sticky='NSEW')
        footer.grid(row=1, column=0, sticky='NSEW')
        footer.rowconfigure(0, weight=1)
        footer.columnconfigure(0, weight=1)

        scriptDisplayBotLeft.grid(row=0, column=0, sticky='NSEW')
        scriptDisplayBotLeft.rowconfigure(0, weight=1)
        scriptDisplayBotLeft.rowconfigure(1, weight=1)
        scriptDisplayBotLeft.columnconfigure(0, weight=1)

        scriptDisplayBotRight = tk.Frame(scriptDisplayBot)

        """Script Tree Fields"""
        self.script_tree_update = True
        self.current_script_id = None
        self.current_script_tree = None
        scriptTree = tk.LabelFrame(scriptDisplayBotRight, text='Script Index')
        columns = list(self.script_tree_headers.keys())[1:]
        self.script_tree = ttk.Treeview(scriptTree, columns=columns, height=25)
        scriptTree.columnconfigure(0, weight=1)
        scriptTree.rowconfigure(0, weight=1)
        self.script_tree.grid(row=0, column=0, sticky='NSEW')

        for name, definition in self.script_tree_headers.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.script_tree.heading(name, text=label, anchor=anchor)
            self.script_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.script_tree_scroll = ttk.Scrollbar(scriptTree, orient=tk.VERTICAL,
                                                command=self.script_tree.yview)
        self.script_tree.configure(yscrollcommand=self.script_tree_scroll.set)
        self.script_tree_scroll.grid(row=0, column=1, sticky='NSEW')

        self.script_tree.bind('<<TreeviewSelect>>', self.on_select_script)
        scriptTree.grid(row=0, column=0, sticky='NSEW')

        """Instruction Tree Fields"""
        self.current_instruction_id = None
        self.instruction_tree_update = True
        self.current_instruction_tree = None
        instructionTree = tk.LabelFrame(scriptDisplayBotRight, text='Instruction Index')
        columns = list(self.instruction_tree_headers.keys())[1:]
        self.instruction_tree = ttk.Treeview(instructionTree, columns=columns, height=25)
        instructionTree.columnconfigure(0, weight=1)
        instructionTree.rowconfigure(0, weight=1)
        self.instruction_tree.grid(row=0, column=0, sticky='NSEW')

        for name, definition in self.instruction_tree_headers.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.instruction_tree.heading(name, text=label, anchor=anchor)
            self.instruction_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.instruction_tree_scroll = ttk.Scrollbar(instructionTree, orient=tk.VERTICAL,
                                                     command=self.instruction_tree.yview)
        self.instruction_tree.configure(yscrollcommand=self.instruction_tree_scroll.set)
        self.instruction_tree_scroll.grid(row=0, column=1, sticky='NSEW')

        self.instruction_tree.bind('<<TreeviewSelect>>', self.on_select_script_instruction)
        instructionTree.grid(row=0, column=1, sticky='NSEW')

        instructionDetails = tk.LabelFrame(scriptDisplayBotRight, text='Instruction Details')
        self.instruction_decoded = tk.Label(instructionDetails, text='Instruction is Decoded')
        self.instruction_decoded.grid(row=0, column=0)
        self.instruction_code = tk.Label(instructionDetails, text='Instruction Code:')
        self.instruction_code.grid(row=1, column=0)
        self.instruction_name = tk.Label(instructionDetails, text='Instruction Name:')
        self.instruction_name.grid(row=2, column=0)
        self.instruction_location = tk.Label(instructionDetails, text='Instruction Location:')
        self.instruction_location.grid(row=3, column=0)

        instructionDescription = tk.Frame(instructionDetails)
        self.instruction_description_label = tk.Label(instructionDescription, text="Description")
        self.instruction_description_label.grid(row=0, column=0, sticky=tk.W)
        self.instruction_description = tk.Text(instructionDescription, width=self.inst_text_width, height=12)
        self.instruction_description.grid(row=1, column=0, sticky='NSEW')
        self.instruction_description_scroll = ttk.Scrollbar(instructionDescription, orient=tk.VERTICAL,
                                                            command=self.instruction_description.yview)
        self.instruction_description.configure(yscrollcommand=self.instruction_description_scroll.set)
        self.instruction_description_scroll.grid(row=1, column=1, sticky='NSEW')
        instructionDescription.grid(row=4, column=0, sticky='NSEW')
        instructionDescription.grid_columnconfigure(0, weight=1)

        self.instruction_parameter_tree_label = tk.Label(instructionDetails, text="Parameters")
        self.instruction_parameter_tree_label.grid(row=5, column=0, sticky=tk.W)

        """Parameter Tree Fields"""
        parameterTree = tk.Frame(instructionDetails)

        columns = list(self.parameter_tree_headers.keys())[1:]
        self.parameter_tree = ttk.Treeview(parameterTree, columns=columns, height=6)
        parameterTree.columnconfigure(0, weight=1)
        parameterTree.rowconfigure(0, weight=1)
        self.parameter_tree.grid(row=0, column=0, sticky='NSEW')

        for name, definition in self.parameter_tree_headers.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.parameter_tree.heading(name, text=label, anchor=anchor)
            self.parameter_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.parameter_tree_scroll = ttk.Scrollbar(parameterTree, orient=tk.VERTICAL,
                                                   command=self.parameter_tree.yview)
        self.parameter_tree.configure(yscrollcommand=self.parameter_tree_scroll.set)
        self.parameter_tree_scroll.grid(row=0, column=1, sticky='NSEW')
        parameterTree.grid(row=6, column=0, sticky='NSEW')

        instructionError = tk.Frame(instructionDetails)
        self.instruction_error_label = tk.Label(instructionError, text='Errors')
        self.instruction_error_label.grid(row=0, column=0, sticky=tk.W)
        self.instruction_error_text = tk.Text(instructionError, width=self.inst_text_width, height=3)
        self.instruction_error_text.grid(row=1, column=0, sticky='NSEW')
        self.instruction_error_scroll = ttk.Scrollbar(instructionError, orient=tk.VERTICAL,
                                                      command=self.instruction_error_text.yview)
        self.instruction_error_text.configure(yscrollcommand=self.instruction_error_scroll.set)
        self.instruction_error_scroll.grid(row=1, column=1, sticky='NSEW')
        instructionError.grid(row=7, column=0, sticky='NSEW')
        instructionError.grid_columnconfigure(0, weight=1)

        instructionDetails.grid(row=0, column=2, sticky='NSEW')
        instructionDetails.rowconfigure(1, weight=1)
        instructionDetails.rowconfigure(2, weight=1)
        instructionDetails.rowconfigure(3, weight=1)
        instructionDetails.rowconfigure(4, weight=1)
        instructionDetails.rowconfigure(5, weight=1)
        instructionDetails.rowconfigure(6, weight=1)
        instructionDetails.columnconfigure(0, weight=1)

        options = self.script_display_select_options
        self.script_display_select_current = 'all'
        script_display_select = tk.Frame(scriptDisplayBotRight)
        self.script_display_select_variable = tk.StringVar()
        self.script_display_select_all = tk.Radiobutton(script_display_select, text=list(options.keys())[0],
                                                        variable=self.script_display_select_variable,
                                                        value=0, command=lambda:
            self.on_script_display_change())
        self.script_display_select_all.grid(row=0, column=0)
        self.script_display_select_error = tk.Radiobutton(script_display_select, text=list(options.keys())[1],
                                                          variable=self.script_display_select_variable,
                                                          value=1,
                                                          command=lambda:
                                                          self.on_script_display_change())
        self.script_display_select_error.grid(row=1, column=0)
        self.script_display_select_all.select()
        script_display_select.grid(row=1, column=0)

        options = self.instruction_display_select_options
        self.instruction_display_select_current = 'all'
        instruction_display_select = tk.Frame(scriptDisplayBotRight)
        self.instruction_display_select_variable = tk.StringVar()
        self.instruction_display_select_variable.set(list(options.keys())[0])
        self.instruction_display_select_all = tk.Radiobutton(instruction_display_select,
                                                             text=list(options.keys())[0],
                                                             variable=self.instruction_display_select_variable,
                                                             value=0,
                                                             command=lambda:
                                                             self.on_instruction_display_change(
                                                                 list(options.values())[0]))
        self.instruction_display_select_all.grid(row=0, column=0)
        self.instruction_display_select_imp = tk.Radiobutton(instruction_display_select,
                                                             text=list(options.keys())[1],
                                                             variable=self.instruction_display_select_variable,
                                                             value=1,
                                                             command=lambda:
                                                             self.on_instruction_display_change(
                                                                 list(options.values())[1]))
        self.instruction_display_select_imp.grid(row=1, column=0)
        self.instruction_display_select_error = tk.Radiobutton(instruction_display_select,
                                                               text=list(options.keys())[2],
                                                               variable=self.instruction_display_select_variable,
                                                               value=2,
                                                               command=lambda:
                                                               self.on_instruction_display_change(
                                                                   list(options.values())[2]))
        self.instruction_display_select_error.grid(row=2, column=0)
        self.instruction_display_select_both = tk.Radiobutton(instruction_display_select,
                                                              text=list(options.keys())[3],
                                                              variable=self.instruction_display_select_variable,
                                                              value=3,
                                                              command=lambda:
                                                              self.on_instruction_display_change(
                                                                  list(options.values())[3]))
        self.instruction_display_select_both.grid(row=3, column=0)
        self.instruction_display_select_only_options = tk.Radiobutton(instruction_display_select,
                                                              text=list(options.keys())[4],
                                                              variable=self.instruction_display_select_variable,
                                                              value=4,
                                                              command=lambda:
                                                              self.on_instruction_display_change(
                                                                  list(options.values())[4]))
        self.instruction_display_select_only_options.grid(row=4, column=0)
        self.instruction_display_select_all.select()
        instruction_display_select.grid(row=1, column=1)
        instruction_display_select.rowconfigure(0, weight=1)
        instruction_display_select.rowconfigure(1, weight=1)
        instruction_display_select.rowconfigure(2, weight=1)
        instruction_display_select.rowconfigure(3, weight=1)
        instruction_display_select.columnconfigure(0, weight=1)

        scriptDisplayBotRight.grid(row=0, column=1, sticky='NSEW')
        scriptDisplayBotRight.rowconfigure(0, weight=2)
        scriptDisplayBotRight.rowconfigure(1, weight=1)
        scriptDisplayBotRight.columnconfigure(0, weight=3)
        scriptDisplayBotRight.columnconfigure(1, weight=6)
        scriptDisplayBotRight.columnconfigure(2, weight=8)

        scriptDisplayBot.grid(row=1, column=0, sticky='NSEW')
        scriptDisplayBot.rowconfigure(0, weight=1)
        scriptDisplayBot.columnconfigure(0, weight=1)
        scriptDisplayBot.columnconfigure(1, weight=12)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def display_script_analysis_new(self, sct_file_info, sct_tree):
        self.current_script_id = None
        self.current_instruction_id = None
        self.cur_highlight_obj_id = None
        self.highlighted_detail = None

        name = 'Script File Details: {}'.format(sct_file_info['Filename'])
        script_num = 'Number of scripts: {}'.format(sct_file_info['Script num'])
        self.error_list = sct_file_info['Errors']
        footer = sct_file_info['Footer']
        self.script_file_title.config(text=name)
        self.script_file_script_num.config(text=script_num)

        self.details_display.delete('all')
        self.details_text_objects = []
        self.highlights_lists = sct_file_info['Inst Locs']
        if self.error_list == '':
            value = 'No Errors\n\nInstructions Used:\n'
            self.details_display.create_text(self.details_canvas_padding['x'], self.details_canvas_padding['y'], anchor=tk.NW, text=value)
            cur_height = self.details_display.bbox('all')[3]
            insts = sct_file_info['Insts']
            separatorPlaced = False
            for inst, count in sorted(insts.items()):
                if inst > 265:
                    if not separatorPlaced:
                        self.details_display.create_text(self.details_canvas_padding['x'], cur_height + self.details_canvas_padding['y'], anchor=tk.NW, text='---------------\n')
                        cur_height = self.details_display.bbox('all')[3]
                        separatorPlaced = True
                    self.details_display.create_text(self.details_canvas_padding['x'], cur_height + self.details_canvas_padding['y'], anchor=tk.NW, text=f'{hex(inst)}: {count}\n', tags=f'{hex(inst)}')
                else:
                    self.details_display.create_text(self.details_canvas_padding['x'], cur_height + self.details_canvas_padding['y'], anchor=tk.NW, text=f'{inst}: {count}', tags=('inst', f'{inst}'))
                cur_height = self.details_display.bbox('all')[3]
        else:
            self.details_display.create_text(self.details_canvas_padding['x'], self.details_canvas_padding['y'],
                                                 anchor=tk.NW, text='Errors:\n\n')
            cur_height = self.details_display.bbox('all')[3]
            for error in self.error_list:
                v = self.details_display.create_text(self.details_canvas_padding['x'], cur_height + self.details_canvas_padding['y'],
                                                     anchor=tk.NW, text=error, tags='error')
                self.details_text_objects.append(v)
                cur_height = self.details_display.bbox('all')[3]

        self.details_display.configure(scrollregion=self.details_display.bbox("all"))

        self.footer_text.delete('1.0', tk.END)
        value = footer
        if len(value) > 1:
            if value[:-1] == '\n':
                value = value[:-1]
        self.footer_text.insert('1.0', value)

        self.populate_scripts(sct_tree)
        self.populate_instructions(None, None)
        self.set_instruction_detail_fields(None, mode='reset')

        t = Timer(0.1, self.reset_scroll_bars)
        t.run()

    def on_select_script(self, *args):
        selected_id = self.script_tree.selection()[0]
        # print('showing: {}'.format(selected_id))
        self.current_script_id = selected_id
        self.current_instruction_id = None
        self.current_instruction_tree = None
        self.callbacks['on_select_script'](self.current_script_id)

        t = Timer(0.1, lambda: self.reset_scroll_bars('Instruction'))
        t.run()

    def populate_scripts(self, scts_tree=None):
        if scts_tree is None:
            if self.current_script_tree is None:
                return
            else:
                scts_tree = self.current_script_tree

        self.current_script_tree = scts_tree

        for row in self.script_tree.get_children():
            self.script_tree.delete(row)

        scripts_to_remove = []
        errorlist = self.error_list.split('\n')
        if self.script_display_select_current == '1':
            for script in scts_tree.keys():
                remove = True
                for error in errorlist:
                    if script == error:
                        remove = False
                if remove:
                    scripts_to_remove.append(script)

        for s in scripts_to_remove:
            scts_tree.pop(s)

        if self.highlighted_detail is None:
            highlight_inst = False
        else:
            highlight_inst = True
            highlight_list = self.highlights_lists[self.highlighted_detail]

        for key, value in scts_tree.items():
            values = [value['Type'], value['Length']]
            if highlight_inst:
                if key in highlight_list:
                    values.append(f'{self.highlighted_detail}')
            if self.current_script_id is not None:
                if key == self.current_script_id:
                    if len(values) > 2:
                        values.pop()
                    values.append('>>>')
            self.script_tree.insert('', 'end', iid=key, text=key, values=values)

    def on_select_script_instruction(self, *args):
        selected_id = self.instruction_tree.selection()[0]
        self.current_instruction_id = selected_id
        self.callbacks['on_select_script_instruction'](self.current_script_id, self.current_instruction_id)

        t = Timer(0.1, lambda: self.reset_scroll_bars('Details'))
        t.run()

    def populate_instructions(self, insts=None, new_id=None):
        self.current_instruction_id = new_id

        for row in self.instruction_tree.get_children():
            self.instruction_tree.delete(row)

        if insts is None:
            if self.current_instruction_tree is None:
                return
            else:
                insts = self.current_instruction_tree

        self.current_instruction_tree = insts

        hasSelection = True
        if new_id is None:
            hasSelection = False

        insts_to_Remove = []

        if self.instruction_display_select_current == '2':
            for key, inst in insts.items():
                if inst['Error'] == 'None':
                    insts_to_Remove.append(key)

        if self.instruction_display_select_current == '1':
            for key, inst in insts.items():
                if not inst['Decoded']:
                    insts_to_Remove.append(key)

        if self.instruction_display_select_current == '3':
            for key, inst in insts.items():
                if inst['Decoded']:
                    insts_to_Remove.append(key)

        if self.instruction_display_select_current == '4':
            for key, inst in insts.items():
                if not inst['Decision']:
                    insts_to_Remove.append(key)

        for i in insts_to_Remove:
            insts.pop(i)

        for key, inst in insts.items():
            # if 'Code' not in inst.keys():
            #     print('pause here')
            values = [inst['Code'], str(inst['Decoded']), inst['Error']]
            if self.hideDefault and values[1] == 'True':
                values[1] = ''
            if self.hideDefault and values[2] == 'None':
                values[2] = ''
            suffix_added = False
            if 'ID' in inst:
                id_int = int(inst['ID'], 16)
                if self.highlighted_detail == id_int:
                    values.append(f'{id_int}')
                    suffix_added = True
            if hasSelection:
                if key == self.current_instruction_id:
                    if suffix_added:
                        values.pop()
                    values.append('>>>')
            pos = key
            values.insert(0, inst.get('pos', ''))
            self.instruction_tree.insert('', 'end', iid=key, text=pos, values=values)

        # print(self.instruction_tree.get_children())

    def on_script_display_change(self):
        pass
        new_option = self.script_display_select_variable.get()

        if new_option == self.script_display_select_current:
            return
        else:
            self.script_display_select_current = new_option
            self.callbacks['on_select_script'](self.current_script_id)

            t = Timer(0.1, lambda: self.reset_scroll_bars('Script'))
            t.run()

    def on_instruction_display_change(self, new_option):
        pass
        new_option = self.instruction_display_select_variable.get()

        if new_option == self.instruction_display_select_current:
            return
        else:
            self.instruction_display_select_current = new_option
            self.callbacks['on_select_script_instruction'](self.current_script_id, self.current_instruction_id)

            t = Timer(0.1, lambda: self.reset_scroll_bars('Instruction'))
            t.run()

    def set_instruction_detail_fields(self, details, mode='set'):
        """Can be used to either set or reset all fields Instruction Detail fields depending on the mode"""

        reset_values = {
            'string': '',
            'label-ID': 'Instruction Code:',
            'label-Name': 'Instruction Name:',
            'label-Location': 'Instruction Location:',
            'text': '\n'
        }

        t = Timer(0.1, lambda: self.reset_scroll_bars('Details'))
        t.run()

        if mode == 'reset':
            self.instruction_decoded.config(text=reset_values['string'])
            self.instruction_code.config(text=reset_values['label-ID'])
            self.instruction_name.config(text=reset_values['label-Name'])
            self.instruction_location.config(text=reset_values['label-Location'])

            self.instruction_description.delete('1.0', tk.END)
            value = reset_values['text']
            if len(value) > 1:
                if value[:-1] == '\n':
                    value = value[:-1]
            self.instruction_description.insert('1.0', value)

            self.instruction_error_text.delete('1.0', tk.END)
            value = reset_values['text']
            if len(value) > 1:
                if value[:-1] == '\n':
                    value = value[:-1]
            self.instruction_error_text.insert('1.0', value)

            self.populate_params(None)

        else:
            decoded = details['Decoded']
            if decoded == 'SCPT':
                ID = details['Code']
            else:
                ID = 'Instruction Code: {}'.format(details['Code'])
            self.instruction_decoded.config(text=decoded)
            self.instruction_code.config(text=ID)

            if decoded in ('This Instruction is Decoded', 'This String is Decoded'):
                name = f'Instruction Name: {details["Name"]}'
                location = f'Instruction Location: {details["Location"]}'
                description = details['Description']
                # print(description)
                errors = details['Errors']
                params = details['Param Tree']
                self.instruction_name.config(text=name)
                self.instruction_location.config(text=location)

                self.instruction_description.delete('1.0', tk.END)
                value = description
                if len(value) > 1:
                    if value[:-1] == '\n':
                        value = value[:-1]
                self.instruction_description.insert('1.0', value)

                self.instruction_error_text.delete('1.0', tk.END)
                value = errors
                if len(value) > 1:
                    if value[:-1] == '\n':
                        value = value[:-1]
                self.instruction_error_text.insert('1.0', value)

                self.populate_params(params)

            else:

                self.instruction_name.config(text=reset_values['label-Name'])

                value = reset_values['text']
                if decoded == 'SCPT':
                    errors = ''
                else:
                    errors = value

                description = details['Description']
                self.instruction_description.delete('1.0', tk.END)
                if len(value) > 1:
                    if value[:-1] == '\n':
                        value = value[:-1]
                self.instruction_description.insert('1.0', description)

                self.instruction_error_text.delete('1.0', tk.END)
                if len(value) > 1:
                    if value[:-1] == '\n':
                        value = value[:-1]
                self.instruction_error_text.insert('1.0', errors)

                self.populate_params(None)

    def populate_params(self, param_tree):
        for row in self.parameter_tree.get_children():
            self.parameter_tree.delete(row)

        if param_tree is None:
            return

        for key, param in param_tree.items():
            values = [param['Name'], param['Details'], param['Error']]
            self.parameter_tree.insert('', 'end', iid=key, text=key, values=values)
            if 'SCPT' in param.keys():
                for key1, param1 in param['SCPT'].items():
                    # print(key1)
                    values = ['SCPT', param1]
                    self.parameter_tree.insert(key, 'end', iid=key1, text=key1, values=values)
            if 'loop' in param.keys():
                for key1, param1 in param['loop'].items():
                    # print(key1)
                    values = ['SCPT', param1]
                    self.parameter_tree.insert(key, 'end', iid=key1, text=key1, values=values)
            if 'switch' in param.keys():
                for key1, param1 in param['switch'].items():
                    # print(key1)
                    values = ['switch', param1]
                    self.parameter_tree.insert(key, 'end', iid=key1, text=key1, values=values)

    def reset_scroll_bars(self, param='All'):
        all_elements = False
        script = False

        if param == 'All':
            self.details_display.yview_moveto('0.00')
            self.footer_text.yview_moveto('0.00')
            all_elements = True

        if param == 'Script' or all_elements:
            self.script_tree.yview_moveto('0.00')
            script = True

        if param == 'Instruction' or all_elements or script:
            self.instruction_tree.yview_moveto('0.00')

        self.instruction_error_text.yview_moveto('0.00')
        self.parameter_tree.yview_moveto('0.00')
        self.instruction_description.yview_moveto('0.00')

    def set_script_start(self):
        start = self.script_file_start.get()

        if not re.search('^0x8[0-9,a-f]{7}$', start):
            return

        self.callbacks['on_set_inst_start'](start, self.current_script_id)

    def highlight_detail(self, event):
        canvas_scrollable_bbox = self.details_display['scrollregion'].split(' ')
        canvas_window_y = self.details_display.yview()
        canvas_window_x = self.details_display.xview()
        canvas_window_bbox = (int(canvas_scrollable_bbox[0]) + int(canvas_window_x[0] * int(canvas_scrollable_bbox[2])),
                              int(canvas_scrollable_bbox[1]) + int(canvas_window_y[0] * int(canvas_scrollable_bbox[3])),
                              int(canvas_scrollable_bbox[0]) + int(canvas_window_x[1] * int(canvas_scrollable_bbox[2])),
                              int(canvas_scrollable_bbox[1]) + int(canvas_window_y[1] * int(canvas_scrollable_bbox[3]))
                              )
        e_x = canvas_window_bbox[0] + event.x
        e_y = canvas_window_bbox[1] + event.y
        closest = self.details_display.find_closest(e_x, e_y, halo=3)
        tags = self.details_display.gettags(closest)
        if 'inst' not in tags:
            return

        if self.cur_highlight_obj_id is not None:
            self.details_display.itemconfigure(self.cur_highlight_obj_id, fill='black')

        next_highlight_inst = int(tags[1])
        if self.highlighted_detail == next_highlight_inst:
            self.highlighted_detail = None
        else:
            self.highlighted_detail = next_highlight_inst
            self.cur_highlight_obj_id = closest
            self.details_display.itemconfigure(closest, fill='red')

        self.populate_scripts()
        if self.current_script_id is not None:
            self.populate_instructions()


class HelpPopupView(tk.Toplevel):
    window_offset = {
        'x': 50,
        'y': 50
    }

    size = {
        'width': 400,
        'height': 400
    }

    text_offset = {
        'x': 10,
        'y': 10
    }

    def __init__(self, parent, title, about_text, position, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks

        help_canvas = tk.Canvas(self, width=self.size['width'], height=self.size['height'])
        help_canvas.grid(row=0, column=0)
        help_canvas.create_text((self.text_offset['x'], self.text_offset['y']),
                                anchor=tk.NW, text=about_text,
                                width=self.size['width'] - self.text_offset['x'])

        self.quit = tk.Button(self, text='Cancel', command=self.callbacks['on_close'])
        self.quit.grid(row=1, column=0)
        canvas_scrollbar = tk.Scrollbar(self, orient="vertical", command=help_canvas.yview)
        help_canvas.configure(yscrollcommand=canvas_scrollbar.set)
        help_canvas.config(scrollregion=help_canvas.bbox("all"))
        canvas_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)

        self.title(title)
        self.resizable(width=False, height=False)
        posX = position['x'] + self.window_offset['x']
        posY = position['y'] + self.window_offset['y']
        pos = '+{0}+{1}'.format(posX, posY)
        self.geometry(pos)


class TabbedHelpPopupView(tk.Toplevel):
    window_offset = {
        'x': 50,
        'y': 50
    }

    size = {
        'width': 400,
        'height': 400
    }

    text_offset = {
        'x': 10,
        'y': 10
    }

    def __init__(self, parent, title, about_text, position, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0)

        for i, (k, v) in enumerate(about_text.items()):
            tab_frame = w.ScrolledTextCanvas(notebook, size=self.size, text_offset=self.text_offset,
                                             text=v)
            notebook.add(tab_frame)
            notebook.tab(i, text=k)

        self.quit = tk.Button(self, text='Cancel', command=lambda: self.callbacks['on_close'](window='help'))
        self.quit.grid(row=1, column=0)
        self.title(title)
        self.resizable(width=False, height=False)
        posX = position['x'] + self.window_offset['x']
        posY = position['y'] + self.window_offset['y']
        pos = '+{0}+{1}'.format(posX, posY)
        self.geometry(pos)


class ExporterView(tk.Toplevel):
    window_offset = {
        'x': 50,
        'y': 50
    }

    size = {
        'width': 400,
        'height': 400
    }

    text_offset = {
        'x': 10,
        'y': 10
    }

    def __init__(self, parent, title, export_fields: dict, position, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        self.export_notebook = ttk.Notebook(self, width=self.size['width'], height=self.size['height'])
        self.export_notebook.grid(row=0, column=0)
        self.export_notebook.rowconfigure(0, weight=1)
        self.export_notebook.columnconfigure(0, weight=1)

        self.export_frame = tk.Frame(self)
        self.export_frame.grid(row=0, column=0, sticky='NSEW')
        self.export_selector = w.LabelInput(self.export_frame, 'Name', field_spec=export_fields['types'])
        self.export_selector.set(export_fields['types']['values'][0])
        self.export_selector.grid(row=0, column=0)
        self.button_extract_data = tk.Button(self.export_frame, text='Extract Data', command=self.export_selected_data)
        self.button_extract_data.grid(row=1, column=0)

        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0)
        self.quit = tk.Button(button_frame, text='Cancel', command=lambda: self.callbacks['on_close'](window='export'))
        self.quit.grid(row=0, column=1)
        self.export_all = tk.Button(button_frame, text='Write all to CSVs', command=lambda: self.write_csv('all'))
        progress_frame = tk.LabelFrame(self, text='Progress')
        progress_frame.grid(row=2, column=0)
        self.progress_text = tk.StringVar()
        self.progress_text.set('')
        progress_text_label = tk.Label(self, textvariable=self.progress_text)
        progress_text_label.grid(row=2, column=0, sticky=tk.W+tk.E)
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=100)
        self.progress_bar.grid(row=3, column=0, sticky=tk.W+tk.E)
        self.title(title)
        self.resizable(width=True, height=True)
        posX = position['x'] + self.window_offset['x']
        posY = position['y'] + self.window_offset['y']
        pos = f'+{posX}+{posY}'
        self.geometry(pos)

        self.export_values = {}

    def update_exports(self, exports):
        self.export_values = exports

        for tab in reversed(range(0, len(self.export_notebook.tabs()))):
            self.export_notebook.forget(tab)

        for i, (k, v) in enumerate(self.export_values.items()):
            tab_frame = tk.Frame(self.export_notebook)
            tab_frame.rowconfigure(0, weight=1)
            tab_frame.columnconfigure(0, weight=1)
            self.export_notebook.add(tab_frame)
            self.export_notebook.tab(i, text=k)

            tab_text = w.ScrolledTextCanvas(tab_frame, size=self.size, text_offset=self.text_offset,
                                            text=v)
            tab_text.grid(row=0, column=0)

            button_frame = tk.Frame(tab_frame)
            button_frame.grid(row=1, column=0)
            tab_button = tk.Button(button_frame, text='Copy to clipboard', command=self.send_to_clipboard)
            tab_button.grid(row=0, column=0)
            tab_button = tk.Button(button_frame, text='Write tab to CSV', command=lambda: self.write_csv('tab'))
            tab_button.grid(row=0, column=1)

        self.export_all.grid(row=0, column=0)

        self.export_notebook.tkraise()

    def export_selected_data(self):
        self.button_extract_data['state'] = 'disabled'
        export_type = self.export_selector.get()
        if export_type == '':
            self.update_progress(0, 'No Export Value Selected...')
            return
        self.callbacks['on_export'](export_type=export_type)

    def send_to_clipboard(self):
        key = self.export_notebook.tab(self.export_notebook.select(), 'text')
        export = self.export_values[key]
        self.clipboard_clear()
        self.clipboard_append(export)
        print(f'sent {key} to clipboard')

    def update_progress(self, percent, text):
        self.progress_text.set(text)
        self.progress_bar['value'] = percent

    def write_csv(self, number):
        if number == 'all':
            to_csv = self.export_values
        else:
            tab_name = self.export_notebook.tab(self.export_notebook.select(), 'text')
            to_csv = {tab_name:  self.export_values[tab_name]}

        self.callbacks['on_write_to_csv'](to_csv)
