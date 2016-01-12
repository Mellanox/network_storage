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
from wx import richtext as rt
from time import clock
from one_click.common.utils import Utils
from one_click.common.constants import Constants as Const


class WizardExecutionPage(wx.Panel):
    """"""

    MAX_GAUGE_VALUE = 100
    GAUGE_INIT_VALUE = 2
    SUCCESS = 0

    # ----------------------------------------------------------------------
    def __init__(self, parent, title, data, page_titles):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizerAndFit(sizer)

        if title is not None:
            title = wx.StaticText(self, -1, title)
            title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
            sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
            sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)

#         log__style = wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL | \
#             wx.HSCROLL | wx.NO_BORDER
#         self.log_text_area = rt.RichTextCtrl(
#             self, -1, "",
#             style=log__style)
        self.log_text_area = wx.TextCtrl(
            self, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        log_text_area_font = wx.Font(10, wx.FONTFAMILY_MODERN,
                                     wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        # font underline, font face, encoding)
        self.log_text_area.SetFont(log_text_area_font)
        sizer.Add(self.log_text_area, 1, wx.EXPAND | wx.ALL, 5)

        self.gauge = wx.Gauge(self, wx.ID_ANY, self.MAX_GAUGE_VALUE)
        sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 5)

    def _increment_gauge(self, delta):
        current_value = self.gauge.GetValue()
        self.gauge.SetValue(current_value + delta)

    def _console_output(self, data, color=None):
        if color is None:
            self.log_text_area.AppendText("%s\n" % data)
        else:
            self.log_text_area.SetDefaultStyle(
                wx.TextAttr(color, wx.WHITE))
            self.log_text_area.AppendText("%s\n" % data)
            self.log_text_area.SetDefaultStyle(
                wx.TextAttr(wx.BLACK, wx.WHITE))

    def run(self, execution_mgr):
        execution_mgr.analyze_data()
        all_provisioning_results = []
        gauge_delta = self.MAX_GAUGE_VALUE / \
            float(execution_mgr.get_num_of_templates())
        self._increment_gauge(self.GAUGE_INIT_VALUE)
        start_run = clock()
        while execution_mgr.has_next():
            template_name = execution_mgr.get_latest_template_name()
            self._console_output("---> Running template '%s'" % template_name)
            ret_val, output, error, exec_time = \
                execution_mgr.run_next_template()
            if ret_val == self.SUCCESS:
                status_code = Utils.parse_status_code(output)
                if status_code != "202":
                    self._console_output(
                        "ERROR: Provisioning job was not created successfully."
                        " Status code returned - %s\n" % status_code,
                        Const.TEXT_COLOUR_ERROR)
                    execution_mgr.clean()
                    sys.exit(1)
                self._increment_gauge(gauge_delta)
                headlines = [("->Summary output for %s:\n" % ip)
                             for ip in execution_mgr.get_switch_ips()]
                summaries = [summary for summary in Utils.parse_summary(output)
                             if summary != ""]
                self._console_output("\n".join(
                    ["\n".join([headline, summary])
                     for headline, summary in zip(headlines, summaries)]))
                statuses = Utils.parse_status(output)
                not_completed_statuses = filter(
                    lambda x: x.strip() != "Completed", statuses)
                if len(not_completed_statuses) != 0:
                    all_provisioning_results.append((template_name, False))
                    self._console_output(
                        "ERROR: provisioning job %s\n" %
                        not_completed_statuses[0].lower(),
                        Const.TEXT_COLOUR_ERROR)
                else:
                    all_provisioning_results.append((template_name, True))
                    self._console_output(
                        "-> Completed successfully."
                        " Total executing time %.4f\n" % exec_time)
            else:
                self._console_output("ERROR: Couldn't connect to NEO\n",
                                     Const.TEXT_COLOUR_ERROR)
                execution_mgr.clean()
                sys.exit(1)
        end_run = clock()

        self._console_output("*** Status Summary ***\n")
        self._console_output("%-15s %s" % ("Template", "Status"))
        self._console_output("%-15s %-10s" % ("-" * 15, "-" * 10))
        for template, finished_successfully in all_provisioning_results:
            result, color = ("Completed", Const.TEXT_COLOUR_SUCCESS) \
                if finished_successfully \
                else ("Failed", Const.TEXT_COLOUR_ERROR)
            self._console_output("%-15s %s" % (template, result), color)

        finished_without_error = all(
            [result for _, finished_successfully in all_provisioning_results])
        self._console_output(
            "\n>>> Configuration completed %s errors. Total time: %.4f" %
            ("without" if finished_without_error else "with",
             (end_run - start_run)))

        execution_mgr.clean()
