from SALSA.byte_array_utils import getTypeFromString, toInt, asStringOfType, toFloat
import re

class SCTAnalysis:
    start_pos = None

    def __init__(self, sct_dict):
        self.Name = sct_dict['Name']
        self.Header = list(sct_dict['Header'].values())
        self.Index = sct_dict['Index']
        self.Stats = sct_dict['Stats']
        self.Positions = sct_dict['Positions']
        self.BodyLength = sct_dict['Body Length']
        self.FooterLength = sct_dict['Footer Length']
        self.TotalLength = self.BodyLength + self.FooterLength
        self.Sections = {}
        sectCount = 0
        for name, sect in sct_dict['Sections'].items():
            # print('Analyzing section {}'.format(sectCount))
            length = int(self.Index[name]['length'], 16)
            position = int(self.Index[name]['pos'], 16)
            self.Sections[name] = SCTSection(sect, name, length, position)
            sectCount += 1
        self.Footer = list(sct_dict['Footer'].values())
        self.IndexedInstructions = list(sct_dict['Implemented Instructions'])
        self.ErrorSections = sct_dict['Errors']
        self.Details = sct_dict['Details']
        # Provides a dictionary for linking segments. Key is position of requester, Value is position of requested
        self.Links = {}
        self.generate_links()

    def get_script_tree(self):
        """Request info from sections for either all or error"""
        script_tree = {}
        for key, value in self.Sections.items():
            current = {'Type': value.type, 'Length': value.length}
            script_tree[key] = current
        return script_tree

    def get_instruction_tree(self, scriptID):
        script = self.Sections[scriptID]
        inst_tree = script.get_instruction_tree(self.start_pos)
        return inst_tree

    def get_sct_info(self):
        sct_info = {'Filename': self.Name, 'Footer': "{}".format('\n'.join(self.Footer)),
                    'Errors': "{}".format('\n'.join(self.ErrorSections)),
                    'Script num': int(self.Header[2], 16), 'Insts': self.Details['Instructions Used']}
        return sct_info

    def get_instruction_details(self, sctID, instID):
        script = self.Sections[sctID]
        inst_details = script.get_instruction_details(instID)
        return inst_details

    def generate_links(self):
        section_links = {}
        for key, value in self.Sections.items():
            tempLinks = value.get_links()
            if not len(tempLinks) == 0:
                section_links[key] = tempLinks
        self.Links = link_results = {}
        for sect_key, sect_link in section_links.items():
            for inst_key, inst_link in sect_link.items():
                for key, link in inst_link.items():
                    target_sect = ''
                    target_pos = toInt(link['start']) + toInt(link['target offset'])
                    prev_sect = ''
                    for pos, label in self.Positions.items():
                        if target_pos < int(pos):
                            break
                        prev_sect = label
                    target_sect = prev_sect
                    # if target_sect == 'Footer44':
                        # print('stop here')
                    if target_pos > self.TotalLength:
                        target_inst_link_info = 'Unable to find link target: target beyond file size'
                    elif target_sect[:6] == "Footer":
                        footer_index = target_sect[6:]
                        target_inst_link_info = 'Links to {0}: {1}'.format(target_sect, self.Footer[int(footer_index)])
                    else:
                        target_inst_link_info = self.Sections[target_sect].get_instruction_link_info_by_position(target_pos)
                    if sect_key not in link_results.keys():
                        link_results[sect_key] = {}
                    if inst_key not in link_results[sect_key].keys():
                        link_results[sect_key][inst_key] = {}
                    link_results[sect_key][inst_key][key] = target_inst_link_info
        for key, value in link_results.items():
            self.Sections[key].set_links(value)

    def set_inst_start(self, start):
        self.start_pos = start

