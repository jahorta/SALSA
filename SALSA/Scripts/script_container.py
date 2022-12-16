import uuid
from itertools import count
from dataclasses import dataclass, field as dc_field
from typing import List, Union, Dict, Tuple

from BaseInstructions.base_instruction_container import BaseParam
from Tools.byte_array_utils import toInt, getTypeFromString, asStringOfType, toFloat

@dataclass
class Link:
    type: str
    trace: List[Union[int, str]]
    origin: int
    target: int
    target_trace: Union[List[Union[int, str]], None] = None
    ID: int = dc_field(default_factory=lambda counter=count(): next(counter))

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

    def __init__(self, param: BaseParam):
        self.ID = param.paramID
        self.type = param.type
        self.link: Union[None, Link] = None
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
                returnValue += '{0}{1}: {2}'.format(formatedReturn, key, nextLevel)
        return returnValue


class SCTInstruction:
    desc_codes = ['add', 'sub', 'mul']

    errors: List[Tuple[str, Union[int, str, bytearray]]]
    links: List[Link]
    parameters: Dict[int, SCTParameter]
    loop_parameters: List[Dict[int, SCTParameter]]

    def __init__(self, script_pos: int, inst_pos: int, inst_id: int):
        self.ID = str(uuid.uuid4()).replace('-', '_')
        self.inst_id = inst_id
        self.inst_pos = inst_pos
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

    def description_insert_param_values(self, d):
        desc = d
        paramSets = {}
        for param in self.parameters.values():
            name = param.name
            paramSets[name] = param.value

        for key, value in paramSets.items():
            keyword = f'<{key}>'
            if not isinstance(value, str):
                value = str(value)
            result = value
            desc = desc.replace(keyword, result)

        return desc

    def resolveDescriptionFuncs(self, temp_desc):

        currentSubstring = temp_desc
        if not isinstance(currentSubstring, str):
            return currentSubstring
        new_desc = ''
        while True:
            nextStarPos = currentSubstring.find('*')
            if nextStarPos == -1:
                new_desc += currentSubstring
                break
            new_desc += currentSubstring[:nextStarPos]
            currentSubstring = currentSubstring[nextStarPos:]
            currentCode = currentSubstring[1:4]
            if currentCode in self.desc_codes:
                tempCommand = currentSubstring.split(' ')[0]
                closeBrackets = tempCommand.rfind(']*')
                currentCommand = currentSubstring[:closeBrackets + 2]
                currentSubstring = currentSubstring[closeBrackets + 2:]
                result = self.run_desc_func(currentCommand)
                new_desc += '{} '.format(result)
            else:
                currentSubstring = currentSubstring[1:]
                new_desc += '*'

        return new_desc

    def run_desc_func(self, func):
        command = func[1:4]
        params = func[5:-2]
        nextStarPos = params.find('*')
        nextCommaPos = params.find(',')
        if -1 < nextStarPos < nextCommaPos:
            internal_func = params[nextStarPos:] + ']*'
            params = self.run_desc_func(internal_func)
        nextCloseParam = params.find(']')
        param1 = params[:params.find(',')]
        suffix = ''
        if nextCloseParam == -1:
            param2 = params[params.find(',') + 1:]
        else:
            param2 = params[params.find(',') + 1:nextCloseParam]
            suffix = params[nextCloseParam + 2:]

        nextStarPos = param2.find('*')
        if -1 < nextStarPos:
            internal_func = param2[nextStarPos:] + ']*'
            param2 = self.run_desc_func(internal_func)

        if command == 'add':
            result = self.add_desc_params(param1, param2)
        elif command == 'sub':
            result = self.subtract_desc_params(param1, param2)
        elif command == 'mul':
            result = self.multiply_desc_params(param1, param2)
        elif command == 'lnk':
            result = self.link_desc_params(param1, param2)
        else:
            result = ''

        return result + suffix

    def get_links(self):
        if self.hasLink:
            return self.links
        else:
            return None

    @staticmethod
    def add_desc_params(param1, param2):
        result_type = getTypeFromString(param1)
        result = toInt(param1) + toInt(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def subtract_desc_params(param1, param2):
        result_type = getTypeFromString(param1)
        result = toInt(param1) - toInt(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def multiply_desc_params(param1, param2):
        result_type = getTypeFromString(param1)
        result = toFloat(param1) * toFloat(param2)
        result = asStringOfType(result, result_type)
        return result

    def link_desc_params(self, param1, param2):
        """
        Reads in two parameters:
        [1] The name of the start point, could be the instruction start (INST), or a param name
        [2] The offset of the link target
        The function then adds this information to the link dictionary and returns a new link
        placeholder with the link index number.
        """
        startPos = -1
        if param1 == 'INST':
            startPos = self.pos
        elif len(self.parameters) > 0:
            for key, value in self.parameters.items():
                if value.name == param1:
                    startPos = value.position
            if startPos == -1:
                return 'Unable to link - invalid start position'
        else:
            return 'Unable to link - invalid start position'
        self.hasLink = True
        linkLabel = 'LINK{}'.format(len(self.links))
        self.links[linkLabel] = {'start': startPos, 'target offset': param2}
        return '<{}>'.format(linkLabel)

    def set_link(self, link_dict):
        for key, value in link_dict.items():
            replace_key = '<{}>'.format(key)
            stringList = self.description.split(replace_key)
            if len(stringList) > 1:
                self.description = stringList[0] + value + stringList[1]
            # print('')

    def get_param_id_by_name(self, name):
        param_id = None
        for key, param in self.parameters.items():
            if param.name == name:
                param_id = key
                break
        return param_id

    def set_skip_refresh(self):
        self.skip_refresh = True


class SCTSection:

    instructions: List[SCTInstruction]
    instruction_groups: Dict[str, Tuple[str, str]]
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
        self.instruction_groups = {}
        self.grouped_instructions = {}
        self.inst_group_hierarchy = {}
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

    def _propagate_links(self):
        pass

    def set_type(self, t: str):
        self.type = t

    def add_error(self, e: str):
        self.errors.append(e)

    def add_garbage(self, key: str, value: bytearray):
        self.garbage[key] = value

    def add_loop(self, loop_id: int):
        self.jump_loops.append(loop_id)


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
    links: List[Link]
    footer: List[str]
    strings: Dict[str, str]
    error_sections: Dict[str, List[str]]
    links_to_sections: Dict[str, List[str]]
    unused_sections: List[str]

    def __init__(self, name: str, index: Union[None, Dict[str, Tuple[int, int]]] = None, header: Union[None, bytearray] = None):
        self.name = name
        self.index = {k: v[0] for k, v in index.items()} if index is not None else {}
        self.header = header if header is not None else bytearray(b'/x07/xd2/x00/x06/x00/x0e/x00/x00')
        self.sections = {}
        self.section_groups = {}
        self.section_group_keys = {}
        self.grouped_section_names = {}
        self.inst_locations = [[] for _ in range(266)]
        self.links = []
        self.footer = []
        self.strings = {}
        self.string_groups = {}
        self.error_sections = {}
        self.errors = []
        self.links_to_sections = {}
        self.unused_sections = []

    def add_section(self, section: SCTSection):
        name = section.name
        self.sections[name] = section
        inst_list = self.sections[name].instructions_used.keys()
        for inst in inst_list:
            self.inst_locations[inst].append(name)
        if len(section.errors) > 0:
            self.error_sections[name] = section.errors

    def add_link(self, link: Link) -> int:
        self.links.append(link)
        return len(self.links) - 1

    def add_footer_entry(self, entry):
        self.footer.append(entry)
        return len(self.footer) - 1


class SCTProject:

    file_name: str
    scripts: Dict[str, SCTScript]

    def __init__(self):
        self.scripts = {}
        self.file_name = 'Untitled.prj'

    def add_script(self, filename: str, script: SCTScript):
        self.scripts[filename] = script
