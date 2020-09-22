import os
import re
import json
import slack
import requests
from requests.exceptions import HTTPError

JIRA_URL = 'https://jira.trimble.tools/'
JIRA_API_PROJ = 'rest/api/latest/project'
JIRA_API_ISSUE = 'rest/api/latest/issue/'
JIRA_WEB_ISSUE = 'browse/'

global JIRA_REGEX_COMP


# Gets JIRA summary for an issue passed to it. This is the slowest part of the program
def jira_summary(issue):
    try:
        jira_response = requests.get(JIRA_URL + JIRA_API_ISSUE + issue, auth=(os.getenv('JIRA_SVC_USER'), os.getenv('JIRA_SVC_PASS')))
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
        jira_issue.append(match.strip())
    print(jira_issue)
    unique_jira_issue = sorted(set(jira_issue), key=jira_issue.index)
    print(unique_jira_issue)

    # Iterate through matches, get summary and publish to Slack
    for issue in unique_jira_issue:
        summary = jira_summary(issue)

        if summary is None:
            continue
        slack_text = f"<{JIRA_URL + JIRA_WEB_ISSUE}{issue}|*{issue.upper()}: {summary}*>\n"

        if thread_ts == '':
            web_client.chat_postMessage(channel=channel, text=slack_text)
        else:
            web_client.chat_postMessage(channel=channel, text=slack_text, thread_ts=thread_ts)


# Main Program
jira_regex = '[A-Za-z]{1,10}-\\d+\\b(?![.?\\-]\\d)'
JIRA_REGEX_COMP = re.compile(jira_regex)
# Start Slack RTM client to receive bot messages
rtm_client = slack.RTMClient(token=os.getenv('SLACK_TOKEN'))
rtm_client.start()
