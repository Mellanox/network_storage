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
import sys
import re
from time import clock


class WizardExecutionPage(wx.Panel):
    """"""

    MAX_GAUGE_VALUE = 100
    GAUGE_INIT_VALUE = 2
    PROVISIONING_SUMMARY_REGEX = r'"Summary": "(.*)"'
    PROVISIONING_STATUS_CODE_REGEX = r"HTTP response status code: (.*)"
    PROVISIONING_STATUS_REGEX = r'"Status": "(.*)"'
    SUCCESS = 0

    # ----------------------------------------------------------------------
    def __init__(self, parent, title, data):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizerAndFit(sizer)

        if title is not None:
            title = wx.StaticText(self, -1, title)
            title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)

        self.log_text_area = wx.TextCtrl(
            self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.log_text_area, 1, wx.EXPAND | wx.ALL, 5)
        self.gauge = wx.Gauge(self, wx.ID_ANY, self.MAX_GAUGE_VALUE)
        sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 5)

    def _increment_gauge(self, delta):
        current_value = self.gauge.GetValue()
        self.gauge.SetValue(current_value + delta)

    def _parse_summary(self, data):
        summaries = re.findall(self.PROVISIONING_SUMMARY_REGEX, data)
        return [raw_summary.replace("\\n", "\n").replace("\\t", "\t")
                for raw_summary in summaries]

    def _parse_status_code(self, data):
        match = re.search(self.PROVISIONING_STATUS_CODE_REGEX, data)
        return None if match is None else match.group(1).strip()

    def _parse_status(self, data):
        return re.findall(self.PROVISIONING_STATUS_REGEX, data)

    def _console_output(self, data):
        self.log_text_area.AppendText("%s\n" % data)

    def run(self, execution_mgr):
        execution_mgr.analyze_data()
        all_provisioning_passed = True
        gauge_delta = self.MAX_GAUGE_VALUE / \
            float(execution_mgr.get_num_of_templates())
        self._increment_gauge(self.GAUGE_INIT_VALUE)
        start_run = clock()
        while execution_mgr.has_next():
            self._console_output("---> Running template '%s'" %
                                 execution_mgr.get_latest_template_name())
            ret_val, output, error, exec_time = \
                execution_mgr.run_next_template()
            if ret_val == self.SUCCESS:
                status_code = self._parse_status_code(output)
                if status_code != "202":
                    self._console_output(
                        "ERROR: Provisioning job was not created successfully."
                        " Status code returned - %s\n" % status_code)
                    execution_mgr.clean()
                    sys.exit(1)
                self._increment_gauge(gauge_delta)
                self._console_output("\n".join(self._parse_summary(output)))
                statuses = self._parse_status(output)
                not_completed_statuses = filter(
                    lambda x: x.strip() != "Completed", statuses)
                if len(not_completed_statuses) != 0:
                    all_provisioning_passed = False
                    self._console_output(
                        "ERROR: provisioning job %s\n" %
                        not_completed_statuses[0].lower())
                else:
                    self._console_output(
                        "-> Completed successfully."
                        " Total executing time %.4f\n" % exec_time)
            else:
                self._console_output("ERROR: Couldn't connect to NEO\n")
                # l TODO - print an informative error Message
                execution_mgr.clean()
                sys.exit(1)
        end_run = clock()
        self._console_output(
            ">>> Configuration completed %s errors. Total time: %.4f" %
            ("without" if all_provisioning_passed else "with",
             (end_run - start_run)))

        execution_mgr.clean()
