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

from oneclick_config_parser import OneClickConfigParser
from one_click.tracker.section_data import SectionData
from one_click.common.constants import Constants as Const
import re


class Tracker(object):

    LOCAL_ARG_REGEX = r"<<([^<>]+)>>"
    GLOBAL_ARG_REGEX = r"<([^<>]+)>"

    def __init__(self, conf_file_path):
        self.parser = OneClickConfigParser()
        self.parser.readFullPathFiles(conf_file_path)
        self.main_data = self.parseMain()
        self.page_titles = self.parsePagesTitles()

        self.page_data = {}
        for page_title in self.page_titles:
            self.page_data[page_title] = self.parsePage(page_title)

#         self.debugMainAttr()
#         self.debugPagesOrder()
#         for page_title, page_data in self.page_data.iteritems():
#             self.debugPageData(page_title, page_data)

    def parseMain(self):
        return {
            Const.ARG_MAIN_NEO_IP:
                self.parser.safeGet(
                    Const.PAGE_TYPE_MAIN, Const.ARG_MAIN_NEO_IP),
            Const.ARG_MAIN_USERNAME:
                self.parser.safeGet(
                    Const.PAGE_TYPE_MAIN, Const.ARG_MAIN_USERNAME),
            Const.ARG_MAIN_PASSWORD:
                self.parser.safeGet(
                    Const.PAGE_TYPE_MAIN, Const.ARG_MAIN_PASSWORD),
            Const.ARG_MAIN_AUTO_DISCOVERY:
                self.parser.safeGetBool(
                    Const.PAGE_TYPE_MAIN, Const.ARG_MAIN_AUTO_DISCOVERY),
            Const.ARG_MAIN_SWITCH_IPS:
                self.parser.safeGetListArg(
                    Const.PAGE_TYPE_MAIN, Const.ARG_MAIN_SWITCH_IPS)
        }

    def debugMainAttr(self):
        print "===> DEBUG : Main Attributes"
        print "%s: %s" % (Const.ARG_MAIN_NEO_IP,
                          self.main_data[Const.ARG_MAIN_NEO_IP])
        print "%s: %s" % (Const.ARG_MAIN_USERNAME,
                          self.main_data[Const.ARG_MAIN_USERNAME])
        print "%s: %s" % (Const.ARG_MAIN_PASSWORD,
                          self.main_data[Const.ARG_MAIN_PASSWORD])
        print "%s: %s" % (Const.ARG_MAIN_AUTO_DISCOVERY,
                          self.main_data[Const.ARG_MAIN_AUTO_DISCOVERY])
        print "%s: %s" % (Const.ARG_MAIN_SWITCH_IPS,
                          str(self.main_data[Const.ARG_MAIN_SWITCH_IPS]))

    def debugPagesOrder(self):
        print "===> DEBUG : Pages Order"
        print self.page_titles

    def debugPageData(self, page_title, page_data):
        print "===> DEBUG : Pages Data on %s" % page_title
        print str(page_data)

    def parsePagesTitles(self):
        attrs = self.parser.options(Const.SECTION_PAGES)
        attrs_by_order = map(str, sorted(map(int, attrs)))
        return [self.parser.safeGet(Const.SECTION_PAGES, attr)
                for attr in attrs_by_order]

    def parsePage(self, page_title):
        page_data = SectionData()
        list_of_args = self.parser.options(page_title)
        for arg in list_of_args:
            local_arg_match_object = re.match(self.LOCAL_ARG_REGEX, arg)
            global_arg_match_object = re.match(self.GLOBAL_ARG_REGEX, arg)
            if local_arg_match_object is not None:
                local_arg_name = local_arg_match_object.group(1)
                local_arg_desc, local_arg_dict = self.parser.safeGetLocalArg(
                    page_title, arg)
                page_data.add_local_arg(
                    local_arg_name, local_arg_dict, local_arg_desc)
            elif global_arg_match_object is not None:
                global_arg_name = global_arg_match_object.group(1)
                global_arg_desc, global_arg_value = \
                    self.parser.safeGetGlobalArg(page_title, arg)
                page_data.add_global_arg(
                    global_arg_name, global_arg_value, global_arg_desc)
            else:
                pass  # handle exception

        return page_data
