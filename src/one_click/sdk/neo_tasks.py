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

import json
from infra.neo_sdk import NeoSdk
from infra.url import URL
from infra.sdk_exceptions import MissingArgument
from infra.sdk_parameters import ParamNames
import httplib


class NeoTasksSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles
    '/app/tasks' requests
    """

    ADD_TASK = "add"
    GET_TASKS = "get"
    GET_ALL_TASKS = "getall"
    DELETE_TASK = "delete"
    RUN_TASK = "run"

    # Descriptions of all the possible events actions
    ADD_TASK_DESCRIPTION = "Adding a new task"
    GET_TASKS_DESCRIPTION = "Getting task data"
    GET_ALL_TASKS_DESCRIPTION = "Getting all tasks data"
    DELETE_TASK_DESCRIPTION = "Removing a task"
    RUN_TASK_DESCRIPTION = "Running a task"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        ADD_TASK: ADD_TASK_DESCRIPTION,
        GET_TASKS: GET_TASKS_DESCRIPTION,
        GET_ALL_TASKS: GET_ALL_TASKS_DESCRIPTION,
        DELETE_TASK: DELETE_TASK_DESCRIPTION,
        RUN_TASK: RUN_TASK_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        ADD_TASK: [],
        GET_TASKS: [ParamNames.TASK_ID],
        GET_ALL_TASKS: [],
        DELETE_TASK: [ParamNames.TASK_ID],
        RUN_TASK: [ParamNames.TASK_ID]}

    def __init__(self):
        """
        Constructor
        """

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.ADD_TASK: self.__addTask,
            self.GET_TASKS: self.__getTasks,
            self.GET_ALL_TASKS: self.__getAllTasks,
            self.DELETE_TASK: self.__deleteTask,
            self.RUN_TASK: self.__runTask}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.ADD_TASK:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_TASKS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_TASKS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.DELETE_TASK:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.RUN_TASK:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoTasksSdk, self).__init__(URL.TASKS_URL)

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

    def __addTask(self, parameters, payload):
        """
        Adding a new task. The request payload is read from a file
        argument given by the user.
        """
        json_data = self._convertInputFileToJSON()
        response = self._neo_session.post(
            self._action_url,
            data=json.dumps(json_data),
            headers=self.REQ_HEADER_CONTENT_JSON)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getTasks(self, parameters, payload):
        """
        Get specific tasks.
        """
        tasks = parameters[ParamNames.TASK_ID]
        url = self._getRequestURL(tasks)
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllTasks(self, parameters, payload):
        """
        Get all tasks.
        """
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __deleteTask(self, parameters, payload):
        """
        Delete a specific task.
        """
        task = parameters[ParamNames.TASK_ID]
        url = self._getRequestURL(task)
        response = self._neo_session.delete(url)
        return response, self.SHOULD_NOT_PRINT_RESPONSE

    def __runTask(self, parameters, payload):
        """
        Run a specific task. The request to run the task, returns
        the relevant job id. If the user adds the [--blocking] flag,
        we wait until the job's status is 'Completed'.
        Otherwise, it's the user's responsibility to check the job status.
        """
        task = parameters[ParamNames.TASK_ID]
        url = self._getRequestURL(task)

        # In case no file was given, run the task without payload,
        # Otherwise, add the payload (file content) to the request.
        if self._arguments.file is None:
            response = self._neo_session.post("/".join([url, "run"]))
        else:
            json_data = self._convertInputFileToJSON()
            response = self._neo_session.post(
                "/".join([url, "run"]),
                data=json.dumps(json_data),
                headers=self.REQ_HEADER_CONTENT_JSON)

        # If the task is blocking and the job was created successfully,
        # block until the job finish
        if self._arguments.blocking and\
                response.status == httplib.ACCEPTED:
            self._validateJob(response)

        return response, self.SHOULD_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1)  add - add a new task.
                --file="file path"
            1)  get - get an existing task.
                --parameters="task_id=value1,value2"
            2)  getall - get all tasks.
            3)  delete - delete an existing task.
                --parameters="task_id=value"
            4)  run - run an existing task.
                --parameters="task_id=value"
                --file="file path"
            """

        file_help = """
            1)  add -
                File should be in the following json format:
                {
                  "schedule": {

                  },
                  "action": "run_cli",
                  "description": "Shows SNMP settings and status",
                  "object_type": "System",
                  "object_ids": [
                    "10.209.24.100"
                  ],
                  "params": {
                    "commandline": [
                      "show snmp"
                    ],
                    "arguments": {
                      "globals": {

                      }
                    }
                  }
                }

            2)  run -
                File should be in the following json format:
                {
                    "object_type": "System",
                    "object_ids": [
                        "10.209.24.102"
                    ]
                }

            Note: When you add a new task, you shouldn't use
            the [--payload] argument.
            """

        self._addOptionArg(parser, option_help, self._getActionOptions())
        self._addParamAndPayloadArgs(parser)
        self._addFileArg(parser, file_help)
        self._addBlockingArg(parser)

    def _validateArgs(self, action):
        '''
        This method validates that all the needed argument were given,
        and that there aren't any extra arguments
        '''

        self._validateParamAndPayloadArgs(action)

        # If the current action is add_task, validate that the [--file]
        # argument exists. Otherwise, if the current action is not add_task or
        # run_task, validate that the [--file] argument doesn't exist.
        if action == self.ADD_TASK:
            if self._arguments.file is None:
                raise MissingArgument("Missing argument [-f] [--file]")
        else:
            if self._arguments.file is not None and action != self.RUN_TASK:
                raise MissingArgument("Unsupported argument [-f] [--file]")

        # If the current action is not run_task, validate that the [--blocking]
        # argument doesn't exist.
        if action != self.RUN_TASK and self._arguments.blocking:
            raise MissingArgument("Unsupported argument [-b] [--blocking]")

if __name__ == "__main__":
    NeoTasksSdk.main()
