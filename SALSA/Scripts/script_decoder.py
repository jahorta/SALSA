import copy
import os
import re
import struct
from typing import Dict, Tuple, List, Callable

from BaseInstructions.bi_facade import BaseInstLibFacade
from Project.project_container import SCTScript, SCTSection, SCTLink, SCTInstruction, SCTParameter
from SALSA.BaseInstructions.bi_container import BaseInstLib, BaseParam
from SALSA.Scripts.scpt_param_codes import SCPTParamCodes
from SALSA.Common.byte_array_utils import word2SignedInt, is_a_number, pad_hex, applyHexMask
from SALSA.Scripts import scpt_arithmetic_fxns as scpt_arithmetic, scpt_compare_fxns as scpt_compare

ind_entry_len = 0x14
ind_name_offset = 0x4
ind_name_max_len = 0x10

endian = {'gc': 'big', 'dc': 'little'}


class SCTDecoder:
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
    _cur_endian = endian['gc']

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

    @classmethod
    def decode_sct_from_file(cls, name, sct, inst_lib: BaseInstLibFacade):
        sct_decoder = cls()
        decoded_sct = sct_decoder._decode_sct(name, sct, inst_lib)
        sct_decoder._organize_sct(decoded_sct)
        return decoded_sct

    def _init(self):
        self._str_sect_links = []
        self._str_foot_links = []
        self._scpt_links = []
        self._index = {}
        self._jmp_if_falses = {}
        self._switches = {}

    def _decode_sct(self, script_name: str, sct: bytearray, inst_lib: BaseInstLibFacade) -> SCTScript:
        self._init()
        self._name = script_name
        self._sct = sct
        self._inst_lib = inst_lib
        self._p_codes = SCPTParamCodes(is_decoder=True)

        header = self._sct[:8]
        ind_entries: int = int.from_bytes(self._sct[8:12], byteorder=self._cur_endian)
        self._sct = self._sct[12:]
        self._index = {}
        for i in range(ind_entries):
            start = self.getInt(pos=i * ind_entry_len)
            sect_name = self.getString(pos=i * ind_entry_len + ind_name_offset, max_len=ind_name_max_len)
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
            print(f'SCTDecoder: Decoding {sect_name}...', end='\r')
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
                        raise EOFError('Final Section was not a String...')
                bounds = (bounds[0], footer_start + 4)

            new_section = self._decode_sct_section(sect_name, bounds)

            # Create or add to a logical section group if needed
            if not in_sect_group:
                if new_section.type == 'Script':
                    if new_section.instructions[-1].inst_id != 12:
                        in_sect_group = True
                        sect_group_key = sect_name
                        decoded_sct.section_groups[sect_group_key] = [sect_name]
                        decoded_sct.section_group_keys[sect_name] = sect_group_key
            else:
                if new_section.type == 'Script':
                    decoded_sct.section_groups[sect_group_key].append(sect_name)
                    decoded_sct.section_group_keys[sect_name] = sect_group_key
                    last_inst = new_section.instructions[-1]
                    if last_inst.inst_id == 12:
                        in_sect_group = False
                        sect_group_key = None
                else:
                    in_sect_group = False
                    sect_group_key = None

            decoded_sct.add_section(new_section)

        print('SCTDecoder: All sections decoded!!!')

        self.section_group_keys = {}

        return decoded_sct

    def _decode_sct_section(self, sect_name, bounds) -> SCTSection:

        sct_start_pos = bounds[0]
        length = bounds[1] - bounds[0]
        section = SCTSection(name=sect_name, length=length, pos=sct_start_pos)
        self._cursor = int(sct_start_pos / 4)

        if length == 16:
            section.set_type('Label')
            return section

        if self.test_for_string():
            currWord = self.getInt(self._cursor * 4)
            while not currWord == 0x0000001d:
                self._cursor += 1
                currWord = self.getInt(self._cursor * 4)
            self._cursor += 1
            string = self.getString(self._cursor * 4, encoding=self._enc)
            if string == '':
                section.add_error('Length of string == 0')
            section.set_type('String')
            section.add_string(self._cursor * 4, string)
            return section

        else:
            section.set_type('Script')

        section = self._create_insts_from_region(bounds, section, 0)

        return section

    def _create_insts_from_region(self, bounds, section: SCTSection, inst_list_id_start):
        self._cursor = bounds[0] // 4
        self.end = bounds[1]
        inst_list_id = inst_list_id_start
        sect_name = section.name
        sct_start_pos = section.start_offset

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
                try_no_refresh = False
                if currWord_int == 0x0000000d:
                    try_no_refresh = True
                    self._cursor += 1
                    currWord_int = self.getInt(self._cursor * 4)
                instResult = self._decode_instruction(currWord_int, inst_pos, sct_start_pos, [sect_name, inst_list_id])
                cur_inst = self._inst_lib.get_inst(instResult.inst_id)
                if try_no_refresh and not cur_inst.forced_new_frame:
                    instResult.set_skip_refresh()
                section.add_instruction(instResult)

                if instResult.inst_id == 3:
                    if sect_name not in self._switches.keys():
                        self._switches[sect_name] = []
                    self._switches[sect_name].append(inst_list_id)

                if instResult.inst_id == 0:
                    if sect_name not in self._jmp_if_falses.keys():
                        self._jmp_if_falses[sect_name] = []
                    self._jmp_if_falses[sect_name].append(inst_list_id)

                if instResult.inst_id == 0x3:
                    # Check for garbage before first entry
                    switch_start = (self._cursor + len(instResult.parameters))
                    min_case_start = None
                    switch_end = switch_start + (len(instResult.loop_parameters) * 2)
                    for i, paramset in enumerate(instResult.loop_parameters):
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
                        raise IndexError('SCPT Decoder: Switch incomplete, switch end < min case start')

                if instResult.inst_id == 0xc:
                    end_cursor = bounds[1] // 4
                    if self._cursor < end_cursor:
                        next_inst = self.getInt(self._cursor * 4)
                        if not ((0 < next_inst < 265) or (next_inst in [4, 8])):
                            section.add_error('Garbage: garbage instruction after return')
                            self._cursor += 1
                            garbage = bytearray(b'')
                            while self._cursor < end_cursor:
                                garbage += self.getWord(self._cursor * 4)
                                self._cursor += 1
                            section.add_garbage('End', garbage)

                if instResult.inst_id == 0xa:
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
                                        mask = self._inst_lib.lib.insts[next_i_id].parameters[0].mask
                                        p1 = param1_code
                                        p1_little = param1_code_little
                                        if mask is not None:
                                            p1 = int(applyHexMask(hex(p1), hex(mask)), 16)
                                            p1_little = int(applyHexMask(hex(p1_little), hex(mask)), 16)
                                        if self._inst_lib.lib.insts[next_i_id].parameters[0].isSigned:
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
                    error_str = f'SCPT Decoder: Extra SCPT parameter found:\n\tSCPT Position: {cur_pos}'
                    error_str += f'\n\tAbsolute Position: {absolute_pos}'
                    error_str += f'\n\tPrevious Instruction: {section.instructions[-1].inst_id}'
                    error_str += f'\n\tLength: {length}\n\tParam: {param.hex()}'

                else:
                    error_str = f'SCPT Decoder: Unknown Instruction Code:\n\tInstruction code: {param.hex()}'
                    error_str += f'\n\tSubscript: {cur_pos}\n\tInstruction List Index: {inst_list_id}'
                    error_str += f'\n\tPrevious Instruction: {section.instructions[-1].inst_id}'
                    error_str += f'\n\tSCPT Position: {cur_pos}\n\tAbsolute Position: {absolute_pos}'

                raise IndexError(error_str)

            # self.cursor += 1

            if (self._cursor * 4) > bounds[1]:
                error = f'SCPT Decoder: Read cursor is past the end of current subscript: {sect_name}'
                raise IndexError(error)

            if self._cursor > self._sctLength:
                raise EOFError(f'SCPT Decoder: Read cursor is past the end of the file')

        return section

    def _decode_instruction(self, inst_id, inst_pos, sct_start_pos, trace):
        cur_inst = SCTInstruction(script_pos=sct_start_pos, inst_pos=inst_pos, inst_id=inst_id)
        base_inst = self._inst_lib.get_inst(inst_id=inst_id)
        self._cursor += 1

        # decode parameters
        parameters = copy.deepcopy(base_inst.parameters)
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
                cur_inst.links.append(param.link)
            cur_inst.add_parameter(p_id, param)
            used_params.append(p_id)
            cur_param_num += 1

        for p in used_params:
            parameters.pop(p)

        willLoop = True
        if base_inst.loop_cond is not None:
            l_c = base_inst.loop_cond
            if l_c['Location'] == 'External':
                if self._loop_cond_tests[l_c['Test']](cur_inst.parameters[l_c['Parameter']].value, l_c['Value']):
                    willLoop = False

        if hasLoop and willLoop:
            max_iter = cur_inst.parameters[base_inst.loop_iter].value
            cur_iter = 0
            done = False
            while not done and cur_iter < max_iter:
                param_group = {}
                for p in loop_parameters:
                    param = self._decode_param(p, [*trace, f'{cur_iter}-{p.paramID}'])
                    param_group[p.paramID] = param
                    if param.link is not None:
                        cur_inst.links.append(param.link)

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
                cur_inst.links.append(param.link)

        return cur_inst

    def _decode_param(self, base_param: BaseParam, trace):
        cur_param = SCTParameter(_id=base_param.paramID, _type=base_param.type)
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

            if base_param.default_value is not None:
                overrideResult = base_param.default_value

            scriptCompare = self.getInt(self._cursor * 4)
            if scriptCompare in overrideCompare:
                cur_param.set_value(overrideResult)
                self._cursor += 1
                return cur_param

            scptResult = self._SCPT_analyze(cur_param)
            done = False
            if isinstance(scptResult, dict) or isinstance(scptResult, bytearray):
                done = True
            elif isinstance(scptResult, str):
                if not is_a_number(scptResult):
                    done = True
                else:
                    scptResult = float(scptResult)
            elif scptResult is None:
                done = True
                cur_param.add_error('Error: No value generated...')

            if not done:
                if 'int' in param_type:
                    scptResult = int(scptResult)
                elif 'short' in param_type:
                    scptResult = int(scptResult) & 0xffff
                elif 'byte' in param_type:
                    scptResult = int(scptResult) & 0xff

            cur_param.set_value(scptResult)

        elif param_type == 'int':
            currWord = self.getWord(self._cursor * 4)
            if self._cur_endian == 'little':
                currWord = bytearray(reversed(currWord))
            raw = currWord
            cur_param.add_raw(raw)
            if base_param.mask is not None:
                cur_param.type += '-masked'
                mask = base_param.mask
                currWord = bytearray.fromhex(applyHexMask(currWord.hex(), hex(mask))[2:])
            if base_param.isSigned:
                cur_param.type += '-signed'
                cur_value = word2SignedInt(currWord, swap_endian=(self._cur_endian == 'little'))
            else:
                cur_value = int.from_bytes(currWord, byteorder=self._cur_endian)
            cur_param.set_value(cur_value)
            if base_param.link_type is not None:
                link_type = base_param.link_type
                origin = self._cursor * 4
                target = self._cursor * 4 + cur_value
                newLink = SCTLink(type=link_type, origin=origin, target=target, trace=trace)
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
        if int.from_bytes(currentWord, byteorder=self._cur_endian) in self._p_codes.no_loop:
            param.add_raw(raw)
            self._cursor += 1
            return currentWord

        raw = bytearray(b'')
        # Resolve the SCPT analysis
        result_stack = [None] * 20
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
                result_stack[stack_index] = cur_result
                stack_index -= 1
                if currentWord == 0x0000000a:
                    stack_index += 1
            elif currentWord in self._p_codes.arithmetic.keys():
                currVals = {'1': result_stack[stack_index], '2': result_stack[stack_index + 1]}
                inputs = []
                cur_result = {self._p_codes.arithmetic[currentWord]: currVals}
                for v in currVals.values():
                    if isinstance(v, str):
                        v = str(v)
                        if is_a_number(v):
                            inputs.append(v)
                    elif not (isinstance(v, dict) or isinstance(v, bytearray) or v is None):
                        inputs.append(v)
                if len(inputs) == 2:
                    result = self._scpt_arithmetic_fxns[self._p_codes.arithmetic[currentWord][3]](inputs[0], inputs[1])
                    result_stack[stack_index] = result
                else:
                    result_stack[stack_index] = cur_result
                stack_index -= 1

            # If not, current action is to input a value
            else:
                action = None

                # Determine the input type from the input_cutoffs table
                for key in self._p_codes.input_cutoffs.keys():
                    if currentWord >= key:
                        action = key
                        break

                # Resolve Input
                if not action == 0x50000000:
                    # Generate values from current word
                    if action is None:
                        cur_result = 'Unable to interpret SCPT instruction: {}'.format(currentWord)
                        continue
                    result = None
                    if action == 0x04000000:
                        self._cursor += 1
                        word = self.getWord(self._cursor * 4)
                        if self._cur_endian == 'little':
                            word = list(reversed(word))
                        raw.extend(word)
                        result = self.getFloat(self._cursor * 4)
                    elif action == 0x08000000:
                        obtainedValue = currentWord & 0xffff00
                        obtainedValue += (currentWord & 0xff) / 256
                        result = obtainedValue
                    else:
                        obtainedValue = currentWord & 0x00ffffff
                        result = self._p_codes.input_cutoffs[action] + f'{obtainedValue}'
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
                        offset = masked_currentWord * 4
                        cur_result = self._p_codes.input_cutoffs[action] + f'{offset}'
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
        return str_bytes.decode(encoding=encoding, errors='backslashreplace')

    def getWord(self, pos) -> bytearray:
        return self._sct[pos: pos + 4]

    # -------------------------- #
    # Organize newly decoded sct #
    # -------------------------- #
    def _organize_sct(self, decoded_sct) -> SCTScript:

        # Setup links
        print('SCPT Decoder: Setting Up Links...')
        done = False
        while not done:
            done = self._setup_scpt_links(decoded_sct)

        self._resolve_scpt_links(decoded_sct)
        self._setup_string_links(decoded_sct)

        self._detect_unused_sections(decoded_sct)

        # Group strings
        print('SCPT Decoder: Creating String Groups...')
        self._create_string_groups(decoded_sct)

        # Group jump if false commands
        print('SCPT Decoder: Creating Jump Groups...')
        self._group_jump_commands(decoded_sct)

        # Group switches
        print('SCPT Decoder: Creating Switch Groups...')
        self._group_switches(decoded_sct)

        # Prune logical script groups with a single entry
        groups_to_remove = []
        for key, group in decoded_sct.section_groups.items():
            if len(group) < 2:
                groups_to_remove.append(key)
        for group in groups_to_remove:
            decoded_sct.section_groups.pop(group)

        # Group Subscripts
        print('SCPT Decoder: Setting Up Links...')
        self._group_subscripts(decoded_sct)

        self._create_group_heirarchies(decoded_sct=decoded_sct)

        return decoded_sct

    def _setup_scpt_links(self, decoded_sct):
        blank_section = SCTSection('', 0, 0)
        sect_keys = list(decoded_sct.sections.keys())
        self.successful_scpt_links = []
        for link in self._scpt_links:
            target_sct = blank_section
            target_sct_id = 0
            while target_sct_id < len(decoded_sct.sections):
                section = decoded_sct.sections[sect_keys[target_sct_id]]
                if section.start_offset <= link.target < section.start_offset + section.length:
                    target_sct: SCTSection = section
                    break
                target_sct_id += 1
            target_inst_id = 0
            while target_inst_id < len(target_sct.instructions):
                inst = target_sct.instructions[target_inst_id]
                if inst.inst_pos == link.target:
                    break
                if target_inst_id == len(target_sct.instructions) - 1:
                    inst_end = target_sct.start_offset + target_sct.length
                else:
                    inst_end = target_sct.instructions[target_inst_id + 1].inst_pos
                if inst.inst_pos < link.target < inst_end:
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
                        new_error = e[1][first_start - inst.inst_pos:link.target - inst.inst_pos]
                        error_ind = i
                        break

                    if new_error is not None:
                        if len(new_error) > 0:
                            inst.errors[error_ind] = ('Garbage', new_error)
                        else:
                            inst.errors.pop(error_ind)

                    if internal:
                        print(
                            f'link position is internal to an instruction at {target_sct.name}:{target_inst_id}: \n\t{link}')
                        decoded_sct.errors.append(
                            f'link position is internal to an instruction at {target_sct.name}:{target_inst_id}: \n\t{link}')
                        break

                    bounds = (link.target, inst_end)
                    suffix_insts = target_sct.instructions[target_inst_id + 1:]
                    target_sct.instructions = target_sct.instructions[:target_inst_id + 1]
                    insts_before = len(target_sct.instructions)
                    changes = self._get_links_to_change(target_sct, insts_before)
                    target_sct = self._create_insts_from_region(bounds, target_sct, target_inst_id + 1)
                    insts_added = len(target_sct.instructions) - insts_before
                    self._set_changes(changes, insts_added)
                    target_sct.instructions += suffix_insts
                    print(
                        f'New instructions decoded at {target_sct.name}:{target_inst_id + 1}. Restarting Link setup...')
                    return False
                    # print(f'link position is incorrect: \n\t{link}')
                    # decoded_sct.errors.append(f'link position is incorrect: {link}')
                    # raise ValueError(f'link position is incorrect: \n\t{link}')
                    # break
                target_inst_id += 1
            origin_inst = decoded_sct.sections[link.trace[0]].instructions[link.trace[1]]
            link_value = ('SCT', f'{target_sct.name}-{target_inst_id}')
            self.successful_scpt_links.append((link, origin_inst, link_value))
            link.target_trace = [target_sct.name, target_inst_id]

        return True

    def _resolve_scpt_links(self, decoded_sct: SCTScript):
        for link in self.successful_scpt_links:
            link, origin_inst, link_value = link
            if '-' in link.trace[2]:
                p_trace = link.trace[2].split('-')
                loop = int(p_trace[0])
                param_i = int(p_trace[1])
                param: SCTParameter = origin_inst.loop_parameters[loop][param_i]
                param.link_value = link_value
            else:
                param_i = int(link.trace[2])
                param: SCTParameter = origin_inst.parameters[param_i]
                param.link_value = link_value

            # add to dict with places that subscripts are called from
            if link.trace[0] != link.target_trace[0]:
                tr_sect = link.trace[0]
                target_tr_sect = link.target_trace[0]
                if target_tr_sect not in decoded_sct.links_to_sections.keys():
                    decoded_sct.links_to_sections[target_tr_sect] = []
                if tr_sect not in decoded_sct.links_to_sections[target_tr_sect]:
                    decoded_sct.links_to_sections[target_tr_sect].append(tr_sect)

    def _setup_string_links(self, decoded_sct):
        # setup string links
        sect_keys = list(decoded_sct.sections.keys())
        for link in self._str_sect_links:
            target_sct_str = ''
            target_sct_id = 0
            while target_sct_id < len(decoded_sct.sections):
                section = decoded_sct.sections[sect_keys[target_sct_id]]
                if link.target == section.start_offset:
                    target_sct_str = section.name
                    break
                if target_sct_id == len(decoded_sct.sections) - 1:
                    sect_end = section.start_offset + section.length
                else:
                    sect_end = decoded_sct.sections[sect_keys[target_sct_id + 1]].start_offset
                if section.start_offset < link.target < sect_end:
                    print(f'link position is incorrect: \n\t{link}')
                    break
                target_sct_id += 1
            origin_inst = decoded_sct.sections[link.trace[0]].instructions[link.trace[1]]
            param: SCTParameter = origin_inst.parameters[int(link.trace[2])]
            param.link_value = ('String', target_sct_str)

        # setup footer links
        for link in self._str_foot_links:
            foot_str = self.getString(link.target)
            f_ind = decoded_sct.add_footer_entry(foot_str)
            origin_inst = decoded_sct.sections[link.trace[0]].instructions[link.trace[1]]
            param: SCTParameter = origin_inst.parameters[int(link.trace[2])]
            param.link_value = ('Footer', f_ind)

    @staticmethod
    def _create_string_groups(decoded_sct):
        cur_group_name = ''
        cur_group = []
        has_header = False
        for name, section in decoded_sct.sections.items():
            if section.type == 'Label':
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
                    print(f'This string is not located contiguously under a label: {section.name}')
                cur_group.append(section.name)
                decoded_sct.strings[section.name] = section.string
            elif section.type == 'Script':
                has_header = False

    @staticmethod
    def _detect_unused_sections(decoded_sct: SCTScript):
        external_section_pattern = '^M[0-9]{4}$'
        called_sections = list(decoded_sct.links_to_sections.keys())
        special_sections = ['init', 'loop']
        string_group_keys = list(decoded_sct.string_groups.keys())
        for sect_name in decoded_sct.sections.keys():
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
                insts = decoded_sct.sections[s].instructions
                group_starts[s] = len(sect_insts)
                sect_insts = [*sect_insts, *insts]

            for jmp_id in jump_list:
                jmp_inst: SCTInstruction = sect_insts[jmp_id]
                jmp_link = jmp_inst.links[0]
                jmp_to_sect_name = jmp_link.target_trace[0]
                jmp_to_id = jmp_link.target_trace[1]
                if jmp_to_id == 0:
                    prev_sect_id = sect_group.index(jmp_to_sect_name) - 1
                    prev_sect_name = sect_group[prev_sect_id]
                    prev_to_id = len(decoded_sct.sections[prev_sect_name].instructions) - 1
                else:
                    prev_sect_name = jmp_to_sect_name
                    prev_to_id = jmp_to_id - 1

                prev_inst = decoded_sct.sections[prev_sect_name].instructions[prev_to_id]
                if not prev_inst.inst_id == 10:
                    print(f'SCPT Decoder: Decode Jumps: No goto inst found: {sect_name}-{jmp_id}')
                    continue

                # Check for a loop and add to loops if true
                if prev_inst.parameters[0].value < 0:
                    group_key = f'{jmp_id}-while'
                    decoded_sct.sections[sect_name].instructions_grouped[group_key] = (f'{sect_name}-{jmp_id}',
                                                                                     f'{prev_sect_name}-{prev_to_id}')
                    decoded_sct.sections[sect_name].jump_loops.append(group_key)
                    continue

                # else, get the end of the false option
                jmp_end_sect = prev_inst.links[0].target_trace[0]
                jmp_end_id = prev_inst.links[0].target_trace[1]

                group_key = f'{jmp_id}-if'
                decoded_sct.sections[sect_name].instructions_grouped[group_key] = (f'{sect_name}-{jmp_id}',
                                                                                 f'{prev_sect_name}-{prev_to_id}')
                if jmp_to_id == jmp_end_id:
                    continue
                group_key = f'{jmp_id}-else'
                decoded_sct.sections[sect_name].instructions_grouped[group_key] = (f'{jmp_to_sect_name}-{jmp_to_id}',
                                                                                 f'{jmp_end_sect}-{jmp_end_id}')

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
            section_insts = []
            group_starts = {}
            for s in sect_group:
                insts = decoded_sct.sections[s].instructions
                group_starts[s] = len(section_insts)
                section_insts = [*section_insts, *insts]

            # Go through each switch in each section
            for s_id in switch_ids:
                # print(f'SCPT Decoder: Switch Groups: Grouping Switch: {sect_name}:{s_id}')
                switch = section_insts[s_id]

                # Get all switch start positions
                num_entries = switch.parameters[1].value
                switch_entry_target_poses = []
                switch_entry_cases = []
                for entry_id in range(num_entries):
                    switch_entry_target_poses.append(switch.loop_parameters[entry_id][3].link.target)
                    switch_entry_cases.append(switch.loop_parameters[entry_id][2].value)

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
                prev_start = None
                prev_case = None
                prev_start_sect = None
                goto_jmp = None
                end_sect = None
                for inst_start, case in switch_entry_start_ids.items():
                    if prev_case is not None:
                        group_key = f'{s_id}-{prev_case}'
                        end_sect = self._find_sect_in_group(group_starts, inst_start - 1)
                        s = prev_start - group_starts[prev_start_sect]
                        e = inst_start - group_starts[end_sect] - 1
                        decoded_sct.sections[sect_name].instructions_grouped[group_key] = (
                            f'{prev_start_sect}-{s}', f'{end_sect}-{e}')
                        if section_insts[inst_start - 1].parameters[0].value < 0:
                            decoded_sct.sections[sect_name].jump_loops.append(group_key)
                        else:
                            if goto_jmp is None:
                                if section_insts[inst_start - 1].inst_id == 10:
                                    goto_jmp = section_insts[inst_start - 1].parameters[0].link.target
                            else:
                                goto_jmp = max(goto_jmp, section_insts[inst_start - 1].parameters[0].link.target)
                    prev_start = inst_start
                    prev_case = case
                    prev_start_sect = start_sect_names[inst_start]

                # Find end of last swtich entry
                last_start = list(switch_entry_start_ids.keys())[-1]
                last_case = switch_entry_start_ids[last_start]
                jmp_groups = 0
                cur_id = last_start

                # if an end for the last section was found previously, set it
                if goto_jmp is not None:
                    group_key = f'{s_id}-{last_case}'
                    decoded_sct.sections[sect_name].instructions_grouped[group_key] = (
                        f'{prev_start_sect}-{last_start}', f'{end_sect}-{cur_id}')
                    continue

                # else search for a goto that matches with the switch.
                # May be error prone if there are random gotos inside a switch entry
                while cur_id < len(section_insts):
                    cur_inst = section_insts[cur_id]
                    if cur_inst.inst_id == 0:
                        jmp_groups += 1
                    elif cur_inst.inst_id == 10:
                        if jmp_groups > 0:
                            jmp_groups -= 1
                        else:
                            group_key = f'{s_id}-{last_case}'
                            decoded_sct.sections[sect_name].instructions_grouped[group_key] = (
                                f'{prev_start_sect}-{last_start}', f'{end_sect}-{cur_id}')
                            break
                    if cur_id == len(section_insts):
                        print(f'SCPT Decoder: Switch Groups: End of final switch entry not found: {sect_name}:{s_id}')
                    cur_id += 1

    @staticmethod
    def _group_subscripts(decoded_sct):
        sections = decoded_sct.sections
        script_filename = decoded_sct.name.split('.')[0]
        cur_group = ''
        suffix = ''
        in_group = False
        for sect_name, section in sections.items():

            if in_group and suffix in sect_name.lower():
                decoded_sct.section_groups[cur_group].append(sect_name)

            if script_filename in sect_name and not in_group:
                in_group = True
                cur_group = sect_name
                suffix = sect_name[len(script_filename):].lower()
                decoded_sct.section_groups[cur_group] = [cur_group]

            if section.type == 'Label':
                in_group = False

    def _create_group_heirarchies(self, decoded_sct):

        # Create grouped section heirarchy
        groups = decoded_sct.section_groups

        # sort groups by size with smallest first
        groups = {k: groups[k] for k in sorted(groups.keys(), key=lambda k: len(groups[k]))}

        new_groups = self._nest_groups(groups)
        new_groups = self._complete_heirarchy_sections(list(decoded_sct.sections.keys()), new_groups)
        decoded_sct.grouped_sections = new_groups

        # Create grouped instruction heirarchies
        for section in decoded_sct.sections.values():
            inst_groups = section.instructions_grouped

            inst_groups = {k: [*range(int(v[0].split('-')[1]), int(v[1].split('-')[1]) + 1)]
                           for k, v in inst_groups.items()}
            new_groups = self._nest_groups(inst_groups, is_sections=False)
            new_groups = self._complete_heirarchy_instructions(list(range(len(section.instructions))), new_groups)
            new_groups = self._remove_duplicate_inst_locations(new_groups)
            new_groups = self._resolve_switches(new_groups)
            section.instructions_grouped = new_groups

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
                if is_sections:
                    insert_index = new_groups[key].index(group_name)
                else:
                    insert_index = new_groups[key].index(new_groups[group_name][0])
                for entry in group:
                    new_groups[key].remove(entry)
                new_groups[key].insert(insert_index, {group_name: group})
            if len(insert_keys) > 0:
                new_groups.pop(group_name)

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

    def _complete_heirarchy_sections(self, full_list, groups):
        heirarchy = []
        skips = []
        for entry in full_list:
            if entry in skips:
                continue
            if entry not in groups.keys():
                heirarchy.append(entry)
                continue
            group = groups[entry]
            heirarchy.append(group)
            skips.extend(self._get_heirarchy_skips(group))
        return heirarchy

    def _complete_heirarchy_instructions(self, full_list, groups):
        heirarchy = []
        skips = []
        for entry in full_list:
            if entry in skips:
                continue
            matching_groups = {}
            for key in groups.keys():
                if str(entry) == key.split('-')[0]:
                    matching_groups[key] = groups[key]
            if len(matching_groups) == 0:
                heirarchy.append(entry)
                continue
            heirarchy.append(matching_groups)
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
            if list(entry.keys())[0].split('-')[1].isnumeric():
                switch_key = list(entry.keys())[0].split('-')[0] + '-switch'
                if switch_key not in switches.keys():
                    switches[switch_key] = []
                switches[switch_key].append(i)
        if len(switches) > 0:
            for switch_key, switch_entries in switches.items():
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
                key_insts.append(int(key.split('-')[0]))
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
            group.pop(entry[0]+1)
        return group

    @staticmethod
    def _reorganize_switch(switch_key, switch_entries, inst_list: list):
        first_entry = min(switch_entries)
        switch = {}
        for i in switch_entries:
            entry = inst_list[i]
            entry_key = list(entry.keys())[0].split('-')[1]
            entry_value = list(entry.values())[0]
            switch[entry_key] = entry_value
        for i in reversed(switch_entries):
            inst_list.pop(i)
        inst_list.insert(first_entry, {switch_key: switch})
        return inst_list

    @staticmethod
    def _get_inst_by_pos(inst_list, start_id, target_pos, origin_sect_name, origin_element_id):
        cur_id = start_id
        while cur_id < len(inst_list):
            cur_inst = inst_list[cur_id]
            if cur_id == len(inst_list):
                print(
                    f'SCPT Decoder: Find Inst: Entry not found: {origin_sect_name}:{origin_element_id} - {target_pos}')
                return
            if cur_inst.inst_pos == target_pos:
                break
            if cur_inst.inst_pos < target_pos < inst_list[cur_id + 1].inst_pos:
                print(
                    f'SCPT Decoder: Find Inst: Target pos in middle of entry {origin_sect_name}:{origin_element_id} - {target_pos}')
                break
            cur_id += 1

        return cur_id

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
            if link.trace[0] != sect_name:
                continue
            if link.trace[1] < start_inst_list_id:
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
            link.trace[1] += offset

        for i in changes['switches']:
            self._switches[changes['sect_name']].append(i + offset)

        for i in changes['jmps']:
            self._jmp_if_falses[changes['sect_name']].append(i + offset)


