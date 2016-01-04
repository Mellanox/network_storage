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

@author: Shachar Langer
@date:   Aug 23, 2015
"""

from infra.url import URL
from infra.sdk_parameters import ParamNames
from infra.neo_sdk import NeoSdk


class NeoUsersSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles '/users'
    requests
    """

    GET_USER = "get"
    GET_ALL_USERS = "getall"
    ADD_USER = "add"
    UPDATE_USER = "update"
    DELETE_USER = "delete"

    # Descriptions of all the possible user actions
    GET_USER_DESCRIPTION = "Getting user data"
    GET_ALL_USERS_DESCRIPTION = "Getting all users data"
    ADD_USER_DESCRIPTION = "Adding user"
    UPDATE_USER_DESCRIPTION = "Updating user"
    DELETE_USER_DESCRIPTION = "Deleting user"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_USER: GET_USER_DESCRIPTION,
        GET_ALL_USERS: GET_ALL_USERS_DESCRIPTION,
        ADD_USER: ADD_USER_DESCRIPTION,
        UPDATE_USER: UPDATE_USER_DESCRIPTION,
        DELETE_USER: DELETE_USER_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_USER: [ParamNames.USERNAME],
        GET_ALL_USERS: [],
        ADD_USER: [],
        UPDATE_USER: [ParamNames.USERNAME],
        DELETE_USER: [ParamNames.USERNAME]}

    def __init__(self):

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_USER: self._getUser,
            self.GET_ALL_USERS: self._getAllUsers,
            self.ADD_USER: self._addUser,
            self.UPDATE_USER: self._updateUser,
            self.DELETE_USER: self._deleteUser}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_USER:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_USERS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.ADD_USER:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NEEDED),
            self.UPDATE_USER:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NEEDED),
            self.DELETE_USER:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoUsersSdk, self).__init__(URL.USERS_URL)

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

    def _getUser(self, parameters, payload):
        username = parameters[ParamNames.USERNAME]
        response = self._neo_session.get(self._getRequestURL(username))
        return response, self.SHOULD_PRINT_RESPONSE

    def _getAllUsers(self, parameters, payload):
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def _addUser(self, parameters, payload):
        response = self._neo_session.post(self._action_url,
                                          data=payload,
                                          headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _updateUser(self, parameters, payload):
        username = parameters[ParamNames.USERNAME]
        response = self._neo_session.put(self._getRequestURL(username),
                                         data=payload,
                                         headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _deleteUser(self, parameters, payload):
        username = parameters[ParamNames.USERNAME]
        response = self._neo_session.delete(self._getRequestURL(username))
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1) get - get an existing user.
                --parameters="username=value"
            2) getall - get all users
            3) add - add a new user.
                --payload="username=value&password=value&role=value"
            4) update - update an existing user.
                --parameters="username=value"
                --payload="password=value&old_password=value&role=value"
            5) delete - delete an existing user.
                --parameters="username=value"
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
    NeoUsersSdk.main()
