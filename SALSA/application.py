import copy
import json
import os
import tkinter as tk
from math import floor
import threading
import multiprocessing
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import re
import queue

from SALSA import views as v
from SALSA.SALSA_strings import HelpStrings
from SALSA.exporter import SCTExporter
from SALSA.script_class import SCTAnalysis
from SALSA.instruction_class import Instruct
from SALSA.sct_model import SctModel
from SALSA.instruction_model import InstructionModel


class Application(tk.Tk):
    """Controls the links between the data models and views"""
    test = True
    title_text = "Skies of Arcadia Legends - Script Assistant"
    about_text = f'{title_text}\nby: Jahorta\n2021'
    default_sct_file = 'me005b.sct'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load settings
        self.settings = Settings()
        if self.settings.get_sct_file() == '':
            self.settings.set_sct_file(self.default_sct_file)
        else:
            self.default_sct_file = self.settings.get_sct_file()
            self.file_select_last_selected = self.default_sct_file
        self.script_dir = self.settings.get_script_dir()

        # Prepping an sct model
        self.sctModel = SctModel(self.script_dir)
        self.sctAnalysis = None
        self.sctDisplayNew = True
        self.activeFile = self.default_sct_file

        # Reading in and setting up the initial instructions
        self.instModel = InstructionModel()
        instDict = self.instModel.load_instructions()
        self.instructionSet = {}
        for key in instDict.keys():
            self.instructionSet[key] = Instruct(instDict[key])

        self.storedInstructionSet = copy.deepcopy(self.instructionSet)

        # Define callbacks for the different views
        self.instruction_callbacks = {
            'on_select_instruction': self.on_select_instruction,
            'on_instruction_commit': self.on_instruction_commit,
            'on_select_parameter': self.on_select_parameter,
            'on_parameter_num_change': self.on_param_num_change
        }
        self.menu_callbacks = {
            'file->script_dir': self.set_script_directory,
            'file->select': self.on_file_select,
            'file->quit': self.on_quit,
            'file->export_data': self.on_create_export_window,
            'view->sct': self.on_move_to_sct,
            'view->inst': self.on_move_to_inst,
            'help->debug': self.on_print_debug,
            'help->help': self.show_help,
            'help->about': self.on_help_about,
            'help->instruction': self.on_help_inst,
            'help->notes': self.on_help_notes
        }
        self.file_select_callbacks = {
            'on_quit': self.file_select_on_quit,
            'on_load': self.on_move_to_sct
        }
        self.about_window_callbacks = {
            'on_close': self.about_window_close
        }
        self.script_callbacks = {
            'on_script_display_change': self.on_script_display_change,
            'on_instruction_display_change': self.on_instruction_display_change,
            'on_select_script': self.on_select_script,
            'on_select_script_instruction': self.on_select_script_instruction,
            'on_set_inst_start': self.on_set_inst_start
        }
        self.exporter_callbacks = {
            'on_export': self.on_data_export,
            'on_close': self.on_export_window_destroy
        }

        # Initialize popup window variables
        self.file_select_scalebar_pos = '0.00'
        self.file_select = None
        self.help_window = None

        # Setup window parameters
        self.title(self.title_text)
        self.resizable(width=True, height=True)
        style = ttk.Style(self)
        style.map("Treeview", background=[('selected', 'focus', 'blue'), ('selected', '!focus', 'blue')])

        # Implement Menu
        menu = v.MainMenu(self, self.menu_callbacks)
        self.config(menu=menu)

        # Load help strings
        self.help = HelpStrings()

        # Setup script parsing view
        self.ScriptFrame = v.ScriptView(self, self.script_callbacks)
        self.ScriptFrame.grid(row=0, column=0, sticky='NEWS')

        # Initialize instruction edit view
        self.InstructionFrame = v.InstructionView(self, self.instModel.fields,
                                                  self.instModel.parameter_model.getAllFields(),
                                                  self.instruction_callbacks, self.instructionSet)
        self.InstructionFrame.grid(row=0, column=0, sticky='NEWS')
        self.populate_instructions(self.instructionSet)
        self.InstructionFrame.tkraise()
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

        # print(self.geometry())
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # initializing exporter
        self.export_window = None
        self.exporter = SCTExporter()
        self.exporter_out: dict = {}
        self.scriptAnalyses = {}
        self.export_type = ''
        self.bind('<<sct_analyzed>>', self.update_export_progress)
        self.scts_analyzed = 0
        self.script_num = 0
        self.script_analysis_queue = queue.Queue()
        self.update_export_queue = queue.Queue()

    def on_select_instruction(self, newID):
        """Save the current instruction details to the current Instruction object"""
        prevInstDetails = self.InstructionFrame.get_current_inst_details()

        prevID = prevInstDetails['Instruction ID']
        self.instructionSet[prevID].set_inst_only(prevInstDetails)
        prevParamDetails = self.InstructionFrame.get_param_fields()
        if not 'inactive' in prevParamDetails:
            paramID = prevParamDetails['ID']
            self.instructionSet[prevID].parameters[paramID].set_parameter_details(prevParamDetails)

        """Update the view with the new instructions and details"""
        self.InstructionFrame.update_instructions(instructions=self.instructionSet, instID=newID)
        self.InstructionFrame.set_instruction_fields()
        self.populate_instructions(self.instructionSet)
        self.populate_parameters(-1)

    def on_select_parameter(self, instID, prevID, newID):
        """Save current parameter details, then open selected parameter"""
        if not prevID == '':
            prevParamDetails = self.InstructionFrame.get_param_fields()
            self.instructionSet[instID].parameters[prevID].set_parameter_details(prevParamDetails)

        self.InstructionFrame.update_instructions(self.instructionSet, instID)
        self.InstructionFrame.set_param_fields(newID)
        self.populate_parameters(-1)

    def on_instruction_commit(self, id):
        """Get most recent instruction and param changes"""
        self.on_select_instruction(id)
        currentInsts = {}
        for key, value in self.instructionSet.items():
            currentInsts[key] = value.get_all()

        self.instModel.save_instructions(currentInsts)
        self.storedInstructionSet = self.instModel.load_instructions()

    def on_create_export_window(self):
        self.exporter = SCTExporter()
        self.exporter_out: dict = {}
        # TODO - test for changes to instruction set to determine whether to redo analyses
        self.scriptAnalyses = {}
        self.export_type = ''
        self.script_num = 0
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}
        self.export_window = v.ExporterView(parent=self, title='Export',
                                            export_fields=self.exporter.get_export_fields(), position=position,
                                            callbacks=self.exporter_callbacks)

    # Called when asked to export data
    def on_data_export(self, export_type='Ship battle turn data'):
        relevant_script_regex = self.exporter.get_export_scripts(export_type)
        script_name_list = []
        script_paths = Path(self.script_dir).glob('**/*')
        for path in script_paths:
            if re.search(relevant_script_regex, path.name):
                script_name_list.append(path.name)
        self.export_type = export_type
        self.scts_analyzed = 0
        self.script_num = len(script_name_list)
        for script in script_name_list:
            self.script_analysis_queue.put(script)
        t = threading.Thread(target=self.run_script_analysis_worker, daemon=True)
        t.start()

    def run_script_analysis_worker(self):
        insts = self.instructionSet
        sct_dir = self.script_dir
        my_sct_model = SctModel(sct_dir)
        while not self.script_analysis_queue.empty():
            try:
                sct = self.script_analysis_queue.get()
            except queue.Empty:
                break
            new_sct_analysis = SCTAnalysis(my_sct_model.load_sct(insts=insts, file=sct))
            self.scriptAnalyses[new_sct_analysis.Name] = new_sct_analysis
            # print(f'{sct} analyzed')
            self.script_analysis_queue.task_done()
            self.update_export_queue.put(new_sct_analysis.Name)
            self.event_generate('<<sct_analyzed>>', when='tail')

    def update_export_progress(self, evt):
        sct_name = self.update_export_queue.get()
        self.scts_analyzed += 1
        progress = floor((self.scts_analyzed / self.script_num) * 100)
        self.export_window.update_progress(percent=progress,
                                           text=f'{sct_name} analyzed: {self.scts_analyzed}'
                                                f'/{self.script_num}')
        self.update_export_queue.task_done()
        self.update()
        if self.scts_analyzed == self.script_num:
            self.export_data()

    def export_data(self):
        sorted_keys = sorted(self.scriptAnalyses.keys())
        sorted_scts = []
        for key in sorted_keys:
            sorted_scts.append(self.scriptAnalyses[key])
        self.exporter_out = self.exporter.export(sct_list=sorted_scts,
                                                 instruction_list=self.instructionSet,
                                                 export_type=self.export_type)
        self.export_window.update_exports(self.exporter_out)

    def on_export_window_destroy(self):
        self.export_window.destroy()

    # Called when a file is selected
    def on_file_select(self):
        """Initialize the file select window"""
        file_path = self.script_dir
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}

        self.file_select = v.FileSelectView(self, self.file_select_last_selected, self.file_select_scalebar_pos,
                                            position, file_path, self.file_select_callbacks)
        self.file_select.populate_files(file_path)
        t = threading.Timer(0.01, self.set_file_select_scrollbar)
        t.start()

    def set_file_select_scrollbar(self):
        self.file_select.file_select_tree.yview_moveto(self.file_select_scalebar_pos)

    def on_quit(self):
        """Check for unsaved changes, prompt to save, quit"""
        currentID = self.InstructionFrame.get_current_inst_details()['Instruction ID']
        self.on_instruction_commit(currentID)
        self.settings.save_settings()
        quit()

    def get_changes(self):
        changes = set({})
        for key in self.instructionSet.keys():
            if not self.instructionSet[key].is_same_as(self.storedInstructionSet[key]):
                changes.add(key)
        return changes

    def ask_save_changes(self):
        changes = self.get_changes()
        if len(changes) > 0:
            text = 'The following instruction IDs have unsaved changes:\n' \
                   '{0}\n' \
                   'Would you like to save these changes?'.format(changes)
            message = tk.messagebox.askyesno('Commit Changes?', text)
            if message:
                currentID = self.InstructionFrame.get_current_inst_details()['Instruction ID']
                self.on_instruction_commit(currentID)

    def on_move_to_sct(self, file=None, scalebarPos=None):
        if scalebarPos is not None:
            self.file_select_scalebar_pos = scalebarPos

        if file is not None:
            self.file_select_last_selected = self.activeFile = file

        print('File Loaded')
        currentID = self.InstructionFrame.get_current_inst_details()['Instruction ID']
        self.on_instruction_commit(currentID)
        try:
            sct_dict = self.sctModel.load_sct(insts=self.instructionSet, file=self.activeFile)
        except FileExistsError as e:
            err_msg = tk.Message(self, text=e)
            return
        # if using sctAnalysis
        else:
            if file is None:
                self.settings.set_sct_file(self.default_sct_file)
            else:
                self.settings.set_sct_file(file)
            if sct_dict is None:
                print('No Script file loaded')
                return
            self.sctAnalysis = SCTAnalysis(sct_dict)
            sct_view_info = self.sctAnalysis.get_sct_info()
            sct_tree = self.sctAnalysis.get_script_tree()
            self.ScriptFrame.display_script_analysis_new(sct_view_info, sct_tree)
        self.ScriptFrame.tkraise()
        """ TODO - If no sct file has been loaded, ask for the user to select one, 
        else re-decode using the new instructions"""

    def on_move_to_inst(self):
        self.InstructionFrame.tkraise()

    def populate_instructions(self, insts):
        self.InstructionFrame.populate_instructions(insts)

    def populate_parameters(self, paramNum=-1):
        self.InstructionFrame.populate_parameters(paramNum)

    def on_param_num_change(self, instID, newParamNum, paramPos=None):
        self.instructionSet[instID].adjust_parameter_number(newParamNum, paramPos)
        self.InstructionFrame.update_instructions(self.instructionSet, instID)
        self.populate_parameters(newParamNum)

    def file_select_on_quit(self):
        """called when file select menu is closed"""
        # print('trying to remove window....')
        self.file_select.destroy()

    def on_set_inst_start(self, start, newID):
        self.sctAnalysis.set_inst_start(start)
        if not newID is None:
            instruct_dict = self.sctAnalysis.get_instruction_tree(newID)
            self.ScriptFrame.populate_instructions(instruct_dict, None)
        self.ScriptFrame.set_instruction_detail_fields(details=None, mode='reset')

    def on_select_script(self, newID):
        script_dict = self.sctAnalysis.get_script_tree()
        if not newID is None:
            instruct_dict = self.sctAnalysis.get_instruction_tree(newID)
            self.ScriptFrame.populate_instructions(instruct_dict, None)
        self.ScriptFrame.populate_scripts(script_dict)
        self.ScriptFrame.set_instruction_detail_fields(details=None, mode='reset')

    def on_select_script_instruction(self, scriptID, instructID):
        if scriptID is None:
            return
        instruct_dict = self.sctAnalysis.get_instruction_tree(scriptID)
        self.ScriptFrame.populate_instructions(instruct_dict, instructID)
        if instructID is None:
            return
        instruct_details = self.sctAnalysis.get_instruction_details(scriptID, instructID)
        self.ScriptFrame.set_instruction_detail_fields(details=instruct_details, mode='set')

    def on_script_display_change(self, mode):
        script_dict = self.sctAnalysis.get_script_tree(mode)
        self.ScriptFrame.populate_scripts(script_dict)
        self.ScriptFrame.populate_instructions(None, None)
        self.ScriptFrame.set_instruction_detail_fields(details=None, mode='reset')

    def on_instruction_display_change(self, scriptID, mode):
        instruct_dict = self.sctAnalysis.get_instruction_tree(scriptID, mode)
        self.ScriptFrame.populate_instructions(instruct_dict, None)
        self.ScriptFrame.set_instruction_detail_fields(details=None, mode='reset')

    def on_print_debug(self):
        print(f'\nWindow Dimensions:\nHeight: {self.winfo_height()}\nWidth: {self.winfo_width()}')

    def on_help_about(self):
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}
        self.help_window = v.HelpPopupView(self, 'About', self.about_text, position, self.about_window_callbacks)

    def on_help_inst(self):
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}
        self.help_window = v.HelpPopupView(self, 'Instruction Details', HelpStrings.instruction_descriptions,
                                           position, self.about_window_callbacks)

    def on_help_notes(self):
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}
        self.help_window = v.HelpPopupView(self, 'Other Notes', HelpStrings.other_notes,
                                           position, self.about_window_callbacks)

    def about_window_close(self):
        self.help_window.destroy()

    def set_script_directory(self):
        dir = tk.filedialog.askdirectory()
        self.settings.set_script_dir(dir)
        self.script_dir = dir
        self.sctModel = SctModel(self.script_dir)

    def show_help(self):
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}
        self.help_window = v.TabbedHelpPopupView(self, 'Help', self.help.get_all(),
                                                 position, self.about_window_callbacks)


class Settings:
    filename = './Lib/settings.json'
    defaults = {
        'previous_sct_file': '',
        'script_directory': './scripts/'
    }

    def __init__(self):
        self.settings = self.__load_settings()

    def __load_settings(self):

        if not os.path.exists(self.filename):
            self.__new_settings_file()
        with open(self.filename, 'r') as fh:
            settings = json.loads(fh.read())

        for key, value in self.defaults.items():
            if key not in settings.keys():
                settings[key] = value

        return settings

    def __new_settings_file(self):
        with open(self.filename, 'w') as fh:
            fh.write(json.dumps(self.defaults))

    def save_settings(self):
        with open(self.filename, 'w') as fh:
            fh.write(json.dumps(self.settings, indent=2))

    def set_sct_file(self, file):
        self.settings['previous_sct_file'] = file
        self.save_settings()

    def get_sct_file(self):
        return self.settings['previous_sct_file']

    def set_script_dir(self, dir):
        self.settings['script_directory'] = dir
        self.save_settings()

    def get_script_dir(self):
        return self.settings['script_directory']
