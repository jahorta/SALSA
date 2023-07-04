from tkinter import ttk

from SALSA.Common.constants import sep


class DataTreeview(ttk.Treeview):

    def __init__(self, parent, name, callbacks=None, can_open=True, return_none=False, selectmode='browse', **kwargs):
        super().__init__(parent, selectmode=selectmode, **kwargs)

        self._parent = parent
        self.name = name
        self.callbacks = callbacks if callbacks is not None else {}
        self.row_data = {}
        self.group_types = {}
        self.cur_selection = []
        self.selection_order = []
        self.return_none = return_none

        self.can_open = can_open

        if can_open:
            self.bind("<ButtonRelease-1>", self.select_entry, add='+')

    def add_callback(self, key, callback):
        self.callbacks[key] = callback

    def select_entry(self, event):
        if 'select' not in self.callbacks:
            raise RuntimeError(f'{type(self)}-{self.name}: no "select" callback given')
        widget = self.identify_row(event.y)
        if widget == '':
            return
        row_data = self.row_data[widget]
        if row_data is not None:
            self.callbacks['select'](self.name, row_data)
        elif self.return_none:
            self.callbacks['select'](self.name, row_data)

    def insert_entry(self, parent, text, values, group_type=None, row_data=None, **kwargs):
        iid = str(len(self.row_data))
        self.row_data[iid] = row_data
        self.group_types[iid] = group_type
        super().insert(parent=parent, iid=iid, text=text, values=values, **kwargs)
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
