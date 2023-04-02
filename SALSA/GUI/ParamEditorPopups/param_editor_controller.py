from typing import Union, Dict

from SALSA.BaseInstructions.bi_container import BaseParam
from SALSA.Common.constants import sep
from SALSA.Common.are_same_checker import are_same
from SALSA.Project.project_container import SCTParameter
from SALSA.GUI.ParamEditorPopups.param_editor_popup import ParamEditPopup, SCPTEditWidget


class ParamEditController:

    def __init__(self, parent, callbacks):
        self.parent = parent
        self.callbacks = callbacks
        self.view: Union[None, ParamEditPopup] = None

        self.setup_view_fxns = {
            'int': self.setup_int_view,
            'scpt': self.setup_scpt_view
        }
        self.param: Union[None, SCTParameter] = None
        self.base_param: Union[None, BaseParam] = None

        self.scpt_rows: Dict[str, int] = {}
        self.scpt_fields: Dict[str, SCPTEditWidget] = {}
        self.old_scpt_fields: Dict[str, SCPTEditWidget] = {}
        self.scpt_callbacks = {'add_child_scpt_rows': self.add_scpt_rows,
                               'remove_child_scpt_rows': self.remove_scpt_rows,
                               'get_var_alias': self.callbacks['get_var_alias'],
                               'has_changes': self.scpt_has_changed,
                               'save': self.scpt_save,
                               'close': self.close_view}

    # ------------------------------------- #
    # Param Editor Show and Close functions #
    # ------------------------------------- #

    def show_param_editor(self, param: SCTParameter, base_param: BaseParam):
        self.view = ParamEditPopup(self.parent)
        self.view.main_frame_label.config(text=base_param.type)
        self.param = param
        self.base_param = base_param
        base_type = base_param.type.split('-')[0]
        self.setup_view_fxns[base_type]()

    def close_view(self):
        self.view.destroy()
        self.view = None
        self.param = None
        self.base_param = None

    # ------------------------------------------- #
    # SCPT parameter editor initial setup methods #
    # ------------------------------------------- #

    # Initial SCPT Parameter View Setup
    def setup_scpt_view(self):
        self.view.set_callbacks(self.scpt_callbacks)
        self.scpt_rows['0'] = 0
        self.scpt_fields['0'] = SCPTEditWidget(self.view.main_frame, self.scpt_callbacks, '0')
        self.scpt_fields['0'].grid(row=0, column=0, sticky='W')

        if self.param.value is not None:
            self.setup_scpt_from_value(value=self.param.value, cur_id='0')

    # Load scpt value into scpt widgets
    def setup_scpt_from_value(self, value, cur_id):
        if isinstance(value, dict):
            for key, parts in value.items():
                self.scpt_fields[cur_id].set_widget_values(key)
                new_keys = self.add_scpt_rows(cur_id)
                for i, value in enumerate(parts.values()):
                    self.setup_scpt_from_value(value=value, cur_id=new_keys[i])
        else:
            self.scpt_fields[cur_id].set_widget_values(value=value)

    # ------------------------------------------- #
    # SCPT parameter editor functionality methods #
    # ------------------------------------------- #

    def add_scpt_rows(self, p_key):
        if p_key not in self.scpt_rows:
            return

        changed_keys = []

        p_row = self.scpt_rows[p_key]
        for key in self.scpt_rows:
            if self.scpt_rows[key] > p_row:
                self.scpt_rows[key] += 2
                changed_keys.append(key)

        new_keys = [f'{p_key}{sep}{j}' for j in range(0, 2)]
        for i, key in enumerate(new_keys):
            changed_keys.append(key)
            if key in self.old_scpt_fields:
                self.scpt_fields[key] = self.old_scpt_fields.pop(key)
                self.scpt_rows[key] = p_row + i + 1
            else:
                self.scpt_fields[key] = SCPTEditWidget(self.view.main_frame, self.scpt_callbacks, key, prefix=i+1)
                self.scpt_rows[key] = p_row + i + 1

        self.regrid_scpt_rows(changed_keys)

        return new_keys

    def remove_scpt_rows(self, p_key):
        if p_key not in self.scpt_rows:
            return

        keys_to_pop = []
        for key in self.scpt_rows.keys():
            if p_key in key and p_key != key:
                keys_to_pop.append(key)

        if len(keys_to_pop) == 0:
            return

        changed_keys = []

        for key in keys_to_pop:
            self.scpt_rows.pop(key)
            self.old_scpt_fields[key] = self.scpt_fields.pop(key)
            self.old_scpt_fields[key].grid_remove()

        p_row = self.scpt_rows[p_key]
        for key in self.scpt_rows:
            if self.scpt_rows[key] > p_row:
                self.scpt_rows[key] -= 2
                changed_keys.append(key)

        self.regrid_scpt_rows(changed_keys=changed_keys)

    def regrid_scpt_rows(self, changed_keys):
        for key in changed_keys:
            self.scpt_fields[key].grid(row=self.scpt_rows[key], column=0, sticky='W')

    # ---------------------------------------- #
    # SCPT Parameter Editor Validation methods #
    # ---------------------------------------- #

    def scpt_save(self):
        new_scpt_value = self.convert_scpt_widgets_to_value()
        if not self.scpt_has_changed(new_scpt_value):
            return
        var_changes = self.get_var_changes(self.param.value, new_scpt_value)
        if var_changes is not None:
            self.callbacks['update_variables'](var_changes)
        self.param.value = new_scpt_value

    def scpt_has_changed(self, new_scpt_value=None):
        if new_scpt_value is None:
            new_scpt_value = self.convert_scpt_widgets_to_value()
        old_scpt_value = self.param.value
        return not are_same(old_scpt_value, new_scpt_value)

    def convert_scpt_widgets_to_value(self, cur_id='0'):
        scpt_widget = self.scpt_fields[cur_id]
        scpt_class = scpt_widget.class_selection.get()
        if scpt_class in ('compare', 'arithmetic'):
            value = {scpt_widget.option_selection.get(): {
                '1': self.convert_scpt_widgets_to_value(cur_id=f'{cur_id}{sep}0'),
                '2': self.convert_scpt_widgets_to_value(cur_id=f'{cur_id}{sep}1')
            }}
        elif scpt_class == 'secondary':
            value = scpt_widget.option_selection.get()
        else:
            value = scpt_widget.get_input()
            if 'float' not in self.base_param.type and cur_id == '0':
                value = int(value)
        return value

    def get_var_changes(self, old_param, new_param):
        old_var_list = self.get_vars(old_param)
        new_var_list = self.get_vars(new_param)
        add_list = []
        for var in new_var_list:
            if var not in old_var_list:
                add_list.append(var)
        remove_list = []
        for var in old_var_list:
            if var not in new_var_list:
                remove_list.append(var)
        changes = {}
        if len(add_list) > 0:
            changes['add'] = add_list
        if len(remove_list) > 0:
            changes['remove'] = remove_list
        return None if len(changes) == 0 else changes

    def get_vars(self, param_value, cur_list=None):
        if cur_list is None:
            cur_list = []
        if isinstance(param_value, dict):
            for value in param_value.values():
                cur_list = self.get_vars(value, cur_list=cur_list)
        elif isinstance(param_value, str):
            if 'Var: ' not in param_value:
                return cur_list
            cur_list.append(param_value)
        return cur_list

    # ---------------------------- #
    # Other parameter type methods #
    # ---------------------------- #

    def setup_int_view(self):
        pass
