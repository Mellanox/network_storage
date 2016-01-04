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

from infra.neo_sdk import NeoSdk
from infra.sdk_parameters import ParamNames
from infra.url import URL


class NeoGroupsSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    '/resources/groups' requests
    """

    GET_GROUPS = "get"
    GET_ALL_GROUPS = "getall"
    ADD_GROUP = "add"
    UPDATE_GROUP = "update"
    DELETE_GROUP = "delete"
    ADD_SYSTEMS_TO_GROUP = "addsys"
    GET_SYSTEMS_IN_GROUP = "getsys"
    GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP = "getsyswprop"
    DELETE_SYSTEMS_FROM_GROUP = "delsys"
    DELETE_ALL_SYSTEMS_IN_GROUP = "delallsys"
    GET_GROUPS_BY_SYSTEMS = "getbysys"

    # Descriptions of all the possible group actions
    GET_GROUPS_DESCRIPTION = "Getting groups data"
    GET_ALL_GROUPS_DESCRIPTION = "Getting all groups data"
    ADD_GROUP_DESCRIPTION = "Adding group"
    UPDATE_GROUP_DESCRIPTION = "Updating group"
    DELETE_GROUP_DESCRIPTION = "Deleting group"
    ADD_SYSTEM_TO_GROUP_DESCRIPTION = "Adding systems to group"
    GET_SYSTEMS_IN_GROUP_DESCRIPTION = "Getting systems in group"
    DELETE_SYSTEMS_FROM_GROUP_DESCRIPTION = "Deleting systems from group"
    DELETE_ALL_SYSTEMS_IN_GROUP_DESCRIPTION = "Deleting all systems in group"
    GET_GROUPS_BY_SYSTEMS_DESCRIPTION = "Getting groups by systems"
    GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP_DESCRIPTION = \
        "Getting systems with properties in group"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_GROUPS: GET_GROUPS_DESCRIPTION,
        GET_ALL_GROUPS: GET_ALL_GROUPS_DESCRIPTION,
        ADD_GROUP: ADD_GROUP_DESCRIPTION,
        UPDATE_GROUP: UPDATE_GROUP_DESCRIPTION,
        DELETE_GROUP: DELETE_GROUP_DESCRIPTION,
        ADD_SYSTEMS_TO_GROUP: ADD_SYSTEM_TO_GROUP_DESCRIPTION,
        GET_SYSTEMS_IN_GROUP: GET_SYSTEMS_IN_GROUP_DESCRIPTION,
        GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP:
            GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP_DESCRIPTION,
        DELETE_SYSTEMS_FROM_GROUP: DELETE_SYSTEMS_FROM_GROUP_DESCRIPTION,
        DELETE_ALL_SYSTEMS_IN_GROUP: DELETE_ALL_SYSTEMS_IN_GROUP_DESCRIPTION,
        GET_GROUPS_BY_SYSTEMS: GET_GROUPS_BY_SYSTEMS_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_GROUPS: [ParamNames.ELEMENT_NAME],
        GET_ALL_GROUPS: [],
        ADD_GROUP: [],
        UPDATE_GROUP: [ParamNames.ELEMENT_NAME],
        DELETE_GROUP: [ParamNames.ELEMENT_NAME],
        ADD_SYSTEMS_TO_GROUP: [ParamNames.ELEMENT_NAME],
        GET_SYSTEMS_IN_GROUP: [ParamNames.ELEMENT_NAME],
        GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP:
            [ParamNames.ELEMENT_NAME, ParamNames.PROPERTIES],
        DELETE_SYSTEMS_FROM_GROUP:
            [ParamNames.ELEMENT_NAME, ParamNames.SYSTEM_ID],
        DELETE_ALL_SYSTEMS_IN_GROUP: [ParamNames.ELEMENT_NAME],
        GET_GROUPS_BY_SYSTEMS: [ParamNames.SYSTEM_ID]}

    def __init__(self):
        """
        Constructor
        """

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_GROUPS: self.__getGroup,
            self.GET_ALL_GROUPS: self.__getAllGroups,
            self.ADD_GROUP: self.__addGroup,
            self.UPDATE_GROUP: self.__updateGroup,
            self.DELETE_GROUP: self.__deleteGroup,
            self.ADD_SYSTEMS_TO_GROUP: self.__addSystemToGroup,
            self.GET_SYSTEMS_IN_GROUP: self.__getSystemsInGroup,
            self.GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP:
                self.__getSystemsWithPropertiesInGroup,
            self.DELETE_SYSTEMS_FROM_GROUP: self.__deleteSystemsFromGroup,
            self.DELETE_ALL_SYSTEMS_IN_GROUP: self.__deleteAllSystemsInGroup,
            self.GET_GROUPS_BY_SYSTEMS: self.__getGroupsBySystems}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_GROUPS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_GROUPS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.ADD_GROUP:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NEEDED),
            self.UPDATE_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NEEDED),
            self.DELETE_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.ADD_SYSTEMS_TO_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NEEDED),
            self.GET_SYSTEMS_IN_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_SYSTEMS_WITH_PROPERTIES_IN_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.DELETE_SYSTEMS_FROM_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.DELETE_ALL_SYSTEMS_IN_GROUP:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_GROUPS_BY_SYSTEMS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoGroupsSdk, self).__init__(URL.GROUPS_URL)

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

    def __getGroup(self, parameters, payload):
        group_names = parameters[ParamNames.ELEMENT_NAME]
        response = self._neo_session.get(self._getRequestURL(group_names))
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllGroups(self, parameters, payload):
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __addGroup(self, parameters, payload):
        response = self._neo_session.post(self._action_url,
                                          data=payload,
                                          headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_PRINT_RESPONSE

    def __updateGroup(self, parameters, payload):
        group_name = parameters[ParamNames.ELEMENT_NAME]
        response = self._neo_session.put(self._getRequestURL(group_name),
                                         data=payload,
                                         headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def __deleteGroup(self, parameters, payload):
        group_name = parameters[ParamNames.ELEMENT_NAME]
        response = self._neo_session.delete(self._getRequestURL(group_name))
        return response, self.SHOULD_PRINT_RESPONSE

    def __addSystemToGroup(self, parameters, payload):
        group_name = parameters[ParamNames.ELEMENT_NAME]
        url = self._getRequestURL("/".join([group_name, "members"]))
        response = self._neo_session.post(url, data=payload)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getSystemsInGroup(self, parameters, payload):
        group_name = parameters[ParamNames.ELEMENT_NAME]
        url = self._getRequestURL("/".join([group_name, "members"]))
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getGroupsBySystems(self, parameters, payload):
        system = parameters[ParamNames.SYSTEM_ID]
        url = self._getRequestURL("".join(["?system_member=", system]))
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getSystemsWithPropertiesInGroup(self, parameters, payload):
        properties = parameters[ParamNames.PROPERTIES]
        group_name = parameters[ParamNames.ELEMENT_NAME]
        url_without_properties = self._getRequestURL(
            "/".join([group_name, "members?props="]))
        url = "".join([url_without_properties, properties])
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __deleteSystemsFromGroup(self, parameters, payload):
        group_name = parameters[ParamNames.ELEMENT_NAME]
        systems = parameters[ParamNames.SYSTEM_ID]
        url = self._getRequestURL("/".join([group_name, "members", systems]))
        response = self._neo_session.delete(url)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def __deleteAllSystemsInGroup(self, parameters, payload):
        group_name = parameters[ParamNames.ELEMENT_NAME]
        url = self._getRequestURL("/".join([group_name, "members"]))
        response = self._neo_session.delete(url)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        '''
        Adding new possible arguments to the argparse object
        that were not added as a default argument.

        '''
        option_help = """
            Actions:
            1)  get - get existing groups.
                --parameters="element_id=value1,value2,..."
            2)  getall - get all groups.
            3)  add - add a new group.
                --payload="elementName=value&description=value"
            4)  update - update an existing group.
                --parameters="elementName=value"
                --payload="description=value"
            5)  delete - delete an existing group.
                --parameters="elementName=value"
            6)  addsys - add existing systems to a group.
                --parameters="elementName=value"
                --payload="system_id=[value1,value2...]"
            7)  getsys - get all the systems in an existing group.
                --parameters="elementName=value"
            8)  getsyswprop - get all the systems in an existing group,
                              and  retrieve additional system properties.
                --parameters="elementName=value&properties=value1,value2..."
            9)  delsys - delete an existing system from a group.
                --parameters="elementName=value&system_id=value"
            10) delallsys - delete all the systems in an existing group.
                --parameters="elementName=value"
            11) getbysys - get all the groups containing an existing system.
                --parameters="system_id=value"
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
    NeoGroupsSdk.main()