class SCTSection:

    def __init__(self, sect_dict, name, length, pos):
        self.name = name
        # if name == '_LOSE':
        #     print('stop here')
        self.length = length
        self.startPos = pos
        self.type = sect_dict['type']
        self.hasString = False
        if not sect_dict['string'] == '':
            self.hasString = True
            self.string = sect_dict['string']

        self.instructions = {}
        instCount = 0
        for key, value in sect_dict['data'].items():
            if key == 'errors':
                continue
            if key == 'final':
                break
            self.instructions[key] = SCTInstruct(self.startPos, value)
            instCount += 1

        self.hasError = False
        if 'errors' in sect_dict.keys():
            self.hasError = True

    def get_instruction_tree(self, start):
        instruction_tree = {}
        for key, value in self.instructions.items():
            current = {}
            code = value.ID
            if code == 'SCPT Parameter':
                current['Code'] = 'SCPT Par'
            elif code == 'Skip 2':
                current['Code'] = 'Skip 2'
            elif -1 < int(code, 16) < 265:
                if value.isDecoded:
                    current['Code'] = value.name
                else:
                    current['Code'] = '{0} ({1})'.format(int(code, 16), code)
            else:
                current['Code'] = value.ID
            current['Decoded'] = value.isDecoded
            if value.hasError:
                current['Error'] = value.get_error_types()
            else:
                current['Error'] = 'None'
            if start is not None:
                pos = int(key) * 4
                pos += self.startPos
                pos = hex(int(start, 16) + pos)
                current['pos'] = pos
            instruction_tree[key] = current
        if self.hasString:
            next = {
                'Code': 'String',
                'Decoded': True,
                'Error': 'None'
            }
            instruction_tree['16'] = next

        return instruction_tree

    def get_instruction_details(self, instID):
        if self.hasString and instID == '16':
            inst_details = {
                'Decoded': 'This String is Decoded',
                'Code': 'String',
                'Name': self.name,
                'Errors': {},
                'Param Tree': {},
                'Description': self.string
            }
        else:
            inst = self.instructions[instID]
            inst_details = inst.get_details()
        return inst_details

    def get_links(self):
        inst_links = {}
        for key, value in self.instructions.items():
            tempLinks = value.get_links()
            if tempLinks is not None:
                inst_links[key] = tempLinks
        return inst_links

    def get_instruction_link_info_by_position(self, pos):
        inst_pos = toInt(pos) - self.startPos
        if not inst_pos % 4 == 0:
            return 'Unable to establish link: position should be divisible by 4 to be at start of an instruction:' \
                   '\nScript: {0}, Instruction: {1}'.format(self.name, inst_pos)
        target_inst = inst_pos / 4
        link_info = 'Link to Section: {0}'.format(self.name)
        if not isinstance(target_inst, int):
            target_inst = int(target_inst)
        if target_inst == 0:
            if self.hasString:
                return link_info + '\nString:\n{}'.format(self.string)
            else:
                return link_info + ', Start of Section'
        if not str(target_inst) in self.instructions.keys():
            return 'Unable to establish link: given position does not correspond to an available instruction:' \
                   '\nScript: {0}, Instruction: {1}'.format(self.name, target_inst)
        return link_info + ', Instruction: {0}'.format(target_inst)

    def set_links(self, link_dict):
        for key, value in link_dict.items():
            self.instructions[key].set_link(value)


