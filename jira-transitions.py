import sys
import argparse
from datetime import datetime
from jira import JIRA


FILE_NAME = "jira-extractor-results.txt"
JIRA_SERVER = "https://jira.com/"
PERSONAL_TOKEN = "<YOUR-PERSONAL-ACCESS-TOKEN>"


class IssueTransition:
    def __init__(self, status, date, delta=0):
        self.status = status
        self.date = date
        self._delta = delta

    # getter
    def get_delta(self):
        return self._delta

    # setter
    def add_delta(self, value):
        self._delta += value

    # creating a property object
    delta = property(get_delta)


def get_date(datetime_value):
    # -9 to trim UTC/mms
    return datetime.strptime(datetime_value[:19], '%Y-%m-%dT%H:%M:%S')


def open_jira():
    print("# TRYING TO LOGIN JIRA")
    jira = JIRA(server=JIRA_SERVER, token_auth=(PERSONAL_TOKEN))
    return jira


def search_jira_issues(query, jira):
    print("# FETCHING SEARCH RESULTS")
    search_results = jira.search_issues(query)
    print(f'# SEARCH RETURNED {len(search_results)} RESULTS')
    return search_results


def get_jira_issue(jira, result_item):
    print(f'# FETCHING ISSUE {result_item.key} DETAILS')
    issue = jira.issue(result_item.key, expand="changelog",
                       fields="created,status,changelog")
    return issue


def get_jira_issue_changelog(issue, transitions_status, previous_date):
    print(f'# FETCHING ISSUE {issue.key} CHANGELOG')
    for history in issue.changelog.histories:
        for item in history.items:
            if (item.field == "status"):
                if (item.fromString in transitions_status):
                    issue_transition = transitions_status[item.fromString]
                    transition_date = get_date(history.created)
                    diff = transition_date - previous_date

                    issue_transition.add_delta(diff.total_seconds())
                    issue_transition.date = transition_date
                    previous_date = transition_date

                    if (item.toString not in transitions_status):
                        transitions_status[item.toString] = IssueTransition(
                            'item.toString', transition_date)


def calculate_time_last_transition(issue, transitions_status):
    last_key = issue.fields.status.name
    last_transition = transitions_status[last_key]
    last_transition.add_delta(
        (datetime.now() - last_transition.date).total_seconds())


def generate_output_file(filename, issue, transitions_status):
    print(f'# WRITING RESULTS')
    with open(filename, 'a') as f:
        f.write(issue.key)
        f.write('\n')
        for key in transitions_status:
            status = transitions_status[key]
            content = f'"{key}" = ' + \
                '{:.2f}'.format(status.delta / 3600) + ' hours'
            f.write(content)
            f.write(',')

        f.write('\n')
        f.write('\n')


def get_args(argv):
    p = argparse.ArgumentParser(
        description="Gets a set of JIRA issues and list them with their implementation time.")
    p.add_argument('-f', dest="filename",
                   help="The output file name.", default=FILE_NAME)
    p.add_argument('-q', dest='query', help="JIRA query.")
    args = p.parse_args(argv)
    if (len(argv) < 1):
        print("Use with -f <filename> -q <JIRA-query>.")
        sys.exit(2)
    return args


def main(argv):
    args = get_args(argv)
    filename = args.filename
    query = args.query

    print("# START")
    jira = open_jira()
    search_results = search_jira_issues(query, jira)

    for result_item in search_results:
        issue = get_jira_issue(jira, result_item)

        creation_date = get_date(issue.fields.created)
        previous_date = creation_date
        transitions_status = {'Open': IssueTransition('Open', creation_date)}

        get_jira_issue_changelog(issue, transitions_status, previous_date)
        calculate_time_last_transition(issue, transitions_status)
        generate_output_file(filename, issue, transitions_status)

    print("# END")


if __name__ == "__main__":
    main(sys.argv[1:])
