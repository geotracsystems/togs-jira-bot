import re
import json
import slack
import requests
from requests.exceptions import HTTPError
from properties import *

JIRA_API_PROJ = 'rest/api/latest/project'
JIRA_API_ISSUE = 'rest/api/latest/issue/'
JIRA_WEB_ISSUE = 'browse/'

global JIRA_REGEX_COMP


# Gets JIRA summary for an issue passed to it. This is the slowest part of the program
def jira_summary(issue):
    try:
        jira_response = requests.get(JIRA_URL + JIRA_API_ISSUE + issue, auth=(JIRA_SVC_USER, JIRA_SVC_PASS))
    except HTTPError as http_err:
        print(f'HTTP Error: {http_err}')
        return

    jira_dict = json.loads(jira_response.content)

    if 'fields' in jira_dict:
        summary = jira_dict["fields"]["summary"]
        return summary
    else:
        return


@slack.RTMClient.run_on(event='message')
def jira_parse(**payload):
    jira_issue = []

    data = payload['data']
    web_client = payload['web_client']
    print(data)

    # Ignore bots
    if 'bot_id' in data:
        return

    # Ignore messages with no text
    try:
        text = data['text']
    except KeyError:
        return

    channel = data['channel']

    # If thread is available, save it
    if 'thread_ts' in data:
        thread_ts = data['thread_ts']
    else:
        thread_ts = ''

    # Find matches in incoming text and add in a list
    matches = JIRA_REGEX_COMP.findall(text)
    # print(matches) #Uncomment for debugging Regex issues
    for match in matches:
        jira_issue.append(match[0].strip())
    print(jira_issue)

    # Iterate through matches, get summary and publish to Slack
    for issue in jira_issue:
        summary = jira_summary(issue)

        if summary is None:
            continue
        slack_text = f"<{JIRA_URL + JIRA_WEB_ISSUE}{issue}|*{issue.upper()}: {summary}*>\n"

        if thread_ts == '':
            web_client.chat_postMessage(channel=channel, text=slack_text)
        else:
            web_client.chat_postMessage(channel=channel, text=slack_text, thread_ts=thread_ts)


# Main Program
# Initial project list (non-TOGS apps already included in list)
togs_project_list = ['MAINE', 'APPL']
togs_project_regex_str = ''

# Get all TOGS projects from JIRA and add to project list
project = requests.get(JIRA_URL + JIRA_API_PROJ, auth=(JIRA_SVC_USER, JIRA_SVC_PASS))
all_project = json.loads(project.content)
for item in all_project:
    if 'projectCategory' in item:
        if item["projectCategory"]["name"] == 'TOGS':
            togs_project_list.append(item["key"])

print(f"Monitoring {len(togs_project_list)} JIRA Projects")
print(togs_project_list)

# Make regex string and compile
for tpr in togs_project_list:
    togs_project_regex_str = togs_project_regex_str + tpr + '|'
project_list = togs_project_regex_str[:-1]

jira_regex = f"((?!(\s|\.|,|\"|\'|\(|/))({project_list})\-[0-9]{{1,}})"
JIRA_REGEX_COMP = re.compile(jira_regex, re.IGNORECASE)

# Start Slack RTM client to receive bot messages
rtm_client = slack.RTMClient(token=SLACK_TOKEN)
rtm_client.start()
