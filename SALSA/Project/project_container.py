import uuid
from itertools import count
from dataclasses import dataclass, field as dc_field
from typing import List, Union, Dict, Tuple

from SALSA.Common.constants import sep, uuid_sep
from SALSA.Scripts import scpt_condition_changes as cond_changes


@dataclass
class SCTLink:
    type: str  # Available types: Jump, Switch, String
    origin: int
    origin_trace: List[Union[int, str]]
    target: int
    target_trace: Union[List[Union[int, str]], None] = None
    ID: int = dc_field(default_factory=lambda counter=count(): next(counter))

    def set_id(self, _id):
        self.ID = _id

    def __repr__(self):
        return f'Link: {self.ID} - {self.origin_trace[0]}:{self.origin_trace[1]}:{self.origin_trace[2]}' \
               f'\n\torigin: {self.origin}, target: {self.target}'

    def __eq__(self, other_link):
        if self.type != other_link.type:
            return False
        for i, element in enumerate(self.target_trace):
            if element != other_link.target_trace[i]:
                return False
        for i, element in enumerate(self.origin_trace):
            if element != other_link.origin_trace[i]:
                return False
        return True


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
        self.linked_string = ('',)
        self.override = None
        self.arithmetic_value = None

    def set_value(self, value: Union[int, float, str, dict, bytearray], override_value=None):
        self.override = override_value
        self.value = value
        self.formatted_value = self._unpack_result_dict(value, 0) if isinstance(value, dict) else str(value)

    def add_raw(self, raw: bytearray):
        self.raw_bytes += raw

    def add_error(self, error: str):
        self.errors.append(error)

    def set_param_log(self, log):
        self.analyze_log = log

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

    def set_override(self, o_value: bytearray):
        self.override = o_value

    def set_arithmetic_result(self, result):
        self.arithmetic_value = result


class SCTInstruction:

    errors: List[Tuple[str, Union[int, str, bytearray]]]
    links_out: List[SCTLink]
    links_in: List[SCTLink]
    parameters: Dict[int, SCTParameter]
    loop_parameters: List[Dict[int, SCTParameter]]

    def __init__(self):
        self.ID: str = str(uuid.uuid4()).replace('-', uuid_sep)
        self.instruction_id = None
        self.absolute_offset = None
        self.skip_refresh = False
        self.frame_delay_param = None
        self.errors = []
        self.links_out = []
        self.links_in = []
        self.parameters = {}
        self.loop_parameters = []
        self.condition = ''
        self.synopsis = ''
        self.ungrouped_position: int = -1
        self.my_goto_uuids = []
        self.my_master_uuids = []

    def set_inst_id(self, inst_id):
        self.instruction_id = inst_id

    def set_pos(self, inst_pos: int):
        self.absolute_offset = inst_pos

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
                self.errors.append((f'loop{sep}{len(self.loop_parameters)-1}{sep}param', p_id))

    def get_links(self):
        return self.links_out if len(self.links_out) > 0 else None

    def generate_condition(self):
        # if the instruction is a switch, just put the value of the choice address
        if self.instruction_id == 3:
            if self.parameters[0].value is None:
                self.condition = '???'
            cond = self.parameters[0].value
            self.condition = cond if isinstance(cond, str) else str(cond)
            return

        # if the instruction is a jmpif, work out a shorthand of the condition
        if self.parameters[0].value is None:
            self.condition = '???'
        condition, cond_type = self._get_subconditions(self.parameters[0].value)
        self.condition = condition

    def _get_subconditions(self, cond_dict):
        result_str = ''
        result_type = 'float'
        if not isinstance(cond_dict, dict):
            return cond_dict if isinstance(cond_dict, str) else str(cond_dict), result_type

        for key, value in cond_dict.items():
            if key in cond_changes.scpt_types.keys():
                result_type = cond_changes.scpt_types[key]
            result_1, result_type_1 = self._get_subconditions(value['1'])
            result_2, result_type_2 = self._get_subconditions(value['2'])
            if key in cond_changes.scpt_log_changes.keys():
                param_key = f'{result_type_1}{sep}{result_type_2}'
                if param_key in cond_changes.scpt_log_changes[key]:
                    key = cond_changes.scpt_log_changes[key][param_key]
            temp_result = key.replace('(1)', result_1)
            result_str = temp_result.replace('(2)', result_2)

        return result_str, result_type

    def __repr__(self):
        return f'{self.instruction_id}'


