import time

import logging
import traceback

from flask import Flask
from github_webhook import Webhook

import common
import config
from common import *
from gitobjects import *
from youtrack.connection import Connection
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging._levelNames[config.LOG_LEVEL])

logfile_handler = TimedRotatingFileHandler(config.LOG_FILE, config.LOG_ROTATE_PERIOD, config.LOG_ROTATE_INTERVAL, config.LOG_ROTATE_BACKUP_COUNT)
logfile_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(logfile_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(console_handler)

if (config.WEBHOOK_SECRET == '<REQUIRED>') or \
        (config.LDAP_EMAIL_DOMAIN == '<REQUIRED>') or \
        (config.DEFAULT_YOUTRACK_URL == '<REQUIRED>') or \
        (config.DEFAULT_YOUTRACK_USER == '<REQUIRED>') or \
        (config.DEFAULT_YOUTRACK_PASS == '<REQUIRED>'):
    sys.exit(logger.error("Your config.py looks unmodified! Fill the actual data to the file and retry. Exit."))

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))

app = Flask(__name__)  # Standard Flask app

web_hook = Webhook(app, config.WEBHOOK_ENDPOINT, config.WEBHOOK_SECRET)

logger.info("Program started.")


def process_push_event(data, conn):

    branch = data["ref"].replace('refs/heads/', '')
    git_repo_full_name = data["repository"]["full_name"]

    commits = data["commits"]

    fix_versions_regex = config.DEFAULT_FIX_VERSIONS_REGEX

    logger.debug('All commits: "%s"' % commits)

    issue_map = {}

    for commit in commits:
        issues = regexp_list_filter([commit["message"]], config.DEFAULT_GIT_ISSUE_NUMBER_MASKS)

        for issue in issues:
            if issue not in issue_map:
                issue_map[issue] = []
            author_issues_list = issue_map[issue]
            author_issues_list.append(CommitInfo(commit["author"]["email"], commit["id"], branch, commit["message"],
                                                 issue))

    for issue in issue_map:
        project_id = issue[0:issue.rfind('-')]

        if project_id not in config.YOUTRACK_PROJECTS:
            logger.warning(
                'Project from committer\'s comment not allowed: "%s". Skipping issue, mentioned in revisions %s.' % (
                    project_id, issue_map[issue]))
            continue

        if git_repo_full_name not in config.YOUTRACK_PROJECTS[project_id]["GITHUB_PROJECTS"]:
            logger.warning(
                'Full name not allowed: "%s". Skipping issue, mentioned in revisions %s.' % (
                    project_id, issue_map[issue]))
            continue

        if not config.YOUTRACK_PROJECTS[project_id]["COMMITTED_TO"]:
            committed_branches_field = None
        else:
            committed_branches_field = config.YOUTRACK_PROJECTS[project_id]["COMMITTED_TO"]

        if not config.YOUTRACK_PROJECTS[project_id]["FIX_VERSIONS"]:
            fix_versions_field = None
        else:
            fix_versions_field = config.YOUTRACK_PROJECTS[project_id]["FIX_VERSIONS"]

        issue_commits = issue_map[issue]

        commit_map = {}

        for commit_info in issue_commits:
            author = commit_info.author

            if author not in commit_map:
                commit_map[author] = []

            author_commits_list = commit_map[author]
            author_commits_list.append(commit_info)

        try:
            for author in commit_map:
                logger.info('Found commits by "%s" for issue "%s" :\n %s' % (author, issue, commit_map[author]))

                post_push_comment(issue, author, commit_map[author], conn, git_repo_full_name)
                post_push_info(issue, project_id, author, commit_map[author], conn, committed_branches_field,
                               fix_versions_field, fix_versions_regex)

        except Exception, ex:
            if '404: Not Found: Issue not found' in ex.message:
                commits_sha1_short = []

                for commit_info in issue_commits:
                    commit_sha1 = commit_info.revision[0:8]
                    commits_sha1_short.append(commit_sha1)

                logger.warning('Issue Not Found: %s, mentioned in commit %s. Skipping issue.' % (issue, ', '.join(commits_sha1_short)))
            else:
                raise


