import enum
from dataclasses import dataclass
from typing import Union

from SALSA.Common.constants import sep
from SALSA.BaseInstructions.bi_facade import BaseInstLibFacade
from SALSA.Project.project_container import SCTProject


class TokenType (enum.Enum):
    flag = 0
    search = 1
    filter = 2


@dataclass
class Token:
    type_: TokenType
    value: str

    def __contains__(self, item: Union[TokenType, str]):
        if isinstance(item, str):
            return item in self.value
        return item == self.type_

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.value == other.value and self.type_ == other.type_
        if isinstance(other, str):
            return other in self.value
        if isinstance(other, TokenType):
            return self.type_ == other
        return False


class TokenList (list):

    def __contains__(self, item: Union[Token, str, TokenType]):
        if isinstance(item, Token):
            return super.__contains__(item)
        if isinstance(item, TokenType) or isinstance(item, str):
            for t in self:
                if item in t:
                    return True
        return False


# Special characters

class SearchTokens:

    def __init__(self, string: str, special_tokens, filter_tokens):
        self.search = TokenList()
        self.locs = TokenList()
        self.filters = TokenList()
        if len(string) == 0:
            return
        combined_part = ''
        combine_level = 0
        for part in string.strip().split(' '):
            if len(part) == 0:
                if combine_level > 0:
                    combined_part += ' '
                continue

            if part[0] == '"':
                combine_level += 1
                if combine_level == 1:
                    if len(part) > 1:
                        combined_part += part[1:]
                    continue

            if combine_level > 0 and part[-1] == '"':
                combine_level -= 1
                part = (combined_part + f' {part[:-1]}').strip()
                combined_part = ''

            if combine_level > 0:
                combined_part += f' {part}'
                continue

            if part in special_tokens:
                self.locs.append(Token(TokenType.flag, part))
                continue

            is_search = True
            for f_token in filter_tokens:
                if len(part) <= len(f_token):
                    continue
                if f_token == part[:len(f_token)]:
                    self.filters.append(Token(TokenType.filter, part))
                    is_search = False
                    break

            if is_search:
                self.search.append(Token(TokenType.search, part))

    @classmethod
    def tokenize(cls, string, type_tokens, filter_tokens):
        return cls(string, type_tokens, filter_tokens)

    def __contains__(self, item: TokenType):
        for t in self.search + self.locs + self.filters:
            if item in t:
                return True
        return False

    def get_filter_list(self, key):
        return [i for i in self.filters if key in i]


loc_tokens = {
        'loc:inst': 'Search base inst details',
        'loc:param': 'Search parameter values',
        'loc:dialog': 'Search dialogue strings'
    }


filter_tokens = {
        'sct:': 'Search within specific script(s)',
        'sect:': 'Searches within specific section(s)',
        'inst:': 'Searches within a specific instruction(s)'
    }


