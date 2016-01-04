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
from wizard_panel import WizardPanel
from one_click.tracker.tracker import Tracker
from one_click.common.constants import Constants as Const

CONF_FILE_PATH = r"conf/configuration_file.cfg"

# http://www.blog.pythonlibrary.org/2012/07/12/wxpython-how-to-create-a-generic-wizard/


class MainFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(
            self, None, title=Const.WIZARD_TITLE, size=(800, 600))
        tr = Tracker(CONF_FILE_PATH)
        self.panel = WizardPanel(self)
        self.panel.addPage(
            Const.PAGE_TITLE_MAIN, tr.main_data, Const.PAGE_TYPE_MAIN)

        page_titles = tr.page_titles
        for index in xrange(len(page_titles)):
            page_title = page_titles[index]
            self.panel.addPage(
                page_title, tr.page_data[page_title], Const.PAGE_TYPE_TEMPLATE)
        self.panel.addPage(Const.PAGE_TITLE_EXEC, None, Const.PAGE_TYPE_EXEC)

        self.Show()
