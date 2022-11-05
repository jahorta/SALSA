import tkinter as tk
from tkinter import ttk
from SALSA.GUI import widgets as w
from pathlib import Path


class HelpPopupView(tk.Toplevel):
    window_offset = {
        'x': 50,
        'y': 50
    }

    size = {
        'width': 400,
        'height': 400
    }

    text_offset = {
        'x': 10,
        'y': 10
    }

    def __init__(self, parent, title, about_text, position, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks

        help_canvas = tk.Canvas(self, width=self.size['width'], height=self.size['height'])
        help_canvas.grid(row=0, column=0)
        help_canvas.create_text((self.text_offset['x'], self.text_offset['y']),
                                anchor=tk.NW, text=about_text,
                                width=self.size['width'] - self.text_offset['x'])

        self.quit = tk.Button(self, text='Cancel', command=self.callbacks['on_close'])
        self.quit.grid(row=1, column=0)
        canvas_scrollbar = tk.Scrollbar(self, orient="vertical", command=help_canvas.yview)
        help_canvas.configure(yscrollcommand=canvas_scrollbar.set)
        help_canvas.config(scrollregion=help_canvas.bbox("all"))
        canvas_scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S)

        self.title(title)
        self.resizable(width=False, height=False)
        posX = position['x'] + self.window_offset['x']
        posY = position['y'] + self.window_offset['y']
        pos = '+{0}+{1}'.format(posX, posY)
        self.geometry(pos)


class TabbedHelpPopupView(tk.Toplevel):
    window_offset = {
        'x': 50,
        'y': 50
    }

    size = {
        'width': 400,
        'height': 400
    }

    text_offset = {
        'x': 10,
        'y': 10
    }

    def __init__(self, parent, title, about_text, position, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        notebook = ttk.Notebook(self)
        notebook.grid(row=0, column=0)

        for i, (k, v) in enumerate(about_text.items()):
            tab_frame = w.ScrolledTextCanvas(notebook, size=self.size, text_offset=self.text_offset,
                                             text=v)
            notebook.add(tab_frame)
            notebook.tab(i, text=k)

        self.quit = tk.Button(self, text='Cancel', command=lambda: self.callbacks['on_close'](window='help'))
        self.quit.grid(row=1, column=0)
        self.title(title)
        self.resizable(width=False, height=False)
        posX = position['x'] + self.window_offset['x']
        posY = position['y'] + self.window_offset['y']
        pos = '+{0}+{1}'.format(posX, posY)
        self.geometry(pos)


class ExporterView(tk.Toplevel):
    window_offset = {
        'x': 50,
        'y': 50
    }

    size = {
        'width': 400,
        'height': 400
    }

    text_offset = {
        'x': 10,
        'y': 10
    }

    def __init__(self, parent, title, export_fields: dict, position, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.callbacks = callbacks
        self.export_notebook = ttk.Notebook(self, width=self.size['width'], height=self.size['height'])
        self.export_notebook.grid(row=0, column=0)
        self.export_notebook.rowconfigure(0, weight=1)
        self.export_notebook.columnconfigure(0, weight=1)

        self.export_frame = tk.Frame(self)
        self.export_frame.grid(row=0, column=0, sticky='NSEW')
        self.export_selector = w.LabelInput(self.export_frame, 'Name', field_spec=export_fields['types'])
        self.export_selector.set(export_fields['types']['values'][0])
        self.export_selector.grid(row=0, column=0)
        self.button_extract_data = tk.Button(self.export_frame, text='Extract Data', command=self.export_selected_data)
        self.button_extract_data.grid(row=1, column=0)

        button_frame = tk.Frame(self)
        button_frame.grid(row=1, column=0)
        self.quit = tk.Button(button_frame, text='Cancel', command=lambda: self.callbacks['on_close'](window='export'))
        self.quit.grid(row=0, column=1)
        self.export_all = tk.Button(button_frame, text='Write all to CSVs', command=lambda: self.write_csv('all'))
        progress_frame = tk.LabelFrame(self, text='Progress')
        progress_frame.grid(row=2, column=0)
        self.progress_text = tk.StringVar()
        self.progress_text.set('')
        progress_text_label = tk.Label(self, textvariable=self.progress_text)
        progress_text_label.grid(row=2, column=0, sticky=tk.W+tk.E)
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate', length=100)
        self.progress_bar.grid(row=3, column=0, sticky=tk.W+tk.E)
        self.title(title)
        self.resizable(width=True, height=True)
        posX = position['x'] + self.window_offset['x']
        posY = position['y'] + self.window_offset['y']
        pos = f'+{posX}+{posY}'
        self.geometry(pos)

        self.export_values = {}

    def update_exports(self, exports):
        self.export_values = exports

        for tab in reversed(range(0, len(self.export_notebook.tabs()))):
            self.export_notebook.forget(tab)

        for i, (k, v) in enumerate(self.export_values.items()):
            tab_frame = tk.Frame(self.export_notebook)
            tab_frame.rowconfigure(0, weight=1)
            tab_frame.columnconfigure(0, weight=1)
            self.export_notebook.add(tab_frame)
            self.export_notebook.tab(i, text=k)

            tab_text = w.ScrolledTextCanvas(tab_frame, size=self.size, text_offset=self.text_offset,
                                            text=v)
            tab_text.grid(row=0, column=0)

            button_frame = tk.Frame(tab_frame)
            button_frame.grid(row=1, column=0)
            tab_button = tk.Button(button_frame, text='Copy to clipboard', command=self.send_to_clipboard)
            tab_button.grid(row=0, column=0)
            tab_button = tk.Button(button_frame, text='Write tab to CSV', command=lambda: self.write_csv('tab'))
            tab_button.grid(row=0, column=1)

        self.export_all.grid(row=0, column=0)
        self.export_notebook.tkraise()

    def export_selected_data(self):
        print('export button pressed')
        self.button_extract_data['state'] = 'disabled'
        export_type = self.export_selector.get()
        if export_type == '':
            self.update_progress(0, 'No Export Value Selected...')
            return
        self.callbacks['on_export'](export_type=export_type)

    def send_to_clipboard(self):
        key = self.export_notebook.tab(self.export_notebook.select(), 'text')
        export = self.export_values[key]
        self.clipboard_clear()
        self.clipboard_append(export)
        print(f'sent {key} to clipboard')

    def update_progress(self, percent, text):
        self.progress_text.set(text)
        self.progress_bar['value'] = percent

    def write_csv(self, number):
        if number == 'all':
            to_csv = self.export_values
        else:
            tab_name = self.export_notebook.tab(self.export_notebook.select(), 'text')
            to_csv = {tab_name:  self.export_values[tab_name]}

        self.callbacks['on_write_to_csv'](to_csv)


class FileSelectView(tk.Toplevel):
    offset = {
        'x': 50,
        'y': 50
    }

    script_tree_headers = {
        '#0': {'label': 'Name', 'width': 200},
        'Focus': {'label': 'Sel', 'width': 50}
    }
    default_width = 100
    default_minwidth = 10
    default_anchor = tk.CENTER

    def __init__(self, parent, last, scalebar_pos, position, filepath, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.file = last
        self.path = filepath
        self.callbacks = callbacks
        self.scalebarPos = scalebar_pos

        fileSelectlabel = tk.LabelFrame(self, text='File Select')
        columns = list(self.script_tree_headers.keys())[1:]
        self.file_select_tree = ttk.Treeview(fileSelectlabel, columns=columns, height=25)
        fileSelectlabel.columnconfigure(0, weight=1)
        fileSelectlabel.rowconfigure(1, weight=1)
        self.file_select_tree.grid(row=0, column=0, sticky='NSEW')

        for name, definition in self.script_tree_headers.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)

            self.file_select_tree.heading(name, text=label, anchor=anchor)
            self.file_select_tree.column(name, anchor=anchor, minwidth=minwidth, width=width, stretch=stretch)

        self.file_select_tree_scroll = ttk.Scrollbar(fileSelectlabel, orient=tk.VERTICAL,
                                                     command=self.file_select_tree.yview)
        self.file_select_tree.configure(yscrollcommand=self.file_select_tree_scroll.set)
        self.file_select_tree_scroll.grid(row=0, column=1, sticky='NSEW')

        self.file_select_tree.bind('<<TreeviewSelect>>', self.on_select_script_file)
        fileSelectlabel.grid(row=0, column=0)

        buttonFrame = tk.Frame(self)
        self.load = tk.Button(buttonFrame, text='Load', command=self.on_load_script_file)
        self.load.grid(row=0, column=3)
        self.quit = tk.Button(buttonFrame, text='Cancel', command=self.callbacks['on_quit'])
        self.quit.grid(row=0, column=4)
        buttonFrame.grid(row=1, column=0, sticky=tk.E)

        self.title('File Select Menu')
        self.resizable(width=False, height=False)
        posX = position['x'] + self.offset['x']
        posY = position['y'] + self.offset['y']
        pos = '+{0}+{1}'.format(posX, posY)
        self.geometry(pos)

    def on_select_script_file(self, *args):
        self.scalebarPos = str(self.file_select_tree.yview()[0])
        file = self.file_select_tree.selection()
        if len(self.file) == 0:
            return
        self.file = file[0]
        self.populate_files(self.path)

    def on_load_script_file(self, *args):
        if self.file is None:
            """message to select a file"""
        else:
            self.callbacks['on_load'](self.file, str(self.scalebarPos))
            self.callbacks['on_quit']()

    def populate_files(self, path):

        self.path = path

        for row in self.file_select_tree.get_children():
            self.file_select_tree.delete(row)

        paths = Path(path).glob('**/*')
        for path in paths:
            # Only list files with the .sct file extension
            if not path.suffix == '.sct':
                continue
            values = []
            if path.name == self.file:
                values.append('***')
            self.file_select_tree.insert('', 'end', iid=str(path.name), text=str(path.name), values=values)
        print(paths, 'loaded')
