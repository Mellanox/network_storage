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
@date:   Aug 25, 2015
"""


class MissingArgument(Exception):
    pass


class ActionNotSupported(Exception):
    pass


class InvalidArgument(Exception):
    pass


class BadFileFormat(Exception):
    pass


class PayloadBadFormat(Exception):
    pass


class FileNotReadable(Exception):
    pass


# ===================================================================
#                Parameter Exceptions
# ===================================================================


class ParamBadFormat(Exception):
    pass


class InvalidParam(Exception):
    pass


class MissingParam(Exception):
    pass
