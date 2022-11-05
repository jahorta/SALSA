import re
import tkinter as tk
from threading import Timer
from tkinter import ttk

from SALSA.GUI import widgets as w
from SALSA.Tools.constants import FieldTypes as FT


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

    script_start_field = {'req': False, 'type': FT.hex, 'pattern': '^8[0-9,a-f]{7}$'}

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
        self.has_start_addr = False

        self.script_file_create_breakpoints = tk.Button(scriptDisplayTop, text='Create Breakpoints', command=self.create_breakpoints)
        self.script_file_create_breakpoints.grid(row=1, column=3)

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

        is_hex = re.search('^0x8[0-9,a-f]{7}$', start) is not None or re.search('^8[0-9,a-f]{7}$', start) is not None
        if not is_hex:
            return

        self.callbacks['on_set_inst_start'](start, self.current_script_id)
        self.has_start_addr = True

    def create_breakpoints(self):
        if not self.has_start_addr:
            return

        self.callbacks['create_breakpoint'](self.current_script_id)


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

