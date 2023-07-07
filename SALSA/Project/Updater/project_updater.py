import copy
from typing import Union

from SALSA.Common.constants import sep
from SALSA.Project.Updater.pu_constants import p_attrs, p_levels, UP, PP, loop_attrs, nd_index
from SALSA.Project.Updater.pu_definitions import update_tasks, p_max_depth
from SALSA.Project.project_container import SCTProject, SCTScript, SCTSection, SCTParameter, SCTInstruction, SCTLink


class ProjectUpdater:
    """Updates a SALSA project to the current version. It does so depth first, so the deepest changes occur first.
    Changes to links are handled by their respective parameters. Separate methods should be made to handle this"""

    log_key = 'PrjUpdater'

    @classmethod
    def update_project(cls, prj: SCTProject) -> SCTProject:
        updater = cls()
        while prj.version in update_tasks:
            prj = updater._upgrade_version(prj)
            prj.version += 1
        return prj

    def _upgrade_version(self, p_piece: Union[SCTProject, SCTScript, SCTSection, SCTParameter, SCTInstruction, SCTLink],
                         cur_version=None, p_level_ind=0, tasks=None):
        if cur_version is None:
            cur_version = p_piece.version
            print(f'{self.log_key}: Now updating project from version v{cur_version} to v{cur_version+1}')
        if tasks is None:
            tasks = update_tasks[p_piece.version]
        max_level = p_max_depth[cur_version]

        p_level = p_levels[p_level_ind]

        if p_level == PP.script:
            print(f'{self.log_key}: Now updating script: {p_piece.name}')

        if p_level == PP.section:
            print(f'{self.log_key}: Now updating section: {p_piece.name}', end='\r')

        if p_level != max_level and p_level_ind + 1 < len(p_levels):

            p_attr_name = p_attrs[cur_version][p_level_ind]
            child_entries = p_piece.__getattribute__(p_attr_name)

            not_dict = False
            if not isinstance(child_entries, dict):
                child_entries = {nd_index: child_entries}
                not_dict = True

            # Handle children
            updated_children = {}
            for child_key, child_piece in child_entries.items():
                if child_piece is not None:
                    child_piece = self._upgrade_version(p_piece=child_piece, cur_version=cur_version, p_level_ind=p_level_ind + 1, tasks=tasks)
                updated_children[child_key] = child_piece

            if not_dict:
                updated_children = updated_children[nd_index]

            p_piece.__setattr__(p_attr_name, updated_children)

        # Handle loop parameters of instructions since those won't be captured by the other recursive section above
        if p_level == PP.instruction and p_level != max_level:
            loop_params = []
            loop_attr_name = loop_attrs[cur_version]
            for loop in p_piece.__getattribute__(loop_attr_name):
                new_loop = {}
                for param_id, param in loop.items():
                    param = self._upgrade_version(p_piece=param, cur_version=cur_version,
                                                  p_level_ind=p_level_ind + 1, tasks=tasks)
                    new_loop[param_id] = param
                loop_params.append(new_loop)
            p_piece.__setattr__(loop_attr_name, loop_params)

        if p_level in tasks:
            for task_num, task in tasks[p_level].items():
                args: list = [p_piece] + task.get(UP.arguments, [])
                p_piece = self.__getattribute__(task[UP.callable])(*args)

        if p_level == PP.script:
            print(f'{self.log_key}: Finished updating script: {p_piece.name}')

        return p_piece

    @staticmethod
    def _retype_link_v1(cur_piece):
        if cur_piece.link is None:
            return cur_piece

        if getattr(cur_piece, 'link_value', None) is None:
            return cur_piece

        if cur_piece.link_value[0] == 'Footer':
            cur_piece.link.type = 'Footer'

        return cur_piece

    @staticmethod
    def _del_attr(cur_piece, *attrs):
        for attr in attrs:
            if attr in cur_piece.__dict__:
                cur_piece.__delattr__(attr)
        return cur_piece

    @staticmethod
    def _change_attribute_names(cur_piece, *changes):
        for change in changes:
            old_attr = change[0]
            if old_attr in cur_piece.__dict__:
                new_attr = change[1]
                setattr(cur_piece, new_attr, getattr(cur_piece, old_attr))
                cur_piece.__delattr__(old_attr)
        return cur_piece

    # ------------------------- #
    # Script specific functions #
    # ------------------------- #

    @staticmethod
    def _modify_section_groups_v1(cur_piece: SCTScript):
        changes = {}
        for i, entry in enumerate(cur_piece.sect_tree):
            if not isinstance(entry, dict):
                continue
            new_entry = {}
            for k, v in entry.items():
                if k == v[0]:
                    new_entry[f'{k}{sep}group'] = v[1:]
            changes[i] = new_entry
        for pos, entry in changes.items():
            cur_piece.sect_tree.pop(pos)
            cur_piece.sect_tree.insert(pos, entry)
        return cur_piece

    @staticmethod
    def _move_string_garbage_v1(cur_piece: SCTScript):
        cur_piece.string_garbage = {}
        for name, sect in cur_piece.string_sections.items():
            if 'end' in sect.garbage:
                cur_piece.string_garbage[name] = sect.garbage
        cur_piece.__delattr__('string_sections')
        return cur_piece

    @staticmethod
    def _move_sect_labels_v1(cur_piece: SCTSection):
        if len(cur_piece.internal_sections_inst) == 0:
            labels = [cur_piece.name]
        else:
            labels, poses = [k for k in cur_piece.internal_sections_inst.keys()], [v for v in cur_piece.internal_sections_inst.values()]
            poses, labels = zip(*sorted(zip(poses, labels)))
            labels = list(labels)
        for inst in cur_piece.insts.values():
            if inst.base_id == 9:
                if len(labels) == 0:
                    inst.label = '??Unknown??'
                else:
                    inst.label = labels.pop(0)
        return cur_piece


if __name__ == '__main__':
    import os
    cur_dir = os.path.dirname(__file__)
    os.chdir(cur_dir)
    os.chdir(os.path.pardir)
    os.chdir(os.path.pardir)
    os.chdir(os.path.pardir)
    from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
    from SALSA.FileModels.project_model import ProjectModel
    from SALSA.Scripts.script_encoder import SCTEncoder
    os.chdir(cur_dir)

    model = ProjectModel()
    project = model.load_project(filepath=os.path.join('./test', 'test_UwU v1.prj'), ignore_dir=True)
    if getattr(project, 'version', None) is None:
        project.version = 1

    # # Only check the first script?
    # project_first_script_name = list(project.scripts.keys())[0]
    # project.scripts = {project_first_script_name: project.scripts[project_first_script_name]}

    project = ProjectUpdater.update_project(project)

    base_insts = BaseInstLibFacade()
    for script in project.scts.values():
        sct = SCTEncoder.encode_sct_file_from_project_script(project_script=script, base_insts=base_insts)

    print('Success...')
