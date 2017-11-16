FILESEXTRAPATHS_prepend := "${THISDIR}/${PN}:"

SRC_URI_append =" file://patchtest"

inherit useradd

USERADD_PACKAGES = "${PN}"
USERADD_PARAM_${PN} = "-u 1200 -r -m -s /bin/sh patchtest"

do_install_append () {
	install -m 0755 ${WORKDIR}/patchtest ${D}${sysconfdir}/init.d
	update-rc.d -r ${D} patchtest start 99 3 5 .
}


