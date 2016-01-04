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
@date:   Sep 20, 2015
"""

from infra.neo_sdk import NeoSdk
from infra.sdk_exceptions import InvalidParam
from infra.url import URL
from infra.sdk_parameters import ParamNames


class NeoMonitorSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    'app/monitoring' requests
    """

    GET_MONITORING_DATA = "get"
    GET_ALL_MONITORING_DATA = "getall"

    # Descriptions of all the possible monitoring data actions
    GET_MONITORING_DATA_DESCRIPTION = "Getting monitoring data"
    GET_ALL_MONITORING_DATA_DESCRIPTION = "Getting all monitoring data"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_MONITORING_DATA: GET_MONITORING_DATA_DESCRIPTION,
        GET_ALL_MONITORING_DATA: GET_ALL_MONITORING_DATA_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_MONITORING_DATA: [ParamNames.DEVICE_IDS, ParamNames.PORT_IDS,
                              ParamNames.COUNTERS, ParamNames.FROM,
                              ParamNames.UNTIL],
        GET_ALL_MONITORING_DATA: []}

    def __init__(self):

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_MONITORING_DATA: self.__getMonitoringData,
            self.GET_ALL_MONITORING_DATA: self.__getAllMonitoringData}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_MONITORING_DATA:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_MONITORING_DATA:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoMonitorSdk, self).__init__(URL.MONITOR_URL)

    def _validateParamExistence(self, parameters, expected_params):
        """
        Overrides function from NeoSdk.

        This function validates that all parameters exist in expected_params.
        Note that not all the expected_params should exist in parameters
        """

        # Check that all given parameters are expected
        for param in parameters:
            if param not in expected_params:
                raise InvalidParam("Parameter '%s' is not supported" % param)

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

    def __getMonitoringData(self, parameters, payload):
        """
        Filter and get specific counters for specific systems
        """

        # Constructing the url. The url format is as follows:
        # /app/monitoring?device_ids=172.30.3.243&port_ids=Eth1/11,Eth1/10&...
        # ...counters=OutBroadcastPkts,OutUcastPkts
        param_list = ["=".join([key, value])
                      for (key, value) in parameters.iteritems()]
        url = "?".join([self._action_url, "&".join(param_list)])
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllMonitoringData(self, parameters, payload):
        """
        Get all monitoring data.
        """
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1) get - Filter and get specific counters for specific systems.
                All parameters are optional, and every combination of
                parameters is acceptable.
                --parameters="device_ids=value1,value2...&
                                port_ids=value1,value2...&
                                counters=value1,value2...&
                                from=value&until=value"
            2) getall - get all monitoring data.
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
    NeoMonitorSdk.main()
