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
@date:   Jan 4, 2016
"""

from one_click.tracker.tracker import Tracker
from one_click.action.action_mgr import ActionMngr
import sys
from os.path import isfile
from time import clock
from one_click.common.utils import Utils

SUCCESS = 0

DATA_FOLDER_PATH = r"data"


def parse_args(args):
    if len(args) != 2:
        sys.exit('Error: Incorrect number of arguments.\n'
                 'Usage %s <configuration-file-path>' % args[0])
    file_path = args[1]
    if not isfile(file_path):
        sys.exit('Error: Configuration file "%s" was not found.' % file_path)
    return file_path


def prepare_to_execute(tracker, execution_mgr):
    execution_mgr.update_data(tracker.main_data, True)
    for template_index, template_name in enumerate(tracker.page_titles):
        execution_mgr.add_template(template_name, True)
        execution_mgr.update_data(tracker.page_data[template_name],
                                  False,
                                  template_index)


def execute(execution_mgr):
    execution_mgr.analyze_data()
    all_provisioning_results = []
    start_run = clock()
    while execution_mgr.has_next():
        template_name = execution_mgr.get_latest_template_name()
        print "---> Running template '%s'" % template_name
        ret_val, output, error, exec_time = \
            execution_mgr.run_next_template()
        if ret_val == SUCCESS:
            status_code = Utils.parse_status_code(output)
            if status_code != "202":
                print "ERROR: Provisioning job was not created successfully."\
                    " Status code returned - %s\n" % status_code
                execution_mgr.clean()
                sys.exit(1)
            headlines = [("->Summary output for %s:\n" % ip)
                         for ip in execution_mgr.get_switch_ips()]
            summaries = [summary for summary in Utils.parse_summary(output)
                         if summary != ""]
            print "\n".join(
                ["\n".join([headline, summary])
                 for headline, summary in zip(headlines, summaries)])
            statuses = Utils.parse_status(output)
            not_completed_statuses = filter(
                lambda x: x.strip() != "Completed", statuses)
            if len(not_completed_statuses) != 0:
                all_provisioning_results.append((template_name, False))
                print "ERROR: provisioning job %s\n" % \
                    not_completed_statuses[0].lower()
            else:
                all_provisioning_results.append((template_name, True))
                print "-> Completed successfully." \
                    " Total executing time %.4f\n" % exec_time
        else:
            print "ERROR: Couldn't connect to NEO\n"
            execution_mgr.clean()
            sys.exit(1)
    end_run = clock()

    print "*** Status Summary ***\n"
    print "%-15s %s" % ("Template", "Status")
    print "%-15s %-10s" % ("-" * 15, "-" * 10)
    for template, finished_successfully in all_provisioning_results:
        result = "Completed" if finished_successfully else "Failed"
        print "%-15s %s" % (template, result)

    finished_without_error = all(
        [result for _, finished_successfully in all_provisioning_results])
    print "\n>>> Configuration completed %s errors. Total time: %.4f" % \
        ("without" if finished_without_error else "with",
         (end_run - start_run))

    execution_mgr.clean()

if __name__ == '__main__':
    file_path = parse_args(sys.argv)
    tracker = Tracker(file_path)
    execution_mgr = ActionMngr(DATA_FOLDER_PATH)
    prepare_to_execute(tracker, execution_mgr)
    execute(execution_mgr)
