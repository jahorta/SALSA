from SALSA.BaseInstructions.bi_container import BaseInst
from Project.project_container import SCTInstruction
from SALSA.Common.byte_array_utils import getTypeFromString, toFloat, asStringOfType, toInt


class DescriptionFormatter:
    log_code = 'Instruction Details Formatter'

    def __init__(self, inst: SCTInstruction, base_inst: BaseInst):
        self.desc_codes = {
            'add': self._add,
            'sub': self._sub,
            'div': self._div,
            'mul': self._mul
        }
        self.inst = inst
        self.base_inst = base_inst

    @classmethod
    def get_formatted_description(cls, inst: SCTInstruction, base_inst: BaseInst):
        formatter = cls(inst, base_inst)
        description = formatter._get_description()
        return formatter._resolve_description_codes(description)

    def _get_description(self):
        desc = self.base_inst.description
        param_sets = {}
        params = self.base_inst.parameters
        for key, param in self.inst.parameters.items():
            name = params[key].name
            param_sets[name] = param.value

        for key, value in param_sets.items():
            keyword = f'<{key}>'
            if not isinstance(value, str):
                value = str(value)
            desc = desc.replace(keyword, value)

        return desc

    def _resolve_description_codes(self, temp_desc):

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
                result = self._run_desc_code(currentCommand)
                new_desc += '{} '.format(result)
            else:
                currentSubstring = currentSubstring[1:]
                new_desc += '*'

        return new_desc

    def _run_desc_code(self, code):
        command = code[1:4]
        params = code[5:-2]
        nextStarPos = params.find('*')
        nextCommaPos = params.find(',')
        if -1 < nextStarPos < nextCommaPos:
            internal_func = params[nextStarPos:] + ']*'
            params = self._run_desc_code(internal_func)
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
            param2 = self._run_desc_code(internal_func)

        if command not in self.desc_codes:
            result = ''
            print(f'{self.log_code}: Unknown command')
        else:
            result = self.desc_codes[command](param1, param2)

        return result + suffix

    @staticmethod
    def _add(param1, param2):
        result_type = getTypeFromString(param1)
        result = toInt(param1) + toInt(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def _sub(param1, param2):
        result_type = getTypeFromString(param1)
        result = toInt(param1) - toInt(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def _mul(param1, param2):
        result_type = getTypeFromString(param1)
        result = toFloat(param1) * toFloat(param2)
        result = asStringOfType(result, result_type)
        return result

    @staticmethod
    def _div(param1, param2):
        result_type = getTypeFromString(param1)
        result = toFloat(param1) / toFloat(param2)
        result = asStringOfType(result, result_type)
        return result
