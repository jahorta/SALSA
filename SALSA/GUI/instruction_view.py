import tkinter as tk
from tkinter import ttk

from SALSA.GUI import widgets as w


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
        selected_ids = self.treeview.selection()
        if len(selected_ids) == 0:
            return
        selected_id = selected_ids[0]
        if self.currentID == selected_id:
            return
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

