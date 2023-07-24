import tkinter as tk
from tkinter import ttk
from typing import Union

tooltip_offset_x = 12
tooltip_offset_y = 1


class HoverToolTip(tk.Toplevel):

    def __init__(self, master, tooltip, x, y, destroy_callback, min_time=None, position='', *args, **kwargs):
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

        self.after(10, self.move_into_position, x, y, position)

        if min_time is not None:
            time = min_time
        else:
            time = 100
        self.after(time, self.check_for_destroy)

    def check_for_destroy(self):
        rel_x = self.master.winfo_pointerx() - self.master.winfo_rootx()
        rel_y = self.master.winfo_pointery() - self.master.winfo_rooty()
        if rel_x < 0 or rel_x > self.master.winfo_width() or rel_y < 0 or rel_y > self.master.winfo_height():
            return self.destroy_callback(self)
        self.after(20, self.check_for_destroy)

    def move_into_position(self, x, y, position):
        if 'above' in position:
            y -= self.winfo_height()
        if 'below' in position:
            y += self.winfo_height()
        if 'center' in position:
            x -= self.winfo_width()//2
        if 'right' in position:
            x -= self.winfo_width()
        self.geometry(f'+{x + tooltip_offset_x}+{y + tooltip_offset_y}')


tooltip_is_active = False
active_tooltip: Union[None, HoverToolTip] = None
tooltip_delay = 700
tooltip_hover_interval = 50


def schedule_tooltip(master, tooltip, delay=tooltip_delay, *args, **kwargs):
    global tooltip_is_active
    if tooltip_is_active:
        return
    tooltip_is_active = True
    if delay > 0:
        check_hover(master, tooltip, delay, args, kwargs)
    else:
        tooltip_generator(master, tooltip, master.winfo_rootx(), master.winfo_rooty(), args, kwargs)


def check_hover(master, tooltip, total_delay, args, kwargs, cur_delay=0):
    rel_x = master.winfo_pointerx() - master.winfo_rootx()
    rel_y = master.winfo_pointery() - master.winfo_rooty()
    if rel_x < 0 or rel_x > master.winfo_width() or rel_y < 0 or rel_y > master.winfo_height():
        global tooltip_is_active
        tooltip_is_active = False
        return
    if cur_delay < total_delay:
        cur_delay += tooltip_hover_interval
        master.after(20, check_hover, master, tooltip, total_delay, args, kwargs, cur_delay)
    else:
        tooltip_generator(master, tooltip, master.winfo_pointerx(), master.winfo_pointery(), args, kwargs)


def tooltip_generator(master, tooltip, x, y, args, kwargs):
    global active_tooltip
    if active_tooltip is not None:
        return
    active_tooltip = HoverToolTip(master, tooltip, x, y, destroy_tooltip, *args, **kwargs)
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