class SCTInstruct:
    desc_codes = ['add', 'sub', 'mul', 'lnk']

    def __init__(self, script_pos, inst_dict):

        self.isDecoded = inst_dict['decoded']
        self.hasError = False
        self.hasInstructError = False
        self.hasParamErrors = False
        self.hasSCPTerror = False
        self.errors = {}
        self.hasLink = False
        self.links = {}
        self.inst_pos = int(inst_dict['start location'])
        self.overall_pos = self.inst_pos + script_pos

        if not self.isDecoded:
            self.ID = inst_dict['data']['word']
        else:
            self.ID = hex(int(inst_dict['instruction']))
            # if self.ID == '0x87':
            #     print('stop here')
            self.name = inst_dict['name']
            if self.name == 'code_error':
                self.name += ': {0}({1})'.format(int(self.ID, 16), self.ID)
            elif self.name[:2] == '??':
                self.name += f' ({int(self.ID, 16)})'
            raw_description = inst_dict['description']
            self.pos = inst_dict['start location']
            self.paramNum = inst_dict['param num']

            if 'errors' in inst_dict.keys():
                self.hasError = True
                self.errors = inst_dict['errors']
                inst_dict = inst_dict.pop('errors')

                self.hasInstructError = False
                for value in self.errors.values():
                    if 'Instruction' in value:
                        self.HasInstructError = True

            self.hasParamErrors = False
            self.parameters = {}
            for key, value in inst_dict['parameters'].items():
                self.parameters[key] = SCTParam(key, value)
                if self.parameters[key].hasError:
                    self.hasParamErrors = True
                    self.hasError = True

            # if self.name == 'Switch':
            #     print('stop here')

            temp_description = self.description_insert_param_values(raw_description)
            self.description = self.resolveDescriptionFuncs(temp_description)

        if self.ID == 'SCPT Parameter':
            self.hasError = True
            self.hasSCPTerror = True
            self.errors = inst_dict['errors']

    def description_insert_param_values(self, d):
        desc = d
        paramSets = {}
        for param in self.parameters.values():
            name = param.name
            paramSets[name] = param.result

        for key, value in paramSets.items():
            keyword = '<{}>'.format(key)
            if not isinstance(value, str):
                value = str(value)
            result = value
            desc = desc.replace(keyword, result)

        return desc

    def get_details(self):
        if self.hasSCPTerror:
            details = {
                'Code': 'SCPT-specific Code was found before an appropriate instruction',
                'Decoded': 'SCPT',
            }
            error_string = ''
            for k, e in self.errors.items():
                error_string += '{0}: {1}\n'.format(k, e)
            details['Description'] = error_string
            return details
        if self.ID == 'Skip 2':
            inst_details = {'Code': 'Skip 2',
                            'Description': 'This is a skip of 2 positions. Not sure why yet, but necessary.'}
        else:
            inst_details = {'Code': '{0} ({1})'.format(int(self.ID, 16), self.ID)}
        if not self.isDecoded:
            inst_details['Decoded'] = 'This Instruction is NOT Decoded'
            inst_details['Description'] = ''
        else:
            inst_details['Name'] = self.name
            inst_details['Decoded'] = 'This Instruction is Decoded'
            inst_details['Description'] = self.description
            inst_details['Errors'] = '{}'.format('{0}: {1}\n'.join(self.errors.keys()).join(self.errors.values()))
            paramTree = {}
            for key, param in self.parameters.items():
                paramTree[key] = param.get_param_as_tree()
            inst_details['Param Tree'] = paramTree

        return inst_details

    def get_error_types(self):
        if self.hasSCPTerror:
            return 'SCPT'
        error_type = 'Inst'
        if self.hasParamErrors:
            error_type = 'Param'
            if self.hasInstructError:
                error_type = 'Both'

        return error_type

    def resolveDescriptionFuncs(self, temp_desc):
        """
        TODO - Work on description functions
        :return:
        """
        currentSubstring = temp_desc
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
                currentCommand = currentSubstring[:closeBrackets+2]
                currentSubstring = currentSubstring[closeBrackets+2:]
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


