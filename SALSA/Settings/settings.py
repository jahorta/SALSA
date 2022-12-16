import os
import json

class Settings:
    defaults = {
        'previous_sct_file': '',
        'script_directory': './scripts/'
    }

    def __init__(self):
        self.filename = './Lib/settings.json'
        self.settings = self._load_settings()

    def _load_settings(self):

        if not os.path.exists(self.filename):
            self._new_settings_file()
        with open(self.filename, 'r') as fh:
            settings = json.loads(fh.read())

        for key, value in self.defaults.items():
            if key not in settings.keys():
                settings[key] = value

        return settings

    def _new_settings_file(self):
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