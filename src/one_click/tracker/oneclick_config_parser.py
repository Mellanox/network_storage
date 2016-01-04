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

from extended_config_parser import ExtendedConfigParser
from ConfigParser import NoOptionError, NoSectionError


class OneClickConfigParser(ExtendedConfigParser):

    def __init__(self, logger=None):
        ExtendedConfigParser.__init__(self, logger)

    def safeGetLocalArg(self, section, option, default=None):
        """
        Get a description and a dictionary of values of option that belongs
        to specified section - if not exist return the default value.
        The returned dictionary will be in the following format:
        {
            "<IP1>": "<value1>",
            "<IP2>": "<value2>",
            "<IP3>": "<value3>"
        }
        @param section    section name
        @param option    option name
        @param default    default value
        @raise exception    NoSectionError or NoOptionError if no such
        section or option in configuration file
        @return    description (string) and dictionary of values
        """
        try:
            raw_config_line = self.safeGet(section, option, default)
            splitted_config_line = [element.strip()
                                    for element in raw_config_line.split(",")]
            arg_description = splitted_config_line[-1]
            arg_dict = dict(
                [tuple(element.strip() for element in ip_and_value.split("="))
                 for ip_and_value in splitted_config_line[:-1]])
            return arg_description, arg_dict
        except (NoSectionError, NoOptionError):
            if default is None:
                raise
            else:
                return default

    def safeGetGlobalArg(self, section, option, default=None):
        """
        Get a description and a value of option that belongs
        to specified section - if not exist return the default value.
        @param section    section name
        @param option    option name
        @param default    default value
        @raise exception    NoSectionError or NoOptionError if no such
        section or option in configuration file
        @return    description (string) and value (string)
        """
        try:
            raw_config_line = self.safeGet(section, option, default)
            value, description = [element.strip()
                                  for element in raw_config_line.split(",")]
            return description, value
        except (NoSectionError, NoOptionError):
            if default is None:
                raise
            else:
                return default

    def safeGetListArg(self, section, option, default=None):
        """
        Get a list values of option that belongs
        to specified section - if not exist return the default value.
        @param section    section name
        @param option    option name
        @param default    default value
        @raise exception    NoSectionError or NoOptionError if no such
        section or option in configuration file
        @return    a list of values (strings)
        """
        try:
            raw_config_line = self.safeGet(section, option, default)
            values = [element.strip()
                      for element in raw_config_line.split(",")]
            return values
        except (NoSectionError, NoOptionError):
            if default is None:
                raise
            else:
                return default