def post_push_comment(issue, author_login, author_commits_list, conn, git_repo_fullname):

    issue_comment = "Git changesets by +%s+ in *%s*:\n" % (author_login, git_repo_fullname)

    for commit in author_commits_list:
        changeset_link = config.DEFAULT_GITHUB_URL % (git_repo_fullname, commit.revision)

        issue_comment += "{monospace}[%s %s]{monospace} in *%s*: {noformat}%s{noformat}\n" % (
            changeset_link,
            commit.revision[0:8],
            commit.branch,
            commit.comment
        )

    # prevent duplicate comments
    comments = common.yt_get_issue_comments(conn, issue, logger)

    comment_found = False
    for comment in comments:
        if comment['text'] == issue_comment:
            comment_found = True
            logger.info('Duplicated comment found for issue %s. Skipping comment.' % issue)
            break

    if not comment_found:
        run_as = author_login

        if not config.LDAP_LOGIN_INCLUDES_EMAIL:
            if author_login.find(config.LDAP_EMAIL_DOMAIN) >= 0:
                run_as = author_login.replace(config.LDAP_EMAIL_DOMAIN, '')

            if (author_login.find('@') >= 0) and (author_login.find(config.LDAP_EMAIL_DOMAIN) < 0):
                run_as = None

        common.yt_add_simple_comment_to_issue(conn, issue, issue_comment, run_as, logger)


def post_push_info(issue, project_id, author_login, author_commits_list, conn, committed_branches_field,
                   fix_versions_field, fix_versions_regex):
    run_as = author_login

    if not config.LDAP_LOGIN_INCLUDES_EMAIL:
       if author_login.find(config.LDAP_EMAIL_DOMAIN) >= 0:
           run_as = author_login.replace(config.LDAP_EMAIL_DOMAIN, '')

       if (author_login.find('@') >= 0) and (author_login.find(config.LDAP_EMAIL_DOMAIN) < 0):
           run_as = None

    branches = set()
    for commit in author_commits_list:
        branches.add(commit.branch)

    for branch in branches:
        if committed_branches_field:
            if common.yt_get_project_has_custom_field(conn, project_id, committed_branches_field):
                logger.info('Adding "%s" custom field for issue: "%s", value: "%s"' % (
                    committed_branches_field,
                    issue,
                    branch))

                committed_field_bundle = common.yt_get_field_bundle(conn, project_id, committed_branches_field)

                common.yt_add_field_value(
                    conn,
                    issue,
                    committed_branches_field,
                    committed_field_bundle,
                    branch,
                    run_as)

                common.yt_add_value_to_issue_field(conn, issue, committed_branches_field, branch, run_as, logger)
            else:
                logger.warning(
                    '1 Field not found in YouTrack! Failed to set "%s" custom field for issue: "%s", value: "%s"' % (
                        committed_branches_field,
                        issue,
                        branch))

        if fix_versions_field:
            if common.yt_get_project_has_custom_field(conn, project_id, fix_versions_field):
                logger.info('Adding "%s" custom field for issue: "%s", value: "%s"' % (
                    fix_versions_field,
                    issue,
                    branch))
            else:
                logger.warning(
                    '2 Field not found in YouTrack! Failed to set "%s" custom field for issue: "%s", value: "%s"' % (
                        fix_versions_field,
                        issue,
                        branch))

                minor_version = common.find_minor_version(branch, fix_versions_regex)

                logger.debug('Minor version: %s' % minor_version)

                if minor_version or branch == 'master':
                    bundle_vals = common.yt_get_versions(conn, project_id)

                    latest_version = common.find_latest_version(bundle_vals, minor_version)

                    logger.debug('Latest version: %s' % latest_version)

                    if latest_version:
                        logger.info('Add fix version [Issue: "%s" Version: "%s"]' % (issue, latest_version))

                        common.yt_add_value_to_issue_field(conn, issue, fix_versions_field, latest_version, run_as)


@web_hook.hook()
def on_push(data):
    """
    Defines a handler for the 'push' event
    """

    logger.info("Received push event, before:" + data["before"][0:8] + ", after:" + data["after"][0:8])
    logger.debug("Got push event with: {0}".format(data))

    try:
        conn = Connection(config.DEFAULT_YOUTRACK_URL, config.DEFAULT_YOUTRACK_USER, config.DEFAULT_YOUTRACK_PASS)
    except Exception, ex:
        logger.error("Unable to connect to YouTrack!")
        logging.basicConfig(filename=config.LOG_FILE, level=logging.DEBUG)
        logging.exception('Got exception on main handler')
        raise

    try:
        process_push_event(data, conn)
    except Exception, ex:
        logger.error("Exception during push event processing")
        logging.basicConfig(filename=config.LOG_FILE, level=logging.DEBUG)
        logging.exception('Got exception on main handler')
        raise


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
