import copy
import math
import queue
import re
import struct
import difflib
from typing import Dict, Tuple, List, Callable, Literal, Union

from SALSA.Common.script_string_utils import fix_string_decoding_errors
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Project.project_container import SCTScript, SCTSection, SCTLink, SCTInstruction, SCTParameter, \
    footer_str_group_name, footer_str_id_prefix
from SALSA.BaseInstructions.bi_container import BaseInstLib, BaseParam
from SALSA.Scripts.scpt_param_codes import SCPTParamCodes
from SALSA.Scripts.default_variables import default_aliases
from SALSA.Common.byte_array_utils import word2SignedInt, is_a_number, pad_hex, applyHexMask
from SALSA.Common.constants import sep
from SALSA.Scripts import scpt_arithmetic_fxns as scpt_arithmetic, scpt_compare_fxns as scpt_compare


ind_entry_len = 0x14
ind_name_offset = 0x4
ind_name_max_len = 0x10

endian: Dict[str, Literal['big', 'little']] = {'gc': 'big', 'dc': 'little'}


class SCTDecoder:
    log_key = 'SCTDecoder'
    _overwriteCheck = False
    _name: str
    _cursor = 0
    _inst_lib = BaseInstLib
    _index: Dict[str, Tuple[int, int]] = {}
    _sctLength = 0
    _sctStart = 0
    _errorCount: int = 0
    _sct: bytearray
    _p_codes: SCPTParamCodes
    _enc = 'shiftjis'
    _str_sect_links: List[SCTLink] = []
    _str_foot_links: List[SCTLink] = []
    _scpt_links: List[SCTLink] = []
    _jmp_if_falses: Dict[str, List[int]]
    _switches: Dict[str, List[int]]
    _last_sect_pos: int
    _cur_endian: Literal['big', 'little'] = endian['gc']
    _strings_only: bool
    _is_validation: bool

    _scpt_arithmetic_fxns: Dict[str, Callable] = {
        '*': scpt_arithmetic.mult,
        '/': scpt_arithmetic.div,
        '+': scpt_arithmetic.add,
        '-': scpt_arithmetic.sub,
        '%': scpt_arithmetic.mod
    }

    _loop_cond_tests: Dict[str, Callable] = {
        '!=': scpt_compare.not_equal,
        '==': scpt_compare.is_equal
    }

    _debug_log: List[str] = []
    _EU_encoding = False

    def _init(self, strings_only=False, is_validation=False):
        self._str_sect_links = []
        self._str_foot_links = []
        self._scpt_links = []
        self._index = {}
        self._jmp_if_falses = {}
        self._switches = {}
        self._variables = {}
        self._instruction_groups = {}
        self._footer_dialog_locs = []
        self._EU_encoding = False

    @classmethod
    def decode_sct_from_file(cls, name, sct, inst_lib: BaseInstLibFacade, status: queue.SimpleQueue=None, strings_only=False, is_validation=False):
        sct_decoder = cls()
        if status is not None:
            status.put({'sub_msg': 'Decoding...'})
        decoded_sct = sct_decoder._decode_sct(name, sct, inst_lib, strings_only=strings_only, is_validation=is_validation)
        if strings_only:
            return decoded_sct
        decoded_sct = sct_decoder._organize_sct(decoded_sct)
        if status is not None:
            status.put({'sub_msg': 'Organizing...'})
        sct_decoder._finalize_sct(decoded_sct)
        if status is not None:
            status.put({'sub_msg': 'Finalizing...'})
        return decoded_sct

    def _decode_sct(self, script_name: str, sct: bytearray, inst_lib: BaseInstLibFacade,
                    strings_only=False, is_validation=False) -> SCTScript:
        print(f'{self.log_key}: Decoding {script_name}')
        self._strings_only = strings_only
        self._is_validation = is_validation
        self._init()
        self._name = script_name
        self._sct = sct
        self._inst_lib = inst_lib
        self._p_codes = SCPTParamCodes(is_decoder=True)

        header = self._sct[:8]
        ind_entries: int = int.from_bytes(self._sct[8:12], byteorder=self._cur_endian)
        self._sct = self._sct[12:]
        self._index = {}
        used_names = []
        for i in range(ind_entries):
            start = self.getInt(pos=i * ind_entry_len)
            sect_name = self.getString(pos=i * ind_entry_len + ind_name_offset, max_len=ind_name_max_len)
            if sect_name in used_names:
                j = 0
                test_name = f'{sect_name}({j})'
                while test_name in used_names:
                    j += 1
                    test_name = f'{sect_name}({j})'
                sect_name = test_name
            used_names.append(sect_name)
            if i < ind_entries - 1:
                next_start = self.getInt(pos=(i + 1) * ind_entry_len)
            else:
                next_start = -1
                self._last_sect_pos = start
            self._index[sect_name] = (start, next_start)
        index_len = ind_entries * 0x14
        self._sct = self._sct[index_len:]
        self._sctStart = 12 + index_len
        decoded_sct = SCTScript(name=script_name, index=self._index, header=header)

        # print(self.indexed_sct['Sections'].items())
        # print(self.indexed_sct['Footer'].items())
        self._cursor = 0
        self._sctLength = len(self._sct)
        in_sect_group = False
        sect_group_key = None
        for sect_name, bounds in self._index.items():
            print(f'{self.log_key}: Decoding {sect_name}...', end='\r')
            if bounds[1] == -1:
                start = None
                if len(self._str_foot_links) != 0:
                    min_footer_link = self._sctLength
                    for link in self._str_foot_links:
                        min_footer_link = min(link.target, min_footer_link)
                    start = min_footer_link
                footer_start = self._find_EOF(sect_name, start=start)
                if footer_start is None:
                    footer_start = -1
                    self._cursor = int(bounds[0] / 4)
                    if not self.test_for_string():
                        raise EOFError(f'{self.log_key}: Final Section was not a String...')
                bounds = (bounds[0], footer_start + 4)

            new_section = self._decode_sct_section(sect_name, bounds)

            if new_section is None and self._strings_only:
                continue

            # Create or add to a logical section group if needed
            if not in_sect_group:
                if new_section.type == 'Script':
                    if new_section.get_instruction_by_index(-1).base_id != 12:
                        in_sect_group = True
                        sect_group_key = f'logical{sep}{sect_name}'
                        decoded_sct.section_groups[sect_group_key] = [sect_name]
                        decoded_sct.section_group_keys[sect_name] = sect_group_key
            else:
                if new_section.type in ('Script', 'Label'):
                    decoded_sct.section_groups[sect_group_key].append(sect_name)
                    decoded_sct.section_group_keys[sect_name] = sect_group_key
                    last_inst = new_section.get_instruction_by_index(-1)
                    if last_inst.base_id == 12:
                        in_sect_group = False
                        sect_group_key = None
                else:
                    last_sect = decoded_sct.sects[decoded_sct.section_groups[sect_group_key][-1]]
                    if last_sect.insts[last_sect.inst_list[-1]].base_id == 9:
                        decoded_sct.section_groups[sect_group_key].pop(-1)
                    in_sect_group = False
                    sect_group_key = None

            decoded_sct.add_section(new_section)

        print(f'{self.log_key}: All sections decoded!!!')

        self.section_group_keys = {}

        return decoded_sct

    def _decode_sct_section(self, sect_name, bounds) -> SCTSection:

        sct_start_pos = bounds[0]
        length = bounds[1] - bounds[0]
        section = SCTSection()
        section.set_name(sect_name)
        section.set_details(length, sct_start_pos)
        self._cursor = int(sct_start_pos / 4)

        if length == 16:
            section.set_type('Label')

        elif self.test_for_string():
            currWord = self.getInt(self._cursor * 4)
            while not currWord == 0x0000001d:
                self._cursor += 1
                currWord = self.getInt(self._cursor * 4)
            self._cursor += 1
            string = self.getString(self._cursor * 4, encoding=self._enc)
            if string == '':
                section.add_error('Length of string == 0')
            section.set_type('String')
            section.set_string(self._cursor * 4, string)
            garbage = self._get_garbage_after_string(bounds=bounds)
            if len(garbage) > 0:
                section.add_garbage('end', garbage)
            return section

        else:
            section.set_type('Script')

        if self._strings_only:
            return None

        section = self._create_insts_from_region(bounds, section, 0)

        return section

    def _create_insts_from_region(self, bounds, section: SCTSection, inst_list_id_start):
        self._cursor = bounds[0] // 4
        self.end = bounds[1]
        inst_list_id = inst_list_id_start
        sect_name = section.name

        while (self._cursor * 4) < bounds[1]:
            self._cur_endian = 'big'
            currWord = self.getWord(self._cursor * 4)
            currWord_int = int.from_bytes(currWord, byteorder=self._cur_endian)

            is_inst = 0 <= currWord_int <= 265
            if not is_inst:
                self._cur_endian = 'little'
                currWord_int = int.from_bytes(currWord, byteorder=self._cur_endian)
                is_inst = 0 <= currWord_int <= 265

            if is_inst:
                inst_pos = self._cursor * 4

                # Test for the dunder code to try to not go to the next frame after this instruction
                try_no_refresh = False
                if currWord_int == 13:
                    try_no_refresh = True
                    self._cursor += 1
                    currWord_int = self.getInt(self._cursor * 4)

                # Test for the dunder code to delay execution of an instruction
                delay_inst = None
                if currWord_int == 129:
                    delay_inst = self._decode_instruction(currWord_int, inst_pos, [sect_name, inst_list_id])
                    delay_inst.length = self._cursor * 4 - inst_pos
                    currWord_int = self.getInt(self._cursor * 4)

                instResult = self._decode_instruction(currWord_int, inst_pos, [sect_name, inst_list_id])

                if instResult.base_id == 9:
                    instResult.label = sect_name

                if try_no_refresh:
                    instResult.skip_refresh = True

                if delay_inst is not None:
                    instResult.delay_param = delay_inst.params[0]
                    numeric = True
                    if instResult.delay_param.arithmetic_value is not None:
                        if not isinstance(instResult.delay_param.arithmetic_value, int):
                            numeric = False
                    elif not isinstance(instResult.delay_param.value, int):
                        if not instResult.delay_param.value.isnumeric():
                            numeric = False
                    if not numeric:
                        instResult.add_error(('frame_delay', 'Non-numeric frame delay given'))

                    inst_size = self._cursor * 4 - instResult.absolute_offset
                    if inst_size != (delay_inst.params[1].value + delay_inst.length):
                        garbage_size = ((delay_inst.params[1].value + delay_inst.length) - inst_size) // 4
                        garbage = bytearray(b'')
                        for i in range(self._cursor, self._cursor + garbage_size):
                            garbage += self.getWord(i * 4)
                        instResult.add_error(('Garbage', garbage))
                        instResult.add_error(('frame_delay', 'improper instruction size given, put into garbage'))
                        self._cursor += garbage_size

                section.add_instruction(instResult)

                if instResult.base_id in (24, 25):
                    self._footer_dialog_locs.append([sect_name, instResult.ID])

                if instResult.base_id in [0, 3]:
                    instResult.generate_condition(default_aliases)

                if instResult.base_id == 3:
                    if sect_name not in self._switches.keys():
                        self._switches[sect_name] = []
                    self._switches[sect_name].append(inst_list_id)

                if instResult.base_id == 0:
                    if sect_name not in self._jmp_if_falses.keys():
                        self._jmp_if_falses[sect_name] = []
                    self._jmp_if_falses[sect_name].append(inst_list_id)

                if instResult.base_id == 0x3:
                    # Check for garbage before first entry
                    switch_start = (self._cursor + len(instResult.params))
                    min_case_start = None
                    switch_end = switch_start + (len(instResult.l_params) * 2)
                    for i, paramset in enumerate(instResult.l_params):
                        case_start = switch_start + (i * 2 + 1) + int(paramset[3].value / 4)
                        min_case_start = case_start if min_case_start is None else min(min_case_start, case_start)

                    if switch_end > min_case_start:
                        garbage_num = min_case_start - switch_end
                        garbage = bytearray(b'')
                        for i in range(garbage_num):
                            garbage += self.getWord(self._cursor * 4)
                            self._cursor += 1
                        instResult.add_error(('Garbage', garbage))
                    elif switch_end < min_case_start:
                        raise IndexError(f'{self.log_key}: Switch incomplete, switch end < min case start')

                if instResult.base_id == 0xc:
                    end_cursor = bounds[1] // 4
                    if self._cursor < end_cursor:
                        next_inst = self.getInt(self._cursor * 4)
                        if not ((0 < next_inst < 265) or (next_inst in [4, 8])):
                            section.add_error('Garbage: garbage instruction after return')
                            garbage = self._sct[self._cursor * 4:bounds[1]]
                            self._cursor = bounds[1] // 4
                            section.add_garbage('end', garbage)

                if instResult.base_id == 0xa:
                    end_cursor = bounds[1] // 4
                    if self._cursor < end_cursor:
                        if not (0 <= self.getInt(self._cursor * 4) <= 265):
                            start_cursor = self._cursor
                            while self._cursor * 4 < bounds[1]:
                                next_i_id = self.getInt(self._cursor * 4)
                                if (0 <= next_i_id <= 265) and next_i_id not in [2, 4]:
                                    param1_code = self.getInt(self._cursor * 4 + 4)
                                    self._cur_endian = 'little'
                                    param1_code_little = self.getInt(self._cursor * 4 + 4)
                                    self._cur_endian = 'big'
                                    if next_i_id in self._inst_lib.lib.p1_scpt:
                                        if (param1_code in self._p_codes.primary_keys
                                                or param1_code in self._p_codes.no_loop):
                                            break
                                        if ((param1_code_little in self._p_codes.primary_keys
                                             or param1_code_little in self._p_codes.no_loop)
                                                and next_i_id != 0):
                                            break
                                        param_prefix = param1_code & 0xff000000
                                        param_little_prefix = param1_code_little & 0xff000000
                                        if param_prefix in self._p_codes.cutoff_prefixes:
                                            break
                                        if param_little_prefix in self._p_codes.cutoff_prefixes and next_i_id != 0:
                                            break
                                    elif next_i_id in self._inst_lib.lib.p1_int:
                                        mask = self._inst_lib.lib.insts[next_i_id].params[0].mask
                                        p1 = param1_code
                                        p1_little = param1_code_little
                                        if mask is not None:
                                            p1 = int(applyHexMask(hex(p1), hex(mask)), 16)
                                            p1_little = int(applyHexMask(hex(p1_little), hex(mask)), 16)
                                        if self._inst_lib.lib.insts[next_i_id].params[0].is_signed:
                                            p1 = word2SignedInt(hex(p1))
                                            p1_little = word2SignedInt(hex(p1_little))
                                        if 0 <= self._cursor * 4 + p1 < self._sctLength:
                                            break
                                        if 0 <= self._cursor * 4 + p1_little < self._sctLength:
                                            break
                                    else:
                                        break

                                self._cursor += 1

                            garbage = bytearray(b'')
                            for i in range(start_cursor, self._cursor):
                                garbage += self.getWord(i * 4)
                            instResult.add_error(('Garbage', garbage))

                inst_list_id += 1

            else:
                cur_pos = self._cursor * 4
                absolute_pos = cur_pos + self._sctStart
                param = currWord

                # Since 0x04000000 is reserved for SCPTAnalyze, capture any instructions following this code as SCPT parameters
                if currWord_int == 0x04000000:
                    length = 0
                    while currWord_int != 0x0000001d:
                        length += 1
                        self._cursor += 1
                        currWord = self.getWord(self._cursor * 4)
                        currWord_int = int.from_bytes(currWord, byteorder=self._cur_endian)
                        param += currWord
                    error_str = f'{self.log_key}: Extra SCPT parameter found:\n\tSCPT Position: {cur_pos}'
                    error_str += f'\n\tAbsolute Position: {absolute_pos}'
                    if int(inst_list_id):
                        error_str += f'\n\tPrevious Instruction: {section.get_instruction_by_index(inst_list_id).base_id}'
                    else:
                        error_str += f'\n\tUnable to determine Previous Instruction: inst_list_id is {inst_list_id}'
                    error_str += f'\n\tLength: {length}\n\tParam: {param.hex()}'

                else:
                    error_str = f'{self.log_key}: Unknown Instruction Code:\n\tInstruction code: {param.hex()}'
                    error_str += f'\n\tSubscript: {cur_pos}\n\tInstruction List Index: {inst_list_id}'
                    if int(inst_list_id):
                        error_str += f'\n\tPrevious Instruction: {section.get_instruction_by_index(inst_list_id).base_id}'
                    else:
                        error_str += f'\n\tUnable to determine Previous Instruction: inst_list_id is {inst_list_id}'
                    error_str += f'\n\tSCPT Position: {cur_pos}\n\tAbsolute Position: {absolute_pos}'

                raise IndexError(error_str)

            if (self._cursor * 4) > bounds[1]:
                error = f'{self.log_key}: Read cursor is past the end of current subscript: {sect_name}'
                raise IndexError(error)

            if self._cursor > self._sctLength:
                raise EOFError(f'{self.log_key}: Read cursor is past the end of the file')

        return section

    def _decode_instruction(self, inst_id, inst_pos, trace):
        cur_inst = SCTInstruction()
        cur_inst.set_inst_id(inst_id)
        cur_inst.set_pos(inst_pos)
        base_inst = self._inst_lib.get_inst(inst_id=inst_id)
        self._cursor += 1

        # decode parameters
        parameters = copy.deepcopy(base_inst.params)
        loop_parameters = []
        hasLoop = base_inst.loop is not None
        if hasLoop:
            loop_parameters = [parameters[_] for _ in base_inst.loop]
            for p_id in base_inst.loop:
                parameters.pop(p_id)

        cur_param_num = 0
        used_params = []
        for p_id, base_param in parameters.items():
            if p_id != cur_param_num:
                break
            param = self._decode_param(base_param, [*trace, f'{p_id}'])
            if param.link is not None:
                cur_inst.links_out.append(param.link)
            cur_inst.add_parameter(p_id, param)
            used_params.append(p_id)
            cur_param_num += 1

        for p in used_params:
            parameters.pop(p)

        willLoop = True
        if base_inst.loop_cond is not None:
            l_c = base_inst.loop_cond
            if l_c['Location'] == 'External':
                if self._loop_cond_tests[l_c['Test']](cur_inst.params[l_c['Parameter']].value, l_c['Value']):
                    willLoop = False

        if hasLoop and willLoop:
            max_iter = cur_inst.params[base_inst.loop_iter].value
            cur_iter = 0
            done = False
            while not done and cur_iter < max_iter:
                param_group = {}
                for p in loop_parameters:
                    param = self._decode_param(p, [*trace, f'{cur_iter}{sep}{p.param_ID}'])
                    param_group[p.param_ID] = param
                    if param.link is not None:
                        cur_inst.links_out.append(param.link)

                cur_inst.add_loop_parameter(param_group)

                if base_inst.loop_cond is not None:
                    l_c = base_inst.loop_cond
                    if l_c['Location'] == 'Internal':
                        if self._loop_cond_tests[l_c['Test']](param_group[l_c['Parameter']].value, l_c['Value']):
                            break

                cur_iter += 1

        if len(parameters) == 0:
            return cur_inst

        for p_id, base_param in parameters.items():
            if p_id != cur_param_num:
                break
            param = self._decode_param(base_param, [*trace, f'{p_id}'])
            cur_inst.add_parameter(base_param.type, param)
            if param.link is not None:
                cur_inst.links_out.append(param.link)

        return cur_inst

    def _decode_param(self, base_param: BaseParam, trace):
        cur_param = SCTParameter(_id=base_param.param_ID, _type=base_param.type)
        param_type = base_param.type
        if 'scpt' in param_type:
            overrideCompare = [0x7f7fffff]
            overrideResult = 0x7f7fffff
            if 'int' in param_type:
                overrideCompare.append(0x7fffffff)
                overrideResult = 0x7fffffff
            elif 'short' in param_type:
                overrideResult = 0xffff
            elif 'byte' in param_type:
                overrideResult = 0xff

            scriptCompare = self.getInt(self._cursor * 4)
            if scriptCompare in overrideCompare:
                cur_param.set_value(overrideResult)
                cur_param.set_override(self.getWord(self._cursor * 4))
                self._cursor += 1
                return cur_param

            scptResult = self._SCPT_analyze(cur_param)
            done = False
            if isinstance(scptResult, dict) or isinstance(scptResult, bytearray):
                done = True
            elif isinstance(scptResult, str):
                if scptResult[:2] == '0x':
                    done = True
                elif not is_a_number(scptResult):
                    done = True
                else:
                    scptResult = float(scptResult)
            elif scptResult is None:
                done = True
                cur_param.add_error('Error: No value generated...')

            if not done and 'float' not in param_type:
                signed = scptResult < 0
                scptResult = math.floor(scptResult)
                if 'int' not in param_type:
                    scptResult = bytearray(scptResult.to_bytes(4, 'big', signed=signed)).hex()
                    if 'short' in param_type:
                        scptResult = applyHexMask(scptResult, '0xffff')[2:]
                    elif 'byte' in param_type:
                        scptResult = applyHexMask(scptResult, '0xff')[2:]

                    scptResult = int.from_bytes(bytes=bytearray.fromhex(scptResult), byteorder='big', signed=signed)

            cur_param.set_value(scptResult)

            if cur_param.arithmetic_value is not None:
                arithmetic_result = float(cur_param.arithmetic_value)
                if 'float' not in param_type:
                    signed = arithmetic_result < 0
                    arithmetic_result = math.floor(arithmetic_result)
                    if 'int' not in param_type:
                        arithmetic_result = bytearray(arithmetic_result.to_bytes(4, 'big', signed=signed)).hex()
                        if 'short' in param_type:
                            arithmetic_result = applyHexMask(arithmetic_result, '0xffff')[2:]
                        elif 'byte' in param_type:
                            arithmetic_result = applyHexMask(arithmetic_result, '0xff')[2:]

                        arithmetic_result = int.from_bytes(bytes=bytearray.fromhex(arithmetic_result), byteorder='big',
                                                           signed=signed)
                cur_param.arithmetic_value = arithmetic_result

        elif 'int' in param_type:
            currWord = self.getWord(self._cursor * 4)
            if self._cur_endian == 'little':
                currWord = bytearray(reversed(currWord))

            if 'var' in param_type:
                param_value = self._resolve_SCPT_code_only()
                cur_param.set_value(param_value)
            else:
                raw = currWord
                cur_param.add_raw(raw)
                if base_param.mask is not None:
                    cur_param.type += f'{sep}masked'
                    mask = base_param.mask
                    currWord = bytearray.fromhex(applyHexMask(currWord.hex(), hex(mask))[2:])
                if base_param.is_signed:
                    cur_param.type += f'{sep}signed'
                    cur_value = word2SignedInt(currWord)
                else:
                    cur_value = int.from_bytes(currWord, byteorder=self._cur_endian)
                cur_param.set_value(cur_value)
                if base_param.link_type is not None:
                    link_type = base_param.link_type
                    origin = self._cursor * 4
                    target = self._cursor * 4 + cur_value
                    newLink = SCTLink(type=link_type, origin=origin, target=target, origin_trace=trace)
                    cur_param.link = newLink
                    if link_type == 'String':
                        if target > self._last_sect_pos:
                            self._str_foot_links.append(newLink)
                        else:
                            self._str_sect_links.append(newLink)
                    else:
                        self._scpt_links.append(newLink)
                        if cur_value < 0:
                            self._debug_log.append(f'Negative link: {newLink}')

            self._cursor += 1

        else:
            cur_param.type = 'unknown type'
            cur_param.set_value(f'unknown result for 0x{self.getWord(self._cursor * 4).hex()}')
            self._cursor += 1

        return cur_param

    def _resolve_SCPT_code_only(self):
        currWord = self.getInt(self._cursor * 4)
        action = None
        # Determine the input type from the input_cutoffs table
        for key in self._p_codes.input.keys():
            if currWord >= key:
                action = key
                break

        value = ''
        value += self._p_codes.input[action]
        value += str(currWord & 0x00ffffff)

        return value

    def _SCPT_analyze(self, param: SCTParameter):

        scpt_result = {}
        param_key = '{}_S'.format(param.ID)
        done = False
        roundNum = 0
        currentWord = self.getWord(self._cursor * 4)
        raw = currentWord
        if self._cur_endian == 'little':
            raw = bytearray(reversed(currentWord))

        # First check that the first word is not a special value
        if int.from_bytes(currentWord, byteorder=self._cur_endian) in self._p_codes.no_loop.keys():
            param.add_raw(raw)
            self._cursor += 1
            return self._p_codes.no_loop[int.from_bytes(currentWord, byteorder=self._cur_endian)]

        raw = bytearray(b'')
        # Resolve the SCPT analysis
        result_stack: List[Union[None, int, float]] = [None] * 20
        flag_stack = [0] * 20
        stack_index: int = 0
        max_index = 18
        while not done:
            currentWord = self.getWord(self._cursor * 4)
            temp_raw = currentWord
            if self._cur_endian == 'little':
                temp_raw = bytearray(reversed(currentWord))
            raw.extend(temp_raw)
            currentWord = int.from_bytes(currentWord, byteorder=self._cur_endian)

            cur_result = ''

            # Make sure that the SCPT Stack wouldn't overflow
            if stack_index >= max_index:
                param.add_error(f'SCPT Stack overflow: {currentWord}')
                break

            # Check for end of the SCPT Analysis loop
            if currentWord == 0x0000001d:
                # in me010a.sct, this is the only value given with the last loop parameter, so it may just return zero if the result stack is initialized with zeros
                # If there are no other instructions, This seems to return the last valid value that was given...
                # TODO - This needs to be tested further.
                scpt_result[f'{param_key}{roundNum}'] = 'return values (0x1d)'
                break

            # Test for values between the highest compare code and the prefix for a float
            if 0x04000000 > currentWord > 0x00000016:
                pass

            # Test whether the current word is a primary code
            elif currentWord in self._p_codes.compare.keys():
                currVals = {'1': result_stack[stack_index], '2': result_stack[stack_index + 1]}
                cur_result = {self._p_codes.compare[currentWord]: currVals}
                nones: int = 0
                for v in currVals.values():
                    if v is None:
                        nones += 1
                result_stack[stack_index + nones] = cur_result
                stack_index -= 1
                if currentWord == 0x0000000a:
                    stack_index += 1
            elif currentWord in self._p_codes.arithmetic.keys():
                currVals = {'1': result_stack[stack_index], '2': result_stack[stack_index + 1]}
                inputs = []
                cur_result = {self._p_codes.arithmetic[currentWord]: currVals}
                nones = 0
                for v in currVals.values():
                    if v is None:
                        nones += 1
                    elif isinstance(v, str):
                        v = str(v)
                        if is_a_number(v):
                            inputs.append(v)
                    elif not (isinstance(v, dict) or isinstance(v, bytearray)):
                        inputs.append(v)
                if len(inputs) == 2:
                    result = self._scpt_arithmetic_fxns[self._p_codes.arithmetic[currentWord][4]](inputs[0], inputs[1])
                    param.set_arithmetic_result(result)
                result_stack[stack_index + nones] = cur_result
                stack_index -= 1

            # If not, current action is to input a value
            else:
                action = None

                # Determine the input type from the input_cutoffs table
                for key in self._p_codes.input.keys():
                    if currentWord >= key:
                        action = key
                        break

                # Resolve Input
                if not action == 0x50000000:
                    # Generate values from current word
                    if action is None:
                        cur_result = f'Unable to interpret SCPT instruction: {currentWord}'
                    else:
                        if action == 0x04000000:
                            self._cursor += 1
                            word = self.getWord(self._cursor * 4)
                            if self._cur_endian == 'little':
                                word = list(reversed(word))
                            raw.extend(word)
                            result = self.getFloat(self._cursor * 4)
                        elif action == 0x08000000:
                            obtainedValue = str((currentWord & 0xffff00) >> 8)
                            obtainedValue += f'+{(currentWord & 0xff)}/256'
                            result = self._p_codes.input[action] + f'{obtainedValue}'
                        else:
                            obtainedValue = currentWord & 0x00ffffff
                            result = self._p_codes.input[action] + f'{obtainedValue}'
                        result_stack[stack_index + 2] = result
                        cur_result = result
                        stack_index += 1

                # Go through secondary codes and perform a function
                else:
                    masked_currentWord = currentWord & 0xffffff
                    if masked_currentWord in self._p_codes.secondary.keys():
                        result = self._p_codes.secondary[masked_currentWord]
                        result_stack[(stack_index + 2)] = result
                        cur_result = result
                    else:
                        offset = masked_currentWord
                        cur_result = self._p_codes.input[action] + f'{offset}'
                        result_stack[(stack_index + 2)] = cur_result
                        if masked_currentWord == 0xf:
                            flag_stack[(stack_index + 2)] = 1
                    stack_index += 1

            scpt_result[f'{param_key}{roundNum}'] = {pad_hex(hex(currentWord), 8): cur_result}
            self._cursor += 1
            roundNum += 1
            if self._cursor >= self._sctLength:
                param.add_error('SCPTanalyze did not finish before next sct section')
                break

        if result_stack[2] is None:
            param.add_error('Error: No value generated')

        param.add_raw(raw)
        param.set_param_log(scpt_result)

        self._cursor += 1

        return result_stack[2]

    # ------------------------ #
    # Decoder helper functions #
    # ------------------------ #

    def _find_EOF(self, last_sect, start):
        end_cursor = self._sctLength - 4 if start is None else start
        last_sect_start = self._index[last_sect][0]
        while end_cursor > last_sect_start:
            cur_word = self.getInt(end_cursor)
            if cur_word == 10:
                if word2SignedInt(self.getWord(end_cursor + 4), ) < 0:
                    end_cursor += 4
                    break
            if cur_word == 12:
                break
            end_cursor -= 1
        if end_cursor == last_sect_start:
            print('Unable to find the EOF, likely the last section is a string or label')
            end_cursor = None
        return end_cursor

    def test_for_string(self):
        cursor = self._cursor
        currWord = self.getInt(cursor * 4)
        if currWord != 0x00000009:
            return False
        while not currWord == 0x0000001d:
            cursor += 1
            currWord = self.getInt(cursor * 4)
        cursor += 1
        testWord = self.getInt(cursor * 4)
        return testWord < 0 or testWord > 265

    def getInt(self, pos: int):
        return int.from_bytes(bytes=self.getWord(pos), byteorder=self._cur_endian)

    def getFloat(self, pos: int):
        word = self.getWord(pos)
        if self._cur_endian == 'little':
            word = bytearray(reversed(word))
        return struct.unpack('!f', word)[0]

    def getString(self, pos: int, max_len=None, encoding='shiftjis') -> str:
        size = 0
        while True:
            cur_pos = pos + size
            cur_byte = self._sct[cur_pos]
            if cur_byte == 0x0:
                break
            size += 1
            if max_len is not None:
                if size == max_len:
                    break
        str_bytes = self._sct[pos: pos + size]

        if len(str_bytes) > 3 and not self._EU_encoding:
            if str_bytes[3] == 0xab:
                self._EU_encoding = True

        alt_encoding = 'cp1252'
        if self._EU_encoding and not str_bytes[:2] == bytearray(b'\x81\x83') and not str_bytes[3:5] == bytearray(b'\x81\x73'):
            encoding, alt_encoding = alt_encoding, encoding

        string = str_bytes.decode(encoding=encoding, errors='backslashreplace')
        if '\\x' in string:
            string = fix_string_decoding_errors(string, encoding)

        if '\\x' in string:
            string = str_bytes.decode(encoding=alt_encoding, errors='backslashreplace')

        return string

    def _get_garbage_after_string(self, bounds):
        offset = 0
        end_of_string = -1
        garbage = bytearray()
        first_zero = True
        expected_zeros = -1
        while (self._cursor * 4) + offset < bounds[1]:
            cur_byte = self._sct[self._cursor * 4 + offset].to_bytes(length=1, byteorder=self._cur_endian)

            if end_of_string > 0:
                garbage.extend(cur_byte)

            elif cur_byte == b'\x00':
                if first_zero:
                    first_zero = False
                    expected_zeros = 1
                    if (offset + expected_zeros) % 4 != 0:
                        expected_zeros += (4 - ((offset + expected_zeros) % 4))
                expected_zeros -= 1
                if expected_zeros == 0:
                    end_of_string = offset

            offset += 1

        return garbage

    def getWord(self, pos) -> bytearray:
        return self._sct[pos: pos + 4]

    # -------------------------- #
    # Organize newly decoded sct #
    # -------------------------- #
    def _organize_sct(self, decoded_sct) -> SCTScript:

        self._create_logical_sections(decoded_sct=decoded_sct)

        # Setup links
        print(f'{self.log_key}: Setting Up Links...', end='\r')
        done = False
        while not done:
            done = self._setup_scpt_links(decoded_sct=decoded_sct)

        self._resolve_scpt_links(decoded_sct=decoded_sct)
        self._setup_string_links(decoded_sct=decoded_sct)

        self._detect_unused_sections(decoded_sct=decoded_sct)

        # Group strings
        print(f'{self.log_key}: Creating String Groups...', end='\r')
        self._create_string_groups(decoded_sct=decoded_sct)

        # Group jump if false commands
        print(f'{self.log_key}: Creating Jump Groups...', end='\r')
        self._group_jump_commands(decoded_sct=decoded_sct)

        # Group switches
        print(f'{self.log_key}: Creating Switch Groups...', end='\r')
        self._group_switches(decoded_sct=decoded_sct)

        # Group Subscripts
        print(f'{self.log_key}: Grouping Subscripts...', end='\r')
        self._group_subscripts(decoded_sct=decoded_sct)

        self._detect_and_move_footer_dialog(decoded_sct=decoded_sct)

        self._create_group_heirarchies(decoded_sct=decoded_sct)

        self._put_inst_ids_into_link_traces(decoded_sct=decoded_sct)

        self._populate_ungrouped_inst_values(decoded_sct=decoded_sct)

        return decoded_sct

    def _create_logical_sections(self, decoded_sct: SCTScript):
        # Prune logical script groups with a single entry
        groups_to_remove = []
        for key, group in decoded_sct.section_groups.items():
            if len(group) < 2:
                groups_to_remove.append(key)
        for group in groups_to_remove:
            decoded_sct.section_groups.pop(group)

        for name, group in decoded_sct.section_groups.items():
            if 'logical' not in name:
                continue
            new_name = group[0]
            if new_name in decoded_sct.sects:
                i = 0
                while True:
                    test_name = f'{new_name}({i})'
                    if test_name not in decoded_sct.sects:
                        break
                    i += 1
                new_name = test_name

            # Setup combined logical section
            new_section: SCTSection = decoded_sct.sects[group[0]]
            new_section.name = new_name
            new_section.internal_sections_inst[group[0]] = 0
            new_section.internal_sections_curs[group[0]] = 0
            for sect_name in group[1:]:
                sect_to_add: SCTSection = decoded_sct.sects[sect_name]
                new_section.internal_sections_inst[sect_name] = len(new_section.insts)
                new_section.internal_sections_curs[sect_name] = sect_to_add.absolute_offset - new_section.absolute_offset
                new_section.insts = {**new_section.insts, **sect_to_add.insts}
                new_section.inst_list.extend(sect_to_add.inst_list)
                for key, value in sect_to_add.insts_used.items():
                    if key not in new_section.insts_used:
                        new_section.insts_used[key] = 0
                    new_section.insts_used[key] += value
                new_section.length += sect_to_add.length
                new_section.jump_loops.extend(sect_to_add.jump_loops)
                new_section.strings = {**new_section.strings, **sect_to_add.strings}
                new_section.errors.extend(sect_to_add.errors)
                new_section.garbage = {**new_section.garbage, **sect_to_add.garbage}
                new_section.inst_errors.extend(sect_to_add.inst_errors)

            keys_before = []
            keys_after = []
            hit_name = False
            for key in decoded_sct.sect_list:
                if key in group:
                    hit_name = True
                    continue
                if not hit_name:
                    keys_before.append(key)
                else:
                    keys_after.append(key)

            sections = {k: decoded_sct.sects[k] for k in keys_before}
            sections[new_name] = new_section
            sections = {**sections, **{k: decoded_sct.sects[k] for k in keys_after}}
            decoded_sct.sects = sections

            decoded_sct.sect_list = [*keys_before, new_name, *keys_after]

            for s in group:
                decoded_sct.folded_sects[s] = new_name

        decoded_sct.section_groups = {}
        decoded_sct.section_group_keys = {}
        for link in self._scpt_links:
            self._update_link_traces(link, decoded_sct)

        for link in self._str_sect_links:
            self._update_link_traces(link, decoded_sct)

        for link in self._str_foot_links:
            self._update_link_traces(link, decoded_sct)

        new_jmps = {}
        for old_name, entries in self._jmp_if_falses.items():
            if old_name not in decoded_sct.folded_sects:
                new_jmps[old_name] = entries
                continue
            new_name = decoded_sct.folded_sects[old_name]
            section_offset = decoded_sct.sects[new_name].internal_sections_inst[old_name]
            new_entries = [_ + section_offset for _ in entries]
            if new_name not in new_jmps.keys():
                new_jmps[new_name] = new_entries
            else:
                new_jmps[new_name].extend(new_entries)
        self._jmp_if_falses = new_jmps

        new_switches = {}
        for old_name, entries in self._switches.items():
            if old_name not in decoded_sct.folded_sects:
                new_switches[old_name] = entries
                continue
            new_name = decoded_sct.folded_sects[old_name]
            section_offset = decoded_sct.sects[new_name].internal_sections_inst[old_name]
            new_entries = [_ + section_offset for _ in entries]
            if new_name not in new_switches.keys():
                new_switches[new_name] = new_entries
            else:
                new_switches[new_name].extend(new_entries)
        self._switches = new_switches

    @staticmethod
    def _update_link_traces(link, decoded_sct):
        if link.origin_trace[0] in decoded_sct.folded_sects:
            old_sect_name = link.origin_trace[0]
            old_inst_pos = link.origin_trace[1]
            section = decoded_sct.sects[decoded_sct.folded_sects[old_sect_name]]
            link.origin_trace[0] = section.name
            link.origin_trace[1] = section.internal_sections_inst[old_sect_name] + old_inst_pos

    def _setup_scpt_links(self, decoded_sct):
        blank_section = SCTSection()
        sect_keys = list(decoded_sct.sects.keys())
        self.successful_scpt_links = []
        for link in self._scpt_links:
            target_sct = blank_section
            target_sct_id = 0
            while target_sct_id < len(decoded_sct.sects):
                section = decoded_sct.sects[sect_keys[target_sct_id]]
                if section.absolute_offset <= link.target < section.absolute_offset + section.length:
                    target_sct: SCTSection = section
                    break
                target_sct_id += 1
            target_inst_id = 0
            while target_inst_id < len(target_sct.insts):
                inst = target_sct.get_instruction_by_index(target_inst_id)
                if inst.absolute_offset == link.target:
                    break
                if target_inst_id == len(target_sct.insts) - 1:
                    inst_end = target_sct.absolute_offset + target_sct.length
                else:
                    inst_end = target_sct.get_instruction_by_index(target_inst_id + 1).absolute_offset
                if inst.absolute_offset < link.target < inst_end:
                    internal = True
                    new_error = None
                    error_ind = None
                    for i, e in enumerate(inst.errors):
                        if e[0] != 'Garbage':
                            continue
                        internal = False
                        first_start = inst_end - len(e[1])
                        if link.target < first_start:
                            internal = True
                            break
                        new_error = e[1][:link.target - first_start]
                        error_ind = i
                        break

                    if new_error is not None:
                        if len(new_error) > 0:
                            inst.errors[error_ind] = ('Garbage', new_error)
                        else:
                            inst.errors.pop(error_ind)

                    if internal:
                        print(f'{self.log_key}: link position is internal to an instruction '
                              f'at {target_sct.name}:{target_inst_id}: \n\t{link}')
                        decoded_sct.errors.append(
                            f'link position is internal to an instruction at {target_sct.name}:{target_inst_id}: \n\t{link}')
                        break

                    bounds = (link.target, inst_end)
                    suffix_insts = target_sct.inst_list[target_inst_id + 1:]
                    target_sct.inst_list = target_sct.inst_list[:target_inst_id + 1]
                    insts_before = len(target_sct.inst_list)
                    changes = self._get_links_to_change(target_sct, insts_before)
                    target_sct = self._create_insts_from_region(bounds, target_sct, target_inst_id + 1)
                    insts_added = len(target_sct.inst_list) - insts_before
                    self._set_changes(changes, insts_added)
                    target_sct.inst_list += suffix_insts
                    print(
                        f'{self.log_key}: New instructions decoded at {target_sct.name}:{target_inst_id + 1}. Restarting Link setup...',
                        end='\r')
                    return False

                target_inst_id += 1

            link.target_trace = [target_sct.name, target_inst_id]
            self.successful_scpt_links.append(link)

        return True

    def _resolve_scpt_links(self, decoded_sct: SCTScript):
        for link in self.successful_scpt_links:

            # add the origin of a link to its target
            target_inst = decoded_sct.sects[link.target_trace[0]].get_instruction_by_index(link.target_trace[1])
            target_inst.links_in.append(link)

            # add to dict with places that subscripts are called from
            if link.origin_trace[0] != link.target_trace[0]:
                tr_sect = link.origin_trace[0]
                target_tr_sect = link.target_trace[0]
                if target_tr_sect not in decoded_sct.links_to_sections.keys():
                    decoded_sct.links_to_sections[target_tr_sect] = []
                if tr_sect not in decoded_sct.links_to_sections[target_tr_sect]:
                    decoded_sct.links_to_sections[target_tr_sect].append(tr_sect)

    def _setup_string_links(self, decoded_sct):
        # setup string links
        sect_keys = list(decoded_sct.sects.keys())
        for link in self._str_sect_links:
            target_sct_str = ''
            target_sct_id = 0
            while target_sct_id < len(decoded_sct.sects):
                section = decoded_sct.sects[sect_keys[target_sct_id]]
                if link.target == section.absolute_offset:
                    target_sct_str = section.name
                    break
                if target_sct_id == len(decoded_sct.sects) - 1:
                    sect_end = section.absolute_offset + section.length
                else:
                    sect_end = decoded_sct.sects[sect_keys[target_sct_id + 1]].absolute_offset
                if section.absolute_offset < link.target < sect_end:
                    print(f'link position is incorrect: \n\t{link}')
                    break
                target_sct_id += 1
            origin_inst = decoded_sct.sects[link.origin_trace[0]].get_instruction_by_index(link.origin_trace[1])
            param: SCTParameter = origin_inst.params[int(link.origin_trace[2])]
            param.linked_string = target_sct_str
            if '\\c' in decoded_sct.sects[target_sct_str].string and not self._is_validation:
                if origin_inst.base_id == 144:
                    if origin_inst.params[1].value != 'decimal: 1+0/256':
                        origin_inst.params[1].set_value('decimal: 1+0/256')
                if origin_inst.base_id == 155:
                    if origin_inst.params[2].value != 'decimal: 1+0/256':
                        origin_inst.params[2].set_value('decimal: 1+0/256')

        # setup footer links
        for link in self._str_foot_links:
            foot_str = self.getString(link.target)
            origin_inst = decoded_sct.sects[link.origin_trace[0]].get_instruction_by_index(link.origin_trace[1])
            param: SCTParameter = origin_inst.params[int(link.origin_trace[2])]
            param.linked_string = foot_str
            param.link.type = 'Footer'

    @staticmethod
    def _create_string_groups(decoded_sct):
        cur_group_name = ''
        cur_group = []
        has_header = False
        i = 0
        new_section_order = []
        new_sections = {}
        for name in decoded_sct.sect_list:

            section = decoded_sct.sects[name]
            if section.type == 'Label':
                new_section_order.append(name)
                has_header = True
                if cur_group_name != '':
                    decoded_sct.string_groups[cur_group_name] = cur_group
                    cur_group = []
                else:
                    if len(cur_group) > 0:
                        strs = '\n'.join(cur_group)
                        print(f'Strings present before string groups will not be assigned a group: {strs}')
                cur_group_name = section.name
            elif section.type == 'String':
                if not has_header:
                    if len(cur_group) > 0:
                        decoded_sct.string_groups[cur_group_name] = cur_group
                        cur_group = []
                    cur_group_name = f'Untitled({i})'
                    new_section_order.append(cur_group_name)
                    new_section = SCTSection()
                    new_section.set_name(cur_group_name)
                    new_section.set_details(0, section.absolute_offset)
                    new_sections[cur_group_name] = new_section
                    new_sections[cur_group_name].set_type('Label')
                    has_header = True
                    i += 1
                    print(
                        f'This string is not located contiguously under a label: {section.name}, new group created: {cur_group_name}')
                cur_group.append(section.name)
                decoded_sct.string_locations[section.name] = cur_group_name
                decoded_sct.strings[section.name] = section.string
                new_section_order.append(name)
            elif section.type == 'Script':
                has_header = False
                new_section_order.append(name)

        if has_header:
            decoded_sct.string_groups[cur_group_name] = cur_group

        for name in list(decoded_sct.string_groups.keys()):
            if len(decoded_sct.string_groups[name]) == 0:
                decoded_sct.string_groups.pop(name)

        new_sections_dict = {}
        new_sections_ungrouped = []
        for name in new_section_order:
            if name in decoded_sct.sects.keys():
                if decoded_sct.sects[name].type == 'String':
                    decoded_sct.string_garbage[name] = decoded_sct.sects[name].garbage
                    continue
                new_sections_dict[name] = decoded_sct.sects[name]
                new_sections_ungrouped.append(name)
                continue
            new_sections_dict[name] = new_sections[name]
            new_sections_ungrouped.append(name)
        decoded_sct.sects = new_sections_dict
        decoded_sct.sect_list = new_sections_ungrouped

    @staticmethod
    def _detect_unused_sections(decoded_sct: SCTScript):
        external_section_pattern = '^M[0-9]{4}$'
        called_sections = list(decoded_sct.links_to_sections.keys())
        special_sections = ['init', 'loop']
        string_group_keys = list(decoded_sct.string_groups.keys())
        for sect_name in decoded_sct.sects.keys():
            if sect_name in [*called_sections, *special_sections, *string_group_keys]:
                continue
            if re.search(external_section_pattern, sect_name):
                continue
            decoded_sct.unused_sections.append(sect_name)

    def _group_jump_commands(self, decoded_sct):
        for sect_name, jump_list in self._jmp_if_falses.items():
            sect_group = []
            if sect_name in decoded_sct.section_group_keys.keys():
                key = decoded_sct.section_group_keys[sect_name]
                group = decoded_sct.section_groups[key]
                for s_name in group[group.index(sect_name):]:
                    sect_group.append(s_name)
            else:
                sect_group.append(sect_name)
            sect_insts = []
            group_starts = {}
            for s in sect_group:
                insts = [decoded_sct.sects[s].insts[i] for i in
                         decoded_sct.sects[s].inst_list]
                group_starts[s] = len(sect_insts)
                sect_insts = [*sect_insts, *insts]

            for jmp_id in jump_list:
                jmp_inst: SCTInstruction = sect_insts[jmp_id]
                jmp_link = jmp_inst.links_out[0]
                jmp_to_sect_name = jmp_link.target_trace[0]
                jmp_to_id = jmp_link.target_trace[1]
                if jmp_to_id == 0:
                    prev_sect_id = sect_group.index(jmp_to_sect_name) - 1
                    prev_sect_name = sect_group[prev_sect_id]
                    prev_to_id = len(decoded_sct.sects[prev_sect_name].inst_list) - 1
                else:
                    prev_sect_name = jmp_to_sect_name
                    prev_to_id = jmp_to_id - 1

                prev_inst = decoded_sct.sects[prev_sect_name].get_instruction_by_index(prev_to_id)
                if not prev_inst.base_id == 10:
                    print(f'SCPT Decoder: Decode Jumps: No goto inst found: {sect_name}{sep}{jmp_id}')
                    continue

                jmp_inst.my_goto_uuids.append(prev_inst.ID)
                prev_inst.my_master_uuids.append(jmp_inst.ID)

                if sect_name not in self._instruction_groups:
                    self._instruction_groups[sect_name] = {}

                # Check for a loop and add to loops if true
                if prev_inst.params[0].value < 0:
                    group_key = f'{jmp_id}{sep}while'
                    self._instruction_groups[sect_name][group_key] = (f'{sect_name}{sep}{jmp_id}',
                                                                      f'{prev_sect_name}{sep}{prev_to_id}')
                    decoded_sct.sects[sect_name].jump_loops.append(group_key)

                    continue

                # else, get the end of the false option
                jmp_end_sect = prev_inst.links_out[0].target_trace[0]
                jmp_end_id = prev_inst.links_out[0].target_trace[1]

                group_key = f'{jmp_id}{sep}if'
                self._instruction_groups[sect_name][group_key] = (f'{sect_name}{sep}{jmp_id}',
                                                                  f'{prev_sect_name}{sep}{prev_to_id}')

                if jmp_to_id == jmp_end_id or jmp_to_sect_name != jmp_end_sect:
                    continue
                group_key = f'{jmp_id}{sep}else'
                self._instruction_groups[sect_name][group_key] = (
                    f'{jmp_to_sect_name}{sep}{jmp_to_id}', f'{jmp_end_sect}{sep}{jmp_end_id - 1}')

    def _group_switches(self, decoded_sct):

        # Go through each section and check for switches
        for sect_name, switch_ids in self._switches.items():
            sect_group = []
            if sect_name in decoded_sct.section_group_keys.keys():
                key = decoded_sct.section_group_keys[sect_name]
                group = decoded_sct.section_groups[key]
                for s_name in group[group.index(sect_name):]:
                    sect_group.append(s_name)
            else:
                sect_group.append(sect_name)
            section_insts: List[SCTInstruction] = []
            group_starts = {}
            for s in sect_group:
                insts = [decoded_sct.sects[s].insts[i] for i in
                         decoded_sct.sects[s].inst_list]
                group_starts[s] = len(section_insts)
                section_insts = [*section_insts, *insts]

            last_inst_pos = section_insts[-1].absolute_offset

            # Go through each switch in each section
            for s_id in switch_ids:
                # print(f'SCPT Decoder: Switch Groups: Grouping Switch: {sect_name}:{s_id}')
                switch_inst: SCTInstruction = section_insts[s_id]

                # Get all switch start positions
                num_entries = switch_inst.params[1].value
                switch_entry_target_poses = []
                switch_entry_cases = []
                for entry_id in range(num_entries):
                    switch_entry_target_poses.append(switch_inst.l_params[entry_id][3].link.target)
                    switch_entry_cases.append(switch_inst.l_params[entry_id][2].value)

                # Create a dicitonary with index for first instructions for each case
                switch_entry_start_ids: Dict[int, str] = {}
                start_sect_names: Dict[int, str] = {}
                for i, entry in enumerate(switch_entry_target_poses):
                    cur_id = self._get_inst_by_pos(section_insts, s_id, entry, sect_name, s_id)
                    start_sect = self._find_sect_in_group(group_starts, cur_id)
                    switch_entry_start_ids[cur_id] = switch_entry_cases[i]
                    start_sect_names[cur_id] = start_sect

                # Range of each switch entry should be from the start to the next start-1
                # For all entries except the last one, create instruction groups for switch entries
                # Then if the goto at the end of an entry is negative, it should be a loop, so add that entry to loops
                # If at least one is positive, record the goto, and the max goto should be the end of the last one
                if sect_name not in self._instruction_groups:
                    self._instruction_groups[sect_name] = {}
                prev_start = None
                prev_case = None
                prev_start_sect = None
                goto_jmp = None
                end_sect = None
                for inst_start, case in switch_entry_start_ids.items():
                    if prev_case is not None:
                        group_key = f'{s_id}{sep}{prev_case}'
                        end_sect = self._find_sect_in_group(group_starts, inst_start - 1)
                        s = prev_start - group_starts[prev_start_sect]
                        e = inst_start - group_starts[end_sect] - 1

                        self._instruction_groups[sect_name][group_key] = (
                            f'{prev_start_sect}{sep}{s}', f'{end_sect}{sep}{e}')

                        prev_inst: SCTInstruction = section_insts[inst_start - 1]
                        if prev_inst.base_id != 10:
                            continue

                        switch_inst.my_goto_uuids.append(prev_inst.ID)
                        prev_inst.my_master_uuids.append(switch_inst.ID)

                        if section_insts[inst_start - 1].params[0].value < 0:
                            decoded_sct.sects[sect_name].jump_loops.append(group_key)
                        elif section_insts[inst_start - 1].params[0].link.target <= last_inst_pos:
                            if goto_jmp is None:
                                goto_jmp = section_insts[inst_start - 1].params[0].link.target
                            else:
                                goto_jmp = max(goto_jmp, section_insts[inst_start - 1].params[0].link.target)

                    prev_start = inst_start
                    prev_case = case
                    prev_start_sect = start_sect_names[inst_start]

                # Find end of last swtich entry
                last_start = list(switch_entry_start_ids.keys())[-1]
                last_case = switch_entry_start_ids[last_start]

                # if an end for the last section was found previously, set it
                if goto_jmp is not None:
                    goto_tgt_ind = self._get_inst_by_pos(section_insts, last_start, goto_jmp, sect_name, switch_inst.ID)
                    group_key = f'{s_id}{sep}{last_case}'
                    self._instruction_groups[sect_name][group_key] = (
                        f'{prev_start_sect}{sep}{last_start}', f'{end_sect}{sep}{goto_tgt_ind-1}')
                    goto_inst = section_insts[goto_tgt_ind - 1]
                    switch_inst.my_goto_uuids.append(goto_inst.ID)
                    goto_inst.my_master_uuids.append(switch_inst.ID)
                    continue

                gotos_ignored = 0
                cur_id = last_start
                goto_found = False
                # else search for a goto that matches with the switch.
                # May be error prone if there are random gotos inside a switch entry
                while cur_id < len(section_insts):
                    cur_inst = section_insts[cur_id]
                    if cur_inst.base_id == 0:
                        cur_id = cur_inst.links_out[0].target_trace[1] - 1
                    elif cur_inst.base_id == 3:
                        new_last_case_target = cur_inst.l_params[-1][3].link.target
                        new_last_case_start = self._get_inst_by_pos(section_insts, cur_id, new_last_case_target, sect_name, switch_inst.ID)
                        cur_id = new_last_case_start
                        gotos_ignored += 1
                    elif cur_inst.base_id == 10:
                        if gotos_ignored > 0:
                            gotos_ignored -= 1
                        else:
                            goto_found = True
                            break
                    cur_id += 1
                    if cur_id == len(section_insts):
                        print(f'SCPT Decoder: Switch Groups: End of final switch entry not found: {sect_name}:{s_id}')

                if not goto_found:
                    cur_id -= 1

                group_key = f'{s_id}{sep}{last_case}'
                self._instruction_groups[sect_name][group_key] = (
                    f'{prev_start_sect}{sep}{last_start}', f'{end_sect}{sep}{cur_id}')
                if goto_found:
                    goto_inst = section_insts[cur_id]
                    switch_inst.my_goto_uuids.append(goto_inst.ID)
                    goto_inst.my_master_uuids.append(switch_inst.ID)

    @staticmethod
    def _group_subscripts(decoded_sct):
        sections = decoded_sct.sects
        script_filename = decoded_sct.name.split('.')[0]
        cur_group = ''
        suffix = ''
        in_group = False
        for sect_name, section in sections.items():

            if in_group and suffix in sect_name.lower():
                decoded_sct.section_groups[cur_group].append(sect_name)
            else:
                in_group = False

            if script_filename in sect_name and not in_group:
                in_group = True
                cur_group = f'{sect_name}{sep}group'
                suffix = sect_name[len(script_filename):].lower()
                if ')' in suffix:
                    suffix = suffix[:-3]
                decoded_sct.section_groups[cur_group] = []

            if section.type == 'Label':
                in_group = False

        empty_sections = []
        for name, group in decoded_sct.section_groups.items():
            if len(group) == 0:
                empty_sections.append(name)

        for name in empty_sections:
            decoded_sct.section_groups.pop(name)

    def _create_group_heirarchies(self, decoded_sct):

        # Create grouped section heirarchy
        groups = decoded_sct.section_groups

        if len(groups) > 0:
            # sort groups by size with the smallest first
            groups = {k: groups[k] for k in sorted(groups.keys(), key=lambda k: len(groups[k]))}

            new_groups = self._nest_groups(groups)
            new_groups = self._complete_heirarchy(list(decoded_sct.sects.keys()), new_groups)
            decoded_sct.sect_tree = new_groups
        else:
            decoded_sct.sect_tree = copy.deepcopy(decoded_sct.sect_list)

        # Create grouped instruction heirarchies
        for section in decoded_sct.sects.values():
            if section.name not in self._instruction_groups:
                section.inst_tree = copy.deepcopy(section.inst_list)
                continue
            inst_groups = self._instruction_groups[section.name]

            inst_groups = {k: [*range(int(v[0].split(sep)[1]), int(v[1].split(sep)[1]) + 1)]
                           for k, v in inst_groups.items()}
            new_groups = self._nest_groups(inst_groups, is_sections=False)
            new_groups = self._complete_heirarchy(list(range(len(section.insts))), new_groups)
            new_groups = self._remove_duplicate_inst_locations(new_groups)
            new_groups = self._resolve_switches(new_groups)
            new_groups = self._replace_pos_with_ids(new_groups, section.inst_list)
            section.inst_tree = new_groups

    def _nest_groups(self, groups, is_sections=True):
        # replace entries in parent groups with child groups
        new_groups = copy.deepcopy(groups)
        for group_name, group in groups.items():
            group = new_groups[group_name]
            insert_keys = []

            for n_group_name, n_group in new_groups.items():
                if group_name == n_group_name:
                    continue
                all_present = True
                for entry in group:
                    if not self._is_in(entry, n_group):
                        all_present = False
                        break
                if all_present:
                    insert_keys.append(n_group_name)

            for key in insert_keys:
                insert_index = new_groups[key].index(new_groups[group_name][0])
                for entry in group:
                    new_groups[key].remove(entry)
                new_groups[key].insert(insert_index, group_name)

        done = False
        all_group_keys = list(new_groups.keys())
        cur_group_ind = 0
        while not done:
            cur_group_key = all_group_keys[cur_group_ind]
            new_groups = self._replace_group_name_with_group(new_groups, cur_group_key)

            # goto next key
            cur_group_ind += 1
            if cur_group_ind >= len(all_group_keys):
                break

            # if next key is not in new groups, find next key which is present
            while all_group_keys[cur_group_ind] not in new_groups.keys():
                cur_group_ind += 1
                if cur_group_ind >= len(all_group_keys):
                    done = True
                    break

        return new_groups

    def _replace_group_name_with_group(self, all_groups, cur_group_key):
        cur_group = all_groups[cur_group_key]
        new_groups = copy.deepcopy(all_groups)
        for i, entry in enumerate(cur_group):
            if entry == cur_group_key:
                continue
            if isinstance(entry, str) and entry in new_groups.keys():
                new_groups = self._replace_group_name_with_group(new_groups, entry)
                new_groups[cur_group_key].insert(i, {entry: new_groups[entry]})
                new_groups[cur_group_key].pop(i+1)
                new_groups.pop(entry)

        return new_groups

    def _is_in(self, entry, group):
        if isinstance(entry, dict):
            for entry_key, entry_value in entry.items():
                key_present = False
                value_present = False
                for obj in group:
                    if not isinstance(obj, dict):
                        continue
                    if entry_key in obj.keys():
                        key_present = True
                        if self._is_in(entry_value, obj[entry_key]):
                            value_present = True
                            break
                        return False
                if not key_present or not value_present:
                    return False
            return True

        if isinstance(entry, list):
            if not isinstance(group, list):
                return False
            for entry_item in entry:
                if not self._is_in(entry_item, group):
                    return False
            return True

        return entry in group

    def _complete_heirarchy(self, full_list, groups):
        heirarchy = []
        skips = []
        for entry in full_list:
            if entry in skips:
                continue
            matching_groups = []
            for key in groups.keys():
                if str(entry) == key.split(sep)[0]:
                    matching_groups += [{key: groups[key]}]
            if len(matching_groups) == 0:
                heirarchy.append(entry)
                continue
            heirarchy = heirarchy + matching_groups
            skips.extend(self._get_heirarchy_skips(matching_groups))
        return heirarchy

    def _get_heirarchy_skips(self, group, skips=None):
        if skips is None:
            skips = []
        if isinstance(group, dict):
            for entry in group.values():
                self._get_heirarchy_skips(entry, skips)
        elif isinstance(group, list):
            for entry in group:
                self._get_heirarchy_skips(entry, skips)
        else:
            skips.append(group)
        return skips

    def _resolve_switches(self, inst_list):
        switches = {}
        for i, entry in enumerate(inst_list):
            if not isinstance(entry, dict):
                continue
            inst_list[i][list(entry.keys())[0]] = self._resolve_switches(list(entry.values())[0])
            if list(entry.keys())[0].split(sep)[1].lstrip('-').isnumeric():
                switch_key = list(entry.keys())[0].split(sep)[0] + f'{sep}switch'
                if switch_key not in switches.keys():
                    switches[switch_key] = []
                switches[switch_key].append(i)
        if len(switches) > 0:
            for switch_key, switch_entries in reversed(switches.items()):
                inst_list = self._reorganize_switch(switch_key, switch_entries, inst_list)
        return inst_list

    def _remove_duplicate_inst_locations(self, new_groups):
        key_insts = self._get_key_insts(new_groups)
        return self._remove_key_insts(new_groups, key_insts)

    def _get_key_insts(self, group, key_insts=None):
        if key_insts is None:
            key_insts = []
        if not isinstance(group, list):
            return key_insts
        for entry in group:
            if not isinstance(entry, dict):
                continue
            for key, value in entry.items():
                key_insts.append(int(key.split(sep)[0]))
                key_insts = self._get_key_insts(value, key_insts)
        return key_insts

    def _remove_key_insts(self, group, key_insts):
        if not isinstance(group, list):
            return group
        for inst in key_insts:
            if inst in group:
                group.remove(inst)
        new_entries = []
        for i, entry in enumerate(group):
            if not isinstance(entry, dict):
                continue
            new_entry = {}
            for key, value in entry.items():
                new_entry[key] = self._remove_key_insts(value, key_insts)
            new_entries.append((i, new_entry))
        for entry in new_entries:
            group.insert(entry[0], entry[1])
            group.pop(entry[0] + 1)
        return group

    @staticmethod
    def _reorganize_switch(switch_key, switch_entries, inst_list: list):
        first_entry = min(switch_entries)
        switch = {}
        for i in switch_entries:
            entry = inst_list[i]
            entry_key = list(entry.keys())[0].split(sep)[1]
            entry_value = list(entry.values())[0]
            switch[entry_key] = entry_value
        for i in reversed(switch_entries):
            inst_list.pop(i)
        inst_list.insert(first_entry, {switch_key: switch})
        return inst_list

    @staticmethod
    def _get_inst_by_pos(inst_list, start_ind, target_pos, origin_sect_name, origin_element_id):
        cur_ind = start_ind
        found = False
        while cur_ind < len(inst_list):
            cur_inst = inst_list[cur_ind]
            if cur_inst.absolute_offset == target_pos:
                found = True
                break
            if cur_inst.absolute_offset < target_pos < inst_list[cur_ind + 1].absolute_offset:
                print(
                    f'SCPT Decoder: Find Inst: Target pos in middle of entry {origin_sect_name}:{origin_element_id} - {target_pos}')
                break
            cur_ind += 1

        if not found:
            print(
                f'SCPT Decoder: Find Inst: Entry not found: {origin_sect_name}:{origin_element_id} - {target_pos}')
            return None

        return cur_ind

    def _replace_pos_with_ids(self, group, instruction_ids_ungrouped):
        if isinstance(group, dict):
            new_groups = {}
            for key, value in group.items():
                if sep in key:
                    key_split = key.split(sep)
                    key = f'{instruction_ids_ungrouped[int(key_split[0])]}{sep}' + sep.join(key_split[1:])
                new_groups[key] = self._replace_pos_with_ids(value, instruction_ids_ungrouped)
        elif isinstance(group, list):
            new_groups = []
            for entry in group:
                new_groups.append(self._replace_pos_with_ids(entry, instruction_ids_ungrouped))
        else:
            new_groups = instruction_ids_ungrouped[group]
        return new_groups

    @staticmethod
    def _find_sect_in_group(group_starts, cur_id):
        group = None
        for g, p in reversed(group_starts.items()):
            if cur_id > p:
                group = g
                break
        return group

    def _get_links_to_change(self, section, start_inst_list_id):
        sect_name = section.name
        changes = {'links': [], 'switches': [], 'jmps': [], 'sect_name': sect_name}

        # Get links that should be changed
        for link in [*self._scpt_links, *self._str_foot_links, *self._str_sect_links]:
            if link.origin_trace[0] != sect_name:
                continue
            if link.origin_trace[1] < start_inst_list_id:
                continue
            changes['links'].append(link)

        # Get switch ids that should be changed
        if sect_name in self._switches:
            pop_entries = []
            for i, entry in enumerate(self._switches[sect_name]):
                if entry >= start_inst_list_id:
                    pop_entries.append(i)
                    changes['switches'].append(entry)
            for i in reversed(pop_entries):
                self._switches[sect_name].pop(i)

        # Get jmp ids that should be changed
        if sect_name in self._jmp_if_falses:
            pop_entries = []
            for i, entry in enumerate(self._jmp_if_falses[sect_name]):
                if entry >= start_inst_list_id:
                    pop_entries.append(i)
                    changes['jmps'].append(entry)
            for i in reversed(pop_entries):
                self._jmp_if_falses[sect_name].pop(i)

        return changes

    def _set_changes(self, changes, offset):

        for link in changes['links']:
            link.origin_trace[1] += offset

        for i in changes['switches']:
            self._switches[changes['sect_name']].append(i + offset)

        for i in changes['jmps']:
            self._jmp_if_falses[changes['sect_name']].append(i + offset)

    # ---------------------------------------------------------- #
    # Add useful fields for script manipulation and organization #
    # ---------------------------------------------------------- #

    def _finalize_sct(self, decoded_sct):

        self._setup_variables(decoded_sct)

        print(f'{self.log_key}: {decoded_sct.name} finished')

    def _setup_variables(self, sct):
        for s_name, section in sct.sects.items():
            for inst_key, inst in section.insts.items():
                for pID, param in inst.params.items():
                    if isinstance(param.value, dict):
                        var_list = self._extract_variables(param.value)
                        self._add_variable_locations(var_list, (s_name, inst_key, f'{pID}'))
                for loop_id, loop in enumerate(inst.l_params):
                    for pID, param in loop.items():
                        if isinstance(param.value, dict):
                            var_list = self._extract_variables(param.value)
                            self._add_variable_locations(var_list, (s_name, inst_key, f'{loop_id}{sep}{pID}'))

        sct.variables = self._variables

    def _extract_variables(self, cur_element, var_list=None):
        if var_list is None:
            var_list = []
        if isinstance(cur_element, dict):
            for value in cur_element.values():
                var_list = self._extract_variables(value, var_list=var_list)
        elif isinstance(cur_element, str):
            if 'Var:' in cur_element:
                var_list.append(cur_element)
        return var_list

    def _add_variable_locations(self, var_list, trace):
        for var in var_list:
            keys = var.split(': ')
            if keys[0] not in self._variables.keys():
                self._variables[keys[0]] = {}
            key_1 = int(keys[1])
            if key_1 not in self._variables[keys[0]]:
                self._variables[keys[0]][key_1] = {'alias': '', 'usage': []}
            self._variables[keys[0]][key_1]['usage'].append(trace)

    @staticmethod
    def _put_inst_ids_into_link_traces(decoded_sct):
        for section in decoded_sct.sects.values():
            for key, inst in section.insts.items():
                inst: SCTInstruction
                for link in inst.links_in:
                    link.target_trace[1] = key
                for link in inst.links_out:
                    link.origin_trace[1] = key

    @staticmethod
    def _populate_ungrouped_inst_values(decoded_sct):
        for section in decoded_sct.sects.values():
            for i, key in enumerate(section.inst_list):
                section.insts[key].ungrouped_position = i

    def _detect_and_move_footer_dialog(self, decoded_sct):
        if len(self._footer_dialog_locs) == 0:
            return

        footer_dialog_strings = []
        for trace in self._footer_dialog_locs:
            inst = decoded_sct.sects[trace[0]].insts[trace[1]]
            string = inst.params[int(inst.links_out[0].origin_trace[2])].linked_string
            if '\\e' in string or '\\c' in string:
                footer_dialog_strings.append((trace, string))

        if len(footer_dialog_strings) == 0:
            return

        decoded_sct.string_groups[footer_str_group_name] = []
        for i, item in enumerate(footer_dialog_strings):
            foot_id = f'{footer_str_id_prefix}{i:03d}'
            decoded_sct.strings[foot_id] = item[1]
            decoded_sct.string_groups[footer_str_group_name].append(foot_id)
            decoded_sct.string_locations[foot_id] = footer_str_group_name
            inst = decoded_sct.sects[item[0][0]].insts[item[0][1]]
            param = inst.params[int(inst.links_out[0].origin_trace[2])]
            param.linked_string = foot_id
