from Project.project_container import SCTScript, SCTSection, SCTInstruction, SCTParameter, SCTProject, SCTLink

classes_enc = [SCTScript, SCTSection, SCTInstruction, SCTParameter, SCTLink]


def jsonize_project(project: SCTProject):
    proj_dict = project.__dict__
    json_proj = jsonize(proj_dict)
    return json_proj


def jsonize(item):
    jsonized_item = {}
    item_type = type(item)
    if item_type in classes_enc:
        jsonized_item = jsonize(item.__dict__)
    elif isinstance(item, dict):
        for key, value in item.items():
            jsonized_item[key] = jsonize(value)
    elif isinstance(item, list):
        jsonized_item = []
        for value in item:
            jsonized_item.append(jsonize(value))
    elif isinstance(item, bytearray):
        jsonized_item = item.hex()
    else:
        jsonized_item = item
    return jsonized_item


def create_project_from_json(json_proj):
    return SCTProject.from_dict(json_proj)