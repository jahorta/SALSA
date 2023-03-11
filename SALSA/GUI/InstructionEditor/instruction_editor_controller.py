import tkinter as tk

from GUI.InstructionEditor.instruction_editor_view import InstructionEditorView
from BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Common.constants import sep


class InstructionEditorController:

    def __init__(self, parent, name, inst_lib_facade: BaseInstLibFacade, callbacks):
        self.name = name

        view_callbacks = {
            'on_select_instruction': self.on_select_instruction,
            'save': self.on_save_changes,
            'set_change': self.add_change,
            'on_close': self.on_close,
            'check_locked': self.check_item_is_locked
        }
        self.view = InstructionEditorView(parent=parent, callbacks=view_callbacks)
        self.inst_lib = inst_lib_facade
        self.callbacks = callbacks

        self.cur_inst = None
        self.param_details = None
        self.changed_values = {}

        self.populate_instruction_tree()

    def populate_instruction_tree(self):
        headers = self.view.get_headers('instruction')
        entries = self.inst_lib.get_tree_entries(headers)
        self.populate_tree(self.view.inst_list_tree, headers, entries)

    def populate_tree(self, tree, headers, entries):
        for item in tree.get_children():
            tree.delete(item)

        for entry in entries:
            first = True
            values = []
            text = ''
            for header in headers:
                if first:
                    text = entry[header]
                    first = False
                    continue
                values.append(entry[header])
            kwargs = {'text': text, 'values': values}
            tree.insert(parent='', index='end', **kwargs)

    def on_select_instruction(self, newID):
        newID = int(newID)
        self.cur_inst = newID
        details = self.inst_lib.get_inst(newID)
        self.view.id_label.config(text=f'{details.instruction_id}')
        skip_type = 'Can skip frame advance after instruction'
        if details.no_new_frame:
            skip_type = 'Frame never advances after instruction'
        elif details.forced_new_frame:
            skip_type = 'Frame always advances after instruction'
        self.view.skip_label.config(text=f'{skip_type}')
        self.view.param2_label.config(text=f'{details.param2}')
        self.view.location_label.config(text=f'{details.location}')
        self.view.link_label.config(text=f'{details.link_type if details.link_type is not None else "None"}')
        self.view.loop_params_label.config(text=f'{details.loop if details.loop is not None else "None"}')
        if details.warning is None:
            self.view.no_warning.tkraise()
        else:
            self.view.warning_label.config(text=f'{details.warning if details.warning is not None else "None"}')
            self.view.warning_frame.tkraise()

        headers = self.view.get_headers('parameter')
        entries = self.inst_lib.get_tree_entries(headers=self.view.get_headers('parameter'), inst_id=newID)
        self.populate_tree(self.view.param_list_tree, headers, entries)

    def check_item_is_locked(self, item_code: list):
        self.inst_lib.check_locked([self.cur_inst, *item_code])

    def add_change(self, key, value):
        key = f'{self.cur_inst}{sep}{key}'
        self.changed_values[key] = value

    def has_changes_remaining(self):
        return len(self.changed_values) > 0

    def on_close(self):
        self.callbacks['close'](self.name, self)

    def ask_save_changes(self):
        pass

    def on_save_changes(self):
        pass