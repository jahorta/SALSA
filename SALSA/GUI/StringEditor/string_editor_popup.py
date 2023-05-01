import tkinter as tk


class StringPopup(tk.Toplevel):
    t = 'SALSA - String Editor'
    log_key = 'VarEditPopup'
    w = 250
    h = 400

    option_settings = {}

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent: tk.Tk = parent
        self.callbacks = callbacks
