"""
@copyright:
    Copyright (C) Mellanox Technologies Ltd. 2014-2015. ALL RIGHTS RESERVED.

    This software product is a proprietary product of Mellanox Technologies
    Ltd. (the "Company") and all right, title, and interest in and to the
    software product, including all associated intellectual property rights,
    are and shall remain exclusively with the Company.

    This software product is governed by the End User License Agreement
    provided with the software product.

@author: Shachar Langer
@date:   Dec 30, 2015
"""

import wx
from copy import deepcopy
from one_click.common.constants import Constants as Const
from one_click.common.utils import Utils


class WizardPage(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, title=None, page_data=None, page_titles=None):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        self.title = title
        self.page_pointers = deepcopy(page_data)
        self.page_pointers.eraseValues()
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        if title is not None:
            title = wx.StaticText(self, -1, title)
            title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)

        self.page_data = page_data
        if self.page_data is not None:
            arg_sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(arg_sizer, 0, wx.EXPAND | wx.ALL, 5)

            global_static_box = wx.StaticBox(self, -1, Const.BOX_TITLE_GLOBAL)
            global_arg_sizer = wx.StaticBoxSizer(
                global_static_box, wx.VERTICAL)
            arg_sizer.Add(global_arg_sizer, 1, wx.EXPAND | wx.ALL, 5)

            local_static_box = wx.StaticBox(self, -1, Const.BOX_TITLE_LOCAL)
            local_arg_sizer = wx.StaticBoxSizer(local_static_box, wx.VERTICAL)
            arg_sizer.Add(local_arg_sizer, 1, wx.EXPAND | wx.ALL, 5)

            global_args = self.page_data.global_args
            for arg_name in global_args:
                self.generate_arg(self, global_arg_sizer, arg_name, True)

            self.local_args_panels = {}
            self.current_panel = None
            switch_ips = self.page_data.local_args.keys()
            self.ips_combobox = wx.ComboBox(
                self, -1, choices=switch_ips, style=wx.CB_READONLY)
            local_arg_sizer.Add(
                self.ips_combobox, 0, wx.ALIGN_CENTER | wx.ALL, 5)

            for switch_ip in switch_ips:
                arg_panel = wx.Panel(self)
                temp_sizer = wx.BoxSizer(wx.VERTICAL)
                arg_panel.SetSizer(temp_sizer)
                arg_panel.Hide()
                # sizer.SetScrollbar(wx.VERTICAL)
                local_arg_sizer.Add(arg_panel, 0, wx.EXPAND | wx.ALL, 5)
                self.local_args_panels[switch_ip] = arg_panel
                local_args = self.page_data.local_args.get(switch_ip)

                for arg_name in local_args:
                    self.generate_arg(
                        arg_panel, temp_sizer, arg_name, False, switch_ip)

            self.ips_combobox.Bind(wx.EVT_COMBOBOX, self.OnSelect)

    def OnSelect(self, event):
        switch_ip = self.ips_combobox.GetValue()
        if self.current_panel is not None:
            self.current_panel.Hide()
        self.current_panel = self.local_args_panels[switch_ip]
        self.current_panel.Show()
        self.Layout()

    def generate_arg(self, parent_panel, sizer, label, is_global,
                     switch_ip=None):
        arg_label = wx.StaticText(parent_panel, -1,
                                  Utils.camelcase_text(label))
        default_value = self.page_data.get_global_arg(
            label) if is_global else self.page_data.get_local_arg(label,
                                                                  switch_ip)
        arg_text = wx.TextCtrl(parent_panel, -1, default_value)

        arg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        arg_sizer.Add(arg_label, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        arg_sizer.Add(arg_text, 1, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizer.Add(arg_sizer, 0, wx.EXPAND | wx.ALL, 0)

        if is_global:
            self.page_pointers.update_global_arg(label, arg_text)
        else:
            self.page_pointers.update_local_arg(label, arg_text, switch_ip)

    def save_args_from_ui(self, data_dict, pointers_dict):
        for key, value in pointers_dict.iteritems():
            if type(value) == dict:
                self.save_args_from_ui(data_dict[key], pointers_dict[key])
            else:
                data_dict[key] = value.GetValue()

    def save(self):
        self.save_args_from_ui(
            self.page_data.global_args, self.page_pointers.global_args)
        self.save_args_from_ui(
            self.page_data.local_args, self.page_pointers.local_args)

    def get_title(self):
        return self.title

    def get_data(self):
        return self.page_data