if __name__ == '__main__':
    import json

    insts = BaseInstLibFacade()

    with open('./../../Lib/Instructions.json', 'r') as fh:
        file = fh.read()
        file_json = json.loads(file)

    insts.set_inst_all_fields(file_json)

    file_of_interest = None
    # file_of_interest = 'me126b.sct'

    if input('Run all scripts?') not in ['Y', 'y']:

        f = file_of_interest if file_of_interest is not None else 'me002a.sct'
        file = os.path.join('./../../scripts/', f)
        with open(file, 'rb') as fh:
            file_ba = bytearray(fh.read())

        sct_out = SCTDecoder.decode_sct_from_file(f.split('.')[0], sct=file_ba, inst_lib=insts)
        print('Done!')

    else:
        files = os.listdir('./../../scripts/')

        scts = {}
        skip_till = file_of_interest if file_of_interest is not None else 'me002a.sct'
        skip = True
        for f in files:
            if f == skip_till:
                skip = False
            if skip:
                continue
            file = os.path.join('./../../scripts/', f)
            with open(file, 'rb') as fh:
                file_ba = bytearray(fh.read())
            print(f'Starting {f.split(".")[0]}')
            sct_out: SCTScript = SCTDecoder.decode_sct_from_file(f.split('.')[0], sct=file_ba, inst_lib=insts)
            scts[f] = sct_out
            print(f'{sct_out.name}Done!')

        print('All Done!!!')
