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
@date:   Aug 24, 2015
"""

import re
from time import sleep
import json
import argparse
from argparse import FileType
import textwrap
import copy
import sys
from os.path import basename
from url import URL
from sdk_exceptions import ActionNotSupported, MissingParam, MissingArgument
from sdk_exceptions import PayloadBadFormat, ParamBadFormat, InvalidParam
from sdk_exceptions import BadFileFormat
from sdk_print import SDKPrint
from neo_connection import NeoConnection


class NeoSdk(object):

    REQ_HEADER_CONTENT_JSON = {"Content-Type": "application/json"}

    PAYLOAD_DELIMITER = "&"
    PARAM_DELIMITER = "&"
    LIST_DELIMITER = ","

    PAYLOAD_REGEX_ARG = "^([^&=]+=[^&=\[\]]+)(&[^&=]+=[^&=\[\]]+)*$"
    PAYLOAD_REGEX_LIST = "^[^=]+=\[[^,=]+(,[^,=]+)*\]$"
    PAYLOAD_REGEX = "%s|%s" % (PAYLOAD_REGEX_ARG, PAYLOAD_REGEX_LIST)
    PARAM_REGEX = "^([^&=]+=[^&=]+)(&[^&=]+=[^&=]+)*$"
    ARG_FORMAT = 0
    LIST_FORMAT = 1

    PARAM_ARG_NEEDED = True
    PARAM_ARG_NOT_NEEDED = False
    PAYLOAD_ARG_NEEDED = True
    PAYLOAD_ARG_NOT_NEEDED = False

    SHOULD_PRINT_RESPONSE = True
    SHOULD_NOT_PRINT_RESPONSE = False

    # Relevant to running tasks - The time (in seconds) between each
    # measurement of a job status
    SLEEP_INTERVALS = 1

    # Relevant to running tasks - The time (in seconds) we should check
    # if the job was completed.
    NUM_OF_SLEEP_INTERVALS = 300

    def __init__(self, url):
        """
        Constructor
        """

        self._arguments = None

        # Parsing the arguments and inserting them to 'self._arguments'
        self._parseArgs()

        # Setting the base url
#         self._base_url = URL.getBaseURL(self._arguments.protocol,
#                                         self._arguments.server)
        self._base_url = "/neo"

        self._action_url = self._base_url + url

        # Login to NEO
        self._neo_session = NeoConnection(self._arguments.username,
                                          self._arguments.password,
                                          self._arguments.server,
                                          port=80,
                                          protocol=self._arguments.protocol)

        self._action_parameters = self._getActionOptions()

    def _getRequestURL(self, url_path):
        return "/".join((self._action_url, url_path))

    @classmethod
    def _castAttributes(cls, input_data, attr_conversion_mapping):
        """
        Convert the values of a given dictionary ('input_data')
        to the type specified in 'attr_conversion_mapping'
        """

        # Deep copying the original dictionary.
        # We don't want to change the original dictionary.
        result = copy.deepcopy(input_data)

        conversion_table = {
            bool: json.loads,
            int: int
        }

        for attrib in attr_conversion_mapping:

            # If the attribute from the 'type dictionary'
            # exists in the given dictionary, change its type
            if attrib in input_data:
                new_type = attr_conversion_mapping[attrib]
                old_value = input_data[attrib]
                new_value = None

                # if the new type is unknown, throw an exception
                if new_type not in conversion_table:
                    raise TypeError("Unsupported type %s" % str(new_type))

                # Convert the attribute to the new type
                try:
                    new_value = conversion_table[new_type](old_value.lower())
                except:
                    raise TypeError("Couldn't read '%s'. '%s' should "
                                    "be of type %s" %
                                    (old_value, old_value, new_type))

                result[attrib] = new_value

        return result

    def _convertInputFileToJSON(self):
        payload_file = self._arguments.file
        try:
            json_data = json.load(payload_file)
        except:
            raise BadFileFormat("Couldn't parse your file. Input file should"
                                " be in a json format.\n For more details,"
                                " read the help section")
        finally:
            payload_file.close()
        return json_data

    # =====================================================================
    #                    Dictionary getters
    # =====================================================================

    def _getActionToDescription(self):
        raise NotImplementedError("'_getActionToDescription' is not "
                                  "implemented")

    def _getActionToExpectedParams(self):
        raise NotImplementedError("'_getActionToExpectedParams' is not "
                                  "implemented")

    def _getActionToFunction(self):
        raise NotImplementedError("'_getActionToFunction' is not "
                                  "implemented")

    def _getActionToNeededArgs(self):
        raise NotImplementedError("'_getActionToFunction' is not "
                                  "implemented")

    # =====================================================================
    #                    Arguments Functions
    # =====================================================================

    def _getActionOptions(self):
        '''
        Returns a list of all the possible action
        choices for the current session.

        This is an abstract method that is implemented by the derived classes.
        '''
        return {}

    def _validateArgs(self, action):
        '''
        Validate that all expected arguments were given.

        This is an abstract method that is implemented by the derived classes.
        '''
        pass

    def _addOptionArg(self, parser, option_help, choices, arg_required=True):
        '''
        Add the 'Option' argument to the command line parser.
        '''

        req_arg = parser.add_argument_group('request arguments')

        req_arg.add_argument("-o", "--option", action="store",
                             required=arg_required, default=None,
                             choices=choices,
                             help=textwrap.dedent(option_help))

    def _addBlockingArg(self, parser):
        parser.add_argument("-b", "--blocking", action="store_true",
                            required=False, default=False,
                            help="Blocks any action while running a task")

    def _addFileArg(self, parser, file_help):
        parser.add_argument("-f", "--file", action="store",
                            required=False, default=None,
                            type=FileType(),
                            help=textwrap.dedent(file_help))

    def _getParamAndPayloadStatus(self, action):
        needed_args = self._getActionToNeededArgs().get(action)
        if not needed_args:
            raise ActionNotSupported("Option '%s' is not supported. "
                                     "Couldn't find it in "
                                     "'_getActionToExpectedParams'" % action)

        return needed_args

    def _validateParamAndPayloadArgs(self, action):
        '''
        Check if 'Parameters' and 'Payload' arguments
        exists or not (as needed).
        '''
        param_needed, payload_needed = self._getParamAndPayloadStatus(action)

        param_exists = self._arguments.parameters is not None
        if param_needed != param_exists:
            arg_state = "Missing" if param_needed else "Unsupported"
            raise MissingArgument("%s argument [-t] [--parameters]" %
                                  arg_state)

        payload_exists = self._arguments.payload is not None
        if payload_needed != payload_exists:
            arg_state = "Missing" if payload_needed else "Unsupported"
            raise MissingArgument("%s argument [-d] [--payload]" %
                                  arg_state)

    def _addParamAndPayloadArgs(self, parser):
        '''
        Adding 'Parameters' and 'Payload' arguments as needed
        '''

        req_data = parser.add_argument_group('request data')

        req_data.add_argument("-d", "--payload", action="store",
                              required=False, default=None,
                              help=textwrap.dedent("""
                                Payload attributes. Valid format:
                                attrib1=value1&attrib2=value2"""))

        req_data.add_argument("-t", "--parameters", action="store",
                              required=False, default=None,
                              help=textwrap.dedent("""
                                URL parameters. Valid formats:
                                1) attrib1=value1&attrib2=value2
                                2) attrib=[value1,value2]
                                """))

    def _addDefaultArgs(self, parser):
        '''
        Add default argument to the command line parser.
        '''

        connection = parser.add_argument_group('connection')
        connection.add_argument("-s", "--server", action="store",
                                required=True, default=None, choices=None,
                                help="NEO server IP address")
        connection.add_argument("-u", "--username", action="store",
                                required=True, default=None, choices=None,
                                help="NEO user name")
        connection.add_argument("-p", "--password", action="store",
                                required=True, default=None, choices=None,
                                help="NEO password")
        connection.add_argument("-r", "--protocol", action="store",
                                default="http", required=False,
                                choices=["http", "https"],
                                help="Protocol (http or https)")

    def _addSessionArgs(self, parser):
        '''
        Adding new possible arguments to the argparse object
        that were not added as a default argument.

        This is an abstract method that is implemented by the derived classes.
        '''
        pass

    def _parseArgs(self):
        '''
        This method parses SDK command line arguments
        '''

        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter)
        self._addDefaultArgs(parser)
        self._addSessionArgs(parser)
        self._arguments = parser.parse_args()
        self._validateArgs(self._arguments.option)

    # =====================================================================
    #                    Parameters Functions
    # =====================================================================

    @classmethod
    def _validateParamExistence(cls, parameters, expected_params):

        # Check that all given parameters are expected
        for param in parameters:
            if param not in expected_params:
                raise InvalidParam("Parameter '%s' is not supported" % param)

        # Check that all expected parameters were given
        for param in expected_params:
            if param not in parameters:
                raise MissingParam("Missing parameter '%s'" % param)

    def _validateParamsFormat(self):
        parameters = self._arguments.parameters
        result = re.match(self.PARAM_REGEX, parameters)

        if result is None:
            raise ParamBadFormat("Bad format. Valid parameter format is: "
                                 "attrib1=value1&attrib2=value2\n")

    def _getParamsAsDict(self):
        '''
        Convert the raw string parameters to a dictionary
        '''
        parmeters = self._arguments.parameters

        return dict([tuple(item.split('=')) for item in
                     parmeters.split(self.PARAM_DELIMITER)])

    # =====================================================================
    #                    Payload Functions
    # =====================================================================

    def _validatePayloadFormat(self):
        payload = self._arguments.payload
        result = re.match(self.PAYLOAD_REGEX, payload)

        if result is None:
            raise PayloadBadFormat("Bad format. Valid payload formats are:\n"
                                   "1) attrib1=value1&attrib2=value2\n"
                                   "2) attrib=[value1,value2]")

        # The payload has 2 possible formats. Return the correct one.
        return self.ARG_FORMAT if result.group(1) \
            is not None else self.LIST_FORMAT

    def _getPayloadAsJson(self, payload_format):
        '''
        Convert the raw payload string to a json
        '''

        payload = self._arguments.payload

        if (payload_format == self.ARG_FORMAT):
            # payload format is "attrib1=value1&attrib2=value2
            return json.dumps(dict([tuple(item.split('=')) for item in
                                    payload.split(self.PAYLOAD_DELIMITER)]))
        else:
            # payload format is "attrib=[value1,value2]"
            raw_list = payload.split('=')[1]
            return json.dumps([item for item in
                               raw_list[1:-1].split(self.LIST_DELIMITER)])

    # =====================================================================
    #                    Execution
    # =====================================================================

    def _validateJob(self, response):

        # Get the id of the job that was created as
        # a result of running the task
        job_id_regex = r"%s/(\d+)" % URL.JOBS_URL
        job_id = re.search(job_id_regex, response.read()).group(1)

        print("[*] Running job %s" % job_id)

        job_status = "Running"
        counter = 0
        while job_status not in ("Completed", "Aborted", "Canceled",
                                 "Completed With Errors") and\
                counter < self.NUM_OF_SLEEP_INTERVALS:
            job_id_res = self._neo_session.get(
                "%s%s/%s" % (self._base_url,
                             URL.JOBS_URL,
                             job_id))
            job_status = json.loads(job_id_res.read())["Status"]
            sleep(self.SLEEP_INTERVALS)
            counter += 1

        job_id_res = self._neo_session.get(
            "%s%s/%s" % (self._base_url,
                         URL.JOBS_URL,
                         job_id))
                         
        sub_jobs_id_res = self._neo_session.get(
            "%s%s?parent_id=%s" % (self._base_url,
                                   URL.JOBS_URL,
                                   job_id))

        job_res = job_id_res.read()
        sub_jobs_res = sub_jobs_id_res.read()
                         
        if job_status == "Completed":
            print("[*] Job completed successfully")
            print("[*] Job response:")
            print(job_res)
            print("[*] Sub Jobs response:")
            print(sub_jobs_res)
        elif counter < self.NUM_OF_SLEEP_INTERVALS:
            print("[*] Job failed. Current status: %s" % job_status)
            print("[*] Job response:")
            print(job_res)
            print("[*] Sub Jobs response:")
            print(sub_jobs_res)
        else:
            print("[*] Couldn't verify job status. It's taking too long.")
            print("[*] Please validate manually the job's status")
            
    def execute(self):
        action = self._arguments.option

        action_description = self._getActionToDescription().get(action)
        if action_description is None:
            raise ActionNotSupported("Option '%s' is not supported. "
                                     "Couldn't find it in "
                                     "'_getActionToDescription'" % action)

        SDKPrint.printHeader(action_description, self._arguments.server,
                             self._arguments.username)

        print("[*] %s stages:" % action_description)
        print(" -1- Setting Up data...")

        param_needed, payload_needed = self._getParamAndPayloadStatus(action)

        parameters = None
        payload = None

        # If the param is not needed, it wasn't added to the argparse,
        # and therefore there's nothing to parse
        if param_needed:
            raw_parameters = self._arguments.parameters
            expected_params = self._getActionToExpectedParams().get(action)
            if expected_params is None:
                raise ActionNotSupported("Option '%s' is not supported. "
                                         "Couldn't find it in "
                                         "'_getActionToExpectedParams'" %
                                         action)

            # if parameters were given, validate and parse them.
            if raw_parameters is not None:
                self._validateParamsFormat()
                parameters = self._getParamsAsDict()
                self._validateParamExistence(parameters, expected_params)
            # if no parameters were given, but there are expected parameters,
            # raise an error
            elif expected_params:
                raise MissingParam("You didn't specify required parameters. "
                                   "To see the list of required parameters, "
                                   "use the [-h] flag.")

        # If the payload is not needed, it wasn't added to the argparse,
        # and therefore there's nothing to parse
        if payload_needed:
            raw_payload = self._arguments.payload

            # if a payload was given, validate and parse it.
            if raw_payload is not None:
                payload_format = self._validatePayloadFormat()
                payload = self._getPayloadAsJson(payload_format)

        print(" -2- Sending %s request..." % action_description)

        action_function = self._getActionToFunction().get(action)

        if action_function is None:
            raise ActionNotSupported("Option '%s' is not supported. "
                                     "Couldn't find it in "
                                     "'_getActionToFunction'" % action)

        # Send the request to NEO
        res, show_res = action_function(parameters, payload)

        SDKPrint.printResponse(action_description, res.status, res.read(),
                               show_res)

    @classmethod
    def main(cls):
        try:
            neoSdkInstance = cls()
            neoSdkInstance.execute()
        except Exception as exc:
            print "-E- Got an error while running %s: %s" % (
                basename(sys.argv[0]), str(exc))
            sys.exit(1)
