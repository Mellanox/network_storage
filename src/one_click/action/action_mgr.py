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
@date:   Dec 31, 2015
"""

from action_utils import ActionUtiles
from one_click.common.constants import Constants as Const
from time import clock
import uuid
import json
import os


class ActionMngr(object):
    """
    """

    def __init__(self, data_path):
        """
        Constructor
        """

        self.template_list = []

        self.templates_data = {}

        self.main_data = None

        self.current_template_index = -1

        self.data_path = data_path

    def add_template(self, template_name):
        self.template_list.append(template_name)

    def update_data(self, data, is_main, template_index=-1):
        if is_main:
            self.main_data = data
        else:
            template_name = self.template_list[template_index]
            self.templates_data[template_name] = data

    def _create_payload_file(self, template_data, switch_ips):
        payload = {
            "params": {
                "arguments": {
                    "globals": template_data.global_args,
                    "devices": template_data.local_args
                }
            },
            "object_ids": [ip.strip() for ip in switch_ips.split(',')],
            "object_type": "System"
        }
        file_path = r"%s\%s" % (self.data_path, str(uuid.uuid4()))
        with open(file_path, "w+") as payload_file:
            json.dump(payload, payload_file, indent=4)
        return file_path

    def _construct_cmd(self, template_name, payload_file_path,
                       neo_ip, username, password):
        return ['python',
                r'%s\neo_provisioning.py' % ActionUtiles.SDK_LOCATION,
                '-s', neo_ip,
                '-u', username,
                '-p', password,
                '-o', 'execute',
                '-t', 'template_name=%s' % template_name,
                '-f', r"%s" % payload_file_path,
                '-b']

    def _generate_template_cmds(self):
        template_cmds = []

        neo_ip = self.main_data[Const.ARG_MAIN_NEO_IP]
        username = self.main_data[Const.ARG_MAIN_USERNAME]
        password = self.main_data[Const.ARG_MAIN_PASSWORD]
        switch_ips = self.main_data[Const.ARG_MAIN_SWITCH_IPS]

        for template_name in self.template_list:
            template_data = self.templates_data[template_name]
            payload_file_path = self._create_payload_file(template_data,
                                                          switch_ips)
            template_cmd = self._construct_cmd(
                template_name, payload_file_path, neo_ip, username, password)
            template_cmds.append(template_cmd)

        return template_cmds

    def analyze_data(self):
        self.template_cmds = self._generate_template_cmds()

    def has_next(self):
        return self.current_template_index < (len(self.template_list) - 1)

    def run_next_template(self):
        self.current_template_index += 1
        cmd = self.template_cmds[self.current_template_index]
        start = clock()
        ret_val, output, error = ActionUtiles.exec_timeout(cmd)
        end = clock()
        return ret_val, output, error, end - start

    def get_num_of_templates(self):
        return len(self.template_list)

    def get_switch_ips(self):
        return [ip.strip()
                for ip in self.main_data[Const.ARG_MAIN_SWITCH_IPS].split(',')]

    def get_latest_template_name(self):
        return self.template_list[self.current_template_index + 1]

    def clean(self):
        for file_name in os.listdir(self.data_path):
            file_path = os.path.join(self.data_path, file_name)
            try:
                os.unlink(file_path)
            except Exception, e:
                print e
