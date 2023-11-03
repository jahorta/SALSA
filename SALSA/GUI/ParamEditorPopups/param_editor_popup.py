import math
import tkinter as tk
from tkinter import ttk
from typing import Union, Dict, List

import SALSA.GUI.Widgets.widgets as w
from SALSA.GUI.themes import light_theme, dark_theme
from SALSA.Common.constants import sep
from SALSA.Scripts.scpt_param_codes import SCPTParamCodes


# --------------------------- #
# Widgets for SCPT parameters #
# --------------------------- #

# SCPT decimal input widget
class DecimalWidget(ttk.Frame):

    def __init__(self, parent, textvariables, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.left_variable = textvariables[0]
        self.left_field = w.RequiredIntEntry(self, b_min=0, b_max=0xffff, width=7, textvariable=self.left_variable)
        self.left_field.grid(row=0, column=0)

        center_label = ttk.Label(self, text='+')
        center_label.grid(row=0, column=1)

        self.right_variable = textvariables[1]
        self.right_field = w.RequiredIntEntry(self, b_min=0, b_max=255, width=4, textvariable=self.right_variable)
        self.right_field.grid(row=0, column=2)

        right_label = ttk.Label(self, text='/256')
        right_label.grid(row=0, column=3)


# SCPT variable input widget
class SCPTVarWidget(ttk.Frame):

    def __init__(self, parent, textvariable, callbacks, is_base, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks

        self.var_variable = textvariable
        self.var_entry = w.RequiredIntEntry(self, width=10, textvariable=self.var_variable)
        self.var_entry.grid(row=0, column=0, sticky=tk.W)
        if not is_base:
            self.var_entry.bind('<FocusOut>', self.load_alias)
            self.var_entry.bind('<Return>', self.load_alias)

        self.alias_label = ttk.Label(self, text='No Alias')
        self.alias_label.grid(row=0, column=1, sticky=tk.W)

    def load_alias(self, e):
        alias = self.callbacks['get_alias']()
        if alias == '':
            alias = 'No Alias'
        self.alias_label.config(text=alias)


class SCPTFloatWidget(ttk.Frame):

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        self.scpt_codes = SCPTParamCodes(is_decoder=False)

        self.float_variable = tk.StringVar(self)
        self.float = w.RequiredFloatEntry(self, textvariable=self.float_variable, width=11)
        self.float.grid(row=0, column=0)

        self.override_value = tk.IntVar(self, 0)
        override = ttk.Checkbutton(self, text='Override Parameter', variable=self.override_value,
                                   command=self.override_clicked)
        override.grid(row=0, column=1)

    def override_clicked(self):
        if self.override_value.get() == 1:
            self.set_override()
        else:
            self.clear_override()

    def set_override(self, init=False):
        self.float.configure(state='disabled')
        if init:
            self.override_value.set(1)

    def clear_override(self):
        self.float.configure(state='normal')

    def get_value(self):
        if self.override_value.get() == 1:
            return 'override'
        return self.float_variable.get()

    def set_value(self, value):
        if value == 'override':
            self.set_override(init=True)
            return
        self.float_variable.set(value)


# Single row widget of SCPT parameter
class SCPTEditWidget(ttk.Frame):

    def __init__(self, parent, callbacks, key: str, is_base, *args, prefix='', is_delay=False, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        self.scpt_codes = SCPTParamCodes(is_decoder=False)
        self.key = key
        self.is_base = is_base
        self.rowconfigure(0, weight=1)

        indent = '\t' * key.count(sep)
        self.prefix_label = ttk.Label(self, text=f'{indent} {prefix}')
        self.prefix_label.grid(row=0, column=0)

        class_options = self.scpt_codes.classes
        if is_delay:
            class_options = ['arithmetic', 'input']

        self.class_selection = tk.StringVar(self)
        self.class_option = ttk.OptionMenu(self, self.class_selection, '---', *class_options,
                                           command=lambda e: self.update_options())
        self.class_option.grid(row=0, column=1, sticky='NSEW')

        self.option_selection = tk.StringVar(self, '---')
        self.option_option = ttk.OptionMenu(self, self.option_selection, '---')
        self.option_option.configure(state='disabled')
        self.option_option.grid(row=0, column=2, sticky='NSEW')

        self.input_option_selection = ''
        self.secondary_option_selection = ''

        self.input_vars = {
            'var': tk.IntVar(self),
            'decimal': [tk.IntVar(self), tk.IntVar(self)]
        }

        self.input_widgets: Dict[str, Union[SCPTVarWidget, SCPTFloatWidget, DecimalWidget]] = {
            'var': SCPTVarWidget(self, textvariable=self.input_vars['var'], callbacks={'get_alias': self.get_var_alias},
                                 is_base=is_base),
            'float': SCPTFloatWidget(self, callbacks={}),
            'decimal': DecimalWidget(self, textvariables=self.input_vars['decimal'])
        }

        self.prev_active_widget = ''
        self.active_widget = ''

    def update_options(self):
        class_selected = self.class_selection.get()
        option_list = list(self.scpt_codes.__getattribute__(class_selected).keys())
        self.option_option.configure(state='normal')
        self.option_option['menu'].delete(0, 'end')
        for option in option_list:
            self.option_option['menu'].add_command(label=option, command=lambda o=option: self.choose_option(o))

        if self.active_widget != '':
            self.prev_active_widget = self.active_widget

        if class_selected in ('compare', 'arithmetic'):
            if self.active_widget != '':
                self.set_active_input_widget('')
            self.option_selection.set(option_list[0])
        elif class_selected == 'secondary':
            if self.active_widget != '':
                self.set_active_input_widget('')
            self.option_selection.set(self.secondary_option_selection)
        elif class_selected == 'input':
            if self.prev_active_widget != self.active_widget:
                self.set_active_input_widget(self.prev_active_widget)
            self.option_selection.set(self.secondary_option_selection)

    def choose_option(self, option):
        self.option_selection.set(option)
        self.update_input_entry()

    def update_input_entry(self):
        if self.class_selection.get() in ('compare', 'arithmetic'):
            # May need to ungrid other entry fields
            self.callbacks['add_child_scpt_rows'](self.key, self.is_base)
            self.set_active_input_widget('')
            return
        self.callbacks['remove_child_scpt_rows'](self.key)

        option_selection = self.option_selection.get()
        if self.class_selection.get() == 'secondary':
            self.secondary_option_selection = option_selection
            return
        self.input_option_selection = option_selection
        widget_type = 'float'
        widget_type = 'var' if 'Var' in option_selection else widget_type
        widget_type = 'decimal' if 'decimal' in option_selection else widget_type
        self.set_active_input_widget(widget_type)

    def set_active_input_widget(self, widget_key):
        if self.active_widget != '':
            self.input_widgets[self.active_widget].grid_remove()
        if widget_key == '':
            return
        self.active_widget = widget_key
        self.input_widgets[widget_key].grid(row=0, column=3, sticky='NSEW')

    def set_widget_values(self, value, override=None):
        self.option_option.configure(state='normal')

        # If value was cleared
        if value is None:
            self.class_selection.set('---')

        # Value is a compare type scpt code
        elif value in self.scpt_codes.compare:
            self.class_selection.set('compare')
            self.update_options()
            self.option_selection.set(value)

        # Value is an arithmetic type scpt code
        elif value in self.scpt_codes.arithmetic:
            self.class_selection.set('arithmetic')
            self.update_options()
            self.option_selection.set(value)

        # Value is a secondary code to get a specific value (Reputation, gold, Character level, etc...)
        elif value in self.scpt_codes.secondary:
            self.class_selection.set('secondary')
            self.update_options()
            self.option_selection.set(value)
            self.secondary_option_selection = value

        # Value is either a variable or a decimal
        elif isinstance(value, str):
            if '/' in value:
                self.class_selection.set('input')
                self.update_options()
                self.option_selection.set('decimal')
                self.set_active_input_widget('decimal')
                value_parts = value.split('/')
                all_value_parts = []
                for part in value_parts:
                    all_value_parts += part.split('+')
                dec_0 = int(all_value_parts[0].split(' ')[1])
                dec_1 = int(all_value_parts[1])
                self.input_vars['decimal'][0].set(dec_0)
                self.input_vars['decimal'][1].set(dec_1)
                self.input_option_selection = 'decimal'
            elif 'Var' in value:
                var_parts = value.split(': ')
                var_type = var_parts[0]
                var_value = int(var_parts[1])
                self.class_selection.set('input')
                self.update_options()
                self.option_selection.set(f'{var_type}: ')
                self.set_active_input_widget('var')
                self.input_vars['var'].set(var_value)
                self.input_widgets['var'].load_alias(None)
                self.input_option_selection = f'{var_type}: '
            else:
                print(f'unknown value type: {value}')

        # Value is just a number to input
        else:
            self.class_selection.set('input')
            self.update_options()
            self.option_selection.set('float: ')
            self.set_active_input_widget('float')
            if override:
                value = 'override'
            self.input_widgets['float'].set_value(value)
            self.input_option_selection = value

    def get_var_alias(self):
        var_type = self.option_selection.get().split(': ')[0]
        return self.callbacks['get_var_alias'](var_type, self.input_vars['var'].get())

    def get_input(self):
        if self.active_widget == 'var':
            return f'{self.option_selection.get()}{self.input_vars["var"].get()}'
        elif self.active_widget == 'decimal':
            return f'decimal: {self.input_vars["decimal"][0].get()}+{self.input_vars["decimal"][1].get()}/256'
        else:
            return float(self.input_widgets['float'].get_value())


# -------------------------- #
# Widgets for int parameters #
# -------------------------- #

# base int widget
class IntEditWidget(tk.Frame):

    def __init__(self, parent, name, signed=True, b_min=-math.inf, b_max=math.inf, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        label = ttk.Label(self, text=f'{name}: ')
        label.grid(row=0, column=0, sticky=tk.W)

        self.entry_field = w.RequiredIntEntry(self, width=15, signed=signed, b_min=b_min, b_max=b_max)
        self.entry_field.grid(row=0, column=1, sticky=tk.W)

        self.remove_value()

    def remove_value(self):
        self.set_value(None)

    def set_value(self, value):
        self.entry_field.delete(0, tk.END)
        if value is None:
            value = 'None'
        self.entry_field.insert(0, value)

    def get_value(self):
        if self.entry_field.get() == 'None':
            return None
        return self.entry_field.get()


class VarSelectionWidget(IntEditWidget):
    def __init__(self, parent, callback, var_type, *args, **kwargs):
        self.var_type = None
        super().__init__(parent, *args, **kwargs)

        self.var_alias_label = ttk.Label(self, text='')
        self.var_alias_label.grid(row=0, column=2)

        self.get_alias_callback = callback
        self.var_type = var_type

    def set_value(self, value):
        super().set_value(value)
        if self.var_type is None:
            return
        alias = self.get_alias_callback(self.var_type, value)
        alias_str = 'No alias'
        if alias is not None:
            alias_str = alias
        self.var_alias_label.configure(text=alias_str)

    def get_value(self):
        value = super().get_value()
        return f'{self.var_type}: {value}'


class FooterEditWidget(tk.Frame):

    def __init__(self, parent, name, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        label = ttk.Label(self, text=f'{name}: ')
        label.grid(row=0, column=0, sticky=tk.W)

        self.entry_variable = tk.StringVar(self)
        entry_field = ttk.Entry(self, textvariable=self.entry_variable, width=25)
        entry_field.grid(row=0, column=1, sticky=tk.W)

    def remove_value(self):
        self.set_value('')

    def set_value(self, value):
        self.entry_variable.set(value)

    def get_value(self):
        return self.entry_variable.get()


class ObjectSelectionWidget(tk.Frame):

    def __init__(self, parent, name, selections: Union[Dict[str, str], List[str]], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        label = ttk.Label(self, text=f'{name}: ')
        label.grid(row=0, column=0, sticky=tk.W + tk.N + tk.S)

        if isinstance(selections, list):
            self.value_dict = {_: _ for _ in selections}
        else:
            self.value_dict = selections

        self.entry_variable = tk.StringVar(self)
        option_field = ttk.OptionMenu(self, self.entry_variable, *list(self.value_dict.keys()))
        option_field.grid(row=0, column=1, sticky=tk.W)

    def remove_value(self):
        self.set_value('')

    def set_value(self, value):
        self.entry_variable.set(value)

    def get_value(self):
        return self.value_dict[self.entry_variable.get()]


# --------------------------- #
# Main Parameter Editor Popup #
# --------------------------- #

class ParamEditPopup(tk.Toplevel):
    t = 'SALSA - Parameter Editor'
    log_key = 'ParamEditPopup'
    w = 500
    h = 250

    option_settings = {}

    def __init__(self, parent, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = None

        self.title(self.t)
        self.geometry(f'{self.w}x{self.h}')
        self.configure(**theme['Ttoplevel']['configure'])

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_frame_label = w.ScrollLabelFrame(self, text='', relief=tk.FLAT, labelanchor='n', theme=theme,
                                                   canvas_style='lightCanvas')
        self.main_frame_label.grid(row=0, column=0, sticky='NSEW')
        self.main_frame = self.main_frame_label.scroll_frame

        self.row_widgets = []

        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky=tk.E)

        clear_button = ttk.Button(button_frame, text='Clear Value', command=self.on_clear)
        clear_button.grid(row=0, column=0)
        ok_button = ttk.Button(button_frame, text='Ok', command=self.on_ok)
        ok_button.grid(row=0, column=1, padx=10)
        cancel_button = ttk.Button(button_frame, text='Cancel', command=self.on_close)
        cancel_button.grid(row=0, column=2)
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def set_callbacks(self, callbacks):
        self.callbacks = callbacks

    def on_clear(self):
        self.callbacks['clear_value']()

    def on_ok(self):
        self.callbacks['save']()
        self.callbacks['close']()

    def on_close(self):
        self.callbacks['close']()

    def change_theme(self, theme):
        self.configure(**theme['Ttoplevel']['configure'])
        self.main_frame_label.change_theme(theme)
