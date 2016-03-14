#!/usr/bin/env python

#
# -*- coding: utf-8 -*-
#

infile = 'linac.lte'
#infile = 'tmp.lte'
beamlinename = 'bl'

idbl = beamlinename.lower()
line_continue_flag = ''
appendflag = False
for line in open(infile, 'r'):
    if line.strip() == '': continue
    line = ''.join(line.lower().strip().split())
    if line.startswith('!'): continue
    if line.startswith(idbl+':line'):
        blist = []
        blist.append(line)
        appendflag = True
    elif appendflag and line_continue_flag == '&':
        blist.append(line)
    line_continue_flag = line[-1]
        
rlist = ''.join(blist).replace('&','')
print(rlist)

class BParser(object):
    def __init__(self, blfile):
        pass
        
class BeamlineParser(BParser):
    pass

def findElement():
    pass

import parser
def testJsonParser():
    infile = 'tmp.json'
    testjp = parser.JsonParser(infile)
    readdict = testjp.toDict()
    testjp.printDict()

    bl = readdict['bl']['line'].replace('(','').replace(')','').replace(',','').split()
    print bl
    for ele in bl:
        try:
            for (k,v) in readdict[ele].items():
                print("%s : %s" % (k, v))
        except:
            pass

if __name__ == '__main__':
    testJsonParser()
