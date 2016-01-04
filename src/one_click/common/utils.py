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


class Utils(object):
    """
    """

    def __init__(self):
        pass

    @staticmethod
    def eraseDictValues(dictionary):
        for key, value in dictionary.iteritems():
            if type(value) == dict:
                Utils.eraseDictValues(value)
            else:
                dictionary[key] = None
