from Project.project_container import SCTScript, SCTSection, SCTInstruction, SCTParameter, SCTProject, SCTLink

classes_enc = [SCTScript, SCTSection, SCTInstruction, SCTParameter, SCTLink]


def dictize_project(project: SCTProject):
    proj_dict = project.__dict__
    proj_dict = dictize(proj_dict)
    return proj_dict


def dictize(item):
    dictized_item = {}
    item_type = type(item)
    if item_type in classes_enc:
        dictized_item = dictize(item.__dict__)
    elif isinstance(item, bytearray):
        dictized_item['obj_type'] = 'bytearray'
        dictized_item['data'] = item.hex()
    elif isinstance(item, dict):
        for key, value in item.items():
            dictized_item[key] = dictize(value)
    elif isinstance(item, list):
        dictized_item = []
        for value in item:
            dictized_item.append(dictize(value))
    else:
        dictized_item = item
    return dictized_item


def create_project_from_dict(proj_dict):
    return SCTProject.from_dict(proj_dict)
