#
# Copyright (C) 2016 Intel Corporation
#
SUMMARY = "Patchtest-oe package groups"
DESCRIPTION = "Packages required to run patchtest-oe test cases using patchtest"

inherit packagegroup

RDEPENDS_${PN} = "\
    python3-pyparsing \
    python3-unidiff \
    python3-pylint \
    "
