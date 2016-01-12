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
from wizard_panel import WizardPanel
from one_click.tracker.tracker import Tracker
from one_click.common.constants import Constants as Const
from ConfigParser import ConfigParser
from os import getcwd


CONF_FILE_PATH = r"conf/configuration_file.cfg"


class MainFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(
            self, None, title=Const.WIZARD_TITLE, size=(800, 600))
        self.SetBackgroundColour(Const.BACKGROUND_COLOUR)

        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        import_conf = file_menu.Append(wx.NewId(), "Import",
                                       "Import configuration from a file")
        self.Bind(wx.EVT_MENU, self.import_configuration_file, import_conf)
#         import_conf.Enable(Falsel)
        export = file_menu.Append(wx.NewId(), "Export",
                                  "Export configurations to a file")
        self.Bind(wx.EVT_MENU, self.export_configuration_file, export)
        file_menu.AppendSeparator()
        exit_app = file_menu.Append(wx.NewId(), "Exit",
                                    "Exit the wizard")
        self.Bind(wx.EVT_MENU, self.exit_wizard, exit_app)
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        self.init_frame(CONF_FILE_PATH)

    def init_frame(self, conf_file_path):
        self.tr = Tracker(conf_file_path)
        self.panel = WizardPanel(self)
        self.sizer.Add(self.panel, 1, wx.EXPAND, 0)
        page_titles = self.tr.page_titles
        self.panel.addPage(
            Const.PAGE_TITLE_MAIN, self.tr.main_data, Const.PAGE_TYPE_MAIN,
            page_titles)

        for index in xrange(len(page_titles)):
            page_title = page_titles[index]
            self.panel.addPage(
                page_title, self.tr.page_data[page_title],
                Const.PAGE_TYPE_TEMPLATE, page_titles)
        self.panel.addPage(
            Const.PAGE_TITLE_EXEC, None, Const.PAGE_TYPE_EXEC, page_titles)
        self.Layout()
        self.Show()

    def exit_wizard(self, evt):
        sys.exit()

    def import_configuration_file(self, evt):

        openFileDialog = wx.FileDialog(
            self, "Import configuration file", r"%s/conf" % getcwd(),
            "", "configuration files (*.cfg)|*.cfg",
            wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return

        self.sizer.Remove(0)
        self.panel.Destroy()
        self.init_frame(openFileDialog.GetPath())

    def export_configuration_file(self, evt):

        # If the current page we are in is not the last page, save it content
        # before exporting it.
        if self.panel.page_num < len(self.panel.pages):
            self.panel.pages[self.panel.page_num].save()

        current_conf = self.generate_conf(self.panel.pages)

        saveFileDialog = wx.FileDialog(self, "Export configuration file",
                                       r"%s/conf" % getcwd(), "",
                                       "configuration files (*.cfg)|*.cfg",
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            return

        with open(saveFileDialog.GetPath(), "w") as output_file:
            current_conf.write(output_file)

    def generate_conf_main(self, conf_parser, main_data):
        conf_parser.add_section(Const.SECTION_MAIN)
        for key, val in main_data.iteritems():
            conf_parser.set(Const.SECTION_MAIN, key, val)

    def generate_conf_pages(self, conf_parser, template_names):
        conf_parser.add_section(Const.SECTION_PAGES)
        for index, template_name in enumerate(template_names, 1):
            conf_parser.set(Const.SECTION_PAGES, str(index), template_name)

    def generate_conf_template(self, conf_parser, template_name,
                               template_data):
        conf_parser.add_section(template_name)
        desc_dict = template_data.arg_to_description
        local_args_dict = {}
        for key, val in template_data.global_args.iteritems():
            desc = "" if key not in desc_dict else desc_dict[key]
            conf_parser.set(template_name, "<%s>" % key, "%s,%s" % (val, desc))
        for ip, arg_val_dict in template_data.local_args.iteritems():
            for arg_name, val in arg_val_dict.iteritems():
                if arg_name not in local_args_dict:
                    local_args_dict[arg_name] = ["%s=%s" % (ip, val)]
                else:
                    local_args_dict[arg_name].append("%s=%s" % (ip, val))
        for key, val in local_args_dict.iteritems():
            desc = "" if key not in desc_dict else desc_dict[key]
            conf_parser.set(template_name, "<<%s>>" %
                            key, "%s,%s" % (", ".join(val), desc))

    def generate_conf(self, pages):
        conf_parser = ConfigParser()
        main_page = pages[0]
        template_pages = pages[1:-1]

        main_data = main_page.get_data()
        self.generate_conf_main(conf_parser, main_data)

        template_names = [
            template_page.get_title() for template_page in template_pages]
        self.generate_conf_pages(conf_parser, template_names)

        for tp in template_pages:
            template_name = tp.get_title()
            template_data = tp.get_data()
            self.generate_conf_template(
                conf_parser, template_name, template_data)
#             conf_parser += "\n".join(
#                 [self.generate_conf_template(tp.get_title(), tp.get_data())
#                  for tp in template_pages])

        return conf_parser
