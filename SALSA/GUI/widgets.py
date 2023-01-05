import platform
import re
import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import ttk
from typing import Dict, List, Union

from SALSA.Common.constants import FieldTypes as FT

# ------ #
# Mixins #
# ------ #
from Common.containers import Dimension, Vector2


class ValidatedMixin:
    """Adds a validation functionality to an input widget"""

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

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


class RequiredEntryMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _focusout_validate(self, event):
        valid = True
        if self.get() == '':
            valid = False
            self.error.set('A value is required')
        return valid


# -------------- #
# Widget Classes #
# -------------- #


class RequiredEntry(ValidatedMixin, RequiredEntryMixin, tk.Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HexEntry(ValidatedMixin, tk.Entry):
    def __init__(self, *args, hex_max_length: int, hex_min_length: int, **kwargs):
        super().__init__(*args, **kwargs)

        self.pattern_internal = "[0-9,a-f]"
        self.prefix = "^"
        self.min_len = hex_min_length
        min_str = '0' * self.min_len
        self.set(min_str)
        self.max_len = hex_max_length
        self.suffix = '{' + str(self.min_len) + ',' + str(self.max_len) + '}$'
        self._set_pattern()

    def _set_pattern(self):
        self.pattern = self.prefix + self.pattern_internal + self.suffix

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        valid = True

        if not re.search(proposed, self.get()):
            valid = False
            error = ''
            if not self.min_len < len(proposed) < self.max_len:
                error = f'length of field should be between {self.min_len} and {self.max_len}'
            valid_chars = ['abcdefABCDEF1234567890']
            if char not in valid_chars:
                error = f'Invalid character: {char}, use one of these for hexadecimal: {"".join(valid_chars)}'
            self.error.set(error)

        return valid


class RequiredHexEntry(RequiredEntryMixin, HexEntry):

    def __init__(self, hex_max_length: int, *args, hex_min_length: int = 0, **kwargs):
        super().__init__(*args, hex_max_length=hex_max_length, hex_min_length=hex_min_length, **kwargs)

    def _focusout_validate(self, **kwargs):
        valid = super()

        if not re.search(self.pattern, self.get()):
            valid = False

        return valid


class RequiredAddrEntry(RequiredHexEntry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, hex_min_length=3, **kwargs)

        self.pattern_length = 8
        self.prefix = '^0x8'
        self.suffix = '{7}$'

        self.set('0x8')

    def _focusout_validate(self, **kwargs):
        valid = super()

        if not len(self.get()) == self.pattern_length:
            valid = False
            error = f'Final address should be the full '
            self.error.set(f'')
        return valid


class RequiredByteEntry(RequiredHexEntry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, hex_max_length=2, **kwargs)


class RequiredShortEntry(RequiredHexEntry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, hex_max_length=4, **kwargs)


class RequiredIntEntry(RequiredHexEntry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, hex_max_length=8, **kwargs)


# ------------- #
# Frame Classes #
# ------------- #

class ScrollCanvas(tk.Frame):

    def __init__(self, parent, size: dict, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.canvas = tk.Canvas(self, width=size['width'], height=size['height'])
        self.canvas.grid(row=0, column=0, sticky='NSEW')
        self.canvas_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvas_scrollbar.set)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas.bind('<Enter>', self.onEnter)  # bind wheel events when the cursor enters the control
        self.canvas.bind('<Leave>', self.onLeave)  # unbind wheel events when the cursor leaves the control

    # whenever the size of the frame changes, alter the scroll region respectively.
    def onCanvasContentChange(self, event):
        """Reset the scroll region to encompass the canvas contents"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # cross platform scroll wheel event
    def onMouseWheel(self, event):
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    # bind wheel events when the cursor enters the control
    def onEnter(self, event):
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    # unbind wheel events when the cursorl leaves the control
    def onLeave(self, event):
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")

    def resize(self):
        width = self.parent.winfo_width()
        height = self.parent.winfo_height()
        self.canvas.configure(width=width - self.canvas_scrollbar.winfo_width(), height=height)


class ScrollTextCanvas(ScrollCanvas):

    def __init__(self, parent, size: dict, text_offset: dict, text: str):
        super().__init__(parent, size)

        self.canvas.create_text((text_offset['x'], text_offset['y']),
                                anchor=tk.NW, text=text,
                                width=size['width'] - text_offset['x'])


class ScrollFrame(ScrollCanvas):

    def __init__(self, parent, size=None, *args, **kwargs):
        size = {'width': 100, 'height': 100} if size is None else size
        super().__init__(parent, size, *args, **kwargs)

        self.viewport = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(0, 0, window=self.viewport, anchor=tk.N + tk.W,
                                                       tags='self.viewport')

        # bind an event whenever the size of the viewPort frame changes.
        self.viewport.bind("<Configure>", self.onCanvasContentChange)

        # bind an event whenever the size of the canvas frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)

        self.onCanvasContentChange(None)

    # whenever the size of the canvas changes alter the window region respectively.
    def onCanvasConfigure(self, event):
        """Reset the canvas window to encompass inner frame when required"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)


# ----- #
# Trees #
# ----- #

class TreeEntry:
    x_pad = 5
    box_x_sel_offset = 5

    def __init__(self, parent_canvas: tk.Canvas, text=None, row=0, offset_selected=False,
                 highlight_selected=True, highlight_color='#8888FF', box_height=20, indent_level=0, indent_width=10,
                 indent_field=0, text_start=0):
        self.canvas: tk.Canvas = parent_canvas
        self.txt_ids: List[int] = []
        self.row = row
        self.box_height = box_height
        self.indent_level = indent_level
        self.indent_field = indent_field
        self.indent_width = indent_width
        self.text = [''] if text is None else text
        self.offset_selected = offset_selected
        self.highlight = None
        self.highlight_color = highlight_color
        self.highlight_selected = highlight_selected
        self.text_start = text_start

        y = self.box_height * self.row + self.box_height // 2
        for i, t in enumerate(self.text):
            x = self.text_start
            x += 0 if i == 0 else self.canvas.bbox(self.txt_ids[i - 1])
            x += self.indent_width * self.indent_level if i == self.indent_field else 0
            x += self.x_pad
            self.txt_ids.append(self.canvas.create_text(x, y, text=t, anchor='w'))

    def update_txt_starts(self, x_list: List[int]):
        for j, i in enumerate(self.txt_ids):
            m_x = x_list[j] - self.canvas.bbox(i)[0]
            self.canvas.move(i, m_x, 0)

    def select(self):
        for i in self.txt_ids:
            x = self.box_x_sel_offset if self.offset_selected else 0
            self.canvas.move(i, x, 0)
            self.canvas.tag_raise(i)
        if self.highlight_selected:
            self.add_highlight()

    def add_highlight(self):
        if self.highlight is None:
            x1 = self.canvas.bbox('all')[2]
            y0 = self.row * self.box_height
            y1 = y0 + self.box_height
            self.highlight = self.canvas.create_rectangle(0, y0, x1, y1, fill=self.highlight_color)
            self.canvas.tag_lower(self.highlight, self.txt_ids[0])

    def deselect(self):
        for i in self.txt_ids:
            x = self.box_x_sel_offset if self.offset_selected else 0
            self.canvas.move(i, x, 0)
        if self.highlight is not None:
            self.remove_highlight()

    def remove_highlight(self):
        if self.highlight is not None:
            self.canvas.delete(self.highlight)
            self.highlight = None

    def _move_y(self, m_ys):
        """Moves the entry in the y direction

        :param m_ys: A list containing scheduled y movements"""
        m_y = m_ys.pop(0)
        for i in self.txt_ids:
            self.canvas.move(i, 0, m_y)
        if len(m_ys) > 0:
            self.canvas.after(10, self._move_y, m_ys)

    def move_rows(self, row_change, increments=1):
        # Linear by interpolation
        tgt_m_y = row_change * self.box_height
        step = tgt_m_y // increments
        m_ys = list(range(0, tgt_m_y, step))
        if m_ys[-1] != tgt_m_y:
            m_ys.append(tgt_m_y)
        self._move_y(m_ys)
        self.row += row_change

    def set_row(self, row):
        target_y = row * self.box_height
        for i in self.txt_ids:
            m_y = target_y - self.canvas.bbox(i)[1]
            self.canvas.move(i, 0, m_y)
        self.row = row

    def set_indent(self, indent_level):
        ind_id = self.txt_ids[self.indent_field]
        m_x = (self.indent_level - indent_level) * self.indent_width
        self.canvas.move(ind_id, m_x, 0)

    def get_layer(self):
        return self.txt_ids[0]

    def lower(self, below_id):
        for _id in self.txt_ids:
            self.canvas.tag_lower(below_id)


class CustomTree(ScrollCanvas):
    """A Canvas with a grid of elements. If an element is selected, will generate a '<<Select>>' event"""

    row_height = 20

    def __init__(self, parent,  headers: List[str], *args, name='', header_widths=None, size=None, color='#FFFFFF', highlight='#AAAAFF',
                 pcnt_height=98, pcnt_width=100, dragable=False, **kwargs):
        size = {'width': 100, 'height': 100} if size is None else size
        super().__init__(parent, size, *args, **kwargs)
        self.parent: tk.Frame = parent
        self.name = name
        self.header_canvas = tk.Canvas(self, width=size['width'], height=self.row_height)
        self.header_canvas.grid(row=0, column=0)
        self.header_list = headers
        self.header_widths = header_widths
        if header_widths is None or len(header_widths) != len(self.header_list):
            self.header_widths = [50]*len(self.header_list)
        x = 0
        for i, header in enumerate(self.header_list):
            self.header_canvas.create_text(x+(self.header_widths[i]//2), 0, text=header, anchor='n')
            x += self.header_widths[i]

        self.color = color
        self.highlight = highlight
        self.pcnt_width = pcnt_width / 100
        self.pcnt_height = pcnt_height / 100

        self.canvas.bind('<Double-Button-1', self.on_double_click)
        self.canvas.bind('<Button-1>', self.on_left_click)
        self.canvas.bind('<KeyPress>', lambda event: self.keys_down.append(event.keycode))
        self.canvas.bind('<KeyRelease>', self.key_release)

        self.keys_down = []
        self.canvas.grid_configure(row=1, column=0)
        self.canvas_scrollbar.grid_configure(row=0, column=1, rowspan=2)

        self.groups: Dict[str, List[int]] = {}
        self.cur_indent = 0
        self.rows: List[TreeEntry] = []
        self.row_ids: Dict[TreeEntry, Union[int, str]] = {}

        self.cur_grid_row = None
        self.motion_widgets_height = None
        self.motion_lists: Dict[str, List[TreeEntry]] = {'top': [], 'sel': [], 'bot': []}

        self.dragable = dragable
        self.dragging = False

        self.in_window = False
        self.callbacks = {}

    def key_release(self, e):
        if e.keycode in self.keys_down:
            self.keys_down.pop(self.keys_down.index(e.keycode))

    def resize(self):
        width = self.parent.winfo_width()
        height = self.parent.winfo_height()
        self.header_canvas.configure(width=width * self.pcnt_width - self.canvas_scrollbar.winfo_width())
        self.canvas.configure(width=width * self.pcnt_width - self.canvas_scrollbar.winfo_width(),
                              height=height * self.pcnt_height - self.header_canvas.winfo_height())

    # --------------------------------- #
    # List Entry Manipulation functions #
    # --------------------------------- #

    def get_row(self, y):
        scroll_y = self.canvas_scrollbar.get()[0]
        x, y0, x, y1 = self.canvas.bbox('all')
        top_y = y1 - y0 * scroll_y
        return (top_y + y) // self.row_height

    def start_group(self, group_name, row=-1, row_data=None, **kwargs):
        self.cur_indent += 1
        text = [group_name].extend(['']*(len(self.header_list)-1))
        self.add_row(text=text, row=row, row_data=row_data)

    def end_group(self):
        self.cur_indent -= 1

    def add_row(self, text, row=-1, row_data=None, **kwargs):
        if len(text) > len(self.header_list):
            err = f'CustomTree: More text values than header fields:\n\tRow text: ' + ', '.join(text)
            err += f'\n\n\tHeaders: '
            raise ValueError(err)
        kwargs['row'] = len(self.rows) if row == -1 else row
        kwargs['text_start'] = 0  # Change this when grouping is implemented
        new_row = TreeEntry(self.canvas, text=text, indent_level=self.cur_indent, **kwargs)
        row = row if row > 0 else len(self.rows)
        if row > 0:
            new_row.lower(self.rows[row-1].get_layer())
        self.rows.insert(row, new_row)
        if row_data is not None:
            self.row_ids[new_row] = row_data

    def clear_all_entries(self):
        self.canvas.delete('all')
        self.rows = []
        self.row_ids = {}
        self.cur_grid_row = None
        self.motion_widgets_height = None
        self.motion_lists: Dict[str, List[TreeEntry]] = {'top': [], 'sel': [], 'bot': []}

    # ------------------------- #
    # Entry selection functions #
    # ------------------------- #

    def get_entry_row(self, event):
        scroll_top_y = self.canvas_scrollbar.get()[0] * self.canvas.bbox('all')[3]
        return int((scroll_top_y + event.y) // self.row_height)

    def on_double_click(self, e):
        cur_row = self.get_entry_row(e)
        if cur_row >= len(self.row_ids):
            return
        self.callbacks['select'](cur_row)

    # ------------------------ #
    # Entry dragging functions #
    # ------------------------ #

    def on_left_click(self, e):
        cur_row = self.get_entry_row(e)

        if (50 in self.keys_down or 60 in self.keys_down) and len(self.motion_lists['sel']) > 0:
            pass
        elif len(self.motion_lists['sel']) == 0:
            self.motion_lists['sel'] = [self.rows[cur_row]]

    def drag(self, e):
        if len(self.motion_lists) == 0 or not self.dragable:
            return
        if not (self.winfo_x() < e.x < self.winfo_width() and
                self.winfo_y() < e.y < self.winfo_y() + ((len(self.rows) - 1) * self.row_height)):
            return
        self.dragging = True
        grid_row = e.y // self.row_height
        if self.cur_grid_row is None:
            self.cur_grid_row = grid_row
            self.motion_lists['top'] = [_ for _ in self.rows if (_ not in self.motion_lists['sel']
                                                                 and self.rows.index(_) < grid_row)]
            self.motion_lists['bot'] = [_ for _ in self.rows if (_ not in self.motion_lists['sel']
                                                                 and _ not in self.motion_lists['top'])]
            self.motion_widgets_height = len(self.motion_lists['sel']) * self.row_height

            first_bot_row = grid_row + len(self.motion_lists['sel'])
            for i, widget in enumerate(self.motion_lists['bot']):
                widget.set_row(first_bot_row + i)

            for i, widget in enumerate(self.motion_lists['sel']):
                widget.set_row(grid_row + i)
                widget.select()

        elif self.cur_grid_row == grid_row:
            return

        else:
            print(f'rect moved: {self.cur_grid_row} -> {grid_row}')
            row_change = grid_row - self.cur_grid_row
            if row_change > 0:
                changed_ids = self.motion_lists['bot'][:row_change]
                self.motion_lists['bot'] = self.motion_lists['bot'][row_change:]
                self.motion_lists['top'] = [*self.motion_lists['top'], *changed_ids]
            else:
                row_ch_id_0 = len(self.motion_lists['top']) + row_change
                changed_ids = self.motion_lists['top'][row_ch_id_0:]
                self.motion_lists['top'] = self.motion_lists['top'][:row_ch_id_0]
                self.motion_lists['bot'] = [*changed_ids, *self.motion_lists['bot']]

            for i, widget in enumerate([*self.motion_lists['top'], *self.motion_lists['sel'],
                                        *self.motion_lists['bot']]):
                widget.set_row(i)
            self.cur_grid_row = grid_row

    def release(self, e):
        if not self.dragging:
            return

        self.dragging = False

        # remove selection offset
        for widget in self.motion_lists['sel']:
            widget.deselect()

        self.rows = [*self.motion_lists['top'], *self.motion_lists['sel'], *self.motion_lists['bot']]

        for i, widget in enumerate(self.rows):
            widget.set_row(i)

        self.cur_grid_row = None
        self.motion_widgets_height = None
        self.motion_lists = {'top': [], 'sel': [], 'bot': []}

    def enable(self):
        pass

    def disable(self):
        pass

    def get_headers(self):
        return self.header_list


class CustomTree2(ttk.Treeview):

    def __init__(self, parent, name, callbacks=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.parent = parent
        self.name = name
        self.callbacks = callbacks if callbacks is not None else {}
        self.row_data = {}
        self.group_types = {}

        self.bind("<Double-ButtonPress-1>", self.open_entry)
        self.bind("<ButtonPress-1>", self.bDown)
        self.bind("<ButtonRelease-1>", self.bUp, add='+')
        self.bind("<B1-Motion>", self.bMove, add='+')
        self.bind("<Shift-ButtonPress-1>", self.bDown_Shift, add='+')
        self.bind("<Shift-ButtonRelease-1>", self.bUp_Shift, add='+')

    def add_callback(self, key, callback):
        self.callbacks[key] = callback

    def open_entry(self, event):
        widget = self.identify_row(event.y)
        row_data = self.row_data[widget]
        if row_data is not None:
            self.callbacks['select'](self.name, row_data)

    def bDown_Shift(self, event):
        select = [self.index(s) for s in self.selection()]
        select.append(self.index(self.identify_row(event.y)))
        select.sort()
        for i in range(select[0], select[-1] + 1, 1):
            self.selection_add(self.get_children()[i])

    def bDown(self, event):
        if self.identify_row(event.y) not in self.selection():
            self.selection_set(self.identify_row(event.y))

    def bUp(self, event):
        if self.identify_row(event.y) in self.selection():
            self.selection_set(self.identify_row(event.y))

    def bUp_Shift(self, event):
        pass

    def bMove(self, event):
        iid = self.identify_row(event.y)
        moveto = self.index(iid)
        parent_iid = self.parent(iid)
        for s in self.selection():
            self.move(s, parent_iid, moveto)

    def insert_entry(self, parent, text, values, group_type=None, row_data=None, **kwargs):
        iid = str(len(self.row_data))
        self.row_data[iid] = row_data
        self.group_types[iid] = group_type
        super().insert(parent=parent, iid=iid, text=text, values=values, **kwargs)
        return iid

    def clear_all_entries(self):
        for row in self.get_children():
            self.delete(row)
