from typing import List

from BaseInstructions.bi_container import BaseInst
from Common.byte_array_utils import getTypeFromString, toInt, asStringOfType, toFloat, float2Hex, padded_hex
from Project.project_container import SCTInstruction


def format_description(inst: SCTInstruction, base_inst: BaseInst):
    desc = description_insert_param_values(inst, base_inst)
    return resolveDescriptionFuncs(desc)


def description_insert_param_values(inst: SCTInstruction, base_inst: BaseInst):
    desc = base_inst.description
    if '<loop>' in desc:
        desc = desc.replace('<loop>', get_loop_desc(inst, base_inst))
    paramSets = {}
    for key, param in inst.parameters.items():
        paramSets[base_inst.parameters[key].name] = param.formatted_value
    for key, value in paramSets.items():
        keyword = f'<{key}>'
        result = str(value)
        desc = desc.replace(keyword, result)
    return desc


def get_loop_desc(inst, base_inst):
    result = ''
    if base_inst.loop is None:
        return result
    iterations = inst.parameters[base_inst.loop_iter].value
    for i in range(iterations):
        result += f'loop {i}'
        for param in inst.loop_parameters[i]:
            param: SCTParameter
            result += f'\n\t{param.ID}\t{param.formatted_value}'
        result += '\n'
    return result


def resolveDescriptionFuncs(desc):
    new_desc = ''
    char_ind = 0
    while char_ind < len(desc):
        next_char = desc[char_ind]
        if next_char == '*':
            result, char_ind = parse_desc_func(desc, char_ind)
            if result is not None:
                next_char = result
        new_desc += next_char
        char_ind += 1

    return new_desc


def parse_desc_func(desc, char_ind):
    cur_pos = char_ind
    cur_pos += 1
    command = desc[cur_pos: cur_pos+3]
    if command not in desc_code_funcs.keys():
        return None, char_ind

    cur_pos += 3
    result = desc[char_ind: cur_pos]

    if desc[cur_pos] != '[':
        return result, cur_pos

    cur_pos += 1
    params = []
    cur_param = ''
    while cur_pos < len(desc):
        next_char = desc[cur_pos]
        if next_char == ',':
            params.append(cur_param)
            cur_param = ''
        elif next_char == ']':
            params.append(cur_param)
            if not len(params) in func_param_nums[command]:
                return None, char_ind
            result = desc_code_funcs[command](*params)
            cur_pos += 2
            break
        elif next_char == '*':
            result, cur_pos = parse_desc_func(desc, cur_pos)
            if result is None:
                return result, cur_pos
            cur_param = result
        else:
            cur_param += next_char
        cur_pos += 1

    return result, cur_pos


def check_params_are_numeric(paramlist: List[str]):
    result = ''
    numeric = True
    for param in paramlist:
        if not param.lstrip('-').isnumeric():
            numeric = False
            result += f'(not numeric){param},'
        else:
            result += f'{param}'

    if numeric:
        return None
    return result


def add_desc_params(param1: str, param2: str):
    result = check_params_are_numeric([param1, param2])
    if result is not None:
        return result

    result_type = getTypeFromString(param1)
    result = toInt(param1) + toInt(param2)
    result = asStringOfType(result, result_type)
    return result


def subtract_desc_params(param1: str, param2: str):
    result = check_params_are_numeric([param1, param2])
    if result is not None:
        return result

    result_type = getTypeFromString(param1)
    result = toInt(param1) - toInt(param2)
    result = asStringOfType(result, result_type)
    return result


def multiply_desc_params(param1: str, param2: str):
    result = check_params_are_numeric([param1, param2])
    if result is not None:
        return result

    result_type = getTypeFromString(param1)
    result = toFloat(param1) * toFloat(param2)
    result = asStringOfType(result, result_type)
    return result


def hex_desc_params(param1: str, form='>'):
    result = check_params_are_numeric([param1])
    if result is not None:
        return result

    if '.' in param1:
        result = float2Hex(float(param1), form)
    else:
        result = padded_hex(int(param1), 8)
    return result


desc_code_funcs = {'add': add_desc_params,
                   'sub': subtract_desc_params,
                   'mul': multiply_desc_params,
                   'hex': hex_desc_params}


func_param_nums = {'add': [2],
                   'sub': [2],
                   'mul': [2],
                   'hex': [1, 2]}
