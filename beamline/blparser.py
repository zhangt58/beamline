#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Python module for parsing MAD-8 lattice file, only used by matchwizard app (deprecated).

.. :Created Time: Sep. 23rd, 2014
.. :Author: Tong Zhang
"""


def madParser(mad_filename, idbl="BL"):
    """function to parse beamline with MAD-8 input format

    :param mad_filename: lattice filename with mad-8 like format
    :param idbl: beamline to be used that defined in lattice file, 
                 default value is ``BL``
    :return: list of dict that contains magnetic elements
    :rtype: list

    :Example:

    >>> import beamline
    >>> beamlinelist = beamline.blparser.madParser('LPA.list', 'BL2')
    >>> print beamlinelist
    >>> [{'type': 'drift', 'l': '0.1', 'ID': 'd0'}, {'type': 'quad', 'k1': '75', 'angle': '75', 'l': '0.1', 'ID': 'q1'}, {'type': 'drift', 'l': '0.18', 'ID': 'd3'}, {'type': 'quad', 'k1': '-75', 'angle': '75', 'l': '0.1', 'ID': 'q2'}, {'type': 'drift', 'l': '0.27', 'ID': 'd6'}, {'type': 'rbend', 'angle': '10', 'l': '0.1', 'ID': 'b1'}, {'type': 'drift', 'l': '1.0', 'ID': 'd8'}, {'type': 'rbend', 'angle': '-5', 'l': '0.1', 'ID': 'b2'}, {'type': 'drift', 'l': '0.45', 'ID': 'd4'}, {'type': 'quad', 'k1': '75', 'angle': '75', 'l': '0.1', 'ID': 'q1'}]

    .. only:: builder_html

    :download:`Download LPA.list <../../../lattice/LPA.list>` for reference.

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
            elementparams = dict(zip(ltmp1[0::2], ltmp1[1::2]))
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
