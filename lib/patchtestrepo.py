# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# patchtestrepo: Repo class used mainly to control a git repo from patchtest
#
# Copyright (C) 2016 Intel Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import utils
import logging
import json
import patchtestpatch

logger = logging.getLogger("patchtest")
info = logger.info


class Repo(object):

    # prefixes used for temporal branches/stashes
    prefix = "patchtest"

    def __init__(self, patch, repodir, commit=None, branch=None):
        self._repodir = repodir
        self._patch = patchtestpatch.Patch(patch)
        self._current_branch = self._get_current_branch()

        # targeted branch defined on the patch may be invalid, so make sure there
        # is a corresponding remote branch
        valid_patch_branch = None
        if self._patch.branch in self.upstream_branches():
            valid_patch_branch = self._patch.branch

        # Target Branch
        # Priority (top has highest priority):
        #    1. branch given at cmd line
        #    2. branch given at the patch
        #    3. current branch
        self._branch = branch or valid_patch_branch or self._current_branch

        # Target Commit
        # Priority (top has highest priority):
        #    1. commit given at cmd line
        #    2. branch given at cmd line
        #    3. branch given at the patch
        #    3. current HEAD
        self._commit = (
            self._get_commitid(commit)
            or self._get_commitid(branch)
            or self._get_commitid(valid_patch_branch)
            or self._get_commitid("HEAD")
        )

        self._workingbranch = "%s_%s" % (Repo.prefix, os.getpid())

        # create working branch
        self._exec(
            {"cmd": ["git", "checkout", "-b", self._workingbranch, self._commit]}
        )

        self._patchmerged = False

        # Check if patch can be merged using git-am
        self._patchcanbemerged = True
        try:
            self._exec(
                {"cmd": ["git", "am", "--keep-cr"], "input": self._patch.contents}
            )
        except utils.CmdException as ce:
            self._exec({"cmd": ["git", "am", "--abort"]})
            self._patchcanbemerged = False
        finally:
            # if patch was applied, remove it
            if self._patchcanbemerged:
                self._exec({"cmd": ["git", "reset", "--hard", self._commit]})

        # for debugging purposes, print all repo parameters
        logger.debug("Parameters")
        logger.debug("\tRepository     : %s" % self._repodir)
        logger.debug("\tTarget Commit    : %s" % self._commit)
        logger.debug("\tTarget Branch    : %s" % self._branch)
        logger.debug("\tWorking branch : %s" % self._workingbranch)
        logger.debug("\tPatch          : %s" % self._patch)

    @property
    def patch(self):
        return self._patch.path

    @property
    def branch(self):
        return self._branch

    @property
    def commit(self):
        return self._commit

    @property
    def ismerged(self):
        return self._patchmerged

    @property
    def canbemerged(self):
        return self._patchcanbemerged

    def _exec(self, cmds):
        _cmds = []
        if isinstance(cmds, dict):
            _cmds.append(cmds)
        elif isinstance(cmds, list):
            _cmds = cmds
        else:
            raise utils.CmdException({"cmd": str(cmds)})

        results = []
        cmdfailure = False
        try:
            results = utils.exec_cmds(_cmds, self._repodir)
        except utils.CmdException as ce:
            cmdfailure = True
            raise ce
        finally:
            if cmdfailure:
                for cmd in _cmds:
                    logger.debug("CMD: %s" % " ".join(cmd["cmd"]))
            else:
                for result in results:
                    cmd, rc, stdout, stderr = (
                        " ".join(result["cmd"]),
                        result["returncode"],
                        result["stdout"],
                        result["stderr"],
                    )
                    logger.debug(
                        "CMD: %s RCODE: %s STDOUT: %s STDERR: %s"
                        % (cmd, rc, stdout, stderr)
                    )

        return results

    def _get_current_branch(self, commit="HEAD"):
        cmd = {"cmd": ["git", "rev-parse", "--abbrev-ref", commit]}
        cb = self._exec(cmd)[0]["stdout"]
        if cb == commit:
            logger.warning(
                "You may be detached so patchtest will checkout to master after execution"
            )
            cb = "master"
        return cb

    def _get_commitid(self, commit):

        if not commit:
            return None

        try:
            cmd = {"cmd": ["git", "rev-parse", "--short", commit]}
            return self._exec(cmd)[0]["stdout"]
        except utils.CmdException as ce:
            # try getting the commit under any remotes
            cmd = {"cmd": ["git", "remote"]}
            remotes = self._exec(cmd)[0]["stdout"]
            for remote in remotes.splitlines():
                cmd = {
                    "cmd": ["git", "rev-parse", "--short", "%s/%s" % (remote, commit)]
                }
                try:
                    return self._exec(cmd)[0]["stdout"]
                except utils.CmdException:
                    pass

        return None

    def upstream_branches(self):
        cmd = {"cmd": ["git", "branch", "--remotes"]}
        remote_branches = self._exec(cmd)[0]["stdout"]

        # just get the names, without the remote name
        branches = set(branch.split("/")[-1] for branch in remote_branches.splitlines())
        return branches

    def merge(self):
        if self._patchcanbemerged:
            self._exec(
                {
                    "cmd": ["git", "am", "--keep-cr"],
                    "input": self._patch.contents,
                    "updateenv": {"PTRESOURCE": self._patch.path},
                }
            )
            self._patchmerged = True

    def clean(self):
        self._exec({"cmd": ["git", "checkout", "%s" % self._current_branch]})
        self._exec({"cmd": ["git", "branch", "-D", self._workingbranch]})
        self._patchmerged = False
