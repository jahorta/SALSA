from typing import Union, Dict
import tkinter as tk
from tkinter import messagebox

from SALSA.GUI.ProjectEditor.instruction_selector import InstructionSelectorWidget
from SALSA.GUI.ParamEditorPopups.param_editor_controller import ParamEditController
from SALSA.Common.setting_class import settings
from SALSA.GUI.ProjectEditor.project_editor_view import ProjectEditorView
from SALSA.GUI.widgets import DataTreeview
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


class ProjectEditorController:
    log_name = 'PrjEditorCtrl'

    default_settings = {
        'style': 'grouped'
    }

    def __init__(self, parent: tk.Tk, view: ProjectEditorView, facade: SCTProjectFacade, callbacks):
        self.parent: tk.Tk = parent
        self.callbacks = callbacks

        self.view: ProjectEditorView = view
        view_callbacks = {
            'update_field': self.update_field,
            'edit_param': self.on_edit_parameter,
            'show_header_selection_menu': self.show_header_selection_menu,
            'show_inst_menu': self.show_instruction_right_click_menu,
            'save_project': self.save_project
        }
        self.view.add_and_bind_callbacks(view_callbacks)

        self.project: SCTProjectFacade = facade
        self.project.set_callback('confirm_remove_inst_group', self.confirm_change_inst_group)
        self.project.set_callback('toggle_change', self.set_change_flag)

        pe_callbacks = {'get_var_alias': self.get_var_alias,
                        'refresh_inst': self.on_refresh_inst,
                        'update_variables': self.update_var_usage,
                        'get_subscript_list': lambda: self.project.get_section_list(self.current['script']),
                        'set_change': self.set_change_flag,
                        'get_instruction_list': lambda: self.project.get_inst_list(self.current['script'], self.current['section'], self.current['instruction'])}
        self.param_editor = ParamEditController(self.view, callbacks=pe_callbacks)

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
        self.trees['instruction'].add_callback('select', self.on_select_tree_entry)

        self.has_changes = False

    def set_change_flag(self):
        self.has_changes = True
        self.view.save_button.configure(state='normal')

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

    def on_select_tree_entry(self, tree_key, entry):
        self.clear_inst_details()
        if tree_key == 'instruction':
            return self.on_select_instruction(entry)
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
        tree_list = self.adjust_tree_entries(tree_list, child_tree)
        self.update_tree(child_tree, tree_list)

    def adjust_tree_entries(self, entries, key):
        if key == 'instruction':
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                entry['frame_delay_param'] = '*' if entry['frame_delay_param'] != 'None' else ''
                entry['skip_refresh'] = '*' if entry['skip_refresh'] == 'True' else ''

        return entries

    def on_select_instruction(self, instructID):
        self.current['instruction'] = instructID
        self.current['parameter'] = None
        self.view.param_tree.clear_all_entries()
        details = self.project.get_instruction_details(**self.current)
        if details is None:
            return
        details['parameter_tree'] = self.project.get_parameter_tree(headings=self.view.get_headers('parameter'),
                                                                    **self.current)
        self.set_instruction_details(details)

    def update_tree(self, tree, tree_dict: Union[dict, None]):
        if tree is None:
            for tree in self.trees.keys():
                self.trees[tree].clear_all_entries()
            return

        # Clear the current tree and all child trees to prevent desync
        cur_tree = tree
        trees_to_clear = [cur_tree]
        while cur_tree != '':
            trees_to_clear.append(tree_children[cur_tree])
            cur_tree = tree_children[cur_tree]

        for t in trees_to_clear:
            if t != '':
                self.trees[t].clear_all_entries()

        if tree_dict is None:
            return

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
                if first:
                    kwargs['text'] = entry[col]
                    first = False
                else:
                    values.append(entry[col])
                entry.pop(col)
            kwargs['values'] = values
            kwargs = {**kwargs, **entry}
            prev_iid = tree.insert_entry(**kwargs)

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

        self.view.delay_label.config(text=str(details['frame_delay_param']))

        for i, link in enumerate(details['links_out']):
            link: SCTLink
            if link.target_trace is None:
                continue
            tgt_sect = link.target_trace[0]
            tgt_section = tk.Label(self.view.link_out.scroll_frame, text=tgt_sect)
            tgt_section.grid(row=i, column=0)

            tgt_inst = self.project.get_inst_ind(script=self.current['script'], section=tgt_sect,
                                                 inst=link.target_trace[1])
            tgt_instruction = tk.Label(self.view.link_out.scroll_frame, text=tgt_inst)
            tgt_instruction.grid(row=i, column=1)

        for i, link in enumerate(details['links_in']):
            link: SCTLink
            if link.origin_trace is None:
                continue
            ori_sect = link.origin_trace[0]
            ori_section = tk.Label(self.view.link_in.scroll_frame, text=ori_sect)
            ori_section.grid(row=i, column=0)

            ori_inst = self.project.get_inst_ind(script=self.current['script'], section=ori_sect,
                                                 inst=link.origin_trace[1])
            ori_instruction = tk.Label(self.view.link_in.scroll_frame, text=ori_inst)
            ori_instruction.grid(row=i, column=1)

    def clear_inst_details(self):
        self.view.inst_label.config(text='ID - Name')
        self.view.inst_description.config(text='')

        for child in self.view.link_out.scroll_frame.winfo_children():
            child.destroy()

        for child in self.view.link_in.scroll_frame.winfo_children():
            child.destroy()

    def on_set_inst_start(self, start, newID):
        pass

    # ----------------- #
    # Right Click Menus #
    # ----------------- #

    # # Header Selection # #

    def show_header_selection_menu(self, e):
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

    # # Instruction Options # #

    def show_instruction_right_click_menu(self, e):
        if e.widget.identify('region', e.x, e.y) == 'heading':
            return
        if self.current['section'] is None:
            return
        sel_iid = self.trees['instruction'].identify_row(e.y)
        self.trees['instruction'].selection_set(sel_iid)
        self.trees['instruction'].focus(sel_iid)
        inst_uuid = self.trees['instruction'].row_data[sel_iid]
        self.current['instruction'] = inst_uuid
        is_removable = self.project.get_inst_is_removable(**self.current)
        inst_label = self.trees['instruction'].item(sel_iid)['values'][0]
        group_type = ''
        if '(' in inst_label and ')' in inst_label:
            group_type = inst_label.split('(')[1].split(')')[0]
        m = tk.Menu(self.view, tearoff=0)

        # if rightclicked row is group, add option for "Add Instruction in group"
        if group_type in ('if', 'else', 'while', 'case'):
            m.add_command(label='Add Instruction Inside Group', command=lambda: self.rcm_add_inst('inside'))

        # if rightclicked row is a switch or case, add option for "Add Switch Case"
        if group_type in ('case', 'switch'):
            m.add_command(label='Add Switch Case', command=self.rcm_add_switch_case)

        # if rightclicked row is a case, add option for delete case
        if group_type != 'case':
            if group_type != 'else':
                m.add_command(label='Add Instruction Above', command=lambda: self.rcm_add_inst('above'))

            if group_type == 'if':
                next_sel_iid = self.trees['instruction'].next(sel_iid)
                if next_sel_iid != '' and 'else' not in self.trees['instruction'].item(next_sel_iid)['values'][0]:
                    m.add_command(label='Add Instruction Below', command=lambda: self.rcm_add_inst('below'))

            m.add_command(label='Remove Instruction', command=self.rcm_remove_inst)
            if not is_removable:
                m.entryconfig('Remove Instruction', state='disabled')

            m.add_command(label='Change Instruction', command=self.rcm_change_inst)
        else:
            m.add_command(label='Delete Case', command=self.rcm_remove_inst)

        m.bind('<Leave>', m.destroy)
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

        inst_uuid = self.project.add_inst(self.current['script'], self.current['section'], pre_rowdata, case=case, direction=direction)
        inst_trace = [self.current['script'], self.current['section'], inst_uuid]
        self.update_tree('instruction', self.project.get_tree(self.view.get_headers('instruction'),
                                                              self.current['script'], self.current['section']))

        sel_iid = str(int(sel_iid) + 1) if direction == 'inside' else sel_iid

        sel_iid = self.trees['instruction'].next(sel_iid) if direction == 'below' else sel_iid

        self.trees['instruction'].see(sel_iid)

        self.view.after(10, self.show_inst_selector, inst_trace, sel_iid)

    def show_inst_selector(self, inst_trace, sel_iid):
        callbacks = {
            'set_inst_id': self.project.change_inst,
            'get_relevant': self.project.base_insts.get_relevant,
            'update_tree': lambda: self.update_tree('instruction', self.project.get_tree(
                self.view.get_headers('instruction'), self.current['script'], self.current['section']))
        }
        cell_bbox = self.trees['instruction'].bbox(sel_iid, 'name')
        x_mod = self.trees['instruction'].winfo_x()
        y_mod = self.trees['instruction'].winfo_y()
        w = InstructionSelectorWidget(self.view.inst_tree_frame, callbacks, inst_trace,
                                      x=cell_bbox[0]+x_mod, y=cell_bbox[1]+y_mod+cell_bbox[3])
        w.bind('<Escape>', w.destroy)
        w.place(x=cell_bbox[0]+x_mod, y=cell_bbox[1]+y_mod, w=cell_bbox[2], h=cell_bbox[3])

    def rcm_remove_inst(self):
        sel_iid = self.trees['instruction'].focus()
        cur_inst_uuid = self.trees['instruction'].row_data[sel_iid]
        self.project.remove_inst(self.current['script'], self.current['section'], cur_inst_uuid)
        self.update_tree('instruction', self.project.get_tree(self.view.get_headers('instruction'), **self.current))

    def rcm_change_inst(self):
        sel_iid = self.trees['instruction'].focus()
        row_data = self.trees['instruction'].row_data[sel_iid]
        inst_trace = [self.current['script'], self.current['section'], row_data]
        self.show_inst_selector(inst_trace, sel_iid)

    def rcm_add_switch_case(self):
        sel_iid = self.trees['instruction'].focus()
        row_data = self.trees['instruction'].row_data[sel_iid]
        # TODO - implement adding a switch case

    # ------------------------------------- #
    # Instruction Confirmation Messageboxes #
    # ------------------------------------- #

    def confirm_change_inst_group(self, children, new_id=None):
        # Create message to confirm change of instruction (separate method)
        cur_inst_id = self.project.get_inst_id(**self.current)

        message = f'Are you sure you want to'

        if new_id is not None:
            message += ' change '
        else:
            message += ' remove '
        message += f'this instruction: {self.project.get_inst_id_name(cur_inst_id)}'
        if new_id is not None:
            message += f' to {self.project.get_inst_id_name(new_id)}?'

            if new_id not in self.project.base_insts.group_inst_list:
                message += '\nThis will remove the instruction group.'
            else:
                message += '\nThis will change the instruction group type.'

        cancel = not tk.messagebox.askokcancel(title='Confirm Instruction Group Removal', message=message)
        if cancel:
            return 'cancel'
        return self.view.inst_group_handling(cur_inst_id, new_id, children)

    # ------------------------ #
    # Parameter editor methods #
    # ------------------------ #

    def on_edit_parameter(self, paramID):
        paramID = str(paramID)
        self.current['parameter'] = paramID
        param = self.project.get_parameter(**self.current)
        inst_id = self.project.get_inst_id(**self.current)
        base_param = self.project.get_base_parameter(inst_id, paramID)
        if param is None and paramID == 'delay':
            param = self.project.add_delay_parameter(**self.current)
        self.param_editor.show_param_editor(param=param, base_param=base_param)

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
        cur_inst_id = self.current['instruction']
        self.on_select_tree_entry('section', self.current['section'])
        self.trees['instruction'].select_by_rowdata(cur_inst_id)
        self.on_select_tree_entry('instruction', cur_inst_id)
