#! /usr/bin/python -u
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
@date:   Aug 23, 2015
"""


class headerDesgin(object):

    SEPERATOR_LENGTH = 70
    SEPERATOR = '='

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(self.SEPERATOR * self.SEPERATOR_LENGTH)
        self.func(*args, **kwargs)
        print(self.SEPERATOR * self.SEPERATOR_LENGTH)


class SDKPrint(object):
    """
    This class contains common SDK printing functions
    """

    SEPERATOR_LENGTH = 70
    SEPERATOR = '-'
    SUCCESS_CODES = set(xrange(200, 205))

    @classmethod
    @headerDesgin
    def printHeader(cls, action, server, username):

        # Displaying the action and login details
        print("<<< NEO - %s SDK >>>" % action)
        print(cls.SEPERATOR * cls.SEPERATOR_LENGTH)
        print("[*] Running Settings:")
        print(" -> NEO server IP address: %s" % server)
        print(" -> NEO user name: %s" % username)

    @classmethod
    @headerDesgin
    def printResponse(cls, action, status_code, text,
                      should_print_response=False):

        # Displaying the response to the User
        print("[*] %s results:" % action)
        print(">> %s request HTTP response status code: %d"
              % (action, status_code))
        if status_code not in cls.SUCCESS_CODES or should_print_response:
            print(">> %s request HTTP response text:\n%s" % (action, text))
