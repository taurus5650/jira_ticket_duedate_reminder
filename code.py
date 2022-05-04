from jira import JIRA
import requests
import json
import os
import sys
from datetime import date, datetime
import logging


# import date
today = date.today()
# file path
os.chdir(sys.path[0])
JQLdueDate_file = (str(today) + " JQLdueDate.txt")
# logging
logging.basicConfig(filename="due_date_reminder_log.txt", level=logging.DEBUG,
                    format="%(asctime)s | %(levelname)s | %(funcName)s | %(message)s")


### The variable need to fill in ###

jira_server = "JIRA_URL"
jira_username = "JIRA_USERNAME"
jira_password = "JIRA_PASSWORD"
jira_JQL = "JIRA_JQL"

# Mattermost channel
webhook_url = "MATTERMOST_INTEGRATION_URL"

### The variable need to fill in ###


def jira_filter():
    jiraServer = {
        "server": jira_server
    }

    jira = JIRA(
        options=jiraServer,
        basic_auth=(jira_username, jira_password)
    )

    for JQLdueDate in jira.search_issues(jira_JQL):

        with open(JQLdueDate_file, "a") as file:

            file.write(
                ' |  @{}  |  JIRA_URL{}  |  {}  | \n'.format(
                    JQLdueDate.fields.assignee.emailAddress,
                    JQLdueDate.key,
                    JQLdueDate.fields.summary
                )
            )
            if "SPTWQA-" in (str(JQLdueDate)):
                logging.info(str(JQLdueDate))

            else:
                logging.debug(str(JQLdueDate))


def send_mattermost():

    if not os.path.exists(JQLdueDate_file):
        logging.info("Today not have ticket")
        exit()
    # if not result, then not generate file, then pass if not file

    else:

        with open(JQLdueDate_file) as file:
            send_mattermost_file = file.read()

            send_mettermost_headers = {
                "Content-Type": "application/json"
            }

            send_mettermost_body = {
                "text": " ##### Due date reminder " + str(today) + "\n\n :red_circle: ** @channel Due date reminder, kindly take a note ** \n" + "\n  | Assignee | Ticket | Summary | \n |:---|:---:|:---| \n " + send_mattermost_file
            }

            send_mattermost_responses = requests.post(
                url=webhook_url, headers=send_mettermost_headers,  data=json.dumps(send_mettermost_body))

            if send_mattermost_responses.status_code == 200:
                logging.info(str(send_mattermost_responses.status_code) + "| " + str(
                    send_mattermost_responses.text) + " | mattermost send successfully")

            else:
                logging.error(str(send_mattermost_responses.status_code) +
                              str(send_mattermost_responses.text))


def remove_file():
    os.remove(JQLdueDate_file)
    logging.info(JQLdueDate_file + " removed success")


if __name__ == '__main__':
    jira_filter()
    send_mattermost()
    remove_file()
