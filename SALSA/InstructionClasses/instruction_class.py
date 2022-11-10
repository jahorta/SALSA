import copy






###################################################################
###################################################################


# This will be depreciated for the class above eventually
class Instruct:
    """Takes in a dictionary containing instruction information and produces an object containing
    the necessary information to decode *.sct files"""

    def __init__(self, inst_dict):

        self.instID = inst_dict['Instruction ID']
        self.name = inst_dict['Name']
        if 'Description' in inst_dict.keys():
            self.description = inst_dict['Description']
        else:
            self.description = '\n'
        self.location = inst_dict['Location']
        self.param1 = inst_dict['Hard parameter one']
        self.param2 = inst_dict['Hard parameter two']
        self.implement = inst_dict['Implement']
        if 'Notes' in inst_dict.keys():
            self.notes = inst_dict['Notes']
        else:
            self.notes = '\n'

        self.parameters = {}
        if len(inst_dict['Parameters']) > 0:
            raw_parameters = inst_dict['Parameters']
            for key, param in raw_parameters.items():
                self.parameters[key] = Parameter(param)

        self.paramNum = len(self.parameters)

    def get_attribute(self, param):
        if param == 'id':
            return self.instID
        if param == 'name':
            return self.name
        if param == 'location':
            return self.location
        if param == 'hparam1':
            return self.param1
        if param == 'hparam2':
            return self.param2
        if param == 'implement':
            return self.implement
        if param == 'param num':
            return self.paramNum
        if param == 'params':
            return self.parameters
        if param == 'description':
            return self.description
        if param == 'notes':
            return self.notes
        return 'Error'

    def get_all(self):
        all_fields = {'Instruction ID': self.instID, 'Name': self.name, 'Description': self.description,
                      'Location': self.location, 'Hard parameter one': self.param1, 'Hard parameter two': self.param2,
                      'Implement': self.implement, 'Parameter num': self.paramNum, 'Notes': self.notes}
        param = {}
        currParam = 0
        for key, value in self.parameters.items():
            if currParam >= self.paramNum:
                break
            param[key] = value.get_fields()
            currParam += 1

        all_fields['Parameters'] = param

        return all_fields

    def set_inst(self, updated_details):
        # print(updated_details)
        self.instID = updated_details['Instruction ID']
        self.name = updated_details['Name']
        if 'Description' in updated_details.keys():
            self.description = updated_details['Description']
        self.location = updated_details['Location']
        self.param1 = updated_details['Hard parameter one']
        self.param2 = updated_details['Hard parameter two']
        self.implement = updated_details['Implement']
        self.notes = updated_details['Notes']
        self.paramNum = updated_details['Parameter num']
        if 'Parameters' in updated_details.keys():
            self.parameters = {}
            if len(updated_details['Parameters']) > 0:
                raw_parameters = updated_details['Parameters']
                for key, param in raw_parameters.items():
                    self.parameters[key] = Parameter(param)

    def set_inst_only(self, updated_details):
        # print(updated_details)
        self.instID = updated_details['Instruction ID']
        self.name = updated_details['Name']
        if 'Description' in updated_details.keys():
            self.description = updated_details['Description']
        self.location = updated_details['Location']
        self.param1 = updated_details['Hard parameter one']
        self.param2 = updated_details['Hard parameter two']
        self.implement = updated_details['Implement']
        self.paramNum = updated_details['Parameter num']
        self.notes = updated_details['Notes']

    def adjust_parameter_number(self, newParamNum, paramPos):

        currentParamNum = self.paramNum

        if currentParamNum < newParamNum:
            blankParam = {'Name': '', 'Type': '', 'Override': False, 'Override condition': '', 'Override offset': '0x00000000',
                          'Override result': '', 'Override compare': '0x00000000', 'Mask': False,
                          'Mask Value': '0x00000000'}
            if paramPos is None:
                for i in range(currentParamNum, newParamNum):
                    ID = str(i)
                    blankParam['ID'] = ID
                    self.parameters[ID] = Parameter(blankParam)
            else:
                for i in reversed(range(paramPos, currentParamNum)):
                    paramToMove = copy.deepcopy(self.parameters[str(i)])
                    self.parameters[str(i+1)] = paramToMove
                blankParam['ID'] = paramPos
                self.parameters[str(paramPos)] = Parameter(blankParam)
        elif newParamNum < currentParamNum:
            if paramPos is not None:
                for i in range(paramPos, newParamNum):
                    paramToMove = copy.deepcopy(self.parameters[str(i + 1)])
                    self.parameters[str(i)] = paramToMove

        self.paramNum = newParamNum

        self._remove_unused_parameters()

        for i in range(len(self.parameters)):
            curID = str(i)
            self.parameters[curID].paramID = curID
            curName = self.parameters[curID].name
            if curName == '' or curName.find('unknown') > -1:
                self.parameters[curID].name = f'unknown{curID}'

    def is_same_as(self, inst):
        oldInst = inst.get_all()
        newInst = self.get_all()
        if oldInst == newInst:
            return True
        else:
            return False

    def _remove_unused_parameters(self):
        if len(self.parameters) > self.paramNum:
            paramToRemove = len(self.parameters) - self.paramNum
            for i in reversed(range(paramToRemove)):
                ID = str(i + self.paramNum)
                self.parameters.pop(ID)

    def get_param_names(self, param_list):
        names = {}
        for param in self.parameters.values():
            if int(param.paramID) in param_list:
                names[int(param.paramID)] = param.name
        return names


