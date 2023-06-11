string_replace_list = [
    ('\\h', ''),
    ('\\e', ''),
    ('\\c', ''),
    ('\\n', '\n'),
    ('', ' '),
    ('…', '...')
]


def SAstr_to_visible(string):
    for item in string_replace_list:
        string = string.replace(item[0], item[1])
    return string


def visible_to_SAstr(string):
    for item in string_replace_list:
        if item[0] == '':
            continue
        string = string.replace(item[1], item[0])
    return string


def SAstr_to_head_and_body(string):
    head_start = string.find('《') + 1
    head_end = string.find('》')
    head = SAstr_to_visible(string[head_start:head_end])
    body_start = string.find(')') + 1
    body = SAstr_to_visible(string[body_start:])
    return head, body


def head_and_body_to_SAstr(head, body):
    head = visible_to_SAstr(head)
    body = visible_to_SAstr(body)
    return f'\\h(《{head}》){body}\\e'
