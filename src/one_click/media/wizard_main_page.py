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
    def __init__(self, parent, title, data, page_titles):
        wx.Panel.__init__(self, parent)
        self.title = title
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

        # =========================================================

        switch_ips_sizer = wx.BoxSizer(wx.VERTICAL)
        switch_ips_label = wx.StaticText(
            self, -1, Const.LABEL_SELECTED_SWITCHES)
        switch_ips_sizer.Add(switch_ips_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        choose_ips_sizer = wx.BoxSizer(wx.HORIZONTAL)
        switch_ips_sizer.Add(choose_ips_sizer, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.left_list_box = wx.ListBox(
            self, -1, choices=[],
            style=wx.TE_MULTILINE | wx.TE_READONLY)
        choose_ips_sizer.Add(self.left_list_box, 2, wx.EXPAND | wx.ALL, 5)
        add_remove_sizer = wx.BoxSizer(wx.VERTICAL)
        choose_ips_sizer.Add(add_remove_sizer, 1, wx.EXPAND | wx.ALL, 5)
        switch_ips = [switch_ip.strip() for switch_ip in
                      data[Const.ARG_MAIN_SWITCH_IPS].split(",")]
        self.right_list_box = wx.ListBox(
            self, -1, choices=switch_ips,
            style=wx.TE_MULTILINE | wx.TE_READONLY)
        choose_ips_sizer.Add(self.right_list_box, 2, wx.EXPAND | wx.ALL, 5)

        add_switch_btn = wx.Button(self, label=Const.BTN_LABEL_ADD_SWITCH)
        add_switch_btn.Bind(wx.EVT_BUTTON, self.onAdd)
        add_remove_sizer.Add(add_switch_btn, 0, wx.ALL, 5)
        remove_switch_btn = wx.Button(
            self, label=Const.BTN_LABEL_REMOVE_SWITCH)
        remove_switch_btn.Bind(wx.EVT_BUTTON, self.onRemove)
        add_remove_sizer.Add(remove_switch_btn, 0, wx.ALL, 5)

        sizer.Add(switch_ips_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.left_list_box.Enable(False)
        add_switch_btn.Enable(False)
        remove_switch_btn.Enable(False)

        # =========================================================

        template_list_sizer = wx.BoxSizer(wx.VERTICAL)
        template_list_label = wx.StaticText(
            self, -1, Const.LABEL_TEMPLATE_LIST)
        template_list_sizer.Add(
            template_list_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        template_list_textctrl = wx.TextCtrl(
            self, -1, "",
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.NO_BORDER)
        template_list_textctrl.SetBackgroundColour(Const.BACKGROUND_COLOUR)
        template_list_sizer.Add(template_list_textctrl, 0,
                                wx.ALIGN_LEFT | wx.ALL, 5)
        template_list = ["%d. %s\n" % (template_num, template_name)
                         for template_num, template_name in
                         enumerate(page_titles, 1)]
        for template in template_list:
            template_list_textctrl.AppendText(template)

        sizer.Add(template_list_sizer, 0, wx.EXPAND | wx.ALL, 5)
#         switch_ips_sizer = wx.BoxSizer(wx.VERTICAL)
#         switch_ips_label = wx.StaticText(self, -1, Const.ARG_MAIN_SWITCH_IPS)
#         switch_ips_sizer.Add(switch_ips_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)
#         switch_ips_text_area = wx.TextCtrl(
#             self, -1, data[Const.ARG_MAIN_SWITCH_IPS],
#             style=wx.TE_MULTILINE | wx.TE_READONLY)
#         self.data_pointers[Const.ARG_MAIN_SWITCH_IPS] = switch_ips_text_area
#         switch_ips_sizer.Add(
#             switch_ips_text_area, 0, wx.ALIGN_LEFT | wx.EXPAND | wx.ALL, 5)
#         discover_btn = wx.Button(self, label=Const.BTN_LABEL_DISCOVER)
#         discover_btn.Bind(wx.EVT_BUTTON, self.onDiscover)
#         discover_btn.Disable()
#         switch_ips_sizer.Add(discover_btn, 0, wx.ALL | wx.ALIGN_LEFT, 5)
#         sizer.Add(switch_ips_sizer, 0, wx.EXPAND | wx.ALL, 5)

    def onAdd(self, evt):
        item_to_add = self.left_list_box.GetSelection()
        if item_to_add != wx.NOT_FOUND:
            item_string = self.left_list_box.GetString(item_to_add)
            self.left_list_box.Delete(item_to_add)  # delete the item
            self.right_list_box.Append(item_string)

    def onRemove(self, evt):
        item_to_add = self.right_list_box.GetSelection()
        if item_to_add != wx.NOT_FOUND:
            item_string = self.right_list_box.GetString(item_to_add)
            self.right_list_box.Delete(item_to_add)  # delete the item
            self.left_list_box.Append(item_string)

    def generate_arg(self, sizer, label, default_value):
        arg_label = wx.StaticText(self, -1, Utils.camelcase_text(label))
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

    def get_title(self):
        return self.title

    def get_data(self):
        return self.main_data