class Parameter:

    def __init__(self, param_dict):

        self.paramID = param_dict['ID']
        self.name = param_dict['Name']
        self.type = param_dict['Type']
        self.hasOverride = param_dict['Override']
        self.overrideCondition = param_dict['Override condition']
        self.overrideOffset = param_dict['Override offset']
        self.overrideResult = param_dict['Override result']
        if 'Override compare' in param_dict.keys():
            self.overrideCompare = param_dict['Override compare']
        else:
            self.overrideCompare = '0x00000000'
        self.hasMask = param_dict['Mask']
        self.mask = param_dict['Mask Value']
        if 'Signed' in param_dict.keys():
            self.isSigned = param_dict['Signed']
        else:
            self.isSigned = False
        if 'Iterations' in param_dict.keys():
            self.iterationChoice = param_dict['Iterations']
            self.iterationID = self.iterationChoice[:self.iterationChoice.find('-')]
            self.iterationParam = self.iterationChoice[self.iterationChoice.find('-'):]
        else:
            self.iterationChoice = ''
        if 'Condition Parameter' in param_dict.keys():
            self.loopConditionParam = param_dict['Condition Parameter']
            if not self.loopConditionParam == '':
                self.loopConditionParamID = self.loopConditionParam[:self.loopConditionParam.find('-')]
                self.loopConditionParamName = self.loopConditionParam[self.loopConditionParam.find('-'):]
            self.loopConditionTest = param_dict['Condition Test']
            self.loopConditionValue = param_dict['Condition Value']
        else:
            self.loopConditionParam = ''
            self.loopConditionTest = ''
            self.loopConditionValue = ''

    def get_attribute(self, param):
        if param == 'id':
            return self.paramID
        if param == 'name':
            return self.name
        if param == 'type':
            return self.type
        if param == 'has override':
            return self.hasOverride
        if 'condition' in param:
            return self.overrideCondition
        if 'offset' in param:
            return self.overrideOffset
        if 'result' in param:
            return self.overrideOffset
        if param == 'has mask':
            return self.hasMask
        if param == 'mask':
            return self.mask

    def set_parameter_details(self, param_details):
        self.paramID = param_details['ID']
        self.name = param_details['Name']
        self.type = param_details['Type']
        self.hasOverride = param_details['Override']
        self.overrideCondition = param_details['Override condition']
        self.overrideOffset = param_details['Override offset']
        self.overrideResult = param_details['Override result']
        if 'Override compare' in param_details:
            self.overrideCompare = param_details['Override compare']
        self.hasMask = param_details['Mask']
        self.mask = param_details['Mask Value']
        self.isSigned = param_details['Signed']
        self.iterationChoice = param_details['Iterations']
        if not self.iterationChoice == '':
            self.iterationID = self.iterationChoice[:self.iterationChoice.find('-')]
            self.iterationParam = self.iterationChoice[self.iterationChoice.find('-'):]
        self.loopConditionParam = param_details['Condition Parameter']
        if not self.loopConditionParam == '':
            self.loopConditionParamID = self.loopConditionParam[:self.loopConditionParam.find('-')]
            self.loopConditionParamName = self.loopConditionParam[self.loopConditionParam.find('-'):]
        self.loopConditionTest = param_details['Condition Test']
        self.loopConditionValue = param_details['Condition Value']

    def get_fields(self):
        param_dict = {'ID': self.paramID, 'Name': self.name, 'Type': self.type, 'Override': self.hasOverride,
                      'Override condition': self.overrideCondition, 'Override offset': self.overrideOffset,
                      'Override result': self.overrideResult, 'Override compare': self.overrideCompare,
                      'Mask': self.hasMask, 'Mask Value': self.mask, 'Signed': self.isSigned,
                      'Iterations': self.iterationChoice, 'Condition Parameter': self.loopConditionParam,
                      'Condition Test': self.loopConditionTest, 'Condition Value': self.loopConditionValue}
        return param_dict