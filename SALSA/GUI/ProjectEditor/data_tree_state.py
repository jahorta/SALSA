from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Dict


@dataclass
class DataViewState:
    open_items: list
    scroll_height: float
    selected_iid: tuple[str]

@dataclass
class DataViewNode:
    state: Union[DataViewState, None]
    children: Union[Dict[str, DataViewNode], None]


class ChildViewStateTree:
    _states: Dict[str, DataViewNode] = {}

    def set_state(self, state: DataViewState, script, section=None, instruction=None):
        if script is None:
            return

        if script not in self._states:
            self._states[script] = DataViewNode(None, {})

        if section is None:
            self._states[script].state = state
            return

        if section not in self._states[script].children:
            self._states[script].children[section] = DataViewNode(None, {})

        if instruction is None:
            self._states[script].children[section].state = state
            return

        if instruction not in self._states[script].children[section].children:
            self._states[script].children[section].children[instruction] = DataViewNode(None, None)

    def get_state(self, script, section=None, instruction=None):
        if script not in self._states:
            return None

        cur_level = self._states[script]
        if section is not None:
            if section not in cur_level.children:
                return None

            cur_level = cur_level.children[section]
            if instruction is not None:
                if instruction not in cur_level.children:
                    return None

                cur_level = cur_level.children[instruction]

        return cur_level.state

    def reset(self):
        self._states = {}
