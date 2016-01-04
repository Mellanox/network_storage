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
@date:   Nov 29, 2015
"""

from infra.neo_sdk import NeoSdk
from infra.url import URL
import json
import httplib
from infra.sdk_parameters import ParamNames
from infra.sdk_exceptions import MissingArgument
import re


class NeoProvisioningSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    provisioning requests
    """

    EXECUTE_PROVISIONING = "execute"
    GET_TEMPLATE_LIST = "list"
    GET_TEMPLATE_DETAILS = "details"
    ADD_TEMPLATE = "add"

    # Descriptions of all the possible provisioning actions
    EXECUTE_PROVISIONING_DESCRIPTION = "Executing provisioning task"
    GET_TEMPLATE_LIST_DESCRIPTION = "Getting template list"
    GET_TEMPLATE_DETAILS_DESCRIPTION = "Getting template details"
    ADD_TEMPLATE_DESCRIPTION = "add"
    
    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        EXECUTE_PROVISIONING: EXECUTE_PROVISIONING_DESCRIPTION,
        GET_TEMPLATE_LIST: GET_TEMPLATE_LIST_DESCRIPTION,
        GET_TEMPLATE_DETAILS: GET_TEMPLATE_DETAILS_DESCRIPTION,
        ADD_TEMPLATE: ADD_TEMPLATE_DESCRIPTION
    }

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        EXECUTE_PROVISIONING: [ParamNames.TEMPLATE_NAME],
        GET_TEMPLATE_LIST: [],
        GET_TEMPLATE_DETAILS: [ParamNames.TEMPLATE_NAME],
        ADD_TEMPLATE: []
    }

    def __init__(self):

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.EXECUTE_PROVISIONING: self._executeProvisioning,
            self.GET_TEMPLATE_LIST: self._getTemplateList,
            self.GET_TEMPLATE_DETAILS: self._getTemplateDetails,
            self.ADD_TEMPLATE: self._addTemplate
        }

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.EXECUTE_PROVISIONING:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_TEMPLATE_LIST:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_TEMPLATE_DETAILS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.ADD_TEMPLATE:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)    
        }

        super(NeoProvisioningSdk, self).__init__(URL.PROVISIONING_URL)

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

    def _executeProvisioning(self, parameters, payload):
        template_name = parameters[ParamNames.TEMPLATE_NAME]
        url = self._getRequestURL(template_name)
        json_data = self._convertInputFileToJSON()
        response = self._neo_session.post(
            url,
            data=json.dumps(json_data),
            headers=self.REQ_HEADER_CONTENT_JSON)

        # If the task is blocking and the job was created successfully,
        # block until the job finish
        if self._arguments.blocking and\
                response.status == httplib.ACCEPTED:
            self._validateJob(response)

        return response, self.SHOULD_PRINT_RESPONSE

    def _getTemplateList(self, parameters, payload):
        url = "".join((self._base_url, URL.TEMPLATES_URL))
        response = self._neo_session.get(url)
        if response.status == httplib.OK:
            templates_data = json.loads(response.read())
            templates_list = "\n".join([template_data["title"]
                                        for template_data in templates_data])
            self._printData("Template list", templates_list)

        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def _extractRelevantDetails(self, response, template_name):
        GLOBAL_ARG_REGEX = "#<([^<>]*)>\|desc:(.*)"
        LOCAL_ARG_REGEX = "#<<([^<>]*)>>\|desc:(.*)"
        template_content = json.loads(response.read())["content"]
        template_args = filter(lambda x: x.startswith("#<"), template_content)
        global_args = []
        local_args = []
        for arg in template_args:
            global_match = re.search(GLOBAL_ARG_REGEX, arg)
            if global_match is not None:
                global_args.append(
                    (global_match.group(1), global_match.group(2)))
            else:
                local_match = re.search(LOCAL_ARG_REGEX, arg)
                if local_match is not None:
                    local_args.append(
                        (local_match.group(1), local_match.group(2)))
        return {
            "global_args": dict(global_args),
            "local_args": dict(local_args)}

    def _printData(self, title, data):
        print "=" * 70
        print "[*] %s:" % title
        print data

    def _getTemplateDetails(self, parameters, payload):
        template_name = parameters[ParamNames.TEMPLATE_NAME]
        url = "".join((self._base_url, URL.TEMPLATES_URL, "/", template_name))
        response = self._neo_session.get(url)
        if response.status == httplib.OK:
            details_dict = self._extractRelevantDetails(
                response, template_name)
            self._printData(
                "Template details", json.dumps(details_dict, sort_keys=True,
                                               indent=4))
        return response, self.SHOULD_NOT_PRINT_RESPONSE
        
    def _addTemplate(self, parameters, payload):
        url = "".join((self._base_url, URL.TEMPLATES_URL))
        json_data = self._convertInputFileToJSON()
        response = self._neo_session.post(
            url,
            data=json.dumps(json_data),
            headers=self.REQ_HEADER_CONTENT_JSON)
            
        return response, self.SHOULD_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1) execute - executing a provisioning task.
                --parameters="template_name=value"
                --file="file path"
            2) list - list all existing templates.
            3) details - get arguments data of a specific template.
                --parameters="template_name=value"
        """

        file_help = """
            File should be in the following json format:
            {
                "params": {
                    "arguments": {
                        "globals": {
                            "vlan_number": "5"
                        },
                        "devices": {
                            "10.209.24.39": {
                                "port_name": "1/5"
                            }
                        }
                    }
                },
                "object_ids": ["10.209.24.39"],
                "object_type": "System"
            }

            Note: When you execute a new provisioning task, you shouldn't use
            the [--payload] argument.
            """

        self._addBlockingArg(parser)
        self._addOptionArg(
            parser, option_help, self._getActionOptions())
        self._addParamAndPayloadArgs(parser)
        self._addFileArg(parser, file_help)

    def _validateArgs(self, action):
        '''
        This method validates that all the needed argument were given,
        and that there aren't any extra arguments
        '''

        self._validateParamAndPayloadArgs(action)

        # If the current action is execute provisioning task,
        # validate that the [--file] argument exists.
        # Otherwise, validate that the [--file] argument doesn't exist.
        if action in (self.EXECUTE_PROVISIONING, self.ADD_TEMPLATE):
            if self._arguments.file is None:
                raise MissingArgument("Missing argument [-f] [--file]")
        else:
            if self._arguments.file is not None:
                raise MissingArgument("Unsupported argument [-f] [--file]")

        # If the current action is not execute task,
        # validate that the [--blocking] argument doesn't exist.
        if action != self.EXECUTE_PROVISIONING and self._arguments.blocking:
            raise MissingArgument("Unsupported argument [-b] [--blocking]")

if __name__ == "__main__":
    NeoProvisioningSdk.main()
