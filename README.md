**Requirements:**
* Python 3.7 or higher
* Install `slackclient` package using `pip`.
* JIRA Service Credentials
* Slack Bot OAuth Token

**Credentials:**

In order for the bot to work, you should store your credentials, Jira URL in a file called `properties.py` in the same directory.
The file should contain the following lines:

```buildoutcfg
SLACK_TOKEN = <Bot OAuth Token>
JIRA_SVC_USER = <JIRA Service Account User>
JIRA_SVC_PASS = <JIRA Service Account Password>
JIRA_URL = <JIRA url.>
```

**Known Issues:**

* Performance. This is a single threaded application with blocking calls. JIRA's API is the slowest. However, for an organization of our size, the performance impact is minimal