class SCTSection:

    instruction_ids_grouped: List[Union[str, Dict[str, Union[list, dict, str]]]]
    type: str
    inst_errors: List[int]
    errors: List[str]
    strings: Dict[int, str]
    instructions_used: Dict[int, int]
    garbage: Dict[str, bytearray]

    def __init__(self):
        self.instruction_ids_ungrouped = []
        self.name = None
        self.length = None
        self.start_offset = None
        self.instructions: Dict[str, SCTInstruction] = {}
        self.instruction_ids_grouped = []
        self.inst_errors = []
        self.errors = []
        self.strings = {}
        self.instructions_used = {}
        self.garbage = {}
        self.string = ''
        self.jump_loops = []
        self.internal_sections_inst = {}
        self.internal_sections_curs = {}

    def set_name(self, name):
        self.name = name

    def set_details(self, length, pos):
        self.length = length
        self.start_offset = pos

    def add_string(self, pos: int, string: str):
        self.strings[pos] = string
        self.string = string

    def add_instruction(self, instruction: SCTInstruction):
        self.instructions[instruction.ID] = instruction
        self.instruction_ids_ungrouped.append(instruction.ID)
        if instruction.instruction_id not in self.instructions_used.keys():
            self.instructions_used[instruction.instruction_id] = 0
        self.instructions_used[instruction.instruction_id] += 1

    def set_type(self, t: str):
        self.type = t

    def add_error(self, e: str):
        self.errors.append(e)

    def add_garbage(self, key: str, value: bytearray):
        self.garbage[key] = value

    def add_loop(self, loop_id: int):
        self.jump_loops.append(loop_id)

    def get_inst_list(self, style):
        return self.instruction_ids_grouped if style == 'grouped' else self.instruction_ids_ungrouped

    def get_instruction_by_index(self, pos):
        return self.instructions[self.instruction_ids_ungrouped[pos]]


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
        self.folded_sections = {}
        self.name = name
        self.index = {k: v[0] for k, v in index.items()} if index is not None else {}
        self.header = header
        self.sections = {}
        self.section_groups = {}
        self.section_group_keys = {}
        self.sections_grouped = {}
        self.section_names_ungrouped = []
        self.inst_locations = [[] for _ in range(266)]
        self.links = []
        self.links_to_sections = {}
        self.footer = []
        self.strings = {}
        self.string_groups = {}
        self.string_locations = {}
        self.string_sections = {}
        self.unused_sections = []
        self.errors = []
        self.error_sections = {}
        self.variables = []
        self.section_num = 0

    def add_section(self, section: SCTSection):
        name = section.name
        self.sections[name] = section
        self.section_names_ungrouped.append(name)
        inst_list = self.sections[name].instructions_used.keys()
        for inst in inst_list:
            self.inst_locations[inst].append(name)
        if len(section.errors) > 0:
            self.error_sections[name] = section.errors
        self.section_num += 1

    def add_link(self, link: SCTLink) -> int:
        self.links.append(link)
        return len(self.links) - 1

    def add_footer_entry(self, entry):
        self.footer.append(entry)
        return len(self.footer) - 1

    def get_sect_list(self, style):
        if style == 'grouped':
            return self.sections_grouped
        return [section.name for section in self.sections.values() if section.type != 'String']


class SCTProject:

    file_name: str
    scripts: Dict[str, SCTScript]
    version = 1

    def __init__(self):
        self.scripts = {}
        self.file_name = 'Untitled.prj'
        self.filepath = None

    def add_script(self, filename: str, script: SCTScript):
        self.scripts[filename] = script
