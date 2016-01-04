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
from one_click.common.utils import Utils
from one_click.common.constants import Constants as Const
from one_click.action.action_utils import ActionUtiles


class WizardMainPage(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent, title, data):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.main_data = data
        self.data_pointers = deepcopy(data)
        Utils.eraseDictValues(self.data_pointers)

        if title is not None:
            title = wx.StaticText(self, -1, title)
            title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)

        login_sizer = wx.BoxSizer(wx.VERTICAL)
        self.generate_arg(
            login_sizer, Const.ARG_MAIN_NEO_IP, data[Const.ARG_MAIN_NEO_IP])
        self.generate_arg(
            login_sizer, Const.ARG_MAIN_USERNAME,
            data[Const.ARG_MAIN_USERNAME])
        self.generate_arg(
            login_sizer, Const.ARG_MAIN_PASSWORD,
            data[Const.ARG_MAIN_PASSWORD])
        sizer.Add(login_sizer, 0, wx.EXPAND | wx.ALL, 5)

        switch_ips_sizer = wx.BoxSizer(wx.VERTICAL)
        switch_ips_label = wx.StaticText(self, -1, Const.ARG_MAIN_SWITCH_IPS)
        switch_ips_sizer.Add(switch_ips_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        switch_ips_text_area = wx.TextCtrl(
            self, -1, data[Const.ARG_MAIN_SWITCH_IPS],
            style=wx.TE_MULTILINE)
        self.data_pointers[Const.ARG_MAIN_SWITCH_IPS] = switch_ips_text_area
        switch_ips_sizer.Add(
            switch_ips_text_area, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, 5)
        discover_btn = wx.Button(self, label=Const.BTN_LABEL_DISCOVER)
        discover_btn.Bind(wx.EVT_BUTTON, self.onDiscover)
        switch_ips_sizer.Add(discover_btn, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        sizer.Add(switch_ips_sizer, 0, wx.EXPAND | wx.ALL, 5)

    def generate_arg(self, sizer, label, default_value):
        arg_label = wx.StaticText(self, -1, label)
        arg_text = wx.TextCtrl(self, -1, default_value)
        self.data_pointers[label] = arg_text
        arg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        arg_sizer.Add(arg_label, 1, wx.ALIGN_LEFT | wx.ALL, 5)
        arg_sizer.Add(arg_text, 1, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizer.Add(arg_sizer, 0, wx.EXPAND | wx.ALL, 0)

    def onDiscover(self, event):
        self.save()
        neo_ip = self.main_data[Const.ARG_MAIN_NEO_IP]
        username = self.main_data[Const.ARG_MAIN_USERNAME]
        password = self.main_data[Const.ARG_MAIN_PASSWORD]
        ret_val, value = ActionUtiles.discover_systems(
            neo_ip, username, password)
        if ret_val == 0:
            self.data_pointers[Const.ARG_MAIN_SWITCH_IPS].SetValue(
                ", ".join(value))
        else:
            print value

    def save_args_from_ui(self, data_dict, pointers_dict):
        for key, value in pointers_dict.iteritems():
            if value is None:
                continue
            if type(value) == dict:
                self.save_args_from_ui(data_dict[key], pointers_dict[key])
            else:
                data_dict[key] = value.GetValue()

    def save(self):
        self.save_args_from_ui(self.main_data, self.data_pointers)

    def get_data(self):
        return self.main_data
