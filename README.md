Patchtest
=========

Introduction
------------

Patchtest is a test framework for community patches based on the standard
unittest python module. As input, it needs tree elements to work propertly:
a patch in mbox format (either created with `git format-patch` or fetched
from 'patchwork'), a test suite and a target repository.

The first test suite intended to be used with patchtest is called patchtest-oe
[1], targeted for patches that get into the openembedded-core mailing list [2]
and corresponding repository [3].

Patchtest can either run on a host or a guest machine, depending on which
environment the execution needs to be done. If you plan to test your own patches
(a good practice before these are sent to the mailing list), the easiest way is
to install and execute on your local host; in the other hand, if automatic
testing is intended, the guest method is strongly recommended. Both methods are
fully explained in usage.adoc.

Installation and Usage
----------------------

Refer to the file 'usage.adoc' in this directory. 

Contributing
------------

The yocto mailing list (yocto@lists.yoctoproject.org) is used for questions,
comments and patch review.  It is subscriber only, so please register before
posting.

Send pull requests to yocto@lists.yoctoproject.org with '[patchtest]' in the
subject.

When sending single patches, please use something like:

    git send-email -M -1 --to=yocto@lists.yoctoproject.org  --subject-prefix=patchtest][PATCH

Maintenance
-----------

Maintainers:
    Paul Barker <pbarker@konsulko.com>

Links
-----
[1] https://git.yoctoproject.org/cgit/cgit.cgi/patchtest-oe/
[2] https://www.yoctoproject.org/tools-resources/community/mailing-lists
[3] https://git.openembedded.org/openembedded-core/
