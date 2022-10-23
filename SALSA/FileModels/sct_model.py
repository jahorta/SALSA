import os
import re

from SALSA.AKLZ.aklz import Aklz
from SALSA.Tools.byte_array_utils import getString, getWord, deriveStringLength, word2Float, applyHexMask, padded_hex, \
    word2SignedInt, toInt
from SALSA.Tools.constants import FieldTypes as FT


class SctModel:
    """Creates an object which can read in and decode *.sct files based on an instruction object"""
    path = './scripts/'
    overwriteCheck = False

    sct_keys = {
        'Name',
        'Header',
        'Index',
        'Stats',
        'Positions',
        'Sections',
        'Footer',
        'Implemented Instructions',
        'Errors'
    }

    header_fields = {
        'misc1': {'req': True, 'type': FT.string},
        'misc2': {'req': True, 'type': FT.string},
        'Index Num': {'req': True, 'type': FT.string}
    }

    index_fields = {
        'name': {'req': True, 'type': FT.string},
        'pos': {'req': True, 'type': FT.integer},
        'length': {'req': True, 'type': FT.integer}
    }

    stats_fields = {
        'index num': {'req': True, 'type': FT.integer},
        'start pos': {'req': True, 'type': FT.integer}
    }

    position_fields = {
        'name': {'req': True, 'type': FT.string}
    }

    section_fields = {
        'type': {'req': True, 'type': FT.string_list, 'values': {'string', 'instructions'}},
        'string': {'req': True, 'type': FT.string},
        'data': {'req': True, 'type': FT.long_string}
    }

    instruction_fields = {
        'decoded': {'req': True, 'type': FT.boolean},
        'instruction': {'req': False, 'type': FT.string},
        'start location': {'req': False, 'type': FT.integer},
        'param num': {'req': False, 'type': FT.integer},
    }

    parameter_types = ['int', 'int-signed', 'int-masked', 'int-signed-masked', 'SCPT', 'override-SCPT', 'switch']

    parameter_fields = {
        'id': {'req': True, 'type': FT.integer},
        'name': {'req': True, 'type': FT.string},
        'type': {'req': True, 'type': FT.string_list, 'values': parameter_types},
        'result': {'req': True, 'type': FT.result}
    }

    error_fields = {
        'Errors': {'req': True, 'Type': FT.long_string}
    }

    indexNum = 0

    def __init__(self, path=None):
        self.instructionNum = 0
        self.instructions = {}
        self.implementedInstKeys = []
        self.cursor = 0
        self.indexed_sct = {}
        self.decoded_sct = {}
        self.sctLength = 0
        self.errorCount: int = 1
        if path is not None:
            self.path = path

    def load_sct(self, insts, file: str):
        self.instructionNum = len(insts)
        self.instructions = insts
        self.implementedInstKeys = []
        for inst in self.instructions.values():
            if inst.implement:
                self.implementedInstKeys.append(str(int(inst.instID)))
        out = self._read_sct_file(file)
        if out is None:
            return None
        name = out[0]
        sct_raw = out[1]
        if sct_raw[0:4].decode(errors='backslashreplace') == 'AKLZ':
            print('file is AKLZ encrypted. Decryption is not yet implemented. Please decrypt file before use.')
            return None
        sct_dict = self._decode_sct(name, sct_raw)
        return sct_dict

    def _read_sct_file(self, file: str):
        filename = os.path.join(self.path, file)
        if os.path.exists(filename):
            with open(filename, 'rb') as fh:
                ba = bytearray(fh.read())
        else:
            raise FileExistsError(
                'This sct file does not exist: {}\nMay need to select the active script folder..'.format(filename))

        if Aklz.is_compressed(ba):
            ba = Aklz().decompress(ba)

        return [file, ba]

    def _decode_sct(self, name, sct_raw):
        self.indexed_sct = self._generate_indexed_sct(sct_raw)
        self.decoded_sct = {
            'Name': name, 'Header': self.indexed_sct['Header'], 'Footer': self.indexed_sct['Footer'],
            'Index': self.indexed_sct['Index'], 'Positions': self.indexed_sct['Positions'],
            'Stats': {'Index Num': self.indexed_sct['Index Num'],
                      'Scripts Start Pos': self.indexed_sct['Index End Pos']},
            'Sections': {}, 'Implemented Instructions': self.implementedInstKeys, 'Errors': [],
            'Body Length': self.indexed_sct['Body Length'],
            'Footer Length': self.indexed_sct['Footer Length'],
            'Details': {
                'Instructions Used': {}, 'Strings': []
            }
        }
        # print(self.indexed_sct['Sections'].items())
        # print(self.indexed_sct['Footer'].items())
        for key, value in self.indexed_sct['Sections'].items():
            self.cursor = 0
            length = len(value)
            if length == 16:
                data = self.__decode_sct_section(value, int(self.indexed_sct['Index'][key]['pos'], 16))
                self.decoded_sct['Sections'][key] = {'type': 'inst', 'data': data, 'string': ''}
                if 'errors' in data.keys():
                    self.decoded_sct['Sections'][key]['errors'] = data['errors']
                    self.decoded_sct['Errors'].append(key)
            elif self.test_for_string(value):
                encoding = 'shiftjis'
                # if re.search('^M.{8}$', key):
                #     encoding = 'UTF-8'
                labelLength = 16
                data = self.__decode_sct_section(value[:16], int(self.indexed_sct['Index'][key]['pos'], 16))
                string = getString(value, labelLength, encoding)
                self.decoded_sct['Sections'][key] = {'type': 'str', 'data': data, 'string': string}
                self.decoded_sct['Details']['Strings'].append(string)
                if string == '':
                    self.decoded_sct['Sections'][key]['error'] = 'Length of string == 0'
            else:
                # print('Decoding: {}'.format(key))
                data = self.__decode_sct_section(value, int(self.indexed_sct['Index'][key]['pos'], 16))
                self.decoded_sct['Sections'][key] = {'type': 'inst', 'data': data, 'string': ''}
                if 'errors' in data.keys():
                    self.decoded_sct['Sections'][key]['errors'] = data['errors']
                    self.decoded_sct['Errors'].append(key)
                    data.pop('errors')
                # noinspection PyAssignmentToLoopOrWithParameter
                for value1 in data.values():
                    if not isinstance(value1, dict):
                        continue
                    if 'instruction' not in value1.keys():
                        continue
                    inst = value1['instruction']
                    if not re.search('^[0-9]+$', inst):
                        continue
                    inst = int(inst)
                    if inst in self.decoded_sct['Details']['Instructions Used']:
                        self.decoded_sct['Details']['Instructions Used'][inst] += 1
                    else:
                        self.decoded_sct['Details']['Instructions Used'][inst] = 1

        return self.decoded_sct

    def _generate_indexed_sct(self, sct):
        index_length = getWord(sct, 8)
        head = 12
        entryLength = 20
        indEnd = head + (entryLength * index_length)
        body_length = len(sct) - index_length
        i = 0
        header = {'misc1': getWord(sct, 0, 'hex'), 'misc2': getWord(sct, 4, 'hex'), 'Index Num': getWord(sct, 8, 'hex')}
        ind = {'Header': header, 'Index Num': index_length, 'Index': {}, 'Index End Pos': indEnd, 'Positions': {},
               'Sections': {}, 'Footer': {}}
        prevPos = 0
        prevTitle = ''
        prevLength = 0
        for i in range(0, index_length):
            titlePos = head + (i * entryLength) + 4
            title = getString(sct, titlePos)
            pos = getWord(sct, head + i * entryLength, 'int')  # get position from file as hex string
            ind['Index'][title] = {'name': title, 'pos': padded_hex(pos, 8)}
            ind['Positions'][pos] = title
            if i > 0:
                prevLength = pos - prevPos
                ind['Index'][prevTitle]['length'] = padded_hex(prevLength, 8)
                sctStart = prevPos + indEnd
                sctEnd = pos + indEnd
                ind['Sections'][prevTitle] = sct[sctStart:sctEnd]
            prevTitle = title
            prevPos = pos
        prevLength = self._find_length_of_last_section(sct[(prevPos + indEnd):])
        ind['Index'][prevTitle]['length'] = padded_hex(prevLength, 8)
        sctStart = prevPos + indEnd
        sctEnd = sctStart + prevLength
        ind['Sections'][prevTitle] = sct[sctStart:sctEnd]
        footerStart = sctStart + prevLength
        footerStartNoIndex = footerStart - indEnd
        footerSCT = sct[footerStart:]
        footerLength = len(footerSCT)
        pos = 0
        index = 0
        while pos < footerLength:
            currFooterStr = getString(footerSCT, pos, replace=False)
            ## test for valid string
            if '\\' in currFooterStr:
                currFooterStr = getString(footerSCT, pos, enc='shiftjis', replace=False)
            ind['Footer'][str(index)] = currFooterStr
            ind['Positions'][pos + footerStartNoIndex] = 'Footer{}'.format(index)
            pos += len(currFooterStr) + 1
            index += 1
        ind['Body Length'] = body_length - footerLength
        ind['Footer Length'] = footerLength
        return ind

    def _find_length_of_last_section(self, sct):
        """Takes in the amount of sct from the beginning of the last section until the end of the file"""
        endBytes = [0, 255]
        sectLength = 0
        if self.test_for_string(sct):
            sectLength += 16
            strNoLabel = sct[16:]
            sectLengths = deriveStringLength(strNoLabel, 0)
            sectLength += len(sectLengths) - 1
            for s in sectLengths:
                sectLength += s
            sectLength += 4 - (sectLength % 4)
        else:
            """checking for 12 or '0xFFFFFFE4' (-29) leads to errors. Might be better to work backwards for all text"""
            # terminators = (int('0x0000000c', 16), int('0xffffffe4', 16))
            # isEOF = False
            # while not isEOF:
            #     current_inst = getWord(sct, sectLength)
            #     sectLength += 4
            #     if current_inst in terminators:
            #         isEOF = True
            """Check starting from the end of the sct file and work backwards. 
            All footer segments should be bounded by at least one single 0x00 bytes, however,
            final instructions tend to have at least two sequential 0x00 bytes"""
            hadOne00 = False
            for i in reversed(range(len(sct))):
                byte = sct[i]
                if byte in endBytes:
                    if hadOne00:
                        break
                    else:
                        lastNotFooterByte = i
                        hadOne00 = True
                # check that the byte is a vaild utf character that would be used in a filename
                # elif is_utf_8_file_character(byte):
                #     hadOne00 = False
                # if its not a vaild character, it is likely part of an instruction
                # else:
                #     lastNotFooterByte = i - 1
                #     break

                # The previous strategy failed for me250a.sct, try without checking for utf8 character
                else:
                    hadOne00 = False
            sectLength = lastNotFooterByte + lastNotFooterByte % 4
        return sectLength

    def __decode_sct_section(self, sct_bytes, sct_start_pos):
        scptErr = False
        self.cursor = 0
        self.sctLength = len(sct_bytes) / 4
        # print(self.sctLength)
        self.errorCount = 0
        insts = {}
        while self.cursor < self.sctLength:

            currWord = getWord(sct_bytes, self.cursor * 4, 'hex')
            currWord_int = int(currWord, 16)
            startPos = self.cursor
            # print('Cursor: {0}, Current Word: {1} -> as int: {2}'.format(self.cursor, currWord, currWord_int))
            # if currWord == '0x000000ca':
            #     print('Restore Health')

            """Apparently, 0x0a000000 is used after some instructions, but never read from file, so capture it along with
            the next instruction, which is sometimes 0x04000000 and triggers a false SCPTAnalyze call. Maybe its used as padding?"""
            if currWord == '0x0a000000':
                insts[str(self.cursor)] = {'decoded': False,
                                           'data': {'word': 'Skip 2', 'length': 2},
                                           'string': '', 'start location': str(sct_start_pos + (self.cursor * 4)),
                                           'function': 'None'}
                self.cursor += 1

            # Since 0x04000000 is reserved for SCPTAnalyze more or less, capture any instructions following this code as SCPT parameters
            elif currWord == '0x04000000':
                if 'errors' not in insts.keys():
                    insts['errors'] = {}
                insts['errors'][self.errorCount] = 'Unknown SCPT parameter'
                self.errorCount += 1
                errors = {}
                inSCPT = True
                while inSCPT:
                    errors[str(self.errorCount)] = currWord
                    self.errorCount += 1
                    self.cursor += 1
                    if self.cursor >= self.sctLength:
                        insts['errors'][str(self.errorCount)] = 'Bad SCPT Parameter Overflowed'
                        self.errorCount += 1
                        break
                    currWord = getWord(sct_bytes, self.cursor * 4, 'hex')
                    # print('Checking word: {}'.format(currWord))
                    if currWord == '0x0000001d':
                        break
                    if currWord in ('0x0000000c', '0xffffffe4'):
                        insts['errors'][str(self.errorCount)] = 'EOF in an SCPT Parameter'
                        self.errorCount += 1
                        break
                if self.overwriteCheck:
                    print('SCPTError from {0} to {1}'.format(startPos, self.cursor))
                    scptErr = True
                errors[str(self.errorCount)] = currWord
                self.errorCount += 1
                insts[str(startPos)] = {'decoded': False,
                                        'data': {'word': 'SCPT Parameter', 'length': (self.cursor - startPos)},
                                        'string': '', 'errors': errors,
                                        'start location': str(sct_start_pos + (self.cursor * 4)),
                                        'function': 'None'}

            # if the current word is not within the instruction number, set a false instruction using the current word
            elif currWord_int >= self.instructionNum or currWord_int < 0:
                if self.overwriteCheck and scptErr:
                    print('next instruction: {}'.format(self.cursor))
                    scptErr = False
                insts[str(self.cursor)] = {'decoded': False, 'data': {'word': currWord, 'length': 1}, 'string': False,
                                           'start location': str(sct_start_pos + (self.cursor * 4)),
                                           'function': 'none'}

            # if the current word is a valid instruction, resolve said instruction
            else:
                instResult = self.__decode_instruction(sct_bytes, currWord, scptErr, sct_start_pos)
                if 'Canceled' in instResult.keys():
                    self.cursor = startPos
                    if 'errors' not in insts.keys():
                        insts['errors'] = {}
                    insts['errors'][self.errorCount] = instResult['Canceled']
                    self.errorCount += 1
                else:
                    insts[str(startPos)] = instResult[str(startPos)]

                # TODO - copy errors from returned value to instruction list for the script segment

            self.cursor += 1
            if self.cursor >= self.sctLength:
                insts['final'] = currWord
        return insts

    def __decode_instruction(self, sct, inst, scptErr, sct_start_pos):
        instDict = {}
        if not str(int(inst, 16)) in self.implementedInstKeys:
            if self.overwriteCheck and scptErr:
                print('next instruction: {}'.format(self.cursor))
                scptErr = False
            instDict[str(self.cursor)] = {'decoded': False, 'data': {'word': inst, 'length': 1},
                                          'start location': str(sct_start_pos + (self.cursor * 4)),
                                          'function': self.instructions[str(int(inst, 16))].location}
        else:
            inst_loc_str = str(sct_start_pos + (self.cursor * 4))
            inst_start_cursor = str(self.cursor)
            if self.overwriteCheck and scptErr:
                print('next instruction: {}'.format(inst_loc_str))
                scptErr = False
                self.overwriteCheck = False
            inst = self.instructions[str(int(inst, 16))]
            paramNum = inst.get_attribute('param num')
            instDict[inst_start_cursor] = {'decoded': True, 'instruction': inst.instID, 'name': inst.name,
                                           'description': inst.description, 'start location': inst_loc_str,
                                           'param num': paramNum,
                                           'function': inst.location}

            # decode parameters
            parameters = inst.get_attribute('params')
            currentParamIndex = 0
            paramResults = {}
            while currentParamIndex < paramNum:
                self.cursor += 1
                if self.cursor >= self.sctLength:
                    if 'errors' not in instDict.keys():
                        instDict['errors'] = {}
                    instDict['errors'][self.errorCount] = 'Instruction overlaps into next sct section'.format()
                    self.errorCount += 1
                    break

                currName = parameters[str(currentParamIndex)].name
                result = {'ID': currentParamIndex, 'name': currName,
                          'position': str(sct_start_pos + (self.cursor * 4))}
                paramType = parameters[str(currentParamIndex)].type

                if 'switch' in paramType:
                    currentParam = parameters[str(currentParamIndex)]
                    resultDict = self._decode_switch_param(currentParam, paramResults, sct)
                    result['type'] = 'switch'

                elif 'loop' in paramType:
                    resultDict = self._decode_loop_param(paramType, paramResults, parameters, currentParamIndex, sct)
                    result['type'] = 'loop'

                else:
                    currentParam = parameters[str(currentParamIndex)]
                    resultDict = self._decode_param(paramType, currentParam, sct)
                    result['type'] = resultDict['type']

                # Error checking
                if 'Error' in result.keys():
                    paramResults['Error'] = result['Error']
                    if 'Cancel' in result.keys():
                        if result['Cancel']:
                            return {'Canceled': paramResults}

                if 'result' in resultDict.keys():
                    result['result'] = resultDict['result']
                else:
                    result['result'] = resultDict

                paramResults[str(currentParamIndex)] = result

                if 'paramSkipNum' in resultDict:
                    currentParamIndex += resultDict['paramSkipNum']
                currentParamIndex += 1

                if 'error' in result.keys():
                    if 'errors' not in instDict.keys():
                        instDict['errors'] = {}
                    instDict['errors'][self.errorCount] = result['error'] + ' location: {}'.format(inst_loc_str)
                    self.errorCount += 1

            instDict[inst_start_cursor]['parameters'] = paramResults
        return instDict

    def _decode_switch_param(self, currentParam, paramResults, sct_bytes):

        entryNumParamID = currentParam.iterationID
        entryLimit = paramResults[entryNumParamID]['result']['result']
        switch = {}
        switchEntries = {}
        switchStart = self.cursor

        # exit if switch is too long
        if entryLimit > (self.sctLength - self.cursor):
            return {'type': 'Switch', 'Error': 'Switch: Goes past end of file', 'Cancel': True}

        switch['Entry Limit'] = entryLimit
        done = False
        entryNum = 0
        while not done:
            currWord = getWord(sct_bytes, self.cursor * 4, 'hex')

            # Do not exit on an index of -1
            if currWord == '0xffffffff':
                # done = True
                offset = getWord(sct_bytes, (self.cursor + 1) * 4, 'hex')
                switchEntries['-1'] = int(offset, 16)

            else:
                offset = getWord(sct_bytes, (self.cursor + 1) * 4, 'hex')
                switchEntries[str(int(currWord, 16))] = int(offset, 16)
            self.cursor += 2

            if self.cursor >= self.sctLength - 2:
                switch['Error'] = 'Switch went past end of file'
                self.cursor = switchStart
                return switch

            entryNum += 1
            if entryNum == entryLimit:
                done = True

            if done:
                self.cursor -= 1

        switch['Entries'] = switchEntries
        return switch

    def _decode_loop_param(self, paramType, paramResults, params, currentParamNum, sct):
        loopDict = {}
        bypass = False
        loopDict['paramSkipNum'] = 0

        if 'end' in paramType:
            return {'type': paramType, 'Error': 'Loop: End before start', 'Cancel': True, 'paramSkipNum': 0}

        if 'condition' in paramType:
            cond_param_ID = params[str(currentParamNum)].loopConditionParamID
            cond_param_value = paramResults[cond_param_ID]['result']['result']
            cond_type = params[str(currentParamNum)].loopConditionTest
            cond_val = params[str(currentParamNum)].loopConditionValue
            prefix = 'not'
            if cond_type == '!=':
                prefix += ' not'
                cond_type = '=='
            execString = f'bypass = {prefix} {toInt(cond_param_value)} {cond_type} {int(cond_val, 16)}'
            lcls = {'bypass': bypass}
            exec(execString, globals(), lcls)
            bypass = lcls['bypass']
            currentParamNum += 1
            loopDict['paramSkipNum'] += 1

        # Get loop iterations
        paramLoopIterID = params[str(currentParamNum)].iterationID
        paramLoopIter = paramResults[paramLoopIterID]['result']['result']

        # Get parameters inside loop
        loopParams = []
        loopParamNum = 0
        isLoopEnd = False
        currentParamNum += 1
        while not isLoopEnd:
            curParamID = params[str(currentParamNum)].paramID
            curParamType = params[str(currentParamNum)].type
            if 'end' in curParamType:
                isLoopEnd = True
            else:
                loopParams.append(curParamID)
            currentParamNum += 1
            loopParamNum += 1

        loopDict['paramSkipNum'] += loopParamNum

        if bypass:
            loopDict['loop'] = {'0': {'0': {'type': 'Bypass', 'result': 'Bypassed'}}}
            loopDict['bypass'] = True
            return loopDict

        # check that loop iterations do not overflow the script grossly
        minLoopLength = loopParamNum - 1 * paramLoopIter
        if 0 > paramLoopIter or minLoopLength > self.sctLength:
            return {'type': paramType, 'Error': 'Loop: Minimum loop length -> sct overflow',
                    'Cancel': True, 'paramSkipNum': 0}
        loopDict['loop'] = {}
        for i in range(paramLoopIter):
            loopDict['loop'][str(i)] = {}
            for ID in loopParams:
                param = params[str(ID)]
                paramType = param.type
                paramResult = self._decode_param(paramType, param, sct)
                loopDict['loop'][str(i)][ID] = {}
                loopDict['loop'][str(i)][ID]['type'] = paramType
                loopDict['loop'][str(i)][ID]['result'] = paramResult
                self.cursor += 1

        self.cursor -= 1

        return loopDict

    def _decode_param(self, paramType: str, currentParam, sct_bytes):
        paramDict = {}
        if 'scpt' in paramType:
            overrideCompare = []
            overrideResult = ''
            overrideOffset = '0x4'
            if 'int' in paramType:
                overrideCompare = ['0x7f7fffff', '0x7fffffff']
                overrideResult = '0x7fffffff'
            elif 'short' in paramType:
                overrideCompare = ['0x7f7fffff']
                overrideResult = '0xffff'
            elif 'byte' in paramType:
                overrideCompare = ['0x7f7fffff']
                overrideResult = '0xff'
            else:
                if currentParam.hasOverride:
                    overrideOffset = currentParam.overrideOffset
                    overrideCompare = currentParam.overrideCompare
                    overrideResult = currentParam.overrideResult
            scriptCompare = getWord(sct_bytes, ((self.cursor - 1) * 4) + int(overrideOffset, 16), 'hex')
            if scriptCompare in overrideCompare:
                paramDict['type'] = 'override-SCPT'
                paramDict['result'] = overrideResult
                return paramDict
            paramDict['result'] = self._SCPT_analyze(currentParam.paramID, sct_bytes)
            paramDict['type'] = 'SCPT'
            if 'error' in paramDict['result'].keys():
                paramDict['error'] = 'SCPTanalyze did not finish before next sct section param {}'.format(
                    currentParam.paramID)
        elif paramType == 'int':
            currWord = getWord(sct_bytes, self.cursor * 4, 'hex')
            paramDict['type'] = 'int'
            paramDict['result'] = {'original value': currWord}
            if currentParam.hasMask:
                mask = currentParam.mask
                currWord = applyHexMask(currWord, mask)
                paramDict['type'] += '-masked'
                paramDict['result']['mask'] = mask
            if currentParam.isSigned:
                paramDict['type'] += '-signed'
                paramDict['result']['result'] = word2SignedInt(paramDict['result']['original value'])
            else:
                paramDict['type'] = 'int'
                paramDict['result']['result'] = int(currWord, 16)

        else:
            paramDict['type'] = 'unknown type'
            paramDict['result'] = 'unknown result for {}'.format(getWord(sct_bytes, self.cursor * 4))

        return paramDict

    def _SCPT_analyze(self, paramID, sct_bytes):
        """
        This interprets an SCPTAnalyze section. Mostly implemented, missing the local_ca check.
        :param paramID:
        :param sct_bytes:
        :return dict:
        """

        compare_codes = {
            '0x00000000': '(1)<(2)',
            '0x00000001': '(1)<=(2)',
            '0x00000002': '(1)>(2)',
            '0x00000003': '(1)>=(2)',
            '0x00000004': '(1)==(2)',
            '0x00000005': '(1)==(2)[5]',
            '0x00000006': '(1)&(2)',
            '0x00000010': '(1)&(2)',  # Same as 6
            '0x00000007': '(1)|(2)',
            '0x00000011': '(1)|(2)',  # Same as 7
            '0x00000008': '(1)!=0 and (2)!=0',
            '0x00000009': '(1)!=0 or (2)!=0',
            '0x0000000a': 'overwrites (1) with (2)',
        }

        arithmetic_codes = {
            '0x0000000b': '(1)*(2)',
            '0x00000012': '(1)*(2)',  # Same as b
            '0x0000000c': '(1)/(2)',
            '0x00000013': '(1)/(2)',  # Same as c
            '0x0000000d': '(1)%(2)',
            '0x00000014': '(1)%(2)',  # Same as d
            '0x0000000e': '(1)+(2)',
            '0x00000015': '(1)+(2)',  # Same as e
            '0x0000000f': '(1)-(2)',
            '0x00000016': '(1)-(2)',  # Same as f
        }

        noLoop = [
            # Special: returns first value, doesn't enter scpt loop
            '0x7f7fffff',
            '0x00800000',
            '0x7fffffff'
        ]

        input_cutoffs = {
            '0x50000000': 'Word: *add[0x8030e3e4,',
            '0x40000000': 'Word: *add[0x803e514,',
            '0x20000000': 'starting from 80310b3c, Bit: ',
            '0x10000000': 'Byte: *add[0x80310a1c,',
            '0x08000000': 'decimal: ',
            '0x04000000': 'float: ',
        }

        """Specific secondary code checks: code <= 0x07, code < 0x21, code == 0x4a"""
        secondary_codes = {
            '0x00000000': 'gold amt',
            '0x00000001': 'Reputation',
            '0x00000002': 'Vyse.curHP',
            '0x00000003': 'Aika.curHP',
            '0x00000004': 'Fina.curHP',
            '0x00000005': 'Drachma.curHP',
            '0x00000006': 'Enrique.curHP',
            '0x00000007': 'Gilder.curHP',
            '0x0000004a': 'Vyse.lvl'
        }

        scpt_result = {}
        returned_value = ''
        param_key = '{}_S'.format(paramID)
        done = False
        roundNum = 0
        currentWord = getWord(sct_bytes, self.cursor * 4, 'hex')

        # First check that the first word is not a special value
        if currentWord in noLoop:
            scpt_result = {
                '0': 'Returned {}'.format(currentWord),
                'returned value': currentWord
            }
            return scpt_result

        # Resolve the SCPT analysis
        result_stack = [None] * 20
        result_stack_index = 0
        result_stack_max = 18
        while not done:
            currentWord = getWord(sct_bytes, self.cursor * 4, 'hex')
            currentResult = ''

            # Make sure that the SCPT Stack wouldn't overflow
            if result_stack_index >= result_stack_max:
                scpt_result[f'{param_key}{roundNum}'] = 'SCPT Stack overflow: {}'.format(currentWord)
                break

            # Check for end of the SCPT Analysis loop
            if currentWord == '0x0000001d':
                done = True
                scpt_result[f'{param_key}{roundNum}'] = 'return values (0x1d)'
                break

            # Test for values between the highest compare code and the prefix for a float
            if int('0x04000000', 16) > int(currentWord, 16) > int('0x00000016', 16):
                pass

            # Test whether the current word is a primary code
            elif currentWord in compare_codes.keys():
                currVals = {'1': result_stack[result_stack_index], '2': result_stack[result_stack_index + 1]}
                currentResult = {compare_codes[currentWord]: currVals}
                result_stack[result_stack_index] = currentResult
                result_stack_index -= 1
                if currentWord == '0x0000000a':
                    result_stack_index += 1
            elif currentWord in arithmetic_codes.keys():
                currVals = {'1': result_stack[result_stack_index], '2': result_stack[result_stack_index + 1]}
                inputs = []
                currentResult = {arithmetic_codes[currentWord]: currVals}
                for v in currVals.values():
                    if not isinstance(v, str):
                        v = str(v)
                    if re.search('^[0-9,.]+$', v) and 0 < len(v.split('.')) <= 2:
                        inputs.append(v)
                if len(inputs) == 2:
                    computeString = f'result = {inputs[0]} {arithmetic_codes[currentWord][3]} {inputs[1]}'
                    lcls = locals()
                    exec(computeString, {}, lcls)
                    result = lcls['result']
                    result_stack[result_stack_index] = result
                else:
                    result_stack[result_stack_index] = currentResult
                result_stack_index -= 1

            # If not, current action is to input a value
            else:
                action = ''
                description = ''

                # Determine the input type from the input_cutoffs table
                for key in input_cutoffs.keys():
                    if int(currentWord, 16) >= int(key, 16):
                        action = key
                        break

                # Resolve Input
                if not action == '0x50000000':
                    # Generate values from current word
                    if action == '':
                        currentResult = 'Unable to interpret SCPT instruction: {}'.format(currentWord)
                    else:
                        result = None
                        if action == '0x04000000':
                            self.cursor += 1
                            currentWord = getWord(sct_bytes, self.cursor * 4, 'hex')
                            obtainedValue = word2Float(currentWord)
                            result = obtainedValue
                        elif action == '0x08000000':
                            obtainedValue = int(applyHexMask(currentWord, '0x00ffff00'), 16)
                            obtainedValue += int(applyHexMask(currentWord, '0x000000ff'), 16) / 256
                            result = obtainedValue
                        else:
                            obtainedValue = str(int(applyHexMask(currentWord, '0x00ffffff'), 16))
                            if action == '0x40000000':
                                obtainedValue = str(int(obtainedValue) * 4)
                            if action in ('0x40000000', '0x10000000'):
                                obtainedValue += ']*'
                            result = input_cutoffs[action] + obtainedValue
                        if result is None:
                            result = 'no result'
                        result_stack[(result_stack_index + 2)] = result
                        currentResult = result
                        result_stack_index += 1

                # Go through secondary codes and perform a function
                else:
                    masked_currentWord = applyHexMask(currentWord, '0xffffff')
                    if masked_currentWord in secondary_codes.keys():
                        result = secondary_codes[masked_currentWord]
                        result_stack[(result_stack_index + 2)] = result
                        currentResult = result
                    else:
                        offset = int(masked_currentWord, 16) * 4
                        currentResult = input_cutoffs[action] + '{}]*'.format(offset)
                        result_stack[(result_stack_index + 2)] = currentResult
                    result_stack_index += 1

            scpt_result[f'{param_key}{roundNum}'] = {currentWord: currentResult}
            if not done:
                self.cursor += 1
                roundNum += 1
            if self.cursor >= self.sctLength:
                scpt_result['error'] = 'SCPTanalyze did not finish before next sct section'
                break

        if result_stack[2] is None:
            scpt_result['returned value'] = 'Error: No value generated'
        else:
            scpt_result['returned value'] = result_stack[2]
        return scpt_result

    @staticmethod
    def test_for_string(sct):
        cursor = 0
        if getWord(sct, cursor * 4, 'hex') == '0x00000009':
            currWord = '0x00000009'
            while not currWord == '0x0000001d':
                cursor += 1
                currWord = getWord(sct, cursor * 4, 'hex')
            cursor += 1
            testWord = getWord(sct, cursor * 4)
            if 0 <= testWord <= 265:
                return False
            else:
                return True
        else:
            return False
