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


class URL(object):
    """
    This class contains all the common urls of REST API actions.
    """

    NEO_BASE_URL = "{0}://{1}/neo"
    LOGIN_URL = "/login"
    USERS_URL = "/app/users"
    GROUPS_URL = "/resources/groups"
    EVENTS_URL = "/app/events"
    TASKS_URL = "/app/tasks"
    JOBS_URL = "/app/jobs"
    EVENT_POLICY_URL = "/app/event_policy"
    NOTIFICATIONS_URL = "/app/notifications"
    MONITOR_URL = "/app/monitoring"
    SW_UPGRADE_URL = "/actions"
    PROVISIONING_URL = "/actions/provisioning"
    TEMPLATES_URL = "/app/provisioning_templates"

    @classmethod
    def getBaseURL(cls, protocol, server):
        return cls.NEO_BASE_URL.format(protocol, server)
