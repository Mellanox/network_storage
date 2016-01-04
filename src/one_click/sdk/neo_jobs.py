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
@date:   Sep 6, 2015
"""

from infra.url import URL
from infra.neo_sdk import NeoSdk
from infra.sdk_parameters import ParamNames


class NeoJobsSdk(NeoSdk):
    """
    This class represents a NEO session that specifically handles 'app/jobs'
    requests
    """

    GET_JOBS = "get"
    GET_ALL_JOBS = "getall"
    GET_PARENT_JOBS = "getparentjobs"
    GET_SUB_JOBS = "getchildjobs"
    GET_JOBS_FOR_SYSTEM = "getsystemjobs"

    # Descriptions of all the possible job actions
    GET_JOBS_DESCRIPTION = "Getting job data"
    GET_ALL_JOBS_DESCRIPTION = "Getting all jobs data"
    GET_PARENT_JOBS_DESCRIPTION = "Getting all parent jobs"
    GET_SUB_JOBS_DESCRIPTION = "Getting all sub jobs of a specific job"
    GET_JOBS_FOR_SYSTEM_DESCRIPTION = "Getting jobs for system"

    # Map each action to its description
    ACTION_TO_DESCRIPTION = {
        GET_JOBS: GET_JOBS_DESCRIPTION,
        GET_ALL_JOBS: GET_ALL_JOBS_DESCRIPTION,
        GET_PARENT_JOBS: GET_PARENT_JOBS_DESCRIPTION,
        GET_SUB_JOBS: GET_SUB_JOBS_DESCRIPTION,
        GET_JOBS_FOR_SYSTEM: GET_JOBS_FOR_SYSTEM_DESCRIPTION}

    # Map each action to a list of expected parameters
    ACTION_TO_EXPECTED_PARAMS = {
        GET_JOBS: [ParamNames.JOB_ID],
        GET_ALL_JOBS: [],
        GET_PARENT_JOBS: [],
        GET_SUB_JOBS: [ParamNames.JOB_ID],
        GET_JOBS_FOR_SYSTEM: [ParamNames.SYSTEM_ID]}

    def __init__(self):
        """
        Constructor
        """

        # Map each action to its execute function
        self.ACTION_TO_FUNCTION = {
            self.GET_JOBS: self.__getJobs,
            self.GET_ALL_JOBS: self.__getAllJobs,
            self.GET_PARENT_JOBS: self.__getParentJobs,
            self.GET_SUB_JOBS: self.__getSubJobs,
            self.GET_JOBS_FOR_SYSTEM: self.__getJobsForSystem}

        # Map each action to (should_have_param_arg, should_have_payload_arg)
        self.ACTION_TO_NEEDED_ARGS = {
            self.GET_JOBS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_ALL_JOBS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_PARENT_JOBS:
                (self.PARAM_ARG_NOT_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_SUB_JOBS:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED),
            self.GET_JOBS_FOR_SYSTEM:
                (self.PARAM_ARG_NEEDED, self.PAYLOAD_ARG_NOT_NEEDED)}

        super(NeoJobsSdk, self).__init__(URL.JOBS_URL)

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

    def __getJobs(self, parameters, payload):
        jobs_ids = parameters[ParamNames.JOB_ID]
        response = self._neo_session.get(self._getRequestURL(jobs_ids))
        return response, self.SHOULD_PRINT_RESPONSE

    def __getAllJobs(self, parameters, payload):
        response = self._neo_session.get(self._action_url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getParentJobs(self, parameters, payload):
        url = "".join([self._action_url, "?parent_id=null"])
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getSubJobs(self, parameters, payload):
        job_id = parameters[ParamNames.JOB_ID]
        url = "".join([self._action_url, "?parent_id=", job_id])
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def __getJobsForSystem(self, parameters, payload):
        systems = parameters[ParamNames.SYSTEM_ID]
        url = "".join([self._action_url, "?object_ids=", systems])
        response = self._neo_session.get(url)
        return response, self.SHOULD_PRINT_RESPONSE

    def _addSessionArgs(self, parser):
        option_help = """
            Actions:
            1) get - get existing jobs.
                --parameters="job_id=value1,value2,value3..."
            2) getall - get all jobs.
            3) getparentjobs - get all parent jobs.
            4) getchildjobs - get all sub jobs for a specific job
                --parameters="job_id=value"
            5) getsystemjobs - get all jobs for a list of systems.
                --parameters="system_id=value1,value2,value3..."
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
    NeoJobsSdk.main()