class SCTParam:
    parameter_types = ['int',
                       'masked-int',
                       'SCPT',
                       'override-SCPT',
                       'switch',
                       'loop']

    def __init__(self, key, param_dict):
        self.ID = key
        # print(self.ID)
        self.name = param_dict['name']
        self.type = param_dict['type']

        self.position = param_dict['position']
        self.hasError = False
        if 'int' in self.type:
            self.word = param_dict['result']['original value']
            self.result = param_dict['result']['result']
            if 'masked' in self.type:
                self.mask = param_dict['result']['mask']
                self.maskValue = param_dict['result']['mask']

        elif self.type not in self.parameter_types:
            self.type = 'unknown ({})'.format(param_dict['type'])
            self.hasError = True
            self.error = 'Unknown parameter type'
            self.result = 'Unknown result'

        elif 'loop' in self.type:
            self.result ='Loop:'
            self.loopBypass = False

            # TODO-Read loop bypass

            if 'Error' in param_dict['result'].keys():
                self.hasError = True
                self.error = param_dict['result']['Error']
                self.result = self.error
                self.loopEntries = {'0_0': 'Loop Error'}
                return

            if 'bypass' in param_dict['result'].keys():
                self.loopEntries = {'0_0': 'Loop Bypassed'}
                self.loopBypass = True
                self.result = 'Loop Bypassed'
                return

            self.loopEntries = {}
            self.loopIter = len(param_dict['result']['loop'])
            tempResult = param_dict['result']['loop']
            for key, item in tempResult.items():
                self.result += f'\nIteration {key}:'
                for key1, item1 in item.items():
                    tempID = f"{key}_{key1}"
                    self.loopEntries[tempID] = item1
                    if 'scpt' in item1['type']:
                        if isinstance(item1['result'], str):
                            out = item1['result']
                        elif isinstance(item1['result']['result'], str):
                            out = item1['result']['result']
                        else:
                            out = item1['result']['result']['returned value']
                    else:
                        out = item1['result']
                    self.result += f'\n\t({tempID}): {out}'

        elif self.type == 'SCPT':
            scptOut = param_dict['result']
            if 'error' in scptOut.keys():
                self.hasError = True
                self.error = scptOut['error']
                scptOut.pop('error')
            self.result = scptOut['returned value']
            self.result = self.formatSCPTResult()
            scptOut.pop('returned value')
            self.scptActions = scptOut

        elif self.type == 'override-SCPT':
            self.result = param_dict['result']

        elif self.type == 'switch':

            if 'Error' in param_dict['result'].keys():
                self.hasError = True
                self.error = param_dict['result']['Error']
                self.switchEntries = {'0': self.error}
                self.switchLimit = 0
                self.result = ''
                return
            else:
                self.switchEntries = param_dict['result']['Entries']
            self.switchLimit = param_dict['result']['Entry Limit']
            self.idx = list(self.switchEntries.keys())
            self.result = ''
            badList = False

            for i in self.idx:
                if not re.search('^[-,0-9]+$', i):
                    badList = True

            if len(self.idx) > self.switchLimit:
                badList = True
            if badList:
                self.result = '\n Bad Switch, probably a parameter instead \n '

            self.idx[-1] = self.switchLimit-1
            resultEntries = {}

            for i in range(len(self.idx)):
                if not re.search('^[-,0-9]+$', str(list(self.switchEntries.values())[i])):
                    print("pause here")
                offset = (i + 1) * 8 + list(self.switchEntries.values())[i]
                offset -= 4
                resultEntries[list(self.switchEntries.keys())[i]] = '*lnk[Switch,{}]*'.format(offset)
            self.result += ' \n'.join('{0}: {1}'.format(key, value) for key, value in resultEntries.items())

        else:
            raise IndexError('Somehow a parameter type was not chosen')

    def get_param_as_tree(self):

        param_dict = {
            'Name': self.name
        }
        if self.hasError:
            param_dict['Error'] = self.error
        else:
            param_dict['Error'] = 'None'

        if re.search('int', self.type):
            if re.search('masked', self.type):
                desc = 'This is a masked int: result: {0}, mask: {1} ({2})'.format(self.result, self.mask, self.word)
            else:
                desc = 'This is an integer: {0} ({1})'.format(self.result, self.word)
            param_dict['Details'] = desc
        elif self.type == 'override-SCPT':
            desc = 'This overrides an SCPTAnalyze call to return: {}'.format(self.result)
            param_dict['Details'] = desc
        elif self.type == 'SCPT':
            desc = 'This is an SCPTAnalyze call:'
            param_dict['Details'] = desc
            scpts = {}
            for key, value in self.scptActions.items():
                scpts[key] = value
            param_dict['SCPT'] = scpts
        elif self.type == 'switch':
            desc = 'This is a switch with a limit of {} entries'.format(self.switchLimit)
            param_dict['Details'] = desc
            entries = {}
            for key, value in self.switchEntries.items():
                newKey = 'sw_{}'.format(key)
                entries[newKey] = value
            param_dict['switch'] = entries
        elif self.type == 'loop':
            desc = 'This is a loop with {} iterations'.format(self.loopIter)
            param_dict['Details'] = desc
            entries = {}
            for key, value in self.loopEntries.items():
                newKey = 'l_{}'.format(key)
                entries[newKey] = value
            param_dict['loop'] = entries
        else:
            desc = 'This is an unknown parameter type:'
            param_dict['Details'] = desc

        # print(param_dict)
        return param_dict

    def formatSCPTResult(self):
        if not isinstance(self.result, dict):
            return self.result
        tempResult = self.unpack_result_dict(self.result, 0)
        return tempResult

    def unpack_result_dict(self, cur_dict, level):
        returnValue = ''
        for key, value in cur_dict.items():

            if not isinstance(value, dict):
                formatedReturn = '\n'
                tabs = '  ' * level
                formatedReturn += tabs
                returnValue += '{0}{1}: {2}'.format(formatedReturn, key, value)
            else:
                nextLevel = self.unpack_result_dict(value, level + 1)
                formatedReturn = '\n'
                tabs = '  ' * level
                formatedReturn += tabs
                returnValue += '{0}{1}: {2}'.format(formatedReturn, key, nextLevel)

        return returnValue
