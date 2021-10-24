import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
from .constants import FieldTypes as FT
import re

##################
# Widget Classes #
##################


class ValidatedMixin:
    """Adds a validation functionality to an input widget"""

    def __init__(self, *args, required=True, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)
        self.required = required

        self.config(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.config(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        """The validation method.

        Don't override this, override _key_validate, and _focus_validate
        """
        self._toggle_error(False)
        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )

    def _focusout_invalid(self, **kwargs):
        """Handle invalid data on a focus event"""
        self._toggle_error(True)
        pass

    def _key_invalid(self, **kwargs):
        """Handle invalid data on a key event.  By default we want to do nothing"""
        pass

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid


class RequiredEntry(ValidatedMixin, ttk.Entry):

    def _focusout_validate(self, event):
        valid = True
        if not self.get() and self.required:
            valid = False
            self.error.set('A value is required')
        return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):

    def _key_validate(self, proposed, action, **kwargs):
        valid = True
        # if the user tries to delete,
        # just clear the field
        if action == '0':
            self.set('')
            return True

        # get our values list
        values = self.cget('values')
        # Do a case-insensitve match against the entered text
        matching = [
            x for x in values
            if x.lower().startswith(proposed.lower())
        ]
        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False
        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get() and self.required:
            valid = False
            self.error.set('A value is required')
        return valid


class ValidatedSpinbox(ValidatedMixin, tk.Spinbox):

    def __init__(self, *args, min_var=None, max_var=None,
                 focus_update_var=None, from_='-Infinity', to='Infinity',
                 **kwargs):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        self.resolution = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = self.resolution.normalize().as_tuple().exponent
        # there should always be a variable,
        # or some of our code will fail
        self.variable = kwargs.get('textvariable') or tk.DoubleVar()

        if min_var:
            self.min_var = min_var
            self.min_var.trace('w', self._set_minimum)
        if max_var:
            self.max_var = max_var
            self.max_var.trace('w', self._set_maximum)
        self.focus_update_var = focus_update_var
        self.bind('<FocusOut>', self._set_focus_update_var)

    def _set_focus_update_var(self, event):
        value = self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self, *args):
        current = self.get()
        try:
            new_min = self.min_var.get()
            self.config(from_=new_min)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

    def _set_maximum(self, *args):
        current = self.get()
        try:
            new_max = self.max_var.get()
            self.config(to=new_max)
        except (tk.TclError, ValueError):
            pass
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)
        self.trigger_focusout_validation()

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        valid = True
        min_val = self.cget('from')
        max_val = self.cget('to')
        no_negative = min_val >= 0
        no_decimal = self.precision >= 0
        if action == '0':
            return True

        # First, filter out obviously invalid keystrokes
        if any([
            (char not in '1234567890'),
            (char == '-' and (no_negative or index != '0')),
            (char == '.' and (no_decimal or '.' in current))
        ]):
            return False

        # At this point, proposed is either '-', '.', '-.',
        # or a valid Decimal string
        # if proposed in '-.':
        #     return True

        # Proposed is a valid Decimal string
        # convert to Decimal and check more:
        proposed = Decimal(proposed)
        proposed_precision = proposed.as_tuple().exponent

        if any([
            (proposed > max_val),
            (proposed_precision < self.precision)
        ]):
            return False

        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.required:
            return True
        value = self.get()
        min_val = self.cget('from')
        max_val = self.cget('to')

        try:
            value = Decimal(value)
        except InvalidOperation:
            self.error.set('Invalid number string: {}'.format(value))
            return False

        if value < min_val:
            self.error.set('Value is too low (min {})'.format(min_val))
            valid = False
        if value > max_val:
            self.error.set('Value is too high (max {})'.format(max_val))

        return valid


