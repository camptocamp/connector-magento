# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from __future__ import print_function

import fileinput
from datetime import date
from distutils.version import StrictVersion

from invoke import exceptions, task
from marabunta.version import MarabuntaVersion

from .common import (
    GIT_REMOTE_NAME,
    HISTORY_FILE,
    MIGRATION_FILE,
    PENDING_MERGES,
    VERSION_FILE,
    build_path,
    cd,
    check_git_diff,
    cookiecutter_context,
    current_version,
    exit_msg,
)

try:
    from builtins import input
except ImportError:
    print('Missing install future from requirements')
    print('Please run `pip install -r tasks/requirements.txt`')

try:
    import yaml
except ImportError:
    print('Missing install pyyaml from requirements')
    print('Please run `pip install -r tasks/requirements.txt`')

try:
    import clipboard
except ImportError:
    print('Missing clipboard from requirements')
    print('Please run `pip install -r tasks/requirements.txt`')


@task(name='push-branches')
def push_branches(ctx, force=False):
    """ Push the local branches to the camptocamp remote

    The branch name will be composed of the id of the project and the current
    version number (the one in odoo/VERSION).

    It should be done at the closing of every release, so we are able
    to build a new patch branch from the same commits if required.
    """
    version = current_version()
    project_id = cookiecutter_context()['project_id']
    branch_name = 'merge-branch-{}-{}'.format(project_id, version)
    response = input('Push local branches to {}? (Y/n) '.format(branch_name))
    if response in ('n', 'N', 'no'):
        exit_msg('Aborted')
    if not force:
        check_git_diff(ctx)
    print('Pushing pending-merge branches...')
    with open(PENDING_MERGES, 'rU') as f:
        merges = yaml.load(f.read())
        if not merges:
            print('Nothing to push')
            return
        for path, setup in merges.items():
            print('pushing {}'.format(path))
            with cd(build_path(path, from_file=PENDING_MERGES)):
                try:
                    ctx.run('git config remote.{}.url'.format(GIT_REMOTE_NAME))
                except exceptions.Failure:
                    remote_url = setup['remotes'][GIT_REMOTE_NAME]
                    ctx.run(
                        'git remote add {} {}'.format(
                            GIT_REMOTE_NAME, remote_url
                        )
                    )
                ctx.run(
                    'git push -f -v {} HEAD:refs/heads/{}'.format(
                        GIT_REMOTE_NAME, branch_name
                    )
                )


def release_get_next_version3digits(old_version, feature=True, patch=False):
    """Backward compat for old 3-digits versionins.

    TODO: trash it as we move all projects to 5 digits.
    """
    warning = (
        'You are still using OLD 3-digits versioning. '
        'Please, consider moving to new versioning w/ 5 digits.'
    )
    print()
    print('!' * len(warning))
    print(warning)
    print('!' * len(warning))
    print()
    try:
        version = StrictVersion(old_version).version
    except ValueError:
        exit_msg("'{}' is not a valid version".format(old_version))
    if feature:
        new_version = (version[0], version[1] + 1, 0)
    elif patch:
        new_version = (version[0], version[1], version[2] + 1)
    return '.'.join([str(v) for v in new_version])


def release_get_next_version(
    old_version, major=False, feature=True, patch=False
):
    if len(old_version.split('.')) == 3:
        if major:
            # not supported here
            feature = True
        return release_get_next_version3digits(
            old_version, feature=feature, patch=patch
        )
    try:
        version = MarabuntaVersion(old_version).version
    except ValueError:
        exit_msg("'{}' is not a valid version".format(old_version))
    if major:
        new_version = list(version[:2]) + [version[2] + 1, 0, 0]
    elif feature:
        new_version = list(version[:-2]) + [version[-2] + 1, 0]
    elif patch:
        new_version = list(version[:-1]) + [version[-1] + 1]
    return '.'.join([str(v) for v in new_version])


@task
def bump(ctx, major=False, feature=False, patch=False, print_only=False):
    """ Increase the version number where needed """
    if not (major or feature or patch):
        exit_msg("should be a --major or --feature or a --patch version")
    old_version = current_version()
    if not old_version:
        exit_msg("the version file is empty")

    version = release_get_next_version(
        old_version, major=major, feature=feature, patch=patch
    )

    print(
        'Increasing version number from {} '
        'to {}...'.format(old_version, version)
    )
    print()
    if print_only:
        exit_msg('PRINT ONLY mode on. Exiting...')

    try:
        ctx.run(
            r'grep --quiet --regexp "- version:.*{}" {}'.format(
                version, MIGRATION_FILE
            )
        )
    except exceptions.Failure:
        with open(MIGRATION_FILE, 'a') as fd:
            fd.write('    - version: {}\n'.format(version))

    with open(VERSION_FILE, 'w') as fd:
        fd.write(version + '\n')

    new_version_index = None
    for index, line in enumerate(fileinput.input(HISTORY_FILE, inplace=True)):
        # Weak heuristic to find where we should write the new version
        # header, anyway, it will need manual editing to have a proper
        # changelog
        if 'unreleased' in line.lower():
            # place the new header 2 lines after because we have the
            # underlining
            new_version_index = index + 2
        if index == new_version_index:
            today = date.today().strftime('%Y-%m-%d')
            new_version_header = "{} ({})".format(version, today)
            print(
                "\n**Features and Improvements**\n\n"
                "**Bugfixes**\n\n"
                "**Build**\n\n"
                "**Documentation**\n\n\n"
                "{}\n"
                "{}".format(new_version_header, '+' * len(new_version_header))
            )

        print(line, end='')

    push_branches(ctx, force=True)

    clipboard.copy(version)

    print()
    print('** Version changed to {} **'.format(version))
    print()
    print('Version {} has been copied to your clipboard'.format(version))
    print()
    print('Please continue with the release by:')
    print()
    print(' * Cleaning HISTORY.rst. Remove the empty sections, empty lines...')
    print(' * Check the diff then run:')
    print('      git add ... # pick the files ')
    print('      git commit -m"Release {}"'.format(version))
    print(
        '      git tag -a {}  '
        '# optionally -s to sign the tag'.format(version)
    )
    print(
        '      # copy-paste the content of the release from HISTORY.rst'
        ' in the annotation of the tag'
    )
    print('      git push --tags && git push')
