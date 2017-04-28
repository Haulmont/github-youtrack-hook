# -*- coding: utf-8 -*-

import os
import re
import sys
from sets import Set

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'api'))
from youtrack import YouTrackException


def regexp_list_filter(list_to_filter, regexps, unique=True):
    matches = []
    for regexp in regexps:
        matches.extend(
            reduce(
                lambda x,y: x+y,
                filter(
                    lambda x: True if len(x) > 0 else False,
                    map(
                        lambda x: re.findall(regexp, x),
                        list_to_filter
                    )
                ),
                []
            )
        )

    if unique:
        matches = list(Set(matches))

    return matches


def find_minor_version(branch_name, branch_regex):
    vals = re.findall(branch_regex, branch_name)
    if vals and vals[0] and len(vals[0]) == 2:
        return vals[0][0] + '.' + vals[0][1]
    else:
        return None


def find_latest_version(versions, minor_version):
    # drop ugly versions, e.g. Release Bla Bla
    versions = filter(lambda x: all(part.isdigit() for part in x.split('.')), versions)

    def versions_cmp(x, y):
        nums_x = map(lambda s: int(s), x.split('.'))
        nums_y = map(lambda s: int(s), y.split('.'))
        return cmp(nums_x, nums_y)

    sorted_versions = sorted(versions, cmp=versions_cmp, reverse=True)

    if not sorted_versions:
        return None

    if not minor_version:
        return sorted_versions[0]
    else:
        nums_minor = map(lambda s: int(s), minor_version.split('.'))
        if len(nums_minor) == 2:
            for v in sorted_versions:
                nums_v = map(lambda s: int(s), v.split('.'))
                if len(nums_v) >= 2 and nums_v[0] == nums_minor[0] and nums_v[1] == nums_minor[1]:
                    return v

    return None


def yt_get_versions(connection, project_id):
    return map(lambda x: x.name, connection.getVersions(project_id))


def yt_add_field_value(connection, issue, field, bundle, value, run_as_user=None):
    yt_add_value_to_bundle(connection, bundle, value)
    yt_add_value_to_issue_field(connection, issue, field, value, run_as_user)


def yt_get_field_bundle(connection, projectId, field, logger=None):
    projectCustomField = connection.getProjectCustomField(projectId, field)

    return projectCustomField["bundle"]

def yt_add_value_to_bundle(connection, bundle, value, logger=None):
    if logger is not None:
        logger.info('Adding "%s" to "%s" bundle' % (value, bundle))

    try:
        connection.addValueToEnumBundle(bundle, value)
    except YouTrackException, ex:
        if re.match('.*Enum bundle value .* already exists\.', ex.message):
            pass
        else:
            raise


def yt_add_value_to_issue_field(connection, issue, field, value, run_as_user=None, logger=None):
    if logger is not None:
        logger.info('Marking "%s" in issue "%s"' % (value, issue))

    try:
        connection.executeCommand(issue, 'add %s %s' % (field, value), run_as=run_as_user)
    except Exception, ex:
        if ('404: Not Found: No such user [ User ] not found' in ex.message)\
                or ('400: Bad Request: Command [comment] is invalid:Unknown command'):
            if logger is not None:
                logger.warning('User "%s" does not exist OR has no access to the issue: %s. Marking the issue as a System User.' % (run_as_user, issue))
            connection.executeCommand(issue, 'add %s %s' % (field, value), run_as=None)
        else:
            raise


def yt_get_issue_comments(connection, issue, logger=None):
    if logger is not None:
        logger.debug('Getting comments for issue "%s"' % issue)
        return connection.getComments(issue)


def yt_get_project_has_custom_field(connection, project_id, custom_field_name):
    fields = connection.getProjectCustomFields(project_id)
    for field in fields:
        if field.name == custom_field_name:
            return True
    return False


def yt_add_simple_comment_to_issue(connection, issue, comment, run_as_user=None, logger=None):
    if logger is not None:
        logger.info('Adding comment "%s" to issue "%s"' % (comment, issue))
        try:
            connection.executeCommand(issue, 'comment', comment=comment, run_as=run_as_user)
        except Exception, ex:
            if ('404: Not Found: No such user [ User ] not found' in ex.message)\
                    or ('400: Bad Request: Command [comment] is invalid:Unknown command'):
                logger.warning('User "%s" does not exist OR has no access to the issue: %s. Commenting as a System User.' % (run_as_user, issue))
                connection.executeCommand(issue, 'comment', comment=comment, run_as=None)
            else:
                raise
