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
from wizard_page import WizardPage
from wizard_main_page import WizardMainPage
from wizard_execution_page import WizardExecutionPage
from one_click.common.constants import Constants as Const
from one_click.action.action_mgr import ActionMngr
from threading import Thread


class WizardPanel(wx.Panel):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)

        self.execution_mgr = ActionMngr(r"data")

        self.pages = []
        self.page_num = 0

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        # add prev/next buttons
        self.prevBtn = wx.Button(self, label=Const.BTN_LABEL_PREV)
        self.prevBtn.Bind(wx.EVT_BUTTON, self.onPrev)
        btnSizer.Add(self.prevBtn, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.prevBtn.Hide()

        self.nextBtn = wx.Button(self, label=Const.BTN_LABEL_NEXT)
        self.nextBtn.Bind(wx.EVT_BUTTON, self.onNext)
        btnSizer.Add(self.nextBtn, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        # finish layout
        self.mainSizer.Add(self.panelSizer, 1, wx.EXPAND)
        self.mainSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT)
        self.SetSizer(self.mainSizer)

    # ----------------------------------------------------------------------
    def addPage(self, title=None, page_data=None, page_type=False):
        """"""

        page_type_to_obj = {
            Const.PAGE_TYPE_MAIN: WizardMainPage,
            Const.PAGE_TYPE_TEMPLATE: WizardPage,
            Const.PAGE_TYPE_EXEC: WizardExecutionPage
        }

        panel = page_type_to_obj[page_type](self, title, page_data)
        self.panelSizer.Add(panel, 2, wx.EXPAND)
        self.pages.append(panel)
        if len(self.pages) > 1:
            # hide all panels after the first one
            panel.Hide()
            self.Layout()

        # If the page we add is a template page, update the execution manager
        if page_type == Const.PAGE_TYPE_TEMPLATE:
            self.execution_mgr.add_template(title)

    # ----------------------------------------------------------------------
    def onNext(self, event):
        """"""

        pageCount = len(self.pages)

        # If we hit "Next" on the first page, we should show the "Previous"
        # button
        if self.page_num == 0:
            self.prevBtn.Show()

        # If we hit "Next" on the page before the last template page, we should
        # change the label of the button to "Run"
        if self.page_num == pageCount - 3:
            self.nextBtn.SetLabel(Const.BTN_LABEL_RUN)

        # If we hit "Next" on the last template page, we should hide the "Next"
        # button and run the execution
        if self.page_num == pageCount - 2:
            self.nextBtn.Hide()
            # TODO Run the templates!

        # Save that data and move to the next page, if not in the execution
        # stage
        if self.page_num != pageCount - 1:
            self.pages[self.page_num].save()
            self.update_exec_mgr()
            self.pages[self.page_num].Hide()
            self.page_num += 1
            self.pages[self.page_num].Show()
            self.panelSizer.Layout()

        # If we hit "Next" on the last template page, we should hide the "Next"
        # button and run the execution
        if self.page_num == pageCount - 1:
            self.nextBtn.Hide()
            self.panelSizer.Layout()
            self.Layout()
            run_thread = Thread(target=self.run_helper)
            run_thread.start()

        self.Layout()

    # ----------------------------------------------------------------------
    def onPrev(self, event):
        """"""

        pageCount = len(self.pages)

        # If we hit "Previous" on the first template page, hide the "Previous"
        # button
        if self.page_num == 1:
            self.prevBtn.Hide()

        # If we hit "Previous" on the last template page, we should change the
        # label of the button to "Next"
        if self.page_num == pageCount - 2:
            self.nextBtn.SetLabel(Const.BTN_LABEL_NEXT)

        # If we hit "Previous" on the execution page, we should show the "Run"
        # button
        if self.page_num == pageCount - 1:
            self.nextBtn.Show()

        # If we hit "Previous" on any page that is not the execution page, we
        # should save the data
        if self.page_num != pageCount - 1:
            self.pages[self.page_num].save()
            self.update_exec_mgr()

        # Show the previous page
        if self.page_num != 0:
            self.pages[self.page_num].Hide()
            self.page_num -= 1
            self.pages[self.page_num].Show()
            self.panelSizer.Layout()

        self.Layout()

    def update_exec_mgr(self):
        if self.page_num == 0:
            self.execution_mgr.update_data(
                self.pages[self.page_num].get_data(), True)
        else:
            self.execution_mgr.update_data(
                self.pages[self.page_num].get_data(), False,
                self.page_num - 1)

    def run_helper(self):
        self.pages[self.page_num].run(self.execution_mgr)
