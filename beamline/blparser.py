#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python module for parsing MAD-8 lattice file
Created Time: Sep. 23rd, 2014
Author: Tong Zhang
"""


def madParser(mad_filename, idbl = "BL"):
    """
    function to parse beamline from MAD-8 input,
    return dict list contains magnetic elements
    usage: parseMAD(madfilnema)
    """
    """ # linux way
    cmd1 = "/bin/grep -m1 -i line " + mad_filename + " | sed 's/.*(\(.*\)).*/\\1/'"
    try:
        import subprocess
        beamline = subprocess.check_output(cmd1,shell=True).strip()
    except AttributeError:
        import os
        beamline = os.popen4(cmd1)[1].read().strip()
    """
    idbl = idbl.lower()
    for line in open(mad_filename, 'r'):
        line = ''.join(line.lower().strip().split())
        if line.startswith(idbl+':line'):
            beamline = line.replace(idbl + ':line=','').replace('(','').replace(')','').split(',')
            break

    try:
        fid = open(mad_filename, 'r')
        elementlist = []
        for element in beamline:
            while True:
                line = fid.readline().lower().strip()
                if line.startswith(element + ':'):
                    elementline = ''.join(line.split()).lower()
                    break
            if not line:
                print("element: " + element + " not found.")
                exit()

            fid.seek(0,0)
            idx1 = elementline.find(':')
            idx2 = elementline.find(',')
            elementtype = elementline[idx1+1:idx2]
            ltmp1 = elementline[idx2+1:].replace('=',' ').replace(',',' ').split()
            elementparams=dict(zip(ltmp1[0::2],ltmp1[1::2]))
            elementparams["type"] = elementtype
            elementparams["ID"] = element
            elementlist.append(elementparams)
        fid.close()
    except UnboundLocalError:
        print "beamline " + idbl + " not found"
        exit()
    
    return elementlist

def main():
    import sys
    mad_filename = sys.argv[1]
    elementlist = madParse(mad_filename)
    for i in range(len(elementlist)):
        print elementlist[i]

if __name__ == '__main__':
    main()
