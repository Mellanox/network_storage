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


class Constants(object):
    """
    """

    SECTION_MAIN = "main"
    SECTION_PAGES = "pages"

    ARG_TYPE_GLOBAL = "globals"
    ARG_TYPE_LOCALS = "locals"
    ARG_TYPE_DESCRIPTIONS = "arg_to_desc"

    ARG_MAIN_NEO_IP = "neo_ip"
    ARG_MAIN_USERNAME = "username"
    ARG_MAIN_PASSWORD = "password"
    ARG_MAIN_AUTO_DISCOVERY = "auto_discovery"
    ARG_MAIN_SWITCH_IPS = "switch_ips"

    BTN_LABEL_NEXT = "Next"
    BTN_LABEL_PREV = "Previous"
    BTN_LABEL_RUN = "Run"
    BTN_LABEL_DISCOVER = "Discover"

    PAGE_TYPE_MAIN = "main"
    PAGE_TYPE_TEMPLATE = "template"
    PAGE_TYPE_EXEC = "execution"

    PAGE_TITLE_MAIN = "NEO Wizard"
    PAGE_TITLE_EXEC = "Execution Status"

    WIZARD_TITLE = "Generic Wizard"

    BOX_TITLE_GLOBAL = "Global Arguments"
    BOX_TITLE_LOCAL = "Local Arguments"
