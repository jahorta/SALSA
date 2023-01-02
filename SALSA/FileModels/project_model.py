import json


class ProjectModel:

    def __init__(self):

        self.filepath = ""

    def set_filepath(self, filepath):
        self.filepath = filepath

    def load_project(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        if self.filepath == '':
            print('Unable to save file, no filepath')
            return
        with open(self.filepath, 'r') as fh:
            proj_dict = json.loads(fh.read())

        return proj_dict

    def save_project(self, proj_dict, indent=False):
        """Function to save instructions to file"""
        print("saving to file")

        with open(self.filepath, 'w') as fh:
            kwargs = {}
            if indent:
                kwargs['indent'] = 2
            fh.write(json.dumps(proj_dict, **kwargs))
