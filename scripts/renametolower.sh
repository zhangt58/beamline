#!/bin/bash
# 
# rename filenames to be lower alphabets
#
# input filenames as parameters
# 
# Author: Tong Zhang
# Dated: 2016-03-21
#

filenames="$@"
cnt=0
for fn in ${filenames}
do
    newfn=$(echo ${fn} | tr [A-Z] [a-z])
    if [ "x${fn}" != "x${newfn}" ]
    then
        printf "Rename %10s to %10s\n" ${fn} ${newfn}
        mv ${fn} ${newfn} 
        cnt=$((cnt+1))
    fi
done
echo "----------------------------"
printf "Total renamed %d files\n" $cnt
