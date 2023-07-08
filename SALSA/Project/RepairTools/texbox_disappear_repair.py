import os.path
from tkinter.filedialog import askdirectory, askopenfile

from BaseInstructions.bi_facade import BaseInstLibFacade
from FileModels.sct_model import SCTModel
from Project.project_container import SCTProject
from Scripts.script_decoder import SCTDecoder


class TBStringToParamRepair:

    @classmethod
    def repair_project(cls, project: SCTProject, inst_lib: BaseInstLibFacade, sct_model: SCTModel):

        directory = askdirectory(title='Where are the scripts located?', initialdir=sct_model.get_default_directory())

        prj_repair = cls()
        missing_files = prj_repair.check_sct_files_exist(directory, list(project.scts.keys()))

        if len(missing_files) > 0:
            print('Some script files were missing from the chosen directory:')
            for file in missing_files:
                print(f'\t{file}')

        sct_model.set_default_directory(directory)

        for name, script in project.scts.items():
            print(f'Repairing script: {name}')
            _, sct = sct_model.read_sct_file(f'{name}.sct')
            dec_script = SCTDecoder.decode_sct_from_file(name, sct, inst_lib, strings_only=True)
            for sect in script.sects.values():
                for inst in sect.insts.values():
                    if inst.base_id not in (144, 155):
                        continue
                    if inst.base_id == 144:
                        linked_str = inst.params[0].linked_string
                    else:
                        linked_str = inst.params[1].linked_string
                    if linked_str in dec_script.sects:
                        if '\\c' in dec_script.sects[linked_str].string:
                            if inst.params[1].value != 'decimal: 1+0/256':
                                inst.params[1].set_value('decimal: 1+0/256')

        return project

    @staticmethod
    def check_sct_files_exist(directory, files) -> list:
        missing_script_files = []
        for script in files:
            if not os.path.exists(os.path.join(directory, f'{script}.sct')):
                missing_script_files.append(script)
        return missing_script_files
