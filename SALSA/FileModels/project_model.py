import json
import os.path

from Common.settings import settings


class ProjectModel:

    def __init__(self):
        self.set_key = 'ProjectModel'
        if self.set_key not in settings.keys():
            settings[self.set_key] = {}
        self.filepath = ""
        self.recent_files = []
        self.max_recents = 10
        self._load_recent_filelist()

    def load_project(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        if self.filepath == '':
            print('Unable to save file, no filepath')
            return
        if not os.path.exists(self.filepath):
            print('File does not exist')
            return

        settings[self.set_key]['directory'] = os.path.dirname(filepath)
        with open(self.filepath, 'r') as fh:
            proj_dict = json.loads(fh.read())

        self.add_recent_file(filepath=filepath)
        return proj_dict

    def save_project(self, proj_dict, filepath=None, indent=False):
        if filepath is not None:
            self.filepath = filepath

        with open(self.filepath, 'w') as fh:
            kwargs = {}
            if indent:
                kwargs['indent'] = 2
            fh.write(json.dumps(proj_dict, **kwargs))

    def get_project_directory(self):
        return settings[self.set_key].get('directory', None)

    def add_recent_file(self, filepath):
        if filepath in self.recent_files:
            file_index = self.recent_files.index(filepath)
            self.recent_files.pop(file_index)
        self.recent_files.insert(filepath, 0)
        if len(self.recent_files) > self.max_recents:
            self.recent_files.pop()
        self._save_recent_filelist()

    def _save_recent_filelist(self):
        for i in range(0, self.max_recents):
            key = f'recent_file_{i}'
            if i >= len(self.recent_files):
                if key in settings[self.set_key].keys():
                    settings[self.set_key].pop(key)
                continue
            cur_path = self.recent_files[i]
            settings[self.set_key][key] = cur_path

    def _load_recent_filelist(self):
        self.recent_files = []
        update_settings_recent = False
        for i in range(0, self.max_recents):
            key = f'recent_file_{i}'
            if key not in settings[self.set_key].keys():
                break
            filepath = settings[self.set_key].get(key, None)
            if filepath is None:
                break
            if not os.path.exists(filepath):
                print(f'Recent file {filepath} does not exist, skipping...')
                update_settings_recent = True
                continue
            self.recent_files.append(filepath)
        if update_settings_recent:
            self._save_recent_filelist()

    def load_recent(self, index):
        return self.load_project(self.recent_files[index])

