
# GitHub YouTrack Receive Hook

**Requires Python 2.7**

GitHub receive hook is designed for updating YouTrack issues by push event.

The hook constantly listens all local interfaces to receive push events from GitHub. Once the hook recieves a push event, it parses the event payload. The hook does two things:

 1. Publishes comments to corresponding issues groupping by the author.
 2. Marking issues for release version

## Setup

### Setting Up YouTrack

First set up VCS integration in Youtrack. Follow the JetBrains [instruction](https://www.jetbrains.com/help/youtrack/standalone/7.0/GitHub-Integration.html) to do this.

During posting the comment the webhook compares the email of GitHub committer with YouTrack user's email. As well as marking issues, the comment publishing performs by user found by email from commit. If email not found, the event performs from the system user. It is advised to provide developer grants to all the committers. The webhook does not publish duplicated comments.

### Setting up GitHub hook

Go to your GitHub project settings

    https://github.com/<github_account>/<project>/settings/hooks

and find new webhook created by previous step. Edit the hook parameters:

Payload URL should be as example:

    http://<webhook_url>:<webhook_port>/postreceive

Content type:

    application/json

Secret

    Use the secret key generated in the previous step (OAuth Token)

Pick "Just the push event" for events you would like to trigger this webhook.

Next check if hook is active.

## Install Python

Install Python 2.7

## Download the Webhook

Download the webhook

    https://git.haulmont.com/platform/github-youtrack-hook

## Download YouTrack REST Python Library

Download the directory

    https://github.com/JetBrains/youtrack-rest-python-library

to the webhook folder and rename the whole library folder to **api**.

## Prepare the Webhook

Rename **config_template.py** to **config.py**

Replace all default fields **\<REQUIRED\>** to your settings.

## Usage

Start python webhook:

    python github_youtrack_hook.py

It should work on address

    http://<webhook_url>:80

Send a push event, wait for a while until the process finishes. You should see some new comments in issues which were mentioned in commits pushed. Check a log file or console window for details.

For the test purposes you can reuse payloads sending them from Recent Deliveries on Webhooks Setting page.