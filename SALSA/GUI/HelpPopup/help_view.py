# Base Python Library Imports
import tkinter as tk
from tkinter import ttk

# SALSA specific imports
from SALSA.GUI import widgets as w


class HelpView(tk.Toplevel):
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
            tab_frame = w.ScrollTextCanvas(notebook, size=self.size, text_offset=self.text_offset,
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

