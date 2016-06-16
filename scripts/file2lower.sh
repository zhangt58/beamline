#!/bin/bash
# 
# translate file content to lower alphabets
#
# input filenames as parameters
# 
# Author: Tong Zhang
# Dated: 2016-03-21
#

filenames="$@"
for fn in ${filenames}
do
    cat ${fn} | tr [A-Z] [a-z] > tmpfn.$$
    
    mv tmpfn.$$ ${fn}
done
