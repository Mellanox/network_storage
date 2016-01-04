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

import re


class Utils(object):
    """
    """

    PROVISIONING_SUMMARY_REGEX = r'"Summary": "(.*)"'
    PROVISIONING_STATUS_CODE_REGEX = r"HTTP response status code: (.*)"
    PROVISIONING_STATUS_REGEX = r'"Status": "(.*)"'

    @staticmethod
    def eraseDictValues(dictionary):
        for key, value in dictionary.iteritems():
            if type(value) == dict:
                Utils.eraseDictValues(value)
            else:
                dictionary[key] = None

    @classmethod
    def parse_summary(cls, data):
        summaries = re.findall(cls.PROVISIONING_SUMMARY_REGEX, data)
        return [raw_summary.replace("\\n", "\n").replace("\\t", "\t")
                for raw_summary in summaries]

    @classmethod
    def parse_status_code(cls, data):
        match = re.search(cls.PROVISIONING_STATUS_CODE_REGEX, data)
        return None if match is None else match.group(1).strip()

    @classmethod
    def parse_status(cls, data):
        return re.findall(cls.PROVISIONING_STATUS_REGEX, data)
