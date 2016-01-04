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


@summary:
    This SDK Retrieves And Displays Data from NEO Various REST APIs. User
    Must Specify REST API Name (Systems, Groups, ... etc.) in Command Line.

    In This Version, The Following REST APIs Are Supported:
    1- Groups
    2- Users
    3- Systems
    4- Ports
    5- Jobs
    6- Events
    7- Tasks
    8- Logs

    Usage:
        ./neo_get_data.py --server <NEO SERVER> --username <USER NAME>
        --password <USER PASSWORD> --protocol <http | https>
        --option <REST API NAME>

    Example:
        ./neo_get_data.py -s 10.0.0.1 -u admin -p 123456 -r https -o systems

@author: Muthanna Nairat
"""
import sys
import argparse
import pprint
from infra.neo_connection import NeoConnection
import json

# ===================== CLASSES SECTION =========================


# This Class Contains NEO URLs For Each
# REST API Which Can Be Accessed In This SDK
class RestAPI(object):

    NEO_BASE_URL = "/neo"
    GROUPS = "/resources/groups"
    SYSTEMS = "/resources/systems"
    USERS = "/app/users"
    PORTS = "/resources/ports"
    JOBS = "/app/jobs"
    EVENTS = "/app/events"
    TASKS = "/app/tasks"
    LOGS = "/app/logs"

    # This Dictionary Maps Command Line Arguments
    # With REST API URL for corresponding interface
    INTERFACE_MAPPER = {
        "groups": GROUPS,
        "users": USERS,
        "systems": SYSTEMS,
        "ports": PORTS,
        "jobs": JOBS,
        "events": EVENTS,
        "tasks": TASKS,
        "logs": LOGS
    }

    @classmethod
    def getUrl(cls, option):
        '''
        @summary:
            This method will generate REST API URL for the specified
            option.

        @param option:
            Takes one option from RestAPI.INTERFACE_MAPPER.
        '''
        # Setting NEO IP Address in Base URL
        base_url = cls.NEO_BASE_URL
        return base_url + RestAPI.INTERFACE_MAPPER[option]


class Converter(object):

    def __init__(self, data):
        self.data = data

    def convert(self):
        '''
        @summary:
            Converts object data format from unicode
            to utf-8. object can be list or dictionary.

        @param data:
            dictionray of unicode data

        @return:
            Converted Data (list or dictionary)
        '''
        if isinstance(self.data, list):
            return self._convertList(self.data)
        elif isinstance(self.data, dict):
            return self._convertDictionary(self.data)

    def _convertList(self, data):
        '''
        @summary:
            Converts List data Format from
            unicode to utf-8

        @param data:
            list of unicode data

        @return:
            Converted list
        '''
        converted_list = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._convertList(item)
            elif isinstance(item, dict):
                item = self._convertDictionary(item)
            converted_list.append(item)
        return converted_list

    def _convertDictionary(self, data):
        '''
        @summary:
            Converts dictionary data Format from
            unicode to utf-8. This function will
            convert format for both Keys and Values

        @param list_to_convert:
            dictionray of unicode data

        @return:
            Converted Dictionary
        '''
        converted_data = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._convertList(value)
            elif isinstance(value, dict):
                value = self._convertDictionary(value)
            converted_data[key] = value
        return converted_data

# ==================== END OF CLASSES SECTION ===================


# ====================== FUNCTIONS SECTION ======================

def parseArgs():
    '''
    @summary:
        this method parses SDK command line
        arguments
    '''
    # Parsing Script Arguments Entered By User
    parser = argparse.ArgumentParser()

    connection = parser.add_argument_group('connection')
    connection.add_argument("-s", "--server", action="store",
                            required=True, default=None,
                            help="NEO server IP address")
    connection.add_argument("-u", "--username", action="store",
                            required=True, default=None,
                            help="NEO user name")
    connection.add_argument("-p", "--password", action="store",
                            required=True, default=None,
                            help="NEO user password")
    connection.add_argument("-r", "--protocol", action="store", required=False,
                            default="http", choices=['http', 'https'],
                            help="Protocol (http or https)")

    req_arg = parser.add_argument_group('request arguments')
    req_arg.add_argument("-o", "--option", action="store", required=True,
                         choices=['groups',
                                  'users',
                                  'systems',
                                  'jobs',
                                  'ports',
                                  'tasks',
                                  'events',
                                  'logs'],
                         default=None,
                         help="Specify which REST API data to retrieve")

    arguments = parser.parse_args()

    # Making Sure User Entered All Required Arguments in Command Line
    if not arguments.server:
        print(" - ERROR - Must Specify NEO Server [-s] [--server]")
        sys.exit(1)

    if not arguments.option:
        print(" - ERROR - Must Specify Option [-o] [--option]")
        sys.exit(1)

    if not arguments.username:
        print(" - ERROR - Must Specify User Name [-u] [--username]")
        sys.exit(1)

    if not arguments.password:
        print(" - ERROR - Must Specify Password [-p] [--password]")
        sys.exit(1)

    return arguments


def execute(arguments):
    '''
    @summary: Main Execution Method
    '''
    print("-" * 70)
    print("[*] Running settings:")
    print(" -> NEO server: " + arguments.server)
    print(" -> Protocol: " + arguments.protocol)
    print(" -> NEO user name: " + arguments.username)
    print(" -> Selected REST API: " + arguments.option)

    # Initializing The Specified REST API URL
    RestAPI_url = RestAPI.getUrl(arguments. option)

    # Starting NEO Session
    print("-" * 70)
    print("[*] Execution Stages:")
    print(" -1- Starting NEO Session...")
    neo_session = NeoConnection(arguments.username,
                                arguments.password,
                                arguments.server,
                                port=80,
                                protocol=arguments.protocol)

    # Sending Request to Access Specified NEO Interface
    print(" -2- Reading Data From REST API: " + RestAPI_url)
    response = neo_session.get(RestAPI_url)
    res_data = json.loads(response.read())
    # Encoding Result Data to utf-8
    data_converter = Converter(res_data)
    encoded_result = data_converter.convert()

    # Displaying Result Data
    print("-" * 70)
    print("[*] Output:")
    pprint.pprint(encoded_result)
    print("-" * 70)

# =================== END OF FUNCTIONS SECTION ==================


if __name__ == "__main__":
    args = parseArgs()
    execute(args)
