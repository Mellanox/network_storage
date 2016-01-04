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
@date:   Sep 13, 2015
"""

import json
from infra.neo_sdk import NeoSdk
from infra.url import URL
from infra.sdk_parameters import ParamNames
from infra.sdk_exceptions import MissingArgument, BadFileFormat


class NeoEventsPolicySdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    '/app/event_policy' requests
    """

    GET_EVENTS_POLICIES = "get"
    GET_ALL_EVENTS_POLICIES = "getall"
    UPDATE_EVENT_POLICY = "update"

    # Descriptions of all the possible events policy actions
    GET_EVENTS_POLICIES_DESCRIPTION = "Getting events policies data"
    GET_ALL_EVENTS_POLICIES_DESCRIPTION = "Getting all events policies data"
    UPDATE_EVENT_POLICY_DESCRIPTION = "Updating event policy"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_EVENTS_POLICIES: GET_EVENTS_POLICIES_DESCRIPTION,
        GET_ALL_EVENTS_POLICIES: GET_ALL_EVENTS_POLICIES_DESCRIPTION,
        UPDATE_EVENT_POLICY: UPDATE_EVENT_POLICY_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_EVENTS_POLICIES: [ParamNames.EVENT_POLICY_ID],
        GET_ALL_EVENTS_POLICIES: [],
        UPDATE_EVENT_POLICY: [ParamNames.EVENT_POLICY_ID]}

    def __init__(self):

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_EVENTS_POLICIES: self.__getEventPolicy,
            self.GET_ALL_EVENTS_POLICIES: self.__getAllEventsPolicies,
            self.UPDATE_EVENT_POLICY: self.__updateEventPolicy}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_EVENTS_POLICIES:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_EVENTS_POLICIES:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.UPDATE_EVENT_POLICY:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoEventsPolicySdk, self).__init__(URL.EVENT_POLICY_URL)

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

    def __getEventPolicy(self, parameters, payload):
        event_policy_id = parameters[ParamNames.EVENT_POLICY_ID]
        response = self._neo_session.get(self._getRequestURL(event_policy_id))
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllEventsPolicies(self, parameters, payload):
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __updateEventPolicy(self, parameters, payload):
        event_policy_id = parameters[ParamNames.EVENT_POLICY_ID]
        url = self._getRequestURL(event_policy_id)
        payload_file = self._arguments.file
        try:
            json_data = json.load(payload_file)
        except:
            raise BadFileFormat("Couldn't parse your file. Input file should"
                                " be in a json format.\n For more details,"
                                " read the help section")
        finally:
            payload_file.close()
        response = self._neo_session.put(
            url,
            data=json.dumps(json_data),
            headers=self.REQ_HEADER_CONTENT_JSON)

        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1)  get - get an existing event policy.
                --parameters="event_policy_id=value1,value2"
            2)  getall - get all events policies.
            3)  update - update an existing event policy.
                --file="file path"
        """

        file_help = """
            File path for new event policy attributes.
            File should be in the following json format:
            {
                "Category": "Device",
                "SubCategory": "General",
                "ActiveConditions": 1,
                "InstanceID": "event_policy_test_trap_received",
                "EventType": "Test Trap Received",
                "Conditions": [
                    {
                        "Severity": "Info",
                        "InstanceID": "event_condition_test_trap",
                        "Attribute": "Trap ID",
                        "ValueType": "str",
                        "Editable": false,
                        "Value": "",
                        "Operator": "exists",
                        "Trigger": "Test Trap",
                        "Active": true,
                        "Mail": false,
                        "Message": "Updated Message"
                    }
                ]
            }
            Note: When you update an event policy, you shouldn't use
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

        # If the current action is update policy events, check the [--file]
        # argument exists
        if action == self.UPDATE_EVENT_POLICY:
            if self._arguments.file is None:
                raise MissingArgument("Missing argument [-f] [--file]")
        else:
            if self._arguments.file is not None:
                raise MissingArgument("Unsupported argument [-f] [--file]")

if __name__ == "__main__":
    NeoEventsPolicySdk.main()
