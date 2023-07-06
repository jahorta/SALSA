import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Union

from SALSA.GUI.themes import dark_theme, light_theme
from SALSA.Common.constants import sep

drag_tree_info = {
    'headers': {
        'id': {'label': 'ID', 'width': 50, 'stretch': False},
        'name': {'label': 'Name', 'width': 50, 'stretch': False}
    },
    'final_item': {'parent': '', 'index': tk.END, 'text': '...', 'values': ['']}
}

default_tree_width = 100
default_tree_minwidth = 10
default_tree_anchor = tk.W
default_tree_stretch = False
default_tree_label = ''


class DragWindow(tk.Toplevel):

    def __init__(self, master, tree_dict, is_darkmode, bbox, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.attributes('-alpha', 0.5)
        self.overrideredirect(True)

        theme = dark_theme if is_darkmode else light_theme
        self.configure(**theme['drag.Ttoplevel']['configure'], bd=0)

        tree = ttk.Treeview(self, columns=list(tree_dict['headers'].keys())[1:], style='drag.Treeview', show='tree')
        tree.grid(row=0, column=0, sticky='NSEW')
        first = True
        for name, d in tree_dict['headers'].items():
            label = d.get('label', default_tree_label)
            anchor = d.get('anchor', default_tree_anchor)
            minwidth = d.get('minwidth', default_tree_minwidth)
            width = d.get('width', default_tree_width)
            stretch = d.get('stretch', default_tree_stretch)
            if first:
                name = '#0'
                first = False
            tree.heading(name, text=label, anchor=anchor)
            tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        for item in tree_dict['items']:
            tree.insert(**item)
        tree.insert(**drag_tree_info['final_item'])

        tree.configure(height=len(tree_dict['items'])+1)

        self.mouse_box = (bbox[0], bbox[1], bbox[0]+bbox[2], bbox[1]+ bbox[3])

    def update_pos(self, x, y):
        x += 2
        y += 2
        if self.mouse_box[0] < x < self.mouse_box[2] and self.mouse_box[1] < y < self.mouse_box[3]:
            self.geometry(f'+{x}+{y}')


placeholder_text = 'PLACEHOLDER'
group_open_y_percent = 2/3  # proportion of a cell
group_open_delay = 800  # delay to open a group by hovering (milliseconds)
move_ignore_event_delay = 20


class DataTreeview(ttk.Treeview):

    def __init__(self, parent, name, is_darkmode=True, callbacks=None, can_open=True, can_move=False, return_none=False,
                 selectmode='browse', prevent_extreme_selection=False, **kwargs):
        super().__init__(parent, selectmode=selectmode, **kwargs)
        self._parent = parent
        self.name = name
        self.callbacks = callbacks if callbacks is not None else {}
        self.row_data = {}
        self.group_types = {}
        self.cur_selection = []
        self.selection_order = []
        self.return_none = return_none
        self.is_darkmode = is_darkmode

        self.can_open = can_open

        if can_move:
            self.unbind_all("<ButtonPress-1>")
            self.bind("<ButtonPress-1>", self.bDown_move)
            self.bind("<ButtonRelease-1>", self.bUp_move, add='+')
            self.bind("<B1-Motion>", self.bMove, add='+')
            self.bind("<Shift-ButtonPress-1>", self.bDown_Shift, add='')
            self.bind("<Shift-ButtonRelease-1>", self.bUp_Shift, add='')

        if can_open:
            self.bind("<ButtonRelease-1>", self.select_entry, add='+')
            # self.bind("<ButtonRelease-1>", self.print_parent_and_index, add='+')

        self.in_motion = False
        self.has_shift = False
        self.first_selected = None
        self.drag_widget: Union[None, DragWindow] = None
        self.placeholder = None
        self.selection_bounds = None
        self.selected = None
        self.group_waiting = ''
        self.parent_restriction = None
        self.move_ignore_counter = 0
        self.prevent_extreme_selection = prevent_extreme_selection
        self.first_entry = None
        self.last_entry = None

    def add_callback(self, key, callback):
        self.callbacks[key] = callback

    def set_darkmode(self, is_darkmode):
        self.is_darkmode = is_darkmode

    def select_entry(self, event):
        if self.in_motion:
            return
        if 'select' not in self.callbacks:
            raise RuntimeError(f'{type(self)}-{self.name}: no "select" callback given')
        row = self.identify_row(event.y)
        if row == '':
            return
        if len(self.selection()) > 1:
            return
        if self.item(row)['text'] == placeholder_text:
            return
        row_data = self.row_data[row]
        if row_data is not None:
            self.callbacks['select'](self.name, row_data)
        elif self.return_none:
            self.callbacks['select'](self.name, row_data)

    def insert_entry(self, parent, text, values, group_type=None, row_data=None, **kwargs):
        iid = str(len(self.row_data))
        self.row_data[iid] = row_data
        self.group_types[iid] = group_type
        super().insert(parent=parent, iid=iid, text=text, values=values, **kwargs)
        self.last_entry = iid
        self.first_entry = '0'
        return iid

    def get_row_by_rowdata(self, row_data):
        temp_row_data = [v for v in self.row_data.values()]
        return list(self.row_data.keys())[temp_row_data.index(row_data)] if row_data in temp_row_data else None

    def select_by_rowdata(self, row_data):
        for iid, data in self.row_data.items():
            if row_data == data:
                self.selection_set(iid)
                break

    def clear_all_entries(self):
        for row in self.get_children():
            self.delete(row)
        self.row_data = {}
        self.first_entry = None
        self.last_entry = None

    def get_selection(self):
        return [self.row_data[self.get_children()[int(s)]] for s in self.cur_selection]

    def get_open_elements(self, parent='', open_items=None):
        if open_items is None:
            open_items = []
        for child in self.get_children(parent):
            is_open = self.item(child)['open']
            if not isinstance(is_open, bool):
                is_open = is_open == 1
            if not is_open:
                continue
            child_uuid = self.row_data.get(child, None)
            if child_uuid is None:
                child_uuid = f'{self.row_data[parent]}{sep}{self.item(child)["values"][0].split(" ")[0]}'
            open_items.append(child_uuid)
            self.get_open_elements(parent=child, open_items=open_items)
        return open_items

    def open_tree_elements(self, open_items):
        for item_uuid in open_items:
            if sep in item_uuid:
                item_uuid, case = item_uuid.split(sep)
                row_id = None
                for child in self.get_children(self.get_row_by_rowdata(item_uuid)):
                    if case in self.item(child)['values'][0]:
                        row_id = child
                        break
            else:
                row_id = self.get_row_by_rowdata(item_uuid)
            if row_id is None:
                continue
            self.see(row_id)
            self.item(row_id, open=True)

    def bDown_Shift(self, event):
        self.has_shift = True
        clicked_row = int(self.identify_row(event.y))
        first_row = int(self.first_selected)
        if clicked_row == first_row:
            self.after(10, self.selection_set, self.first_selected)
            return
        select = [str(i) for i in range(min(clicked_row, first_row), max(clicked_row, first_row)+1)]

        # Make sure that the first and last entries cannot be selected (label and return)
        if self.prevent_extreme_selection:
            root_children = self.get_children('')
            first = root_children[0]
            if first in select:
                select.remove(first)
            last = root_children[-1]
            if last in select:
                select.remove(last)
        self.selected = select
        self.selection_set(select)

    def bUp_Shift(self, event):
        self.has_shift = False

    def bDown_move(self, event):
        if self.identify_row(event.y) not in self.selection():
            sel = self.identify_row(event.y)
            self.selection_set(sel)
            self.first_selected = sel
            self.selected = sel

    def bUp_move(self, event):
        if not self.in_motion:
            return
        final_index = self.index(self.placeholder)
        insert_after_index = 0 if final_index == 0 else final_index - 1
        insert_after_iid = self.get_children(self.parent(self.placeholder))[insert_after_index]

        insert_in_group = False
        if final_index == 0:
            insert_after_iid = self.parent(insert_after_iid)
            insert_in_group = True

        insert_after_data: Union[None, str] = self.row_data.get(insert_after_iid, None)
        if insert_after_data is None:
            case = self.item(insert_after_iid)['values'][0].split(' ')[0]
            insert_after_data = f'{self.row_data[(self.parent(insert_after_iid))]}{sep}{case}'

        # Assorted cleanup
        self.in_motion = False
        self.placeholder = None
        self.drag_widget.destroy()
        self.drag_widget = None
        self.parent_restriction = None
        self.move_ignore_counter = 0

        # Callback to have the items moved and tree refreshed
        self.callbacks['move_items'](self.name, self.selection_bounds, insert_after_data, insert_in_group)
        self.selection_bounds = None

    def bMove(self, event):
        if self.has_shift:
            return
        if not self.in_motion:
            if self.move_ignore_counter < move_ignore_event_delay:
                self.move_ignore_counter += 1
                return
            # should prevent moving the first and last entries alone if prevent extreme selection is on
            if (self.prevent_extreme_selection and len(self.selected) == 1 and
                    self.first_selected in (self.first_entry, self.last_entry)):
                return
            self.selection_set(self.selected)
            self.in_motion = True
            self.start_motion()
            if sep in self.selection_bounds[0]:
                self.parent_restriction = self.parent(self.placeholder)

        sel_iid = self.identify_row(event.y)
        # No need to update position bc
        if sel_iid == '':
            return

        if self.parent_restriction is not None:
            if self.parent_restriction != self.parent(sel_iid):
                return

        self.drag_widget.update_pos(event.x_root, event.y_root)
        if sel_iid == self.placeholder:
            return

        if len(self.get_children(sel_iid)) > 0:
            if not self.item(sel_iid)['open'] in (True, 1):
                if self.group_waiting != '':
                    return
                bbox = self.bbox(sel_iid)
                if event.y < bbox[1] + int(bbox[3] * group_open_y_percent):
                    self.group_waiting = sel_iid
                    self.after(15, self.delayed_open_group, sel_iid, 0, group_open_delay)
                    return
        self.group_waiting = ''
        moveto = self.index(sel_iid)
        for s in self.selection():
            parent = self.parent(self.identify_row(event.y))
            self.move(s, parent, moveto)

    def start_motion(self):
        selection = self.selection()
        base_parent, parent_list = self.motion_get_parent_base_and_list(selection)
        selection = self.motion_select_all_children(base_parent, parent_list, selection)
        selection = self.sort_sel_iids(selection)
        bounds = (selection[0], selection[-1])
        new_bounds = []
        for entry in bounds:
            data = self.row_data.get(entry, None)
            if data is None:
                data = f'{self.row_data[self.parent(entry)]}{sep}{self.item(entry)["values"][0].split(" ")[0]}'
            new_bounds.append(data)
        self.selection_bounds = tuple(new_bounds)
        index = self.index(bounds[0])
        values = [''] * (len(self['columns']) - 1)
        self.placeholder = self.insert(parent=base_parent, index=index, iid='placeholder', text=placeholder_text, values=values)
        self.selection_set(self.placeholder)

        item_iids = selection[:5] if len(selection) > 5 else selection

        items = [{'parent': '', 'index': tk.END, 'text': self.item(i)['text'], 'values': self.item(i)['values'][0]} for i in item_iids]
        tree_dict = {**drag_tree_info, 'items': items}

        bbox = self.winfo_rootx(), self.winfo_rooty(), self.winfo_rootx()+self.winfo_width(), self.winfo_rooty()+self.winfo_height()

        self.drag_widget = DragWindow(self, is_darkmode=self.is_darkmode, bbox=bbox, tree_dict=tree_dict)

        for s in selection:
            self.delete(s)

    def motion_get_parent_base_and_list(self, selection) -> Tuple[str, List[str]]:
        base_parent = None
        parent_list = []
        for s in selection:
            cur_parent = self.parent(s)
            if base_parent is None:
                base_parent = cur_parent
            if cur_parent == '':
                base_parent = cur_parent
            if base_parent != '':
                base_parent = str(min(int(base_parent), int(cur_parent)))
            if cur_parent not in parent_list:
                parent_list.append(cur_parent)
        return base_parent, parent_list

    def motion_select_all_children(self, base_parent, parent_list, selection):
        i = 0
        while i < len(parent_list):
            p = parent_list[i]
            if p == base_parent:
                i += 1
                continue
            children = self.get_children(p)
            for c in children:
                if c not in selection:
                    selection.append(c)
                    if len(self.get_children(c)) > 0:
                        parent_list.append(c)
            i += 1
        return selection

    @staticmethod
    def sort_sel_iids(selection: List[str]):
        int_sel = list({int(s) for s in selection})
        int_sel.sort()
        return [str(s) for s in int_sel]

    def delayed_open_group(self, group_iid, time_elapsed, time_finished):
        if self.group_waiting != group_iid:
            return
        if time_elapsed > time_finished:
            self.item(group_iid, open=True)
        else:
            self.after(100, self.delayed_open_group, group_iid, time_elapsed + 100, time_finished)

    def print_parent_and_index(self, event):
        iid = self.identify_row(event.y)
        print(f'parent: {self.parent(iid)}, index: {self.index(iid)}')

