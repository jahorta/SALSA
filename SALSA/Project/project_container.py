import uuid
from itertools import count
from dataclasses import dataclass, field as dc_field
from typing import List, Union, Dict, Tuple


@dataclass
class SCTLink:
    type: str
    trace: List[Union[int, str]]
    origin: int
    target: int
    target_trace: Union[List[Union[int, str]], None] = None
    ID: int = dc_field(default_factory=lambda counter=count(): next(counter))

    def set_id(self, _id):
        self.ID = _id

    def __repr__(self):
        return f'Link: {self.ID} - {self.trace[0]}:{self.trace[1]}:{self.trace[2]}' \
               f'\n\torigin: {self.origin}, target: {self.target}'


class SCTParameter:

    value: Union[int, float, str, dict, bytearray, None]
    formatted_value: str
    raw_bytes: bytearray
    analyze_log: dict
    skip_refresh: bool
    link_value: (str, str)

    def __init__(self, _id, _type):
        self.ID = _id
        self.type = _type
        self.link: Union[None, SCTLink] = None
        self.errors = []
        self.analyze_log = {}
        self.value = None
        self.formatted_value = ''
        self.raw_bytes = bytearray(b'')
        self.link_result = ('',)

    def set_value(self, value: Union[int, float, str, dict, bytearray]):
        self.value = value
        self.formatted_value = self._unpack_result_dict(value, 0) if isinstance(value, dict) else str(value)

    def add_raw(self, raw: bytearray):
        self.raw_bytes += raw

    def add_error(self, error: str):
        self.errors.append(error)

    def set_param_log(self, log):
        self.analyze_log = log

    def get_param_as_tree(self):
        pass

    def _unpack_result_dict(self, cur_dict, level):
        returnValue = ''
        for key, value in cur_dict.items():
            if not isinstance(value, dict):
                formatedReturn = '\n'
                tabs = '  ' * level
                formatedReturn += tabs
                returnValue += f'{formatedReturn}{key}: {value}'
            else:
                nextLevel = self._unpack_result_dict(value, level + 1)
                formatedReturn = '\n'
                tabs = '  ' * level
                formatedReturn += tabs
                returnValue += f'{formatedReturn}{key}: {nextLevel}'
        return returnValue

    def __repr__(self):
        return f'{self.formatted_value}'

    @classmethod
    def from_dict(cls, param_dict, links):
        param = cls(param_dict['ID'], param_dict['type'])
        for link in links:
            if param_dict['link']['ID'] == link.ID:
                param.link = link
                break
        param.errors = param_dict['errors']
        param.analyze_log = param_dict['analyze_log']
        param.value = param_dict['value']
        param.formatted_value = param_dict['formatted_value']
        param.raw_bytes = bytearray.fromhex(param_dict['raw_bytes'])
        param.link_result = param_dict['link_result']
        return param


class SCTInstruction:
    desc_codes = ['add', 'sub', 'mul']

    errors: List[Tuple[str, Union[int, str, bytearray]]]
    links: List[SCTLink]
    parameters: Dict[int, SCTParameter]
    loop_parameters: List[Dict[int, SCTParameter]]

    def __init__(self, script_pos: int, inst_pos: int, inst_id: int):
        self.ID = str(uuid.uuid4()).replace('-', '_')
        self.inst_id = inst_id
        self.inst_pos = inst_pos
        self.script_pos = script_pos
        self.overall_pos = self.inst_pos + script_pos
        self.skip_refresh = False
        self.errors = []
        self.links = []
        self.parameters = {}
        self.loop_parameters = []

    def add_error(self, value: Tuple[str, Union[int, str, bytearray]]):
        self.errors.append(value)

    def add_parameter(self, param_id, param: SCTParameter):
        self.parameters[param_id] = param
        if len(param.errors) > 0:
            self.errors.append(('param', param_id))

    def add_loop_parameter(self, loop_param: Dict[int, SCTParameter]):
        self.loop_parameters.append(loop_param)
        for p_id, param in loop_param.items():
            if len(param.errors) > 0:
                self.errors.append((f'loop-{len(self.loop_parameters)-1}-param', p_id))

    def get_links(self):
        return self.links if len(self.links) > 0 else None

    def __repr__(self):
        return f'{self.inst_id}: {", ".join([_.__repr__() for _ in self.parameters])}'

    # def get_param_id_by_name(self, name):
    #     param_id = None
    #     for key, param in self.parameters.items():
    #         if param.name == name:
    #             param_id = key
    #             break
    #     return param_id

    def set_skip_refresh(self):
        self.skip_refresh = True

    @classmethod
    def from_dict(cls, inst_dict, links: List[SCTLink]):
        inst = cls(script_pos=inst_dict['script_pos'], inst_id=inst_dict['inst_id'], inst_pos=inst_dict['inst_pos'])
        inst.ID = inst_dict['ID']
        inst.skip_refresh = inst_dict['skip_refresh']
        inst.errors = inst_dict['errors']
        inst_links = {}
        inst_link_ids = [_['ID'] for _ in inst_dict['links']]
        for link in links:
            if link.ID in inst_link_ids:
                inst_links[link.ID] = link
        for ID in inst_link_ids:
            inst.links.append(inst_links[ID])
        for key, param in inst_dict['parameters'].items:
            inst.parameters[key] = SCTParameter.from_dict(param_dict=param, links=inst.links)
        for param_group in inst_dict['loop_parameters']:
            params = {}
            for key, param in param_group.items():
                params[key] = SCTParameter.from_dict(param_dict=param, links=inst.links)
            inst.loop_parameters.append(params)
        return inst


