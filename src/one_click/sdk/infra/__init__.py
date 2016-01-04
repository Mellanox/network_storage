"""
@copyright:
    Copyright (C) Mellanox Technologies Ltd. 2014-2015. ALL RIGHTS RESERVED.

    This software product is a proprietary product of Mellanox Technologies
    Ltd. (the "Company") and all right, title, and interest in and to the
    software product, including all associated intellectual property rights,
    are and shall remain exclusively with the Company.

    This software product is governed by the End User License Agreement
    provided with the software product.
"""
import time


def localTzname():
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    if is_dst:
        offsetHour = time.altzone / 3600
    else:
        offsetHour = time.timezone / 3600
    return 'Etc/GMT%+d' % offsetHour
