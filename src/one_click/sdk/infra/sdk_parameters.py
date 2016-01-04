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
@date:   Sep 1, 2015
"""


class ParamNames(object):

    # User attributes
    PASSWORD = "password"
    OLD_PASSWORD = "old_password"
    ROLE = "role"
    USERNAME = "username"

    # Group attributes
    ELEMENT_NAME = "elementName"
    DESCRIPTION = "description"
    PROPERTIES = "properties"

    # System attributes
    SYSTEM_ID = "system_id"

    # Event attributes
    EVENT_ID = "event_id"

    # Task attributes
    TASK_ID = "task_id"

    # Job attributes
    JOB_ID = "job_id"

    # Event policy attributes
    EVENT_POLICY_ID = "event_policy_id"

    # Notification attributes
    NOTIFICATION_ID = "notification_id"

    # Monitoring attributes
    DEVICE_IDS = "device_ids"
    PORT_IDS = "port_ids"
    COUNTERS = "counters"
    FROM = "from"
    UNTIL = "until"
    TIME_ZONE = "tz"

    # Provisioning attributes
    TEMPLATE_NAME = "template_name"