class ProjectSearcher:

    def __init__(self, base_insts: BaseInstLibFacade, project: SCTProject):
        self.b_insts = base_insts
        self.prj = project

        self.search_loc_fxns = {
            'loc:inst': self.search_insts,
            'loc:param': self.search_params,
            'loc:dialog': self.search_dialogue
        }

    def search(self, search_string):
        tokens = SearchTokens.tokenize(search_string, list(loc_tokens.keys()), list(filter_tokens.keys()))

        search_locs = []
        if TokenType.flag not in tokens:
            search_locs += [k for k in self.search_loc_fxns.keys()]
        else:
            for token in tokens.locs:
                if token.value in self.search_loc_fxns.keys():
                    search_locs.append(token.value)

        links = {}
        for loc in search_locs:
            results = self.search_loc_fxns[loc](tokens)
            if len(results) > 0:
                links[loc[4:]] = results

        return links

    def search_insts(self, tokens: SearchTokens):
        r_insts = [int(t.value[5:]) for t in tokens.get_filter_list('inst:')]

        if len(r_insts) == 0:
            if len(tokens.search) > 0:
                r_insts = []
                for token in tokens.search:
                    for ind, inst in enumerate(self.b_insts.get_all_insts()):
                        if token.value in inst.name:
                            r_insts.append(ind)
                        elif token.value == str(inst.instruction_id):
                            r_insts.append(ind)
                        elif token.value in inst.description:
                            r_insts.append(ind)
                        elif token.value in inst.default_notes:
                            r_insts.append(ind)
                        elif inst.link_type is not None:
                            if token.value in inst.link_type:
                                r_insts.append(ind)
                        else:
                            for param in inst.params.values():
                                if token.value in param.name:
                                    r_insts.append(ind)
                                    break
                                if param.default_value is not None:
                                    if isinstance(param.default_value, str):
                                        if token.value in param.default_value:
                                            r_insts.append(ind)
                                            break
                                    elif token.value == param.default_value:
                                        r_insts.append(ind)
                                        break

            else:
                r_insts = [i for i, _ in enumerate(self.b_insts.get_all_insts())]

        sct_filters = tokens.get_filter_list('sct:')
        sect_filters = tokens.get_filter_list('sect:')
        links = {}
        for sct_name, sct in self.prj.scts.items():
            if len(sct_filters) > 0:
                if sct_name not in sct_filters:
                    continue
            for sect_name, sect in sct.sects.items():
                if len(sect_filters) > 0:
                    if sect_name not in sect_filters:
                        continue
                for inst_id, inst in sect.insts.items():
                    if inst.base_id in r_insts:
                        if sct_name not in links:
                            links[sct_name] = [(sect_name, inst_id)]
                        else:
                            links[sct_name].append((sect_name, inst_id))

        return links

    def search_params(self, tokens: SearchTokens):
        if len(tokens.search) == 0:
            return {}

        sct_filters = tokens.get_filter_list('sct:')
        sect_filters = tokens.get_filter_list('sect:')
        inst_filters = tokens.get_filter_list('inst:')
        links = {}
        for sct_name, sct in self.prj.scts.items():
            if len(sct_filters) > 0:
                if sct_name not in sct_filters:
                    continue

            for sect_name, sect in sct.sects.items():
                if len(sect_filters) > 0:
                    if sect_name not in sect_filters:
                        continue

                for inst_id, inst in sect.insts.items():
                    if len(inst_filters) > 0:
                        if inst.base_id not in inst_filters:
                            continue

                    for token in tokens.search:
                        if inst.delay_param is not None:
                            if token.value in str(inst.delay_param.value):
                                if sct_name not in links:
                                    links[sct_name] = []
                                links[sct_name].append((sect_name, inst_id, 'delay'))
                        for param_id, param in inst.params.items():
                            if 'string' in param.type or 'jump' in param.type:
                                continue
                            if token.value == str(param.value):
                                if sct_name not in links:
                                    links[sct_name] = []
                                links[sct_name].append((sect_name, inst_id, param_id))
                        for loop_ind, loop in enumerate(inst.l_params):
                            for param_id, param in loop.items():
                                if token.value == str(param.value):
                                    if sct_name not in links:
                                        links[sct_name] = []
                                    links[sct_name].append((sect_name, inst_id, f'{loop_ind}{sep}{param_id}'))

        return links

    def search_dialogue(self, tokens: SearchTokens):
        d_strings = {}
        sct_filters = tokens.get_filter_list('sct:')
        for sct_name, sct in self.prj.scts.items():
            if len(sct_filters) > 0:
                if sct_name not in sct_filters:
                    continue

            for sid, s in sct.strings.items():
                for token in tokens.search:
                    if sid == token.value or token.value in s:
                        if sct_name not in d_strings:
                            d_strings[sct_name] = []
                        d_strings[sct_name].append((sct.string_locations[sid], sid))

        return d_strings
