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
@date:   Dec 6, 2015
"""
import httplib
import urllib
from infra import localTzname


class NeoConnectionError(Exception):
    pass


class NeoConnection(object):
    SESSION_PREFIX = "session="
    REST_VERSION = "1.0.2"

    def __init__(self, username, password, server="localhost", port=80,
                 protocol="http"):
        self._connection = None
        self._username = username
        self._password = password
        self._server = server
        self._protocol = protocol
        self._port = port
        self._session = None
        self._connect()

    def _connect(self):
        if self._protocol == "http":
            self._connection = httplib.HTTPConnection(self._server, self._port)
        else:
            self._connection = httplib.HTTPSConnection(self._server,
                                                       self._port)
        self._connection.connect()

    def _login(self):
        if self._session:
            return True
        url = "/neo/login"
        data = urllib.urlencode({'username': self._username,
                                 'password': self._password})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        self._connection.request("POST", url, data, headers)
        resp = self._connection.getresponse()
        if not resp or resp.status != httplib.OK:
            raise NeoConnectionError(
                "Failed to connect with NEO on '%s'" % self._server)
        cookies = resp.getheader("Set-Cookie")
        cookies = cookies.split(";")
        for cookie in cookies:
            cookie = cookie.strip()
            if cookie and cookie.startswith(self.SESSION_PREFIX):
                self._session = cookie[len(self.SESSION_PREFIX):]
                return True
        raise NeoConnectionError(
            "Failed to connect with NEO on '%s'" % self._server)

    def _updateHeaders(self, headers):
        new_headers = {
            "Cookie": self.SESSION_PREFIX + self._session,
            "Rest-Version": self.REST_VERSION
        }
        new_headers.update(headers)
        return new_headers

    def get(self, url, headers={}):
        self._login()
        if "tz=" not in url:
            url = "%s%stz=%s" % (
                url, '&' if '?' in url else '?', str(localTzname()))
        self._connection.request("GET", url,
                                 headers=self._updateHeaders(headers))
        return self._connection.getresponse()

    def put(self, url, data, headers={}):
        self._login()
        self._connection.request("PUT", url, data,
                                 self._updateHeaders(headers))
        return self._connection.getresponse()

    def delete(self, url, headers={}):
        self._login()
        self._connection.request("DELETE", url,
                                 headers=self._updateHeaders(headers))
        return self._connection.getresponse()

    def post(self, url, data, headers={}):
        self._login()
        self._connection.request("POST", url, data,
                                 self._updateHeaders(headers))
        return self._connection.getresponse()
