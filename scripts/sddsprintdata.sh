#!/bin/bash

#
# script made for datautils.py module, class: DataExtracter
# input parameters:
#  sddsfile: sdds file for data extracting, full name
#  datapath: full path for data

datapath=$1
cmdline=$2

cd ${datapath}
${cmdline}
#sddsprintout ${sddsfile} -notitle -nolabel \
#    -col=${kw1},format="%.16e" \
#    -col=${kw2},format="%.16e"
