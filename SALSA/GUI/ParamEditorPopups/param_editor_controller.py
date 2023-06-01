from typing import Union, Dict

from SALSA.BaseInstructions.bi_container import BaseParam
from SALSA.Common.constants import sep
from SALSA.Common.are_same_checker import are_same
from SALSA.Project.project_container import SCTParameter
from SALSA.GUI.ParamEditorPopups.param_editor_popup import ParamEditPopup, SCPTEditWidget, IntEditWidget, \
    FooterEditWidget, ObjectSelectionWidget, VarSelectionWidget
from SALSA.Scripts.scpt_param_codes import SCPTParamCodes


class ParamEditController:

    log_code = 'ParamEditCtrlr'

    def __init__(self, parent, callbacks):
        self.column_id = None
        self.param_id = None
        self.parent = parent
        self.callbacks = callbacks
        self.view: Union[None, ParamEditPopup] = None

        self.setup_view_fxns = {
            'int': self.setup_int_view,
            'scpt': self.setup_scpt_view
        }
        self.param: Union[None, SCTParameter] = None
        self.base_param: Union[None, BaseParam] = None
        self.scpt_codes = SCPTParamCodes()

        self.scpt_rows: Dict[str, int] = {}
        self.scpt_fields: Dict[str, SCPTEditWidget] = {}
        self.old_scpt_fields: Dict[str, SCPTEditWidget] = {}
        self.scpt_callbacks = {'add_child_scpt_rows': self.add_scpt_rows,
                               'remove_child_scpt_rows': self.remove_scpt_rows,
                               'has_changes': self.scpt_has_changed,
                               'save': self.scpt_save, 'close': self.close_view,
                               'clear_value': lambda: self.clear_value('scpt')}

        self.int_callbacks = {'save': self.int_save, 'close': self.close_view,
                              'clear_value': lambda: self.clear_value('int')}

        self.int_field: Union[None, IntEditWidget, ObjectSelectionWidget, FooterEditWidget] = None

    # ------------------------------------- #
    # Param Editor Show and Close functions #
    # ------------------------------------- #

    def show_param_editor(self, param: Union[SCTParameter, None], base_param: BaseParam, param_id=None, column_id=None):
        self.view = ParamEditPopup(self.parent)
        self.view.main_frame_label.config(text=base_param.type)
        self.param = param
        if self.param is not None:
            self.scpt_callbacks |= {'get_var_alias': self.callbacks['get_var_alias']}
        else:
            self.param_id = param_id
            self.column_id = column_id
        self.base_param = base_param
        base_type = base_param.type.split('-')[0]
        self.setup_view_fxns[base_type]()

    def close_view(self):
        self.view.destroy()
        self.view = None
        self.param = None
        self.base_param = None
        self.param_id = None
        self.column_id = None

    def clear_value(self, param_base_type):
        if param_base_type == 'scpt':
            self.clear_scpt()
        elif param_base_type == 'int':
            self.clear_int()
        else:
            print(f'{self.log_code}: Unrecognized reset value option: {param_base_type}')

    # ------------------------------------------- #
    # SCPT parameter editor initial setup methods #
    # ------------------------------------------- #

    # Initial SCPT Parameter View Setup
    def setup_scpt_view(self, cleared=False):
        self.view.set_callbacks(self.scpt_callbacks)
        self.scpt_rows['0'] = 0
        self.scpt_fields['0'] = SCPTEditWidget(parent=self.view.main_frame, callbacks=self.scpt_callbacks, key='0',
                                               is_base=self.param is None)
        self.scpt_fields['0'].grid(row=0, column=0, sticky='W')
        if cleared:
            return
        value = self.param.value if self.param is not None else self.base_param.default_value
        if value is None:
            return
        kwargs = {'value': value, 'cur_id': '0'}
        if self.param is not None:
            if self.param.override is not None:
                kwargs |= {'override': True}

        self.setup_scpt_from_value(value=value, cur_id='0')

    # Load scpt value into scpt widgets
    def setup_scpt_from_value(self, value, cur_id, override=False):
        if isinstance(value, dict):
            for key, parts in value.items():
                self.scpt_fields[cur_id].set_widget_values(key)
                new_keys = self.add_scpt_rows(cur_id)
                for i, value in enumerate(parts.values()):
                    self.setup_scpt_from_value(value=value, cur_id=new_keys[i])
        else:
            self.scpt_fields[cur_id].set_widget_values(value=value, override=override)

    # Clear SCPT value
    def clear_scpt(self):
        for field in self.scpt_fields.values():
            field.destroy()
        self.scpt_fields = {}
        self.scpt_rows = {}
        self.old_scpt_fields = {}
        self.setup_scpt_view(cleared=True)

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
                self.scpt_fields[key] = SCPTEditWidget(self.view.main_frame, self.scpt_callbacks, key, prefix=i + 1)
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

        # If editing a base parameter
        if self.param is None:
            self.callbacks['set_change'](self.param_id, self.column_id, new_scpt_value)
            return

        var_changes = self.get_var_changes(self.param.value, new_scpt_value)
        if var_changes is not None:
            self.callbacks['update_variables'](var_changes)
        if new_scpt_value == 'override':
            param_type = self.base_param.type.split('-')[1]
            value, override_value = self.scpt_codes.overrides[param_type]
            self.param.set_value(value=value, override_value=override_value)
        else:
            self.param.set_value(new_scpt_value)
        self.callbacks['refresh_inst']()
        self.callbacks['set_change']()

    def scpt_has_changed(self, new_scpt_value=None):
        if new_scpt_value is None:
            new_scpt_value = self.convert_scpt_widgets_to_value()
        old_scpt_value = self.param.value if self.param is not None else self.base_param.default_value
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
        elif scpt_class in ('decimal', 'float'):
            value = scpt_widget.get_input()
            if 'float' not in self.base_param.type and cur_id == '0' and value != 'override':
                value = int(value)
        else:
            value = None
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

    # -------------------------- #
    # Int parameter type methods #
    # -------------------------- #

    def setup_int_view(self):
        self.view.set_callbacks(self.int_callbacks)

        if self.param is None:
            self.int_field = IntEditWidget(self.view.main_frame, name=self.base_param.name)
            value = self.base_param.default_value
        elif 'subscript' in self.base_param.type:
            self.int_field = ObjectSelectionWidget(self.view.main_frame, name=self.base_param.name,
                                                   selection_list=self.callbacks['get_subscript_list']())
            value = self.param.link.target_trace[0]
        elif 'jump' in self.base_param.type:
            self.int_field = ObjectSelectionWidget(self.view.main_frame, name=self.base_param.name,
                                                   selection_list=self.callbacks['get_instruction_list']())
            value = self.callbacks['get_inst_identifier'](self.param.link.target_trace[0])
        elif 'footer' in self.base_param.type:
            self.int_field = FooterEditWidget(self.view.main_frame, name=self.base_param.name)
            value = self.param.link_result
        elif 'string' in self.base_param.type:
            self.int_field = ObjectSelectionWidget(self.view.main_frame, name=self.base_param.name,
                                                   selection_list=self.callbacks['get_string_list']())
            value = self.param.link_result

        elif 'var' in self.base_param.type:
            var_type = f'{self.base_param.type.split(sep)[-1].capitalize()}Var: '
            self.int_field = VarSelectionWidget(self.view.main_frame, name=f'{self.base_param.name} - {var_type}',
                                                var_type=var_type, signed=False, b_min=0)
            value = self.param.value
        else:
            self.int_field = IntEditWidget(self.view.main_frame, name=self.base_param.name)
            value = self.param.value
        self.int_field.grid(row=0, column=0)
        self.int_field.set_value(value)

    def int_save(self):
        value = self.int_field.get_value()

        cur_value = self.param.value if self.param is not None else self.base_param.default_value

        if value == 'None':
            value = None

        if value is None or cur_value is None:
            if value is None and cur_value is None:
                return

        elif value == cur_value:
            return

        if self.param is None:
            self.callbacks['set_change'](self.param_id, self.column_name, value)
            return

        if 'subscript' in self.base_param.type:
            inst_id = self.callbacks['get_first_inst'](value)
            self.param.link.target_trace = [value, inst_id]
        elif 'jump' in self.base_param.type:
            inst_id = self.callbacks['get_inst_by_pos'](value)
            self.param.link.target_trace[1] = inst_id
        elif 'footer' in self.base_param.type:
            self.param.link_result = value
        elif 'string' in self.base_param.type:
            self.param.link_result = value
        else:
            self.param.value = value

        self.callbacks['refresh_inst']()
        self.callbacks['set_change']()

    def clear_int(self):
        self.int_field.remove_value()
