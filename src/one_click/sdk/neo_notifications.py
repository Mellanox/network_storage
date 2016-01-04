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
@date:   Sep 16, 2015
"""

import json
from infra.neo_sdk import NeoSdk
from infra.url import URL
from infra.sdk_parameters import ParamNames


class NeoNotificationsSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    '/app/notifications' requests
    """

    GET_NOTIFICATION = "get"
    GET_ALL_NOTIFICATIONS = "getall"
    UPDATE_NOTIFICATION = "update"
    DELETE_NOTIFICATION = "delete"

    GET_NOTIFICATION_DESCRIPTION = "Getting notification data"
    GET_ALL_NOTIFICATIONS_DESCRIPTION = "Getting all notifications data"
    UPDATE_NOTIFICATION_DESCRIPTION = "Updating notification"
    DELETE_NOTIFICATION_DESCRIPTION = "Deleting notification"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_NOTIFICATION: GET_NOTIFICATION_DESCRIPTION,
        GET_ALL_NOTIFICATIONS: GET_ALL_NOTIFICATIONS_DESCRIPTION,
        UPDATE_NOTIFICATION: UPDATE_NOTIFICATION_DESCRIPTION,
        DELETE_NOTIFICATION: DELETE_NOTIFICATION_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_NOTIFICATION: [ParamNames.NOTIFICATION_ID],
        GET_ALL_NOTIFICATIONS: [],
        UPDATE_NOTIFICATION: [ParamNames.NOTIFICATION_ID],
        DELETE_NOTIFICATION: [ParamNames.NOTIFICATION_ID]}

    def __init__(self):

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_NOTIFICATION: self.__getNotification,
            self.GET_ALL_NOTIFICATIONS: self.__getAllNotifications,
            self.UPDATE_NOTIFICATION: self.__updateNotification,
            self.DELETE_NOTIFICATION: self.__deleteNotification}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_NOTIFICATION:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_NOTIFICATIONS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.UPDATE_NOTIFICATION:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NEEDED),
            self.DELETE_NOTIFICATION:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoNotificationsSdk, self).__init__(URL.NOTIFICATIONS_URL)

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

    def __getNotification(self, parameters, payload):
        notification = parameters[ParamNames.NOTIFICATION_ID]
        response = self._neo_session.get(self._getRequestURL(notification))
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllNotifications(self, parameters, payload):
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __updateNotification(self, parameters, payload):
        temp_payload = json.loads(payload)
        converted_payload = self._castAttributes(temp_payload,
                                                 {"read": bool})
        notification = parameters[ParamNames.NOTIFICATION_ID]
        response = self._neo_session.put(self._getRequestURL(notification),
                                         data=json.dumps(converted_payload),
                                         headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def __deleteNotification(self, parameters, payload):
        notification = parameters[ParamNames.NOTIFICATION_ID]
        response = self._neo_session.delete(self._getRequestURL(notification))
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1) get - get an existing notification
                --parameters="notification_id=value"
            2) getall - get all notifications
            3) update - update an existing notification
                --parameters="notification_id=value"
                --payload="read={True/False}"
            4) delete - delete an existing notification
                --parameters="notification_id=value"
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
    NeoNotificationsSdk.main()
