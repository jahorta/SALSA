import tkinter as tk

from GUI.InstructionEditor.instruction_editor_view import InstructionEditorView
from BaseInstructions.base_instruction_facade import BaseInstLibFacade


class InstructionEditorController:

    def __init__(self, view, inst_lib_facade: BaseInstLibFacade, callbacks, position):

        self.view: InstructionEditorView = view
        self.inst_lib_facade = inst_lib_facade
        self.callbacks = callbacks

        # TODO - link callbacks for buttons and canvases as needed in view

    def on_select_instruction(self, newID):
        """Save the current instruction details to the current Instruction object"""
        pass

    def on_select_parameter(self, instID, prevID, newID):
        """Save current parameter details, then open selected parameter"""
        pass

    def on_instruction_commit(self, id):
        """Get most recent instruction and param changes"""
        pass

    def get_changes(self):
        pass

    def ask_save_changes(self):
        pass