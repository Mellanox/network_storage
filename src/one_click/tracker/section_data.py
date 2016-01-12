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

import json
from one_click.common.utils import Utils
from one_click.common.constants import Constants as Const


class SectionData(object):

    def __init__(self):
        self.global_args = {}
        self.local_args = {}
        self.arg_to_description = {}

    def add_global_arg(self, arg_name, value, description):
        self.global_args[arg_name] = value
        self.arg_to_description[arg_name] = description

    def add_local_arg(self, arg_name, ip_to_value_dict, description):
        for switch_ip in ip_to_value_dict:
            if self.local_args.get(switch_ip) is None:
                self.local_args[switch_ip] = {}
            self.local_args[switch_ip][arg_name] = ip_to_value_dict[switch_ip]
        self.arg_to_description[arg_name] = description

    def get_global_arg(self, arg_name):
        return self.global_args[arg_name]

    def get_local_arg(self, arg_name, ip=None):
        return self.local_args[arg_name] if ip is None \
            else self.local_args[ip][arg_name]

    def update_global_arg(self, arg_name, value):
        if arg_name in self.global_args:
            self.global_args[arg_name] = value
        # raise an error

    def update_local_arg(self, arg_name, value, ip):
        if ip in self.local_args:
            if arg_name in self.local_args[ip]:
                self.local_args[ip][arg_name] = value
        # raise an error

    def eraseValues(self):
        Utils.eraseDictValues(self.global_args)
        Utils.eraseDictValues(self.local_args)

    def has_args(self):
        return len(self.global_args) != 0 or \
            sum([len(val) for val in self.local_args.values()]) != 0

    def __str__(self):
        result = {
            Const.ARG_TYPE_GLOBAL: self.global_args,
            Const.ARG_TYPE_LOCALS: self.local_args,
            Const.ARG_TYPE_DESCRIPTIONS: self.arg_to_description
        }
        return json.dumps(result, indent=4)
