import enum


class PP(enum.Enum):
    project = 0
    script = 1
    section = 2
    instruction = 3
    parameter = 4
    link = 5


class UP(enum.Enum):
    callable = 0
    arguments = 1


p_levels = [PP.project, PP.script, PP.section, PP.instruction, PP.parameter, PP.link]

p_attrs = {
    1: ['scripts', 'sections', 'instructions', 'parameters', 'link'],
    2: ['scts', 'sects', 'insts', 'params', 'link']
}

loop_attrs = {
    1: 'loop_parameters',
    2: 'loop_params'
}

nd_index = -1