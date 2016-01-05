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
@date:   Dec 30, 2015
"""

import subprocess
import threading
import re
from time import sleep


class ActionUtiles(object):

    IP_REGEX = "\'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\'"
    SDK_LOCATION = r"src\one_click\sdk"

    def __init__(self):
        pass

    @staticmethod
    def exec_timeout(command_list, input_file=subprocess.PIPE, input_str="",
                     timeout=120):
        """
        Execute the given command list, feeding the given input to the program.
        Return a tuple containing the return code, stdout and stderr.

        Kills the process after the given time expires.
        """

        output = [""]
        error = [""]
        code = [0]
        process = [None]

        def target():
            process[0] = subprocess.Popen(command_list,
                                          stdin=input_file,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
            output[0], error[0] = process[0].communicate(
                input_file if input_file != subprocess.PIPE else None)
            code[0] = process[0].returncode

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)

        if thread.is_alive():
            process[0].terminate()
            thread.join()
            error[0] = "Your script timed out! Took more than %d seconds.\n" \
                % timeout
            code[0] = -1

        return code[0], output[0], error[0]

    @staticmethod
    def discover_systems(neo_ip, username, password):

        num_of_attempts = 0
        system_ips = []
        while num_of_attempts < 3:
            commands = [
                'python', r'%s\neo_get_data.py' % ActionUtiles.SDK_LOCATION,
                '-s', neo_ip,
                '-u', username,
                '-p', password,
                '-o', 'systems']
            ret_val, output, error = ActionUtiles.exec_timeout(commands)
            if ret_val == 0:
                system_ips = re.findall(ActionUtiles.IP_REGEX, output)
                if len(system_ips) == 0:
                    return 1, "Couldn't find any systems"
                else:
                    return 0, map(lambda x: x.strip("'"), system_ips)
            num_of_attempts += 1
            sleep(1)

        return 1, "Couldn't connect to NEO"
