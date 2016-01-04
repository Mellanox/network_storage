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
@date:   Aug 30, 2015
"""


from infra.neo_sdk import NeoSdk
from infra.url import URL
from infra.sdk_parameters import ParamNames


class NeoEventsSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    '/app/events' requests
    """

    GET_ALL_EVENTS = "getall"
    GET_EVENT = "get"
    GET_EVENTS_FOR_SYSTEMS = "getforsys"

    # Descriptions of all the possible events actions
    GET_ALL_EVENTS_DESCRIPTION = "Getting all events data"
    GET_EVENT_DESCRIPTION = "Getting event data"
    GET_EVENTS_FOR_SYSTEMS_DESCRIPTION = "Getting events for systems"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_ALL_EVENTS: GET_ALL_EVENTS_DESCRIPTION,
        GET_EVENT: GET_EVENT_DESCRIPTION,
        GET_EVENTS_FOR_SYSTEMS: GET_EVENTS_FOR_SYSTEMS_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_ALL_EVENTS: [],
        GET_EVENT: [ParamNames.EVENT_ID],
        GET_EVENTS_FOR_SYSTEMS: [ParamNames.SYSTEM_ID]}

    def __init__(self):
        """
        Constructor
        """
        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_ALL_EVENTS: self.__getAllEvents,
            self.GET_EVENT: self.__getEvent,
            self.GET_EVENTS_FOR_SYSTEMS: self.__getEventsForSystems}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_ALL_EVENTS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_EVENT:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_EVENTS_FOR_SYSTEMS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoEventsSdk, self).__init__(URL.EVENTS_URL)

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

    def __getEvent(self, parameters, payload):
        event_id = parameters[ParamNames.EVENT_ID]
        url = self._getRequestURL(event_id)
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllEvents(self, parameters, payload):
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getEventsForSystems(self, parameters, payload):
        systems_ids = parameters[ParamNames.SYSTEM_ID]
        url = "".join([self._action_url, "?object_ids=", systems_ids])
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        '''
        Adding new possible arguments to the argparse object
        that were not added as a default argument.

        '''
        option_help = """
            Actions:
            1)  get - get an existing event.
                --parameters="event_id=value"
            2)  getall - get all events
            3)  getforsys - get all events for a specific list of systems.
                --parameters="system_id=value1,value2"
            """

        self._addOptionArg(parser, option_help, self._getActionOptions())
        self._addParamAndPayloadArgs(parser)

    def _validateArgs(self, action):
        '''
        This method validates that all the needed argument were given,
        and that there aren't any extra arguments
        '''

        self._validateParamAndPayloadArgs(action)

if __name__ == "__main__":
    NeoEventsSdk.main()
