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
@date:   Oct 11, 2015
"""

import json
from infra.sdk_exceptions import MissingArgument, BadFileFormat
from infra.url import URL
from infra.neo_sdk import NeoSdk


class NeoSWUpgradeSDK(NeoSdk):
    """
    This class represents a NEO session that specifically handles SW upgrade
    requests
    """

    UPGRADE_SOFTWARE = "upgrade"

    # Descriptions of all the possible sSW upgrade actions
    UPGRADE_SOFTWARE_DESCRIPTION = "Upgrading software"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        UPGRADE_SOFTWARE: UPGRADE_SOFTWARE_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        UPGRADE_SOFTWARE: []}

    def __init__(self):
        """
        Constructor
        """

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.UPGRADE_SOFTWARE: self._upgradeSoftware}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.UPGRADE_SOFTWARE:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoSWUpgradeSDK, self).__init__(URL.SW_UPGRADE_URL)

    def _getActionToDescription(self):
        return self.ACTION_TO_DESCRIPTION

    def _getActionToExpectedParams(self):
        return self.ACTION_TO_EXPECTED_PARAMS

    def _getActionToFunction(self):
        return self.ACTION_TO_FUNCTION

    def _getActionToNeededArgs(self):
        return self.ACTION_TO_NEEDED_ARGS

    def _getActionOptions(self):
        '''
        Returns a list of all the possible action
        choices for the current session.
        '''

        return self._getActionToDescription()

    def _upgradeSoftware(self, parameters, payload):
        """
        Upgrading software. The request payload is read from a file
        argument given by the user.
        """
        payload_file = self._arguments.file
        try:
            json_data = json.load(payload_file)
        except:
            raise BadFileFormat("Couldn't parse your file. Input file should"
                                " be in a json format.\n For more details,"
                                " read the help section")
        finally:
            payload_file.close()
        response = self._neo_session.post(
            self._action_url,
            data=json.dumps(json_data),
            headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1) upgrade - upgrade software.
                --file="file path"
        """

        file_help = """
            File path for software upgrade attributes.
            File should be in the following json format:
            {
                "action":"sw_upgrade",
                "params":
                {
                    "description":"",
                    "protocol":"scp",
                    "server":"<host_name>",
                    "path":"<image_path>",
                    "image":"<selected_image>",
                    "username":"<username>",
                    "password":"<password>"
                },
                "object_ids":["<system_IP>"],
                "description":""
            }
            Note: When you do a software upgrade, you shouldn't use
            the [--payload] argument.
            """

        self._addOptionArg(parser, option_help, self._getActionOptions())
        self._addParamAndPayloadArgs(parser)
        self._addFileArg(parser, file_help)

    def _validateArgs(self, action):
        '''
        This method validates that all the needed argument were given,
        and that there aren't any extra arguments
        '''

        self._validateParamAndPayloadArgs(action)

        # If the current action is upgrade (SW upgrade), validate that the
        # [--file] argument exists. Otherwise, if the current action is not
        # upgrade, validate that the [--file] argument doesn't exist.
        if action == self.UPGRADE_SOFTWARE:
            if self._arguments.file is None:
                raise MissingArgument("Missing argument [-f] [--file]")
        else:
            if self._arguments.file is not None:
                raise MissingArgument("Unsupported argument [-f] [--file]")

if __name__ == "__main__":
    NeoSWUpgradeSDK.main()