class HexEntry (ValidatedMixin, tk.Entry):

    def __init__(self, *args, pattern="^0x[0-9,a-f]+$", **kwargs):
        super().__init__(*args, **kwargs)

        self.pattern = pattern

        self.pattern_length = 0
        self.pattern_prefix = ''
        inPrefix = True
        for i in range(len(self.pattern)):
            if inPrefix:
                nextLetter = self.pattern[i]
                if nextLetter == '[':
                    inPrefix = False
                elif nextLetter == '^':
                    continue
                else:
                    self.pattern_prefix += nextLetter
            else:
                nextLetter = self.pattern[i]
                if nextLetter == '{':
                    self.pattern_length = int(self.pattern[i+1])
                    self.pattern_length += len(self.pattern_prefix)

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        valid = True
        if action == '0':
            return True

        for i in range(len(self.pattern_prefix)):
            if int(index) == i:
                if current[:i] == self.pattern_prefix[:i]:
                    return char == self.pattern_prefix[i]
        else:
            if int(index) < len(self.pattern_prefix):
                return False

        # After prefix, filter out obviously invalid keystrokes
        if '0x' in current:
            if any([
                (char not in ('1234567890abcdef'))
            ]):
                return False
            if len(proposed) > 10:
                return False

        # Check total length
        if 0 < self.pattern_length:
            if len(proposed) > self.pattern_length:
                return False

        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.required and self.get() == '':
            return True

        if not re.search(self.pattern, self.get()):
            valid = False

        return valid


class NoEntry(ValidatedMixin, tk.Entry):

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        return False

    def set(self, text):
        self.delete(0, "end")
        self.insert(0, text)


class NoText(ValidatedMixin, tk.Text):

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        return False

    def set(self, value):
        self.delete('1.0', tk.END)
        if len(value) > 1:
            value = value[:-1]
        self.insert('1.0', value)

class LabelInput(tk.Frame):
    """A widget containing a label and input together."""

    field_types = {
        FT.string: (RequiredEntry, tk.StringVar),
        FT.string_list: (ValidatedCombobox, tk.StringVar),
        FT.long_string: (tk.Text, lambda: None),
        FT.decimal: (ValidatedSpinbox, tk.DoubleVar),
        FT.integer: (ValidatedSpinbox, tk.IntVar),
        FT.boolean: (ttk.Checkbutton, tk.BooleanVar),
        FT.hex: (HexEntry, tk.StringVar),
    }

    def __init__(self, parent, label='', input_class=None,
                 input_var=None, input_args=None, label_args=None,
                 field_spec=None, **kwargs):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        if field_spec:
            required = field_spec.get('req', False)
            field_type = field_spec.get('type', FT.string)
            input_class = input_class or self.field_types.get(field_type)[0]
            var_type = self.field_types.get(field_type)[1]
            self.variable = input_var if input_var else var_type()
            # min, max, increment
            if 'min' in field_spec and 'from_' not in input_args:
                input_args['from_'] = field_spec.get('min')
            if 'max' in field_spec and 'to' not in input_args:
                input_args['to'] = field_spec.get('max')
            if 'inc' in field_spec and 'increment' not in input_args:
                input_args['increment'] = field_spec.get('inc')
            # values
            if 'values' in field_spec and 'values' not in input_args:
                input_args['values'] = field_spec.get('values')
            if 'pattern' in field_spec and 'pattern' not in input_args:
                input_args['pattern'] = field_spec['pattern']
        else:
            self.variable = input_var

        if input_class in (ttk.Button, ttk.Radiobutton):
            input_args["text"] = label
            input_args["variable"] = self.variable
        elif input_class is ttk.Checkbutton:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["variable"] = self.variable
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args["textvariable"] = self.variable

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input) == tk.Text:
                return self.input.get('1.0', tk.END)
            else:
                return self.input.get()
        except (TypeError, tk.TclError):
            # happens when numeric fields are empty.
            return ''

    def set(self, value, *args, **kwargs):
        if type(self.variable) == tk.BooleanVar:
                self.variable.set(bool(value))
        elif self.variable:
                self.variable.set(value, *args, **kwargs)
        elif type(self.input) in (ttk.Checkbutton, ttk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete('1.0', tk.END)
            if len(value) > 1:
                if value[:-1] == '\n':
                    value = value[:-1]
            self.input.insert('1.0', value)
        else:
            self.input.delete(0, tk.END)
            self.input.insert(0, value)

    def set_trace(self, callback, type='w'):
        self.variable.trace(type, callback)

    def config(self, args):
        if 'state' in args:
            self.input.config(state=args['state'])
