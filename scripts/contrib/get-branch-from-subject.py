#!/usr/bin/env python3
#
# Extract subject prefixes from mboxes
#
import re
import argparse


def get_subject_prefix(data):
    prefix = ""
    pattern1 = re.compile("(?<=Subject: )(\[.*\])")

    for subject in data.split("\n"):
        match1 = pattern1.search(subject)
        if match1:
            prefix = match1.group(1)
            break

    return prefix


def valid_branch(branch):
    """Check if branch is valid name"""
    lbranch = branch.lower()

    invalid = (
        lbranch.startswith("patch")
        or lbranch.startswith("rfc")
        or lbranch.startswith("resend")
        or re.search("^v\d+", lbranch)
        or re.search("^\d+/\d+", lbranch)
    )

    return not invalid


def get_branch(filename):
    f = open(filename, "r")
    data = f.read()

    fullprefix = get_subject_prefix(data)
    branch, branches, valid_branches = None, [], []

    if fullprefix:
        prefix = fullprefix.strip("[]")
        branches = [b.strip() for b in prefix.split(",")]
        valid_branches = [b for b in branches if valid_branch(b)]

    if len(valid_branches):
        branch = valid_branches[0]

    return (fullprefix, branch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get branches from mboxes")
    parser.add_argument("mboxs", nargs="+", help="Pathname of the mbox file")
    args = parser.parse_args()

    for mbox in args.mboxs:
        fullprefix, branch = get_branch(mbox)
        print("%s:%s:%s" % (mbox, fullprefix, branch))
