import tkinter as tk
from tkinter import ttk
from typing import Union

tooltip_offset_x = 12
tooltip_offset_y = 1


class HoverToolTip(tk.Toplevel):

    def __init__(self, master, tooltip, x, y, destroy_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.overrideredirect(True)
        self.wm_focusmodel('active')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.destroy_callback = destroy_callback

        tooltip_frame = ttk.Frame(self, style='tooltip.TFrame')
        tooltip_frame.grid(row=0, column=0)
        self.tooltip = ttk.Label(tooltip_frame, text=tooltip)
        self.tooltip.grid(row=0, column=0, sticky='NSEW', padx=1, pady=1)

        self.geometry(f'+{x + tooltip_offset_x}+{y + tooltip_offset_y}')

        self.after(100, self.check_for_destroy)

    def check_for_destroy(self):
        rel_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        rel_y = self.master.winfo_pointery() - self.master.winfo_rooty()
        if rel_x < 0 or rel_x > self.master.winfo_width() or rel_y < 0 or rel_y > self.master.winfo_height():
            return self.destroy_callback(self)
        self.after(20, self.check_for_destroy)


tooltip_is_active = False
active_tooltip: Union[None, HoverToolTip] = None
tooltip_delay = 700
tooltip_hover_interval = 50


def schedule_tooltip(master, tooltip, delay=tooltip_delay):
    global tooltip_is_active
    if tooltip_is_active:
        return
    tooltip_is_active = True
    check_hover(master, tooltip, total_delay=delay)


def check_hover(master, tooltip, total_delay, cur_delay=0):
    rel_x = master.winfo_pointerx() - master.winfo_rootx()
    rel_y = master.winfo_pointery() - master.winfo_rooty()
    if rel_x < 0 or rel_x > master.winfo_width() or rel_y < 0 or rel_y > master.winfo_height():
        global tooltip_is_active
        tooltip_is_active = False
        return
    if cur_delay < total_delay:
        cur_delay += tooltip_hover_interval
        master.after(20, check_hover, master, tooltip, total_delay, cur_delay)
    else:
        tooltip_generator(master, tooltip, master.winfo_pointerx(), master.winfo_pointery())


def tooltip_generator(master, tooltip, x, y):
    global active_tooltip
    if active_tooltip is not None:
        return
    active_tooltip = HoverToolTip(master, tooltip, x, y, destroy_tooltip)
    active_tooltip.tkraise()


def destroy_tooltip(tooltip):
    global tooltip_is_active
    tooltip_is_active = False
    tooltip.destroy()
    global active_tooltip
    active_tooltip = None


if __name__ == '__main__':
    w = tk.Tk()
    w.geometry('+200+200')

    label = tk.Label(w, text='test label for tooltip')
    label.pack()
    label.bind('<Enter>', lambda e: schedule_tooltip(label, 'This is a tooltip', e))

    w.mainloop()