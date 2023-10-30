from typing import Union, Dict, Literal
import tkinter as tk
from tkinter import messagebox, ttk

from SALSA.GUI.Widgets.widgets import LabelNameEntry
from SALSA.GUI.Widgets.hover_tooltip import schedule_tooltip
from SALSA.GUI.Widgets.data_treeview import DataTreeview
from SALSA.Common.constants import sep, label_name_sep, link_sep
from SALSA.GUI.fonts_used import SALSAFont
from SALSA.GUI.ProjectEditor.instruction_selector import InstructionSelectorWidget
from SALSA.GUI.ParamEditorPopups.param_editor_controller import ParamEditController
from SALSA.Common.setting_class import settings
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.Project.project_facade import SCTProjectFacade
from SALSA.Project.project_container import SCTLink

tree_children = {
    '': 'script',
    'script': 'section',
    'section': 'instruction',
    'instruction': 'parameter',
    'parameter': ''
}

tree_parents = {v: k for k, v in tree_children.items()}

group_handle_width = 20


class ProjectEditorController:
    log_name = 'PrjEditorCtrl'

    default_settings = {
        'style': 'grouped'
    }

    def __init__(self, parent: tk.Tk, view: ProjectEditorView, facade: SCTProjectFacade, callbacks, theme):
        self.parent: tk.Tk = parent
        self.callbacks = callbacks

        self.project: SCTProjectFacade = facade
        self.project.set_callback('confirm_remove_inst_group', self.confirm_change_inst_group)
        self.project.set_callback('set_change', self.set_change_flag)
        self.project.set_callback('delay_set_change', self.delay_set_change_flag)

        self.view: ProjectEditorView = view
        view_callbacks = {
            'update_field': self.update_field,
            'edit_param': self.on_edit_parameter,
            'show_header_selection_menu': self.show_header_selection_menu,
            'show_script_menu': self.show_script_right_click_menu,
            'show_section_menu': self.show_section_right_click_menu,
            'show_inst_menu': self.show_instruction_right_click_menu,
            'save_project': self.save_project,
            'set_mem_offset': self.set_mem_offset,
            'param_rcm': self.param_right_click_menu,
            'inst_is_label': self.check_is_label,
            'show_rename_widget': self.show_sect_rename_widget,
            'refresh_offsets': self.callbacks['refresh_offsets']
        }
        self.view.add_and_bind_tree_callbacks(view_callbacks)

        pe_callbacks = {'get_var_alias': self.get_var_alias,
                        'refresh_inst': self.on_refresh_inst,
                        'update_variables': self.update_var_usage,
                        'get_subscript_list': lambda: self.project.get_section_list(self.current['script']),
                        'set_change': self.set_change_flag,
                        'get_instruction_list': lambda: self.project.get_inst_list(self.current['script'],
                                                                                   self.current['section'],
                                                                                   self.current['instruction'])}
        self.param_editor = ParamEditController(self.view, callbacks=pe_callbacks, theme=theme)

        if self.log_name not in settings:
            settings[self.log_name] = {}

        for s, v in self.default_settings.items():
            if s not in settings[self.log_name]:
                settings[self.log_name][s] = v

        self.current: Dict[str, Union[str, None]] = {
            'script': None,
            'section': None,
            'instruction': None,
            'parameter': None
        }

        self.cur_mem_offset = 0
        self.script_refresh_offset_queue = []
        self.encoding_errors = []

        self.trees: Dict[str, DataTreeview] = {
            'script': self.view.scripts_tree,
            'section': self.view.sections_tree,
            'instruction': self.view.insts_tree,
            'parameter': self.view.param_tree
        }

        self.project.set_callback(key='update_scripts', callback=lambda: self.update_tree('script',
                                                                                          self.project.get_tree(
                                                                                              self.view.get_headers(
                                                                                                  'script'))))

        self.trees['script'].add_callback('select', self.on_select_tree_entry)
        self.trees['section'].add_callback('select', self.on_select_tree_entry)
        self.trees['section'].add_callback('move_items', self.on_move_items)
        self.trees['instruction'].add_callback('select', self.on_select_tree_entry)
        self.trees['instruction'].add_callback('move_items', self.on_move_items)

        self.has_changes = False

        self.link_font = SALSAFont()

        self.entry_widget: Union[None, InstructionSelectorWidget, LabelNameEntry, ttk.Frame] = None

    def delay_set_change_flag(self, delay):
        self.view.after(delay, self.set_change_flag)

    def set_change_flag(self, script=None):
        script = self.current.get('script', None) if script is None else script
        if script not in self.script_refresh_offset_queue and script is not None:
            self.script_refresh_offset_queue.append(script)

        self.has_changes = True
        self.view.save_button.configure(state='normal')

    def set_mem_offset(self):
        mem_offset_value = self.view.mem_offset_var.get()
        self.cur_mem_offset = 0 if mem_offset_value == '' else int(mem_offset_value, 16)
        if self.current['section'] is not None:
            self.update_tree('instruction', self.project.get_tree(self.view.get_headers('instruction'), **self.current))

    def save_project(self):
        self.callbacks['save_project']()
        self.has_changes = False
        self.view.save_button.configure(state='disabled')

    def load_project(self):
        for key in list(self.current.keys()):
            self.current[key] = None
        for tree in self.trees.values():
            tree.clear_all_entries()
        self.update_tree('script', self.project.get_tree(self.view.get_headers('script')))
        if len(self.project.get_project_encode_errors()) > 0:
            self.encoding_errors = ['True']
        self.check_encoding_errors()

    def on_select_tree_entry(self, tree_key, entry):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        self.clear_inst_details()
        if tree_key == 'instruction':
            self.callbacks['toggle_frame_state'](self.view.inst_frame, 'normal')
            return self.on_select_instruction(entry)
        self.callbacks['toggle_frame_state'](self.view.inst_frame, 'disabled')
        kwargs = {'style': settings[self.log_name]['style']}
        self.current[tree_key] = entry
        cur_key = tree_key
        while True:
            kwargs[cur_key] = self.current[cur_key]
            cur_key = tree_parents[cur_key]
            if cur_key == '':
                break
        child_tree = tree_children[tree_key]
        kwargs['headers'] = self.view.get_headers(tree_key=child_tree)
        tree_list = self.project.get_tree(**kwargs)
        self.update_tree(child_tree, tree_list)

    def on_select_instruction(self, instructID):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        self.current['instruction'] = instructID
        self.current['parameter'] = None
        self.view.param_tree.clear_all_entries()
        details = self.project.get_instruction_details(**self.current)
        if details is None:
            return
        details['parameter_tree'] = self.project.get_parameter_tree(headings=self.view.get_headers('parameter'),
                                                                    **self.current)
        self.set_instruction_details(details)

    def update_tree(self, tree, tree_dict: Union[dict, None], clear_other_trees=True):
        if tree is None:
            for tree in self.trees.keys():
                self.trees[tree].clear_all_entries()
            return

        # Clear the current tree and all child trees to prevent desync
        cur_tree = tree
        trees_to_clear = [cur_tree]
        if clear_other_trees:
            while cur_tree != '':
                trees_to_clear.append(tree_children[cur_tree])
                cur_tree = tree_children[cur_tree]

        for t in trees_to_clear:
            if t != '':
                self.trees[t].clear_all_entries()

        if tree_dict is None:
            return

        tree_dict = self.adjust_tree_entries(tree_dict, tree)
        self._add_tree_entries(tree, tree_dict)

    def _add_tree_entries(self, tree_key: str, tree_list):
        tree = self.trees[tree_key]
        if not isinstance(tree_list, list):
            return
        parent_list = ['']
        prev_iid = -1
        headers = self.view.get_headers(tree_key)
        for entry in tree_list:
            if isinstance(entry, str):
                if entry == 'group':
                    parent_list.append(prev_iid)
                elif entry == 'ungroup':
                    if len(parent_list) == 1:
                        raise RuntimeError(f'{self.log_name}: unable to lower group level, not enough groups left')
                    parent_list.pop()
                else:
                    raise ValueError(f'{self.log_name}: Unknown command in tree list sent to _add_tree_entries')
                continue
            kwargs = {'parent': parent_list[-1], 'index': 'end'}
            values = []
            first = True
            for col in headers:
                if col == 'name':
                    if 'group_type' in entry.keys():
                        entry[col] += f' ({entry["group_type"]})'
                elif col == 'absolute_offset':
                    if entry[col] in ('', 'None') or entry[col] is None:
                        entry[col] = ''
                    else:
                        entry[col] = hex(int(entry[col]) + self.cur_mem_offset)

                    if self.current['script'] is not None:
                        if self.current['script'] in self.script_refresh_offset_queue:
                            entry[col] = '??RefreshPls'
                if first:
                    kwargs['text'] = entry[col]
                    first = False
                else:
                    values.append(entry[col])
                entry.pop(col)
            kwargs['values'] = values
            kwargs = {**kwargs, **entry}
            prev_iid = tree.insert_entry(**kwargs)

    def adjust_tree_entries(self, entries, key):
        if key == 'instruction':
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                entry['delay_param'] = '*' if entry['delay_param'] != 'None' else ''
                entry['skip_refresh'] = '*' if entry['skip_refresh'] == 'True' else ''
        return entries

    def set_instruction_details(self, details):
        if details is None:
            return
        self.view.inst_label.config(text=f'{details["instruction_id"]} - {details["name"]}')
        self.view.inst_description.config(text=details['description'])

        self.update_tree('parameter', details['parameter_tree'])

        self.view.skip_ckeck_var.set(int(details['skip_refresh']))
        if details['no_new_frame']:
            self.view.skip_error_label.config(text='This instruction never skips')
        elif details['forced_new_frame']:
            self.view.skip_error_label.config(text='This instruction always skips')
        else:
            self.view.skip_error_label.config(text='')

        self.view.delay_label.config(text=str(details['delay_param']))

        for i, link in enumerate(details['links_out']):
            link: SCTLink
            if link.target_trace is None:
                continue
            tgt_frame = tk.Frame(self.view.link_out.scroll_frame)
            tgt_frame.bind('<Enter>', self.handle_link_font)
            tgt_frame.bind('<Leave>', self.handle_link_font)
            tgt_frame.grid(row=i, column=0, sticky=tk.E + tk.W, pady='5 0', padx=5)
            tgt_frame.columnconfigure(0, weight=1)

            tgt_sect = link.target_trace[0]
            tgt_inst = self.project.get_inst_ind(script=self.current['script'], section=tgt_sect,
                                                 inst=link.target_trace[1])

            tgt_label = ttk.Label(tgt_frame, text=f'{tgt_sect}{link_sep}{tgt_inst}',
                                  font=self.link_font.font, style='canvas.TLabel')
            tgt_label.grid(row=0, column=0, sticky=tk.E + tk.W)
            tgt_label.bind('<ButtonRelease-1>', self.goto_link)

        for i, link in enumerate(details['links_in']):
            link: SCTLink
            if link.origin_trace is None:
                continue
            ori_frame = tk.Frame(self.view.link_in.scroll_frame)
            ori_frame.grid(row=i, column=0, sticky=tk.E + tk.W, pady='5 0', padx=5)
            ori_frame.bind('<Enter>', self.handle_link_font)
            ori_frame.bind('<Leave>', self.handle_link_font)
            ori_frame.columnconfigure(0, weight=1)

            ori_sect = link.origin_trace[0]
            ori_inst = self.project.get_inst_ind(script=self.current['script'], section=ori_sect,
                                                 inst=link.origin_trace[1])

            ori_label = ttk.Label(ori_frame, text=f'{ori_sect}{link_sep}{ori_inst}',
                                  font=self.link_font.font, style='canvas.TLabel')
            ori_label.grid(row=0, column=0, sticky=tk.E + tk.W)
            ori_label.bind('<ButtonRelease-1>', self.goto_link)

    def handle_link_font(self, e):
        font = self.link_font.font if e.type == tk.EventType.Leave else self.link_font.hover_font
        style = 'canvas.TLabel' if e.type == tk.EventType.Leave else 'link.TLabel'
        for child in e.widget.winfo_children():
            child.configure(font=font, style=style)

    def goto_link(self, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        link_parts = e.widget['text'].split(link_sep)
        sect = link_parts[0]
        inst = self.project.get_inst_uuid_by_ind(script=self.current['script'], section=sect, inst_ind=link_parts[1])
        self.resolve_link(sect=sect, inst=inst)

    def resolve_link(self, script=None, sect=None, inst=None, param=None):
        if script is None:
            script = self.current['script']
        if sect is None:
            sect = self.current['section']
        if inst is None:
            inst = self.current['instruction']

        if script != self.current['script']:
            sel_iid = self.trees['script'].get_iid_from_rowdata(script)
            self.trees['script'].see(sel_iid)
            self.trees['script'].focus(sel_iid)
            self.trees['script'].selection_set([sel_iid])
            self.on_select_tree_entry('script', script)
            self.view.after(10, self.resolve_link, None, sect, inst, param)
        elif sect != self.current['section']:
            sel_iid = self.trees['section'].get_iid_from_rowdata(sect)
            self.trees['section'].see(sel_iid)
            self.trees['section'].focus(sel_iid)
            self.trees['section'].selection_set([sel_iid])
            self.on_select_tree_entry('section', sect)
            self.view.after(10, self.resolve_link, None, None, inst, param)
        elif inst != self.current['instruction']:
            sel_iid = self.trees['instruction'].get_iid_from_rowdata(inst)
            self.trees['instruction'].see(sel_iid)
            self.trees['instruction'].focus(sel_iid)
            self.trees['instruction'].selection_set([sel_iid])
            self.on_select_tree_entry('instruction', inst)
            if param is not None:
                self.view.after(10, self.resolve_link, None, None, None, param)
        elif param is not None:
            sel_iid = self.trees['parameter'].get_iid_from_rowdata(param)
            self.trees['parameter'].see(sel_iid)
            self.trees['parameter'].focus(sel_iid)
            self.trees['parameter'].selection_set([sel_iid])

    def clear_inst_details(self):
        self.view.inst_label.config(text='ID - Name')
        self.view.inst_description.config(text='')

        for child in self.view.link_out.scroll_frame.winfo_children():
            child.destroy()

        for child in self.view.link_in.scroll_frame.winfo_children():
            child.destroy()

    def refresh_tree(self, tree_key, keep_selection=False, clear_others=True):
        if len(self.trees[tree_key].get_children('')) == 0:
            return
        open_items = self.trees[tree_key].get_open_elements()
        cur_y_view, _ = self.trees[tree_key].yview()
        kwargs = {'script': self.current['script']} if tree_key != 'script' else {}
        kwargs |= {'section': self.current['section']} if tree_key not in ('script', 'section') else {}
        kwargs |= {'instruction': self.current['instruction']} if tree_key not in ('script', 'section', 'instruction') else {}
        cur_sel = []
        if keep_selection:
            cur_sel = self.trees[tree_key].selection()
        self.update_tree(tree_key, self.project.get_tree(self.view.get_headers(tree_key), **kwargs),
                         clear_other_trees=clear_others)
        self.trees[tree_key].open_tree_elements(open_items)
        self.trees[tree_key].yview_moveto(cur_y_view)
        if keep_selection and len(cur_sel) > 0:
            children = list(self.trees[tree_key].row_data.keys())
            cur_sel = tuple([s for s in cur_sel if s in children])
            self.trees[tree_key].selection_set(cur_sel)

    def refresh_all_trees(self, skip_param_tree=True, keep_selection=True):
        for key in reversed(self.trees.keys()):
            if key == 'parameter' and skip_param_tree:
                continue
            self.refresh_tree(tree_key=key, keep_selection=keep_selection, clear_others=False)

    def check_is_label(self, inst_uuid):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return False
        return self.project.inst_is_label(self.current['script'], self.current['section'], inst_uuid)

    def show_sect_rename_widget(self, tree_key, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return

        column = self.trees[tree_key].identify_column(e.x)

        if tree_key == 'section':
            if '0' not in column:
                return
        else:
            if '1' not in column:
                return

        sel_iid = self.trees[tree_key].identify_row(e.y)

        if tree_key == 'section':
            sect_name = self.trees[tree_key].row_data.get(sel_iid)

            p_num = 1
            parent = self.trees[tree_key].parent(sel_iid)
            while parent is not '':
                p_num += 1
                parent = self.trees[tree_key].parent(sel_iid)
            if e.x < p_num * group_handle_width:
                return

            prefix = ''
        elif tree_key == 'instruction':
            label_label = self.trees[tree_key].item(sel_iid)['values'][0]
            if label_name_sep not in label_label:
                return
            label_parts = label_label.split(label_name_sep)
            sect_name = label_parts[1]
            prefix = label_parts[0]
        else:
            return

        bbox = self.trees[tree_key].bbox(sel_iid, column)
        if tree_key == 'section':
            widget = LabelNameEntry(self.trees[tree_key])
            widget.insert(0, sect_name)
            widget.place(x=bbox[0] + group_handle_width - 4, y=bbox[1], width=bbox[2] - group_handle_width + 4, height=bbox[3])
            self.trees[tree_key].after(10, widget.focus_set)

            widget.bind('<Return>', lambda ev: self.rename_section(ev, widget, None))
            widget.bind('<Escape>', lambda ev: self.delete_entry_widget())
        else:
            widget = ttk.Frame(self.trees[tree_key])
            widget.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            widget.columnconfigure(1, weight=1)

            label = ttk.Label(widget, text=prefix)
            label.grid(row=0, column=0, padx='2 0')
            widget.entry_widget = LabelNameEntry(widget)
            widget.entry_widget.insert(0, sect_name)
            widget.entry_widget.grid(row=0, column=1, sticky=tk.W + tk.E, padx='13 0')
            self.trees[tree_key].after(10, widget.entry_widget.focus_set)

            widget.entry_widget.bind('<Return>', lambda ev: self.rename_section(ev, widget, sel_iid))
            widget.entry_widget.bind('<Escape>', lambda ev: self.delete_entry_widget())

        self.entry_widget = widget

        for tree in self.trees.values():
            tree.unbind_events()

    def rename_section(self, e, widget, sel_iid):
        label_uuid = None
        if sel_iid is not None:
            label_uuid = self.trees['instruction'].row_data.get(sel_iid, None)
            if label_uuid is None:
                return

        new_name = e.widget.get()
        if new_name == self.current['section']:
            return self.delete_entry_widget()

        if self.project.is_sect_name_used(self.current['script'], new_name):
            schedule_tooltip(widget, 'This name is in use', delay=0, min_time=1500, position='above center',
                             is_warning=True)
            return self.shake_widget(widget)

        if new_name == '':
            schedule_tooltip(widget, 'A name is required', delay=0, min_time=1500, position='above center',
                             is_warning=True)
            return self.shake_widget(widget)

        self.delete_entry_widget()

        if sel_iid is not None:
            if new_name == self.trees['instruction'].item(sel_iid)['values'][0].split(label_name_sep)[1]:
                return

        self.project.change_section_name(self.current['script'], self.current['section'], label_uuid, new_name)

        if sel_iid is not None:
            if sel_iid == '0':
                self.current['section'] = new_name
        else:
            self.current['section'] = new_name

        self.refresh_all_trees()

    def shake_widget(self, widget):
        shake_speed = 70
        shake_intensity = 2
        widget_x = widget.winfo_x()
        self.view.after(shake_speed * 1, lambda: widget.place_configure(x=widget_x + shake_intensity))
        self.view.after(shake_speed * 2, lambda: widget.place_configure(x=widget_x - shake_intensity))
        self.view.after(shake_speed * 3, lambda: widget.place_configure(x=widget_x + shake_intensity))
        self.view.after(shake_speed * 4, lambda: widget.place_configure(x=widget_x - shake_intensity))
        self.view.after(shake_speed * 5, lambda: widget.place_configure(x=widget_x))

    # ----------------- #
    # Right Click Menus #
    # ----------------- #

    # # Header Selection # #

    def show_header_selection_menu(self, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        if e.widget.identify('region', e.x, e.y) != 'heading':
            return
        widget_name = e.widget.name
        m = tk.Menu(self.view, tearoff=0)
        m.vars = []
        available_headers = self.view.get_headers(widget_name, get_all=True)
        header_order = self.view.get_header_order(widget_name)
        first = True
        for header in header_order:
            active = int(header in self.view.visible_headers[widget_name])
            name = available_headers[header]['label']
            m.vars.append(tk.IntVar(m, active))
            m.add_checkbutton(label=name, onvalue=1, offvalue=0, variable=m.vars[-1],
                              command=lambda h=header: self.toggle_header(widget_name, h))
            if first:
                m.entryconfigure(name, state='disabled')
                first = False
        m.bind('<Leave>', m.destroy)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def toggle_header(self, tree, header):
        if header not in self.view.visible_headers[tree]:
            self.view.visible_headers[tree].append(header)
            self.view.sort_visible_headers(tree)
        else:
            self.view.visible_headers[tree].remove(header)
        cur_tree = self.trees[tree]
        display_columns = self.view.visible_headers[tree][1:]
        cur_tree['displaycolumns'] = display_columns
        self.view.fit_headers(cur_tree)

    # # Script Options # #

    def show_script_right_click_menu(self, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        if e.widget.identify('region', e.x, e.y) == 'heading':
            return
        sel_iid = self.trees['script'].identify_row(e.y)
        if sel_iid == '':
            return
        self.trees['script'].selection_set(sel_iid)
        self.trees['script'].focus(sel_iid)
        m = tk.Menu(self.view, tearoff=0)

        # add command to remove script from project
        m.add_command(label='Remove script from project', command=self.rcm_del_script)

        m.bind('<Escape>', m.destroy)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def rcm_del_script(self):
        sel_iid = self.trees['script'].focus()
        rowdata = self.trees['script'].row_data[sel_iid]

        self.project.remove_script(rowdata)
        self.refresh_tree('script')

    # # Section Options # #

    def show_section_right_click_menu(self, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        if e.widget.identify('region', e.x, e.y) == 'heading':
            return
        sel_iid = self.trees['section'].identify_row(e.y)
        if sel_iid == '':
            return
        if sel_iid not in self.trees['section'].selection():
            self.trees['section'].selection_set(sel_iid)
            self.trees['section'].focus(sel_iid)

        if len(self.trees['section'].selection()) > 1:
            is_multiple = True
            row_data = [self.trees['section'].row_data.get(s, None) for s in self.trees['section'].selection()]
            is_group = False
        else:
            is_multiple = False
            row_data = self.trees['section'].row_data.get(sel_iid, None)
            is_group = len(self.trees['section'].get_children(sel_iid)) > 0
            self.current['section'] = row_data
        m = tk.Menu(self.view, tearoff=0)

        # commands to add section from project
        if not is_multiple:
            m.add_command(label='Rename Section', command=lambda ev=e: self.show_sect_rename_widget('section', ev))
            m.add_command(label='Add New Section Above', command=lambda: self.rcm_add_sect('above', *row_data))
            m.add_command(label='Add New Section Below', command=lambda: self.rcm_add_sect('below', *row_data))

        # command to remove section from project
        label = 'Delete Section'
        label += 's' if is_multiple else ''
        m.add_command(label=label, command=lambda: self.rcm_del_sect(row_data))

        m.add_separator()

        if is_group and not is_multiple:
            m.add_command(label='Ungroup sections', command=lambda: self.rcm_ungroup_sections(*row_data))

        if is_multiple:
            m.add_command(label='Group sections', command=lambda: self.rcm_group_sections(row_data))

        if not is_multiple:
            m.add_separator()
            m.add_command(label='Open all groups', command=self.trees['section'].open_all_groups)
            m.add_command(label='Close all groups', command=self.trees['section'].close_all_groups)

        m.bind('<Escape>', m.destroy)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def rcm_add_sect(self, direction, relative_section):
        self.project.add_section(self.current['script'], relevant_sect=relative_section, is_above=direction == 'above')
        self.refresh_all_trees(keep_selection=False)
        self.on_select_tree_entry('script', self.current['script'])

    def rcm_del_sect(self, sections):
        if not isinstance(sections, list):
            sections = [sections]
        for s in sections:
            self.project.remove_section(self.current['script'], s)
        self.refresh_all_trees(keep_selection=False)
        self.on_select_tree_entry('script', self.current['script'])

    def rcm_ungroup_sections(self, section):
        self.project.ungroup_section(self.current['script'], section)
        self.refresh_all_trees(keep_selection=False)
        self.on_select_tree_entry('script', self.current['script'])

    def rcm_group_sections(self, sections):
        self.project.group_sections(self.current['script'], section_bounds=(sections[0], sections[-1]))
        self.refresh_all_trees(keep_selection=False)
        self.on_select_tree_entry('script', self.current['script'])

    # # Instruction Options # #

    def show_instruction_right_click_menu(self, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        if e.widget.identify('region', e.x, e.y) == 'heading':
            return
        if self.current['section'] is None:
            return
        sel_iid = self.trees['instruction'].identify_row(e.y)
        if sel_iid == '':
            return
        self.trees['instruction'].selection_set(sel_iid)
        self.trees['instruction'].focus(sel_iid)
        inst_label = self.trees['instruction'].item(sel_iid)['values'][0]
        group_type = ''
        if '(' in inst_label and ')' in inst_label:
            group_type = inst_label.split('(')[1].split(')')[0]
        if group_type == 'case':
            sel_iid = self.trees['instruction'].parent(sel_iid)
        inst_uuid = self.trees['instruction'].row_data[sel_iid]
        self.current['instruction'] = inst_uuid

        parent_is_case = False
        parent_iid = self.trees['instruction'].parent(sel_iid)
        if parent_iid != '':
            if self.trees['instruction'].row_data.get(parent_iid, None) is None:
                parent_is_case = True
        restrictions = self.project.get_inst_rcm_restrictions(parent_is_case=parent_is_case, **self.current)

        m = tk.Menu(self.view, tearoff=0)
        # if rightclicked row is group, add option for "Add Instruction in group"
        if group_type in ('if', 'else', 'while', 'case'):
            m.add_command(label='Add Instruction Inside Group', command=lambda: self.rcm_add_inst('inside'))

        # if rightclicked row is a switch or case, add option for "Add Switch Case"
        if group_type in ('case', 'switch'):
            m.add_command(label='Add Switch Case', command=self.rcm_add_switch_case)

        # if rightclicked row is a case, add option for delete case
        if group_type != 'case':
            if group_type != 'else' and 'first' not in restrictions:
                m.add_command(label='Add Instruction Above', command=lambda: self.rcm_add_inst('above'))

            if 'last' not in restrictions:
                if group_type == 'if':
                    next_sel_iid = self.trees['instruction'].next(sel_iid)
                    if 'else' not in self.trees['instruction'].item(next_sel_iid)['values'][0]:
                        m.add_command(label='Add Instruction Below', command=lambda: self.rcm_add_inst('below'))
                else:
                    m.add_command(label='Add Instruction Below', command=lambda: self.rcm_add_inst('below'))

            m.add_command(label='Remove Instruction', command=self.rcm_remove_inst)
            if restrictions != '':
                m.entryconfig('Remove Instruction', state='disabled')

            if restrictions == '':
                m.add_command(label='Change Instruction', command=self.rcm_change_inst)
        else:
            m.add_command(label='Remove Case', command=self.rcm_remove_switch_case)

        if self.project.inst_is_label(self.current['script'], self.current['section'], self.current['instruction']):
            m.add_command(label='Change Label Section Name', command=lambda: self.show_sect_rename_widget('instruction', e))

        if len(self.trees['instruction'].selection()) < 2:
            m.add_separator()
            m.add_command(label='Open all groups', command=self.trees['instruction'].open_all_groups)
            m.add_command(label='Close all groups', command=self.trees['instruction'].close_all_groups)

        m.bind('<Escape>', m.destroy)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def rcm_add_inst(self, direction):
        sel_iid = self.trees['instruction'].focus()
        pre_rowdata = self.trees['instruction'].row_data[sel_iid]

        # if switch case selected
        case = None
        if pre_rowdata is None:
            parent_sel_iid = self.trees['instruction'].parent(sel_iid)
            parent_rowdata = self.trees['instruction'].row_data[parent_sel_iid]
            pre_rowdata = parent_rowdata

            case = self.trees['instruction'].item(sel_iid)['values'][0]
            case = case.split(' ')[0]

        inst_uuid = self.project.add_inst(self.current['script'], self.current['section'],
                                          pre_rowdata, case=case, direction=direction)
        inst_trace = [self.current['script'], self.current['section'], inst_uuid]
        self.refresh_tree('instruction')

        sel_iid = str(int(sel_iid) + 1) if direction == 'inside' else sel_iid

        sel_iid = self.trees['instruction'].next(sel_iid) if direction == 'below' else sel_iid

        self.trees['instruction'].see(sel_iid)

        self.view.after(10, self.show_inst_selector, inst_trace, sel_iid)

    def show_inst_selector(self, inst_trace, sel_iid):
        callbacks = {
            'is_group': self.project.inst_is_group,
            'get_children': self.project.get_inst_group,
            'group_inst_handler': self.confirm_change_inst_group,
            'set_inst_id': self.project.change_inst,
            'get_relevant': self.project.base_insts.get_relevant,
            'update_tree': self.refresh_all_trees,
            'destroy_widget': self.delete_entry_widget
        }
        cell_bbox = self.trees['instruction'].bbox(sel_iid, 'name')
        x_mod = self.trees['instruction'].winfo_x()
        y_mod = self.trees['instruction'].winfo_y()
        w = InstructionSelectorWidget(self.view.inst_tree_frame, callbacks, inst_trace,
                                      x=cell_bbox[0] + x_mod, y=cell_bbox[1] + y_mod + cell_bbox[3])
        w.bind('<Escape>', lambda event: self.delete_entry_widget())
        w.place(x=cell_bbox[0] + x_mod, y=cell_bbox[1] + y_mod, w=cell_bbox[2], h=cell_bbox[3])
        self.entry_widget = w
        for tree in self.trees.values():
            tree.unbind_events()

    def delete_entry_widget(self):
        self.entry_widget.destroy()
        self.entry_widget = None
        for tree in self.trees.values():
            tree.bind_events()

    def rcm_remove_inst(self):
        sel_iid = self.trees['instruction'].focus()
        cur_inst_uuid = self.trees['instruction'].row_data[sel_iid]
        end_kwargs = {'result': None, 'cur_inst_uuid': cur_inst_uuid}
        if self.project.inst_is_group(**self.current):
            children = self.project.get_inst_group(self.current['script'], self.current['section'], cur_inst_uuid)
            return self.confirm_change_inst_group(children=children, end_callback=self.finish_remove_inst,
                                                  end_kwargs=end_kwargs)
        self.finish_remove_inst(**end_kwargs)

    def finish_remove_inst(self, result, cur_inst_uuid):
        if result is not None:
            if result == 'cancel':
                return
        self.project.remove_inst(self.current['script'], self.current['section'], cur_inst_uuid, result)
        self.refresh_all_trees()

    def rcm_change_inst(self):
        sel_iid = self.trees['instruction'].focus()
        row_data = self.trees['instruction'].row_data[sel_iid]
        inst_trace = [self.current['script'], self.current['section'], row_data]
        self.show_inst_selector(inst_trace, sel_iid)

    def rcm_add_switch_case(self):
        sel_iid = self.trees['instruction'].focus()
        row_data = self.trees['instruction'].row_data[sel_iid]
        if row_data is None:
            row_data = self.trees['instruction'].row_data[self.trees['instruction'].parent(sel_iid)]
        self.project.add_switch_case(self.current['script'], self.current['section'], row_data)
        self.refresh_tree('instruction')

    def rcm_remove_switch_case(self):
        sel_iid = self.trees['instruction'].focus()
        case = self.trees['instruction'].item(sel_iid)['values'][0].split(' ')[0]
        inst = self.trees['instruction'].row_data[self.trees['instruction'].parent(sel_iid)]

        children = self.project.get_inst_group(self.current['script'], self.current['section'], inst)
        children = {case: children[f'{inst}{sep}switch'][case]}
        end_callback = self.finish_remove_switch_case
        end_kwargs = {'instruction': inst, 'case': case, 'result': None}
        warning_suffix = '' if case is None else f'case: ({case})'

        self.confirm_change_inst_group(children=children, end_callback=end_callback, end_kwargs=end_kwargs,
                                       warning_suffix=warning_suffix, new_id=None)

    def finish_remove_switch_case(self, **kwargs):
        if kwargs['result'] == 'cancel':
            return
        self.project.remove_switch_case(script=self.current['script'], section=self.current['section'], **kwargs)
        self.refresh_tree('instruction')

    # -------------------------------------- #
    # Group Change Confirmation Messageboxes #
    # -------------------------------------- #

    def confirm_change_inst_group(self, children, end_callback, end_kwargs, warning_suffix='', new_id=None):
        # Create message to confirm change of instruction (separate method)
        cur_inst_id = self.project.get_inst_id(**self.current)
        new_id = None if new_id is None else int(new_id)

        message = f'Are you sure you want to'

        message += ' change ' if new_id is not None else ' remove '
        message += f'this instruction: {self.project.get_inst_id_name(cur_inst_id)} {warning_suffix}'
        if new_id is not None:
            message += f' to {self.project.get_inst_id_name(new_id)}?'
            message += '\nThis will remove the instruction group.' if new_id not in self.project.base_insts.group_inst_list else '\nThis will change the instruction group type.'

        cancel = not tk.messagebox.askokcancel(title='Confirm Instruction Group Removal', message=message)
        if cancel:
            end_kwargs['result'] = cancel
            return end_callback(**end_kwargs)
        return self.view.inst_group_handling(cur_inst_id, new_id, children, end_callback, end_kwargs)

    def confirm_remove_sect_group(self, children, end_callback, end_kwargs, warning_suffix='', new_id=None):
        pass

    # ------------------------ #
    # Parameter editor methods #
    # ------------------------ #

    def on_edit_parameter(self, paramID):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        paramID = str(paramID)
        self.current['parameter'] = paramID
        param = self.project.get_parameter(**self.current)
        inst_id = self.project.get_inst_id(**self.current)
        base_param = self.project.get_base_parameter(inst_id, paramID)
        if param is None and paramID == 'delay':
            param = self.project.create_delay_parameter()
        end_callback = self.finish_edit_delay_parameter if paramID == 'delay' else None
        end_kwargs = {'param': param} if paramID == 'delay' else None
        self.param_editor.show_param_editor(param=param, base_param=base_param, param_id=paramID,
                                            end_callback=end_callback, end_kwargs=end_kwargs)

    def finish_edit_delay_parameter(self, param):
        if param.value in (0, '0', None, 'None'):
            self.project.remove_delay_parameter(**self.current)
            return
        else:
            self.project.set_delay_parameter(delay_parameter=param, **self.current)

    def get_var_alias(self, var_type, var_id):
        return self.project.get_var_alias(self.current['script'], var_type, var_id)

    def update_var_usage(self, changes):
        self.project.update_var_usage(changes, **self.current)

    # -------------- #
    # View Callbacks #
    # -------------- #

    def update_field(self, field, value):
        self.project.update_inst_field(field=field, value=value, **self.current)

    def on_refresh_inst(self):
        self.project.refresh_condition(**self.current)
        self.on_select_tree_entry('section', self.current['section'])
        self.trees['instruction'].select_by_rowdata(self.current['instruction'])
        self.on_select_tree_entry('instruction', self.current['instruction'])

    def param_right_click_menu(self, row, e):
        if self.entry_widget is not None:
            self.shake_widget(self.entry_widget)
            return
        if not self.project.has_loops(**self.current):
            return
        m = tk.Menu(self.view, tearoff=0)

        param = e.widget.row_data[row]
        if param is None:
            loop_num = int(e.widget.item(row)['text'][4:])
            m.add_command(label='Add Loop Parameter Above',
                          command=lambda: self.handle_loop_param_change('add-above', loop_num=loop_num))
            m.add_command(label='Add Loop Parameter Below',
                          command=lambda: self.handle_loop_param_change('add-below', loop_num=loop_num))
            m.add_command(label='Remove Loop Parameter',
                          command=lambda: self.handle_loop_param_change('remove', loop_num=loop_num))

        if self.project.inst_is_switch(**self.current):
            m.entryconfigure('Add a Loop Parameter Above', state='disabled')
            m.entryconfigure('Add a Loop Parameter Below', state='disabled')
            m.entryconfigure('Remove this Loop Parameter', state='disabled')

            def blank():
                pass

            m.add_command(label='Use Instruction Tree to edit a Switch', command=blank)
        m.bind('<Escape>', m.destroy)
        try:
            m.tk_popup(e.x_root, e.y_root)
        finally:
            m.grab_release()

    def handle_loop_param_change(self, change: Literal['add-above', 'add-below', 'remove'], loop_num=None):
        has_changed = False
        if 'add' in change:
            position = loop_num if 'below' not in change else loop_num + 1
            has_changed = self.project.add_loop_param(**self.current, position=position)
        if change == 'remove':
            has_changed = self.project.remove_loop_param(**self.current, loop_num=loop_num)
        if has_changed:
            self.set_change_flag()
            self.refresh_tree('instruction', keep_selection=True)
            param_tree = self.project.get_parameter_tree(headings=self.view.get_headers('parameter'), **self.current)
            self.update_tree('parameter', param_tree)

    def add_callback(self, key: str, callback: callable):
        self.callbacks[key] = callback

    def on_move_items(self, tree_key, sel_bounds, insert_after, insert_in_group, refresh_only=False):
        section = self.current['section'] if tree_key == 'instruction' else None

        if not refresh_only:
            self.project.move_items(sel_bounds, insert_after, insert_in_group, self.current['script'], section)

        if tree_key == 'section':
            self.trees['instruction'].clear_all_entries()

        self.refresh_all_trees(skip_param_tree=True)

    def check_encoding_errors(self):
        if len(self.encoding_errors) > 0:
            self.view.error_button.grid()
            self.show_error_warning()
        else:
            self.view.error_button.grid_remove()

    def show_error_warning(self):
        message = 'Encoding errors were found.\n\nPlease resolve these for proper script encoding.'
        tk.messagebox.showwarning(title='Confirm Instruction Group Removal', message=message)
