"""
@copyright:
    Copyright (C) Mellanox Technologies Ltd. 2014-2015. ALL RIGHTS RESERVED.

    This software product is a proprietary product of Mellanox Technologies
    Ltd. (the "Company") and all right, title, and interest in and to the
    software product, including all associated intellectual property rights,
    are and shall remain exclusively with the Company.

    This software product is governed by the End User License Agreement
    provided with the software product.

@author: Samer Deeb
@date: Nov 12, 2013
"""

import os
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError, NoSectionError
from os.path import isfile


class ExtendedConfigParserException(Exception):
    pass


class ExtendedConfigParser(ConfigParser):

    """
    This class is used to retrieve configuration values
    from configuration file.
    User should use read() base class API to load configuration file to memory
    and then can get the requested values.
    """

    BASE_DIR = r"../"
    CONF_DIR = r"/conf"

    def __init__(self, logger=None):
        ConfigParser.__init__(self)
        self.logger = logger
        self.conf_files = []

    def read(self, conf_files_names):
        """
        Load configuration files to memory
        """
        normalzied_conf_files = []
        if isinstance(conf_files_names, basestring):
            conf_files_names = [conf_files_names]

        for conf_file_name in conf_files_names:
            conf_file = os.path.normpath(os.path.join(self.BASE_DIR,
                                                      self.CONF_DIR,
                                                      conf_file_name))

            normalzied_conf_files.append(conf_file)

        self.readFullPathFiles(normalzied_conf_files)

    def readFullPathFiles(self, conf_files):

        if isinstance(conf_files, basestring):
            conf_files = [conf_files]

        for conf_file in conf_files:
            if not isfile(conf_file):
                raise ExtendedConfigParserException(
                    "{0} file not found.".format(conf_file))
            self.conf_files.append(conf_file)
        ConfigParser.read(self, self.conf_files)

    def safeGet(self, section, option, default=None):
        """
        Get value of option that belong to specified section -
        if not exist return the default value.
        @param section    section name
        @param option    option name
        @param default    default value
        @raise exception    NoSectionError or NoOptionError if no such section
        or option in configuration file
        @return    option value (string)
        """
        try:
            return self.get(section, option)
        except (NoSectionError, NoOptionError):
            if default is None:
                raise
            else:
                return default

    def safeGetBool(self, section, option, default=None):
        """
        Get boolean value of option that belong to specified section -
        if not exist return the default value.
        @param section    section name
        @param option    option name
        @param default    default value
        @raise exception    NoSectionError or NoOptionError if no such
        section or option in configuration file
        @return    boolean value (True or False)
        """
        try:
            return self.getboolean(section, option)
        except (NoSectionError, NoOptionError, ValueError):
            if default is None:
                raise
            else:
                return default

    def safeGetInt(self, section, option, default=None):
        """
        Get integer value of option that belong to specified section -
        if not exist return the default value.
        @param section    section name
        @param option    option name
        @param default    default value
        @raise exception    NoSectionError or NoOptionError if no such
        section or option in configuration file
        @return    integer value
        """
        try:
            return self.getint(section, option)
        except (NoSectionError, NoOptionError, ValueError):
            if default is None:
                raise
            else:
                return default
