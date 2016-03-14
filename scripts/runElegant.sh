#!/bin/bash

#
# script made for simulation.py module
# input parameters:
#  elefile: .ele file for elegant tracking, full name
#  simpath: simulation path for data
#  simexec: elegant path
#

elefile=$1
simpath=$2
simexec=$3

cd ${simpath}
${simexec} ${elefile} >& /dev/null
