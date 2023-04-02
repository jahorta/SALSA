import struct
from typing import Union

from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Common.byte_array_utils import float2Hex
from SALSA.Common.constants import sep
from SALSA.Project.project_container import SCTScript, SCTSection
from SALSA.Scripts.scpt_param_codes import SCPTParamCodes
from SALSA.Scripts.scpt_compare_fxns import is_equal, not_equal


class SCTEncoder:
    log_key = 'SCTEncoder'
    skip_refresh = 13
    _placeholder = bytearray(b'\x7f\x7f\xff\xff')
    _str_label = b'\x00\x00\x00\x09\x04\x00\x00\x00\x3f\x80\x00\x00\x00\x00\x00\x1d'
    endian_struct_format = {'big': '>', 'little': '<'}
    _header_offset_length = 0x4
    _header_name_length = 0x10
    _default_header_start = bytearray(b'\x07\xd2\x00\x06\x00\x0e\x00\x00')

    # These variables are for validation purposes only, validation should be false in production
    validation: bool = True

    use_garbage: bool
    combine_footer_links: bool
    add_spurious_refresh: bool

    param_tests = {'==': is_equal, '!=': not_equal}

    def __init__(self, script: SCTScript, base_insts: BaseInstLibFacade, update_inst_pos=True, endian='big'):
        self.sct_body = bytearray()
        # for decoder, encoder validation only
        if self.validation:
            if '099' in script.name:
                self.sct_body = bytearray(b'\x4F\x00\x00\x00\x00\x00\x00\x04\x00\x00\x66\x43\x1D\x00\x00\x00\x00\x00\x00'
                                          b'\x04\x00\x00\x34\x43\x1D\x00\x00\x00\x00\x00\x00\x04\x00\x00\x16\x43\x1D\x00'
                                          b'\x00\x00\x00\x00\x00\x04\x00\x00\x80\x3F\x1D\x00\x00\x00\x00\x00\x00\x04\x00'
                                          b'\x00\x00\x00\x1D\x00\x00\x00\x00\x00\x00\x04\x00\xC0\x0F\xC5\x1D\x00\x00\x00'
                                          b'\x00\x00\x00\x04\x00\x00\x80\x3F\x1D\x00\x00\x00')
            if '241a' in script.name:
                self.sct_body = bytearray(b'\x0b\x00\x00\x00\xc4\xe2\x00\x00')
            if '513a' in script.name or '576a' in script.name:
                self.sct_body = bytearray(b'\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00'
                                          b'\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00'
                                          b'\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D'
                                          b'\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00\x0D\x00\x00\x00')
            self._additions = {
                'M04523-177-1': b'\x50\x00\x00\x01',
                'M04524-177-1': b'\x50\x00\x00\x01',
                'M04525-177-1': b'\x50\x00\x00\x01',
                'K08cut8-136-1': b'\x50\x00\x00\x01',
                'l01cut6-134-0': b'\x50\x00\x00\x01',
                'l01cut7-134-0': b'\x50\x00\x00\x01',
                'doc00_init01-136-1': b'\x50\x00\x00\x01',
                'hama_big01-136-1': b'\x50\x00\x00\x01',
                'hama_change01-136-1': b'\x50\x00\x00\x01',
                'me260aq02-136-1': {'ind': [1], 'value': b'\x50\x00\x00\x01'},
                'me260aq03-136-1': {'ind': [1], 'value': b'\x50\x00\x00\x01'},
                'q04a_start-136-1': {'ind': [1], 'value': b'\x50\x00\x00\x01'},
                'me260aq05-136-1': {'ind': [1], 'value': b'\x50\x00\x00\x01'},
                'camb02-232-3': {'ind': [8], 'value': b'\x04\x00\x00\x00\x42\x80\x00\x00'},
                'camb02-224-13': {'ind': [10], 'value': b'\x04\x00\x00\x00\x42\xF9\x00\x00'},
                '_EV_VER2-50-0': {'ind': [2], 'value': b'\x50\x00\x00\x01'}
            }

        self.update_inst_pos = update_inst_pos

        self.script = script
        self.bi = base_insts
        self.sct = bytearray()
        self.sct_head = self.script.header if self.script.header is not None else self._default_header_start
        self.sct_foot = bytearray()
        self.header_dict = {}
        self.footer_dict = {}
        self.added_string_groups = []
        self.endian = endian
        self.param_code = SCPTParamCodes(is_decoder=False)

        # Links will start off being a dictionary with origin_offset: (string or section or jmp_target)
        # They will then be iterated upon to replace the value with the location of the target
        # Finally, they will be used to replace the original
        self.sct_links = {}
        self.string_links = {}
        self.footer_links = {}
        self.inst_positions = {}

    @classmethod
    def encode_sct_file_from_project_script(cls, project_script: SCTScript, base_insts: BaseInstLibFacade,
                                            use_garbage=True, combine_footer_links=True, add_spurious_refresh=True):

        encoder = cls(script=project_script, base_insts=base_insts)
        encoder.encode_sct_file(use_garbage=use_garbage, combine_footer_links=combine_footer_links,
                                add_spurious_refresh=add_spurious_refresh)

        return encoder.sct

    def encode_sct_file(self, use_garbage=True, combine_footer_links=False, add_spurious_refresh=False):
        self.use_garbage = use_garbage
        self.combine_footer_links = combine_footer_links
        self.add_spurious_refresh = add_spurious_refresh

        # encode sections in order
        for name in self.script.section_names_ungrouped:
            section = self.script.sections[name]
            self._encode_section(name=name, section=section)

            # if string group header is added, add strings below it
            if name in self.script.string_groups.keys():
                self.added_string_groups.append(name)
                self._add_strings(name)

        # Resolve through jmp_links
        for link_offset, jmp_to in self.sct_links.items():
            jmp_to_pos = self.inst_positions[jmp_to[1]]
            jmp_offset = self._make_word(i=(jmp_to_pos - link_offset), signed=True)
            self._sct_body_replace_hex(location=link_offset, value=jmp_offset, validation=self._placeholder)

        # Resolve string links
        for link_offset, section in self.string_links.items():
            str_pos = self.header_dict[section]
            str_offset = str_pos - link_offset
            str_offset_word = self._make_word(i=str_offset, signed=True)
            self._sct_body_replace_hex(location=link_offset, value=str_offset_word, validation=self._placeholder)

        # Add footer entries in order by links while resolving links
        added_footer_entries = {}
        for offset, string in self.footer_links.items():
            if combine_footer_links and string in added_footer_entries:
                str_pos = added_footer_entries[string]
            else:
                str_pos = len(self.sct_body) + len(self.sct_foot)
            str_offset = str_pos - offset
            str_offset_word = self._make_word(i=str_offset)
            self.sct_foot.extend(self._encode_string(string=string, align=False))
            self._sct_body_replace_hex(location=offset, value=str_offset_word, validation=self._placeholder)

        # Build header
        header_len = self._make_word(len(self.header_dict))
        self.sct_head.extend(header_len)
        for name, offset in self.header_dict.items():
            self.sct_head.extend(self._make_word(offset))
            self.sct_head.extend(self._encode_string(string=name, align=False, size=self._header_name_length))

        # Combine file portions together
        self.sct = self.sct_head + self.sct_body + self.sct_foot

        return self.sct

    def _add_strings(self, string_group_name):
        string_group = self.script.string_groups[string_group_name]
        for name in string_group:
            self.header_dict[name] = len(self.sct_body)
            self.sct_body.extend(self._str_label)
            string = self.script.strings[name]

            # Add String using encode string
            self.sct_body.extend(self._encode_string(string=string, align=True))

            string_sect: SCTSection = self.script.string_sections[name]
            if 'end' in string_sect.garbage:
                self.sct_body.extend(string_sect.garbage['end'])

    def _encode_section(self, name, section):
        # If the section is a label, just add the entry to the header and add a string label
        sect_list = [name]
        if len(section.internal_sections_inst.keys()) > 0:
            sect_list = list(section.internal_sections_inst)
        sect_name = name
        for inst_id in section.instruction_ids_ungrouped:
            inst = section.instructions[inst_id]
            if inst.instruction_id == 9:
                sect_name = sect_list[0]
                self.header_dict[sect_name] = len(self.sct_body)
                sect_list.pop(0)
            self._encode_instruction(inst, trace=[sect_name])

        # add garbage at end of section if needed
        if self.use_garbage:
            if 'end' in section.garbage.keys():
                self.sct_body.extend(section.garbage['end'])

    def _encode_instruction(self, instruction, trace):
        base_inst = self.bi.get_inst(instruction.instruction_id)
        trace.append(str(instruction.instruction_id))
        self.inst_positions[instruction.ID] = len(self.sct_body)
        if self.update_inst_pos:
            instruction.absolute_offset = len(self.sct_body)

        # add 13 code if needed or wanted
        if instruction.skip_refresh:
            if self.add_spurious_refresh or (not base_inst.no_new_frame and not base_inst.forced_new_frame):
                self.sct_body.extend(self._make_word(self.skip_refresh))

        delay_pos = None
        inst_pos = -1
        if instruction.frame_delay_param is not None or instruction.frame_delay_param == 0:
            self.sct_body.extend(self._make_word(129))
            base_param = self.bi.get_inst(129).parameters[0]
            self._encode_param(param=instruction.frame_delay_param, base_param=base_param, trace=[*trace, str(-1)])
            delay_pos = len(self.sct_body)
            self.sct_body.extend(b'0000')
            inst_pos = len(self.sct_body)

        # add instruction code to sct_body
        self.sct_body.extend(self._make_word(instruction.instruction_id))

        loop_iter_param_location = None
        loop_iter_param_value = None
        # cycle through and add parameters
        for p_id in base_inst.params_before:
            if base_inst.loop_iter is not None:
                if p_id == base_inst.loop_iter:
                    loop_iter_param_location = len(self.sct_body)
                    loop_iter_param_value = instruction.parameters[p_id].value
            self._encode_param(param=instruction.parameters[p_id], base_param=base_inst.parameters[p_id],
                               trace=[*trace, str(p_id)])

        do_loop = True
        has_loop_cond = False
        # Check for an external loop bypass
        if base_inst.loop_cond is not None:
            if base_inst.loop_cond['Location'] == 'External':
                value1 = instruction.parameters[base_inst.loop_cond['Parameter']].value
                if not isinstance(value1, int):
                    value1 = int(value1)
                value2 = base_inst.loop_cond['Value']
                if not isinstance(value2, int):
                    value2 = int(value2)
                test = base_inst.loop_cond['Test']
                do_loop = not self.param_tests[test](value1, value2)
            else:
                has_loop_cond = True

        break_loops = False
        loop_iters_performed = 0
        if do_loop:
            for loop in instruction.loop_parameters:
                for p_id, param in loop.items():
                    self._encode_param(param=loop[p_id], base_param=base_inst.parameters[p_id],
                                       trace=[*trace, str(p_id)])

                    # Check internal loop conditions
                    if not has_loop_cond:
                        continue

                    if p_id == base_inst.loop_cond['Parameter']:
                        value1 = param.value

                        if isinstance(value1, dict) and param.arithmetic_value is not None:
                            value1 = param.arithmetic_value

                        if not isinstance(value1, int):
                            value1 = int(value1)

                        value2 = base_inst.loop_cond['Value']

                        if not isinstance(value2, int):
                            value2 = int(value2)

                        test = base_inst.loop_cond['Test']
                        if self.param_tests[test](value1, value2):
                            break_loops = True
                            break
                loop_iters_performed += 1
                if break_loops:
                    break

        if loop_iter_param_value is not None:
            if loop_iters_performed != loop_iter_param_value:
                self._sct_body_replace_hex(location=loop_iter_param_location, value=self._make_word(loop_iters_performed))

        for p_id in base_inst.params_after:
            self._encode_param(param=instruction.parameters[p_id], base_param=base_inst.parameters[p_id],
                               trace=[*trace, str(p_id)])

        # add garbage at then of instruction if needed
        garbage_index = None
        for i, e in enumerate(instruction.errors):
            if e[0] == 'Garbage':
                garbage_index = i
                break

        if garbage_index is not None and self.use_garbage:
            garbage = instruction.errors[garbage_index][1]
            self.sct_body.extend(garbage)

        if delay_pos is not None:
            inst_len = len(self.sct_body) - inst_pos
            self._sct_body_replace_hex(delay_pos, bytearray(self._make_word(inst_len)))

    def _encode_param(self, param, base_param, trace):
        # if needed, setup link and use 0x7fffffff as placeholder
        if param.link is not None:
            link_value = param.link_value
            if link_value[0] == 'Footer':
                self.footer_links[len(self.sct_body)] = param.link_result
            elif link_value[0] == 'String':
                self.string_links[len(self.sct_body)] = link_value[1]
            elif link_value[0] == 'SCT':
                self.sct_links[len(self.sct_body)] = param.link.target_trace
            else:
                print(f'{self.log_key}: Unknown param link type: {link_value[0]}')
            self.sct_body.extend(self._placeholder)
            return

        # generate parameter with encode scpt if needed
        if 'scpt' in base_param.type:
            if param.override is not None:
                value = param.override
            else:
                no_loop = False
                if isinstance(param.value, str):
                    if param.value in self.param_code.no_loop.keys():
                        no_loop = True

                if no_loop:
                    value = self._make_word(self.param_code.no_loop[param.value])
                    if self.validation:
                        self._check_additions(trace, value)
                else:
                    value = self._encode_scpt_param(param=param.value)
                    if self.validation:
                        self._check_additions(trace, value)
                    value.extend(self._make_word(self.param_code.stop_code))
        else:
            if 'code' in base_param.type:
                value = self._encode_scpt_param(param.value)
            else:
                value = self._make_word(param.value, signed=base_param.is_signed)
            if self.validation:
                self._check_additions(trace, value)

        # add parameter
        self.sct_body.extend(value)

    def _encode_scpt_param(self, param):
        param_bytes = bytearray()

        if param is None:
            return param_bytes

        # if parameter is an integer, it should be stored as a float within the script files, so convert to float
        if isinstance(param, int):
            param = float(param)

        # If the parameter is a float, enter the float into script file
        if isinstance(param, float):
            param_bytes.extend(self._make_word(self.param_code.input['float: ']))
            form = f'{self.endian_struct_format[self.endian]}f'
            param_bytes.extend(float2Hex(param, form))

        # if the parameter is complex, go through the requisite parameter dictionary encoding values then keys
        elif isinstance(param, dict):
            for key, value in param.items():
                param_bytes.extend(self._encode_scpt_param(value))
                if key in self.param_code.compare:
                    param_bytes.extend(self._make_word(self.param_code.compare[key]))
                if key in self.param_code.arithmetic:
                    param_bytes.extend(self._make_word(self.param_code.arithmetic[key]))

        # If the parameter is a string, it is likely located in input headers or secondary locations
        elif isinstance(param, str):
            if param in self.param_code.secondary:
                cutoff = self.param_code.input['IntVar: ']
                value = self.param_code.secondary[param]
            else:
                param_parts = param.split(' ')
                cutoff = self.param_code.input[param_parts[0] + ' ']
                if cutoff == self.param_code.input['decimal: ']:
                    d_parts = param_parts[1].split('/')
                    value = int(d_parts[0]) << 8
                    value = value | int(d_parts[1])
                else:
                    value = int(param_parts[1])
            param_bytes.extend(self._make_word(cutoff | value))

        else:
            print(f'unknown code?')

        return param_bytes

    def _check_additions(self, trace, ba: bytearray):
        key = '-'.join(trace)
        if key in self._additions:
            addition = self._additions[key]
            if isinstance(addition, dict):
                will_add = False
                if 0 in addition['ind']:
                    will_add = True
                addition['ind'] = [_-1 for _ in addition['ind']]
                if not will_add:
                    return
                addition = addition['value']
            ba.extend(addition)

    def _make_word(self, i: int, signed=None):
        signed = False if signed is None else signed
        return bytearray(i.to_bytes(length=4, byteorder=self.endian, signed=signed))

    def _encode_string(self, string, encoding='shiftjis', align=True, size=-1):
        str_bytes = bytearray(string.encode(encoding=encoding, errors='backslashreplace'))

        if size > 0:
            if len(str_bytes) > size:
                return str_bytes[:size]
            extra_bytes = b'\x00' * (size - len(str_bytes))
            str_bytes.extend(extra_bytes)
            return str_bytes

        str_bytes.extend(b'\x00')
        if not align:
            return str_bytes

        extra_bytes = b''
        if len(str_bytes) % 4 != 0:
            extra_bytes = b'\x00' * (4 - len(str_bytes) % 4)
        str_bytes.extend(extra_bytes)
        return str_bytes

    def _sct_body_replace_hex(self, location: int, value: bytearray, validation: Union[None, bytearray] = None):
        if validation is None:
            valid = True
        else:
            valid = validation.hex() == self.sct_body[location: location+len(validation)].hex()

        if not valid:
            print(f'{self.log_key}: Validation failed for hex replacement in sct_body: {self.sct_body[location: location+len(validation)-1].hex()} != {validation.hex()}')
            return

        self.sct_body = self.sct_body[:location] + value + self.sct_body[location+len(value):]

