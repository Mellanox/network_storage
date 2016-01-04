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
@date:   Dec 3, 2015
"""

from tzlocal import get_localzone


class NeoSessions(object):

    REST_VERSION = '1.0.2'

    def __init__(self, session):
        self.session = session

    def _updateVersion(self, headers):
        headers.update({'Rest-Version': self.REST_VERSION})

    def get(self, url, data=None, headers={}):

        # Adding TimeZone to url
        if "tz=" not in url:
            url = "%s%stz=%s" % (
                url, '&' if '?' in url else '?', str(get_localzone()))

        self._updateVersion(headers)
        return self.session.get(url, data=data, headers=headers)

    def put(self, url, data=None, headers={}):
        self._updateVersion(headers)
        return self.session.put(url, data=data, headers=headers)

    def post(self, url, data=None, headers={}):
        self._updateVersion(headers)
        return self.session.post(url, data=data, headers=headers)

    def delete(self, url, data=None, headers={}):
        self._updateVersion(headers)
        return self.session.delete(url, data=data, headers=headers)
