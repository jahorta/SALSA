import math
from typing import List

from SALSA.BaseInstructions.bi_container import BaseInst
from SALSA.Common.byte_array_utils import getTypeFromString, toInt, asStringOfType, toFloat, float2Hex, padded_hex, is_hex
from SALSA.Project.project_container import SCTInstruction, SCTParameter


def format_description(inst: SCTInstruction, base_inst: BaseInst, callbacks):
    desc = description_insert_param_values(inst, base_inst, callbacks)
    return resolveDescriptionFuncs(desc, inst, base_inst, callbacks)


def description_insert_param_values(inst: SCTInstruction, base_inst: BaseInst, callbacks):
    desc = base_inst.description
    if '<loop>' in desc:
        desc = desc.replace('<loop>', get_loop_desc(inst, base_inst))
    if '<switch>' in desc:
        desc = desc.replace('<switch>', get_switch_desc(inst, base_inst, callbacks))
    paramSets = {}
    for key, param in inst.params.items():
        paramSets[base_inst.params[key].name] = param.formatted_value
    for key, value in paramSets.items():
        keyword = f'<{key}>'
        result = str(value)
        desc = desc.replace(keyword, result)
    return desc


def get_loop_desc(inst, base_inst):
    result = ''
    if base_inst.loop is None:
        return result
    iterations = inst.params[base_inst.loop_iter].value
    for i in range(iterations):
        result += f'loop {i}'
        for param in inst.l_params[i].values():
            result += f'\n\t{param.ID}\t{param.formatted_value}'
        result += '\n'
    return result


def get_switch_desc(inst, base_inst, callbacks):
    result = f'{inst.condition}'
    if base_inst.loop is None:
        return result
    iterations = inst.params[base_inst.loop_iter].value
    for i in range(iterations):
        l_param = inst.l_params[i]
        result += f'\n\t{l_param[2].value}: {callbacks["get_inst"](l_param[3].link)}'
    return result


def resolveDescriptionFuncs(desc, inst, base_inst, callbacks):
    new_desc = ''
    char_ind = 0
    while char_ind < len(desc):
        next_char = desc[char_ind]
        if next_char == '*':
            result, char_ind = parse_desc_func(desc, char_ind, inst, base_inst, callbacks)
            if result is not None:
                next_char = result
        new_desc += next_char
        char_ind += 1

    return new_desc


def parse_desc_func(desc, char_ind, inst, base_inst, callbacks):
    cur_pos = char_ind
    cur_pos += 1
    command = desc[cur_pos: cur_pos + 3]
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
            if not len(params) in desc_code_param_nums[command]:
                return None, char_ind
            result = desc_code_funcs[command](*params, inst=inst, base_inst=base_inst, callbacks=callbacks)
            cur_pos += 2
            break
        elif next_char == '*':
            result, cur_pos = parse_desc_func(desc, cur_pos, inst, base_inst, callbacks)
            if result is None:
                return result, cur_pos
            cur_param = result
        else:
            cur_param += next_char
        cur_pos += 1

    return result, cur_pos


# --------------------------------------------------- #
# Check that parameter is numeric conversion function #
# --------------------------------------------------- #

def check_params_are_numeric(paramlist: List[str]):
    result = ''
    numeric = True
    for param in paramlist:
        if not param.lstrip('-').isnumeric():
            numeric = False
        result += f'{param},'

    if numeric:
        return None
    return result


# -------------------- #
# Arithmetic functions #
# -------------------- #

def add_desc_params(param1: str, param2: str, **kwargs):
    result = check_params_are_numeric([param1, param2])
    if result is not None:
        return result

    result_type = getTypeFromString(param1)
    result = toInt(param1) + toInt(param2)
    result = asStringOfType(result, result_type)
    return result


def subtract_desc_params(param1: str, param2: str, **kwargs):
    result = check_params_are_numeric([param1, param2])
    if result is not None:
        return result

    result_type = getTypeFromString(param1)
    result = toInt(param1) - toInt(param2)
    result = asStringOfType(result, result_type)
    return result


def multiply_desc_params(param1: str, param2: str, **kwargs):
    result = check_params_are_numeric([param1, param2])
    if result is not None:
        return result

    result_type = getTypeFromString(param1)
    result = toFloat(param1) * toFloat(param2)
    result = asStringOfType(result, result_type)
    return result


# ----------------------- #
# Hex conversion function #
# ----------------------- #

def hex_desc_params(param1: str, form='>', **kwargs):
    result = check_params_are_numeric([param1])
    if result is not None:
        return result

    if '.' in param1:
        result = float2Hex(float(param1), form)
    else:
        result = padded_hex(int(param1), 8)
    return result


# ---------------------------------------------------------------------- #
# Variable name and location conversion functions and relevant variables #
# ---------------------------------------------------------------------- #

var_locs = {
    'Bit': '0x80310b3c',
    'Byte': '0x80310a1c',
    'Int': '0x8030e3e4',
    'Float': '0x8030e514'
}

var_sizes = {
    'Bit': 1/8,
    'Byte': 1,
    'Int': 4,
    'Float': 4
}


def replace_vars_with_locs(param1: str, **kwargs):
    var_pieces = param1.split('Var: ')
    if len(var_pieces) == 1:
        return param1
    result = ' '.join(var_pieces[0].split(' ')[:-1])
    for i in range(len(var_pieces)):
        if i == len(var_pieces)-1:
            result += ' '.join(var_pieces[i].split(' ')[-1])
            continue
        successful = True
        var_type = var_pieces[i].split(' ')[-1]
        if var_type not in var_locs:
            successful = False
        var_ind = var_pieces[i+1].split(" ")[0]
        if not var_ind.isnumeric():
            successful = False
        offset = var_sizes[var_type] * int(var_ind)
        offset_int = math.floor(offset)
        loc = hex(int(var_locs[var_type], 16) + offset_int)
        var_loc_str = loc
        remainder = offset - offset_int
        if var_sizes[var_type] < 0:
            exponent = round(remainder * 8)
            var_loc_str += f' & {padded_hex(2**exponent, 2)}'
        if not successful:
            result += f'{var_pieces[i]}Var: '
            result += var_pieces[i+1].split(" ")[0]
        else:
            result += ' '.join(var_pieces[i].split(' ')[1:-1])
            result += f' {var_loc_str}'


# ----------------------- #
# String display function #
# ----------------------- #

def get_parameter_string(param_name, inst: SCTInstruction, base_inst: BaseInst, callbacks):
    string_id = None
    for param in inst.params.values():
        if base_inst.params[param.ID].name == param_name:
            string_id = param.linked_string
    if string_id is None:
        return f'No string found for parameter {param_name}'
    no_head, head, body = callbacks['get_str'](string_id)
    if head is None:
        head = ''
    connector = '\n' if no_head else ''
    return f'{head}{connector}{body}'

# ------------------------------------------------------------------ #
# Dicts for description code functions and allowed parameter numbers #
# ------------------------------------------------------------------ #

desc_code_funcs = {
    'add': add_desc_params,
    'sub': subtract_desc_params,
    'mul': multiply_desc_params,
    'hex': hex_desc_params,
    'loc': replace_vars_with_locs,
    'str': get_parameter_string
}

desc_code_param_nums = {
    'add': [2],
    'sub': [2],
    'mul': [2],
    'hex': [1, 2],
    'loc': [1],
    'str': [1]
}
