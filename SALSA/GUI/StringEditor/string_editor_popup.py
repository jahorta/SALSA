import tkinter as tk
from tkinter import ttk
from typing import Literal

from SALSA.GUI.Widgets.hover_tooltip import schedule_tooltip
from SALSA.GUI.Widgets.toggle_button import ToggleButton
from SALSA.GUI.Widgets.data_treeview import DataTreeview
from SALSA.GUI.themes import dark_theme, light_theme

tree_settings = {
    'script': {
        'name': {'label': 'Name', 'width': 80, 'stretch': False}
    },
    'string': {
        'location': {'label': 'Name', 'width': 110, 'stretch': False},
        'string': {'label': 'Name', 'width': 100, 'stretch': True}
    }
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''

note_font = {}

tooltips = {
    'no_head': 'Removing the header will allow for 5 lines of body text instead of 4 and delete the current header.',
    'body': 'NOTE: [ and ] are used for open and close quotes respectively. Using " or \' will only give the close quote.'
}

tooltip_delay = 500

quote_types = {
    'US/JP': ('《', '》'),
    'EU': ('«', '»')
}

quote_replacement = {
    'US/JP': [[quote_types['EU'][i], quote_types['US/JP'][i]] for i in range(len(quote_types['US/JP']))],
    'EU': [[quote_types['US/JP'][i], quote_types['EU'][i]] for i in range(len(quote_types['EU']))]
}

sp_chars = {
    'EU': '€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ¡¢£¤¥¦§¨©ª«¬SHY®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ',
    'US/JP': '、。，．・：；？！゛゜´｀¨＾￣＿ヽヾゝゞ〃仝々〆〇ー―‐／＼～∥｜…‥‘’“”（）〔〕［］｛｝〈〉《》「」『』【】＋－±×÷＝≠＜＞≦≧∞∴♂♀°′″℃￥＄￠￡％＃＆＊＠§☆★○●◎◇◆□■△▲▽▼※〒→←↑↓〓∈∋⊆⊇⊂⊃∪∩∧∨￢⇒⇔∀∃∠⊥⌒∂∇≡≒≪≫√∽∝∵∫∬Å‰♯♭♪†‡¶◯ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩαβγδεζηθικλμνξοπρστυφχψωАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя│┌┐┘└├┬┤┴┼━┃┏┓┛┗┣┳┫┻╋┠┯┨┷┿┝┰┥┸╂①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹ㍉㌔㌢㍍㌘㌧㌃㌶㍑㍗㌍㌦㌣㌫㍊㌻㎜㎝㎞㎎㎏㏄㎡㍻〝〟№㏍℡㊤㊥㊦㊧㊨㈱㈲㈹㍾㍽㍼∮∑∟⊿￤＇＂'
}


class StringPopup(tk.Toplevel):
    t = 'SALSA - String Editor'
    log_key = 'StrEditPopup'
    w = 600
    h = 500

    option_settings = {}

    def __init__(self, parent, callbacks, name, is_darkmode, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = callbacks
        self.name = name
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.theme = dark_theme if is_darkmode else light_theme
        self.configure(**self.theme['Ttoplevel']['configure'])

        # if self.log_key not in settings:
        #     settings.add_group(self.log_key)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        upper_frame = ttk.Frame(self)
        upper_frame.grid(row=1, column=0, sticky='NSEW')
        upper_frame.columnconfigure(1, weight=1)
        upper_frame.rowconfigure(0, weight=1)

        script_tree_frame = ttk.LabelFrame(upper_frame, text='Scripts')
        script_tree_frame.grid(row=0, column=0, sticky='NSEW', padx=5)
        script_tree_frame.rowconfigure(0, weight=1)

        columns = list(tree_settings['script'].keys())[1:]
        self.scripts = DataTreeview(script_tree_frame, name='script', columns=columns)
        self.scripts.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in tree_settings['script'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.scripts.heading(name, text=label, anchor=anchor)
            self.scripts.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        script_tree_scrollbar = ttk.Scrollbar(script_tree_frame, orient='vertical', command=self.scripts.yview)
        script_tree_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.scripts.config(yscrollcommand=script_tree_scrollbar.set)
        self.scripts.config(show='tree')
        self.scripts.add_callback('select', self.on_script_select)

        string_tree_frame = ttk.LabelFrame(upper_frame, text='Strings')
        string_tree_frame.grid(row=0, column=1, sticky='NSEW', padx=5)
        string_tree_frame.columnconfigure(0, weight=1)
        string_tree_frame.rowconfigure(0, weight=1)

        columns = list(tree_settings['string'].keys())[1:]
        self.strings = DataTreeview(string_tree_frame, name='strings', columns=columns)
        self.strings.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in tree_settings['string'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            self.strings.heading(name, text=label, anchor=anchor)
            self.strings.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)
        string_tree_scrollbar = ttk.Scrollbar(string_tree_frame, orient='vertical', command=self.strings.yview)
        string_tree_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.strings.config(yscrollcommand=string_tree_scrollbar.set)
        self.strings.config(show='tree')
        self.strings.add_callback('select', self.edit_string)

        lower_frame = ttk.Frame(self)
        lower_frame.grid(row=2, column=0, sticky='NSEW', padx=5)
        lower_frame.columnconfigure(0, weight=1)

        encode_frame = ttk.Frame(lower_frame)
        encode_frame.grid(row=0, column=0, sticky=tk.W)

        str_encode_label = ttk.Label(encode_frame, text='String Encoding:   ')
        str_encode_label.grid(row=0, column=0, pady=1)
        self.str_encode_toggle = ToggleButton(encode_frame, on_text='US/JP', off_text='EU', theme=self.theme,
                                              command=self.set_encoding, bd=0, highlightthickness=0)
        self.str_encode_toggle.grid(row=0, column=1)

        no_head_frame = ttk.Frame(lower_frame)
        no_head_frame.grid(row=1, column=0, sticky=tk.W)

        self.no_head_var = tk.IntVar()
        self.no_head = ttk.Checkbutton(no_head_frame, text=' Remove Header', variable=self.no_head_var, onvalue=1, offvalue=0,
                                       command=lambda: self.set_change('no_head', self.no_head_var.get() == 1), state='disabled')
        self.no_head.grid(row=0, column=0, sticky=tk.W)
        no_head_warning_label = ttk.Label(no_head_frame, text='⚠', anchor='w', justify=tk.LEFT)
        no_head_warning_label.grid(row=0, column=1)
        no_head_warning_label.bind('<Enter>', lambda e: schedule_tooltip(no_head_warning_label, tooltips['no_head']))

        head_frame = ttk.Frame(lower_frame)
        head_frame.grid(row=2, column=0, sticky=tk.W)

        head_label = ttk.Label(head_frame, text='Textbox Header')
        head_label.grid(row=1, column=0, sticky=tk.W)
        self.head_entry = ttk.Entry(head_frame, state='disabled', width=65)
        self.head_entry.grid(row=1, column=0, sticky=tk.W)
        self.head_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.head_entry.bind('<FocusOut>', lambda e, k='head': self.on_entry_focus_out(k, e))
        self.head_add_quote_label = ttk.Label(head_frame, text='')
        self.head_add_quote_label.grid(row=1, column=1, sticky=tk.W)
        self.head_add_quote_button = ttk.Button(head_frame, text='add header quotes', command=self.add_quotes_to_head)
        self.head_add_quote_button.grid(row=1, column=3, sticky=tk.W, padx=3)

        body_label_frame = ttk.Frame(lower_frame)
        body_label_frame.grid(row=3, column=0, sticky=tk.W)
        body_label = ttk.Label(body_label_frame, text='Textbox Body')
        body_label.grid(row=0, column=0)
        body_tooltip_label = ttk.Label(body_label_frame, text='ⓘ')
        body_tooltip_label.grid(row=0, column=1)
        body_tooltip_label.bind('<Enter>', lambda e: schedule_tooltip(body_tooltip_label, tooltips['body']))

        insert_frame = ttk.Frame(lower_frame)
        insert_frame.grid(row=4, column=0, sticky=tk.E+tk.W)

        self.body_entry = tk.Text(lower_frame, wrap=tk.WORD, height=5, **self.theme['text']['configure'],
                                  undo=True, maxundo=-1, autoseparators=True)
        self.body_entry.grid(row=5, column=0, sticky=tk.W + tk.E, pady='0 5')
        self.body_entry.bind('<FocusIn>', self.on_text_focus_in)
        self.body_entry.bind('<FocusOut>', lambda e, k='body': self.on_text_focus_out(k, e))

        self.update_scripts()

        self.cur_script = ''
        self.cur_string_id = ''
        self.string_defaults = {}
        self.string_changes = {}
        self.header_invalid = False
        self.cur_encoding: Literal['US/JP', 'EU'] = 'US/JP'
        self.cur_script_encoding: Literal['US/JP', 'EU'] = 'US/JP'
        self.scheduled_tooltip = None
        self.active_tooltip = None

        self.title(self.t)

        posX = self.parent.winfo_x() + (self.parent.winfo_width() - self.w)//2
        posY = self.parent.winfo_y() + (self.parent.winfo_height() - self.h)//2
        pos = f'{self.w}x{self.h}+{posX}+{posY}'
        self.geometry(pos)

    def update_scripts(self):
        self._clear_editor_fields()
        self._change_editor_state('disabled')
        self.strings.clear_all_entries()
        script_tree = self.callbacks['get_scripts']()
        for entry in script_tree:
            self.scripts.insert_entry(parent='', index='end', text=entry['name'], values=[], row_data=entry['row_data'])

    def _change_editor_state(self, state):
        self.no_head.configure(state=state)
        self.head_entry.configure(state=state)
        self.head_add_quote_button.configure(state=state)
        self.body_entry.configure(state=state)

    def _clear_editor_fields(self):
        self.no_head_var.set(0)
        self.head_entry.delete(0, tk.END)
        self.body_entry.delete(1.0, tk.END)

    def on_script_select(self, name, script):
        self.cur_script = script
        self.cur_string_id = ''
        self._clear_editor_fields()
        self._change_editor_state('disabled')
        self._update_string_tree(script)

    def _update_string_tree(self, script):
        self.strings.clear_all_entries()
        headers = list(tree_settings['string'].keys())
        string_tree = self.callbacks['get_string_tree'](script, headers)
        parent_list = ['']
        prev_iid = -1
        encoding_set = False
        for entry in string_tree:
            if isinstance(entry, str):
                if entry == 'group':
                    parent_list.append(prev_iid)
                elif entry == 'ungroup':
                    if len(parent_list) == 1:
                        raise RuntimeError(f'{self.log_key}: unable to lower group level, not enough groups left')
                    parent_list.pop()
                else:
                    raise ValueError(f'{self.log_key}: Unknown command in tree list sent to _add_tree_entries')
                continue
            if not encoding_set:
                if 'string' in entry:
                    if '《' in entry['string']:
                        self.cur_script_encoding = 'US/JP'
                        encoding_set = True
                        self.str_encode_toggle.set_state_by_value(self.cur_script_encoding)
                    if '«' in entry['string']:
                        self.cur_script_encoding = 'EU'
                        encoding_set = True
                        self.str_encode_toggle.set_state_by_value(self.cur_script_encoding)
            kwargs = {'parent': parent_list[-1], 'index': 'end'}
            values = []
            first = True
            for col in headers:
                if col == 'name':
                    if 'group_type' in entry.keys():
                        entry[col] += f' ({entry["group_type"]})'
                if first:
                    kwargs['text'] = entry[col]
                    first = False
                else:
                    values.append(entry[col])
                entry.pop(col)
            kwargs['values'] = values
            kwargs = {**kwargs, **entry}
            prev_iid = self.strings.insert_entry(**kwargs)

    def edit_string(self, name, string_id):
        if len(self.string_changes) > 0:
            self.save()

        self._change_editor_state('normal')
        self._clear_editor_fields()

        self.cur_string_id = string_id
        no_head, head, body = self.callbacks['get_string_to_edit'](string_id, self.cur_script)
        self.header_invalid = False
        self.body_entry.insert(tk.INSERT, body)
        if head is None:
            self.head_entry.insert(0, 'This instruction does not support headers')
            self._change_editor_state('disabled')
            self.body_entry.configure(state='normal')
            self.header_invalid = True
            return

        no_head = 1 if no_head else 0
        self.no_head_var.set(no_head)
        self.head_entry.insert(0, head)
        if '《' in head:
            self.cur_encoding = 'US/JP'
        elif '«' in head:
            self.cur_encoding = 'EU'
        else:
            self.cur_encoding = self.cur_script_encoding

        self.str_encode_toggle.set_state_by_value(self.cur_encoding)

    def add_quotes_to_head(self):
        left, right = quote_types[self.cur_encoding]
        self.head_entry.insert(0, left)
        self.head_entry.insert(tk.END, right)
        self.set_change('head', self.head_entry.get())

    def set_encoding(self, new_encoding: Literal['US/JP', 'EU']):
        self.cur_encoding = new_encoding
        head = self.head_entry.get()
        for quote_set in quote_replacement[self.cur_encoding]:
            head = head.replace(quote_set[0], quote_set[1])

        self.head_entry.delete(0, tk.END)
        self.head_entry.insert(0, head)
        self.set_change('head', self.head_entry.get())

    @staticmethod
    def on_entry_focus_in(e):
        e.widget.cur_value = e.widget.get()

    def on_entry_focus_out(self, key, e):
        if e.widget.get() == e.widget.cur_value:
            print('same value')
            return
        self.set_change(key=key, value=e.widget.get())

    @staticmethod
    def on_text_focus_in(e):
        e.widget.cur_value = e.widget.get(1.0, tk.END)

    def on_text_focus_out(self, key, e):
        new_value: str = e.widget.get(1.0, tk.END).rstrip(' \n\t')
        if new_value == e.widget.cur_value:
            print('same text')
            return
        self.set_change(key=key, value=new_value)

    def set_change(self, key, value):
        if self.cur_script not in self.string_changes:
            self.string_changes[self.cur_script] = {self.cur_string_id: {key: value}}
        elif self.cur_string_id not in self.string_changes[self.cur_script]:
            self.string_changes[self.cur_script][self.cur_string_id] = {key: value}
        elif key not in self.string_changes[self.cur_script][self.cur_string_id]:
            self.string_changes[self.cur_script][self.cur_string_id][key] = value
        elif self.string_changes[self.cur_script][self.cur_string_id][key] != value:
            self.string_changes[self.cur_script][self.cur_string_id][key] = value
        else:
            return

    def save(self):
        for script, strings in self.string_changes.items():
            for string_id, string_changes in strings.items():
                self.callbacks['save'](script, string_id, string_changes)
        self.string_changes = {}

    def close(self):
        self.focus()
        self.after(10, self.save_and_close)

    def save_and_close(self):
        self.save()
        self.callbacks['close'](self.name, self)

    def change_theme(self, dark_mode=True):
        self.theme = dark_theme if dark_mode else light_theme

        self.body_entry.configure(**self.theme['text']['configure'])
        self.configure(**self.theme['Ttoplevel']['configure'])
        self.str_encode_toggle.change_theme(self.theme)

