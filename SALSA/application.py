import copy
import datetime
import json
import os
import queue
import re
import threading
import tkinter as tk
from math import floor
from pathlib import Path
from threading import Timer
from tkinter import ttk, messagebox, filedialog

from SALSA.GUI import views as v
from SALSA.Tools.SALSA_strings import HelpStrings
from SALSA.Tools.exporter import SCTExporter
from SALSA.Tools.instruction_class import Instruct
from SALSA.FileModels.instruction_model import InstructionModel
from SALSA.Tools.script_class import SCTAnalysis
from SALSA.FileModels.sct_model import SctModel


class Application(tk.Tk):
    """Controls the links between the data models and views"""
    test = True
    title_text = "Skies of Arcadia Legends - Script Assistant"
    about_text = f'{title_text}\nby: Jahorta\n2021'
    default_sct_file = 'me005b.sct'
    export_thread: threading.Thread

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
            'on_close': self.about_window_close,
            'on_write_to_csv': self.export_as_csv
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
        self.export_type = ''
        self.script_exports = {}
        self.export_script_names = []
        self.queue_to_exporter: queue.Queue = queue.Queue()
        self.queue_from_exporter: queue.Queue = queue.Queue()
        self.export_start_time = None

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
        self.script_exports = []
        self.export_type = ''
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}
        self.export_window = v.ExporterView(parent=self, title='Export',
                                            export_fields=self.exporter.get_export_fields(), position=position,
                                            callbacks=self.exporter_callbacks)

    # Called when asked to export data
    def on_data_export(self, export_type='Ship battle turn data'):
        print('exporting data')
        self.export_start_time = datetime.datetime.now()
        self.script_exports = {}
        args = self.exporter.get_export_args(export_type)
        relevant_script_regex = args.get('scripts', None)
        split_by_sct = args.get('split_by_sct', False)
        self.export_script_names = []
        script_paths = Path(self.script_dir).glob('**/*')
        total_scripts = 0
        print('export path:', self.script_dir)
        for path in script_paths:
            total_scripts += 1
            print(f'testing {path.name} for pattern {relevant_script_regex}')
            if re.search(relevant_script_regex, path.name):
                self.export_script_names.append(path.name)

        print(total_scripts, 'scripts in directory')
        print(len(self.export_script_names), 'scripts selected for export')
        self.export_type = export_type

        # Start a background thread
        self.export_thread = threading.Thread(target=self.perform_script_analysis)
        self.export_thread.start()

        if split_by_sct:
            # Add script names to the queue for the export thread
            script_num = len(self.export_script_names)
            for i, script in enumerate(self.export_script_names):
                    pkg = {'index': i + 1, 'script': script, 'script_num': script_num}
                    self.queue_to_exporter.put(pkg)
        else:
            pkg = {'index': 1, 'script_list': self.export_script_names, 'script_num': len(self.export_script_names)}
            self.queue_to_exporter.put(pkg)

        # After adding all script names, add a signal that exporting is finished
        self.queue_to_exporter.put({'done': True})

        # Start polling for completed analyses
        self.add_analysis_to_export()

    def perform_script_analysis(self):
        done = False
        while not done:
            # Get the next package of script information
            in_pkg = self.queue_to_exporter.get()
            self.queue_to_exporter.task_done()

            # Check if no more analyses to perform
            if 'done' not in in_pkg.keys():
                i = in_pkg['index']
                script_num = in_pkg['script_num']
                if 'script_list' in in_pkg.keys():
                    sct_list = in_pkg['script_list']
                    scripts = []
                    for sct in sct_list:
                        new_sct_analysis = SCTAnalysis(self.sctModel.load_sct(insts=self.instructionSet, file=sct))
                        print(f'{sct} analyzed: {i}/{script_num}')
                        progress = floor((i / script_num) * 100)
                        self.export_window.update_progress(progress, f'{sct} analyzed: {i}/{script_num}')
                        i += 1
                        scripts.append(new_sct_analysis)
                    new_sct_export = self.exporter.export(sct_list=scripts,
                                                          instruction_list=self.instructionSet,
                                                          export_type=self.export_type)
                    out_pkg = {'analysis': new_sct_export}
                    self.queue_from_exporter.put(out_pkg)
                    self.queue_from_exporter.put({'done': True})
                else:
                    sct = in_pkg['script']
                    new_sct_analysis = SCTAnalysis(self.sctModel.load_sct(insts=self.instructionSet, file=sct))
                    print(f'{sct} analyzed: {i}/{script_num}')
                    new_sct_export = self.exporter.export(sct_list=[new_sct_analysis], instruction_list=self.instructionSet,
                                                          export_type=self.export_type)
                    out_pkg = {'analysis': new_sct_export}
                    self.queue_from_exporter.put(out_pkg)
            else:
                done = True

    def add_analysis_to_export(self):
        script_num = len(self.export_script_names)
        done = False
        if not self.queue_from_exporter.empty():
            in_pkg = self.queue_from_exporter.get()
            self.queue_from_exporter.task_done()
            if 'done' in in_pkg.keys():
                done = True
            else:
                self.script_exports = {**self.script_exports, **in_pkg['analysis']}
                progress = floor(((len(self.script_exports)) / script_num) * 100)
                self.export_window.update_progress(progress, f'{list(in_pkg["analysis"].keys())[0]} analyzed: '
                                                             f'{len(self.script_exports)}/{script_num}')

        if len(self.script_exports) >= script_num or done:
            print('All exports completed:', len(self.script_exports), '/', script_num)
            self.export_window.update_exports(self.script_exports)
            self.export_thread.join()
            d_time = datetime.datetime.now() - self.export_start_time
            d = {"days": d_time.days}
            d["hours"], rem = divmod(d_time.seconds, 3600)
            d["minutes"], d["seconds"] = divmod(rem, 60)
            time_difference = "{days} days {hours}:{minutes}:{seconds}".format(**d)
            print('Time to complete export: ', time_difference)
            self.export_window.update_progress(100, f'All scripts analyzed!')
        else:
            self.after(100, self.add_analysis_to_export)

    def export_as_csv(self, csv_dict):
        if len(csv_dict) > 1:
            title = 'Export all to CSV'
        elif len(csv_dict) == 1:
            key = list(csv_dict.keys())[0]
            title = f'Export {key} to CSV'
        else:
            title = 'CSV Write Error'
            body = 'CSV dict has no entries'
            tk.messagebox.showerror(title=title, message=body)
            return
        out_dir = tk.filedialog.askdirectory(parent=self, title=title, mustexist=True)
        if not os.path.exists(out_dir):
            title = 'CSV Write Error'
            body = 'CSV dict has no entries'
            tk.messagebox.showerror(title=title, message=body)
        for key, csv in csv_dict.items():
            key += '.csv'
            filename = os.path.join(out_dir, key)
            with open(filename, 'w', encoding='shiftjis') as fh:
                fh.write(csv)

    # Called when a file is selected
    def on_file_select(self):
        """Initialize the file select window"""
        file_path = self.script_dir
        position = {'x': self.winfo_x(), 'y': self.winfo_y()}

        self.file_select = v.FileSelectView(self, self.file_select_last_selected, self.file_select_scalebar_pos,
                                            position, file_path, self.file_select_callbacks)
        self.file_select.populate_files(file_path)
        t = Timer(0.01, self.set_file_select_scrollbar)
        t.start()

    def set_file_select_scrollbar(self):
        self.file_select.file_select_tree.yview_moveto(self.file_select_scalebar_pos)

    def on_quit(self):
        """Check for unsaved changes, prompt to save, quit"""
        currentID = self.InstructionFrame.get_current_inst_details()['Instruction ID']
        self.on_instruction_commit(currentID)
        self.settings.save_settings()
        self.quit()

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

    def about_window_close(self, window):
        if window == 'help':
            self.help_window.destroy()
        elif window == 'export':
            self.export_window.destroy()

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