class SCTSection:

    instructions: List[SCTInstruction]
    instructions_grouped: Dict[str, Tuple[str, str]]
    type: str
    inst_errors: List[int]
    errors: List[str]
    strings: Dict[int, str]
    instructions_used: Dict[int, int]
    garbage: Dict[str, bytearray]

    def __init__(self, name, length, pos):
        self.name = name
        self.length = length
        self.start_offset = pos
        self.instructions = []
        self.instructions_grouped = {}
        self.inst_errors = []
        self.errors = []
        self.strings = {}
        self.instructions_used = {}
        self.garbage = {}
        self.string = ''
        self.jump_loops = []

    def add_string(self, pos: int, string: str):
        self.strings[pos] = string
        self.string = string

    def add_instruction(self, instruction: SCTInstruction):
        self.instructions.append(instruction)
        if instruction.inst_id not in self.instructions_used.keys():
            self.instructions_used[instruction.inst_id] = 0
        self.instructions_used[instruction.inst_id] += 1

    def set_type(self, t: str):
        self.type = t

    def add_error(self, e: str):
        self.errors.append(e)

    def add_garbage(self, key: str, value: bytearray):
        self.garbage[key] = value

    def add_loop(self, loop_id: int):
        self.jump_loops.append(loop_id)

    @classmethod
    def from_dict(cls, section_dict, links):
        section = cls(section_dict['name'], section_dict['length'], section_dict['start_offset'])
        for inst in section_dict['instructions']:
            section.instructions.append(SCTInstruction.from_dict(inst, links))
        section.instructions_grouped = section_dict['instructions_grouped']
        section.inst_errors = section_dict['inst_errors']
        section.errors = section_dict['errors']
        section.strings = section_dict['strings']
        section.instructions_used = section_dict['instructions_used']
        section.garbage = section_dict['garbage']
        section.string = section_dict['string']
        section.jump_loops = section_dict['jump_loops']
        return section


class SCTScript:
    start_pos = None

    special_addresses = {
        'bit': '0x80310bc',
        'byte': '0x80310a1c'
    }

    sections: Dict[str, SCTSection]
    section_groups: Dict[str, List[str]]
    section_group_keys: Dict[str, str]
    inst_locations: List[List[str]]
    links: List[SCTLink]
    footer: List[str]
    strings: Dict[str, str]
    error_sections: Dict[str, List[str]]
    links_to_sections: Dict[str, List[str]]
    unused_sections: List[str]

    def __init__(self, name: str, index: Union[None, Dict[str, Tuple[int, int]]] = None,
                 header: Union[None, bytearray] = None):
        self.name = name
        self.index = {k: v[0] for k, v in index.items()} if index is not None else {}
        self.header = header if header is not None else bytearray(b'/x07/xd2/x00/x06/x00/x0e/x00/x00')
        self.sections = {}
        self.section_groups = {}
        self.section_group_keys = {}
        self.grouped_section_names = {}
        self.inst_locations = [[] for _ in range(266)]
        self.links = []
        self.links_to_sections = {}
        self.footer = []
        self.strings = {}
        self.string_groups = {}
        self.unused_sections = []
        self.errors = []
        self.error_sections = {}

    def add_section(self, section: SCTSection):
        name = section.name
        self.sections[name] = section
        inst_list = self.sections[name].instructions_used.keys()
        for inst in inst_list:
            self.inst_locations[inst].append(name)
        if len(section.errors) > 0:
            self.error_sections[name] = section.errors

    def add_link(self, link: SCTLink) -> int:
        self.links.append(link)
        return len(self.links) - 1

    def add_footer_entry(self, entry):
        self.footer.append(entry)
        return len(self.footer) - 1

    @classmethod
    def from_dict(cls, script_dict):
        script = cls(name=script_dict['name'], index=script_dict['index'], header=script_dict['header'])
        for link in script_dict['links']:
            script.links.append(SCTLink(**link))
            script.links[-1].set_id(link['ID'])

        for key, value in script_dict['sections'].items():
            script.sections[key] = SCTSection.from_dict(value, script.links)
        script.section_groups = script_dict['section_groups']
        script.section_group_keys = script_dict['section_group_keys']
        script.grouped_section_names = script_dict['grouped_section_names']
        script.inst_locations = script_dict['inst_locations']
        script.links_to_sections = script_dict['links_to_sections']
        script.footer = script_dict['footer']
        script.strings = script_dict['strings']
        script.string_groups = script_dict['string_groups']
        script.unused_sections = script_dict['unused_sections']
        script.errors = script_dict['errors']
        script.error_sections = script_dict['error_sections']
        return script


class SCTProject:

    file_name: str
    scripts: Dict[str, SCTScript]

    def __init__(self):
        self.scripts = {}
        self.file_name = 'Untitled.prj'

    def add_script(self, filename: str, script: SCTScript):
        self.scripts[filename] = script

    @classmethod
    def from_dict(cls, proj_dict):
        project = cls()
        for key, script in proj_dict['scripts'].items():
            project.scripts[key] = SCTScript.from_dict(script)
        project.filename = proj_dict['file_name']
        return project