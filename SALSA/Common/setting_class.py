import os
import configparser


class Settings(configparser.ConfigParser):
    defaults = {
        'DEFAULT': {}
    }

    def __init__(self):
        super().__init__()
        self.filename = './UserSettings/config.ini'
        self._load_settings()

    def _load_settings(self):
        if not os.path.exists(self.filename):
            self._new_settings_file()

        with open(self.filename, 'r') as configfile:
            self.read(configfile)

    def _new_settings_file(self):
        for name, group in self.defaults.items():
            self[name] = group
        with open(self.filename, 'w') as configfile:
            self.write(configfile)

    def _save_settings(self):
        with open(self.filename, 'w') as configfile:
            self.write(configfile)

    def set_setting(self, group, setting, value):
        self[group][setting] = value
        self._save_settings()


settings = Settings()
