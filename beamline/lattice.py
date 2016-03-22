#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classes/routines to handle lattice issues for online model and runtime calculation

class LteParser: parse elegant lattice definition files for simulation
    1: convert lte file into dict/json format for further usage;
    2: resolve rpn expressions within element definitions;
    3: retain prefixed information of lte file as '_prefixstr' key in json/dict;

class Lattice: handle lattice issues from json/dict definition
    1: instantiate with json/dict lattice definition, e.g. from LteParser.file2json();
    2: generate lte file for elegant simulation;
    3: iteratively expand the beamline definition in lte file;
    4: generate lte file after manipulations.

Author      : Tong Zhang
Created     : 2016-01-28
Last updated: 2016-03-08
"""

import json
import time
import os
from pyrpn import rpn

class LteParser(object):
    def __init__(self, infile):
        self.infile = infile

        self.confstr = ''    # configuration string line for given element
        self.confdict = {}   # configuration string line to dict
        self.confjson = {}   # configuration string line to json
        self.prestrdict = {} # prefix string line to dict, e.g. line starts with '%'
        
        self.stodict = {}    # sto key-value dict
        self.resolvePrefix() # sto string information

    def resolvePrefix(self):
        """ extract prefix information into dict with the key of '_prefixstr'
        """
        tmpstrlist = []
        for line in open(self.infile, 'r'):
            if line.startswith('%'):
                stolist = line.replace('%','').split('sto')
                rpnexp = stolist[0] # rpn expression
                rpnvar = stolist[1].strip() # rpn variable
                rpnval = rpn.Rpn.solve_rpn(rpnexp)
                stostr = '% {val} sto {var}'.format(val = rpnval, var = rpnvar)
                tmpstrlist.append(stostr)
                self.stodict[rpnvar] = rpnval
        self.prestrdict['_prefixstr'] = tmpstrlist

    def getKw(self, kw):
        """ Extract doc snippet for element configuration,
            :param kw: element name
            return: one line of configuration string

        USAGE: getKw('Q10')
        """
        ikw = kw.lower()
        line_continue_flag = ''
        appendflag = False
        try:
            for line in open(self.infile, 'r'):
                if line.strip() == '': continue
                line = ' '.join(line.strip().split())
                if line.startswith('!'): continue
                if line.lower().startswith(ikw + ' :') or line.lower().startswith(ikw + ':'):
                    conflist = [] # list to put into element configuration
                    conflist.append(line)
                    appendflag = True
                elif appendflag and line_continue_flag == '&':
                    conflist.append(line)
                line_continue_flag = line[-1]
                if line_continue_flag != '&': appendflag = False
            conf_str = ''.join(conflist).replace('&',',')
            if 'line' in conf_str.lower().split('=')[0]: # if bl defines lattice
                conf_str = conf_str.lower().replace(',',' ')[::-1].replace('enil','beamline,lattice'[::-1],1)[::-1] # avoid the case with bl keyword has 'line'
        except:
            conf_str = ''

        self.confstr = conf_str

        return self

    def toDict(self):
        """ convert self.confstr to dict, could apply chain rule, write to self.confdict
        
        USAGE: ins = LteParser(infile)
               ins.getKw(kw).toDict()
        """
        self.confdict = self.str2dict(self.confstr)
        return self

    def str2dict(self, rawstr):
        """ convert str to dict format

        USAGE: rdict = str2dict(rawstr)
        """
        kw_list = []
        sp1     = rawstr.split(':')
        kw_name = sp1[0].strip().upper()
        kw_desc = sp1[1:]
        sp2     = kw_desc[0].replace(',',';;',1).split(';;')
        kw_type = sp2[0].strip()
        try:
            kw_vals = sp2[1].replace(",",'=').split('=')
            [(not (i.isspace() or i == '')) and kw_list.append(i) for i in kw_vals]
            ks = [k.strip() for k in kw_list[0::2]]
            vs = [v.strip().replace('"','').replace("'",'') for v in kw_list[1::2]]
            kw_vals_dict = dict(zip(ks,vs))
            rdict = {kw_name: {kw_type: kw_vals_dict}}
        except:
            rdict = {kw_name: kw_type}
        return rdict

    def dict2json(self, idict):
        """ convert dict into json

        USAGE: rjson = dict2json(idict)
        """
        return json.dumps(idict)

    def getKwAsJson(self, kw):
        """ return keyword configuration as a json

        Usage: rjson = getKwAsJson(kw)
        """
        return self.dict2json(self.getKwAsDict(kw))

    def getKwAsDict(self, kw):
        """ return keyword configuration as a dict

        Usage: rdict = getKwAsDict(kw)
        """
        self.getKw(kw)
        return self.str2dict(self.confstr)

    def detectAllKws(self):
        """ Detect all keyword from infile, return as a list
        
        USAGE: kwslist = detectAllKws()
        """
        kwslist = []
        for line in open(self.infile, 'r'):
            #if line.strip() == '': continue
            line = ''.join(line.strip().split())
            if line.startswith("!"): continue
            #if ':' in line and not "line" in line:
            if ':' in line:
                kwslist.append(line.split(':')[0])
        return kwslist

    def file2json(self, jsonfile = None):
        """ Convert entire lte file into json like format
        
        USAGE: 1: kwsdictstr = file2json()
               2: kwsdictstr = file2json(jsonfile = 'somefile')

        show pretty format with pipeline: | jshon, or | pjson
        if jsonfile is defined, dump to defined file before returning json string
        """
        kwslist = self.detectAllKws()
        kwsdict = {}
        idx = 0
        for kw in sorted(kwslist, key = str.lower):
            #print kw
            idx += 1
            tdict = self.getKwAsDict(kw)
            self.rpn2val(tdict)
            kwsdict.update(tdict)
        kwsdict.update(self.prestrdict)
        try:
            with open(os.path.expanduser(jsonfile), 'w') as outfile:
                json.dump(kwsdict, outfile)
        except:
            pass
        return json.dumps(kwsdict)

    def scanStoVars(self, strline):
        """ scan input string line, replace sto parameters with calculated results.
        """
        for wd in strline.split():
            if self.stodict.has_key(wd):
                strline = strline.replace(wd, str(self.stodict[wd]))
        return strline

    def rpn2val(self, rdict):
        # {"b11": {"csrcsben": {"hgap": "1.500000000e-02", "integration_order": "4", "nonlinear": "1", "angle": "10.24pi*180/", "n_kicks": "100", "l": "0.210.24pi*180/*10.24pi*180/sin/", "edge1_effects": "1", "edge2_effects": "1", "block_csr": "0", "sg_halfwidth": "1", "csr": "csr_on_off", "e1": "0.000000000e+00", "bins": "512", "e2": "10.24pi*180/"}}}
        """ Resolve the rpn string into calulated float number

        USAGE: rpn2val(rdict)
            :param rdict: json like dict
        """

        kw_name  = rdict.keys()[0] # b11
        kw_val   = rdict[kw_name] 
        try:
            kw_type  = kw_val.keys()[0] # csrcsben
            kw_param = kw_val.values()[0]
            if kw_type != 'beamline':
                for k,v in kw_param.items():
                    try:
                        v = self.scanStoVars(v)
                        kw_param[k] = rpn.Rpn.solve_rpn(v) # update rpn string to float
                    except: # cannot solve rpn string
                        pass
        except: 
            pass # element that only has type name, e.g. {'bpm01': 'moni'}

    def solve_rpn(self):
        """ solve rpn string in self.confdict, and update self.confdict
        
        USAGE: ins = LteParser(infile)
               ins.getKw(kw).toDict().solve_rpn()
        """
        self.rpn2val(self.confdict)
        return self

#===========================================================================

class Lattice(object):
    """ class for handling lattice configurations and operations
    """
    def __init__(self, elements):
        """ initialize the class with input elements

            elements should be dict converted from json, 
            if not convert first by json.loads(elements)
        """
        if isinstance(elements, str): 
            self.all_elements = json.loads(elements)
        else: # elements is dict already
            self.all_elements = elements

        self.kws_ele, self.kws_bl = self.getAllKws()

    def dumpAllElements(self):
        """ dump all element configuration lines as json format.
        """
        return json.dumps(self.all_elements)

    def getAllEle(self):
        """ return all element keywords
        """
        return self.kws_ele

    def getAllBl(self):
        """ return all beamline keywords
        """
        return self.kws_bl
    
    def getBeamline(self, beamlineKw):
        """ get beamline definition from all_elements, return as a list
        """
        lattice_string = self.all_elements.get(beamlineKw.upper()).values()[0].get('lattice')
        return lattice_string[1:-1].split() # drop leading '(' and trailing ')' and split into list

    def getFullBeamline(self, beamlineKw, extend = False):
        """ get beamline definition from all_elements,
            expand iteratively with the elements from all_elements
            e.g. 
            element 'doub1' in 
            chi   : line=(DBLL2 , doub1 , DP4FH , DP4SH , DBLL5 , DBD   , 
                          B11   , DB11  , B12   , DB12  , PF2   , DB13  , 
                          B13   , DB14  , B14   , DBD   , DBLL5 , doub2 ,
                          DP5FH , DP5SH , DBLL2 , PSTN1)
            should be expaned with 'doub1' configuration:
            doub1 : line=(DQD3, Q05, DQD2, Q06, DQD3)

            since:
            getBeamline('doub1') = [u'dqd3', u'q05', u'dqd2', u'q06', u'dqd3'] = A
            getBeamline('doub2') = [u'dqd3', u'q05', u'dqd2', u'q06', u'dqd3'] = B
            getBeamline('chi') = [u'dbll2', u'doub1', u'dp4fh', u'dp4sh', u'dbll5', u'dbd', u'b11', u'db11', u'b12', u'db12', u'pf2', u'db13', u'b13', u'db14', u'b14', u'dbd', u'dbll5', u'doub2', u'dp5fh', u'dp5sh', u'dbll2', u'pstn1']

            thus: getFullBeamline('chi') should return:
            [u'dbll2', A, u'dp4fh', u'dp4sh', u'dbll5', u'dbd', u'b11', u'db11', u'b12', u'db12', u'pf2', u'db13', u'b13', u'db14', u'b14', u'dbd', u'dbll5', B, u'dp5fh', u'dp5sh', u'dbll2', u'pstn1']

            if extend = True, element like '2*D01' would be expended to be D01, D01
        """
        try:
            assert beamlineKw.upper() in self.kws_bl
            rawbl = self.getBeamline(beamlineKw)
            fullbl = []
            if not extend:
                for ele in rawbl:
                    if self.isBeamline(ele):
                        fullbl.extend(self.getFullBeamline(ele))
                    else: # if not beamline, do not expand
                        fullbl.append(ele)
            else: # extend
                for ele in rawbl:
                    ele_num_name_dict = self.rinseElement(ele)
                    elename = ele_num_name_dict['name']
                    elenum  = ele_num_name_dict['num']
                    if self.isBeamline(elename):
                        fullbl.extend(self.getFullBeamline(elename, extend = True) * elenum)
                    else:
                        fullbl.extend([elename] * elenum)
            return fullbl
        except AssertionError:
            print('ERROR: %s is not a right defined beamline.' % beamlineKw)

    def isBeamline(self, kw):
        """ test if kw is a beamline
        """
        return kw.upper() in self.kws_bl
            
    def getAllKws(self):
        """ extract all keywords into two categories
            
            kws_ele: magnetic elements
            kws_bl: beamline elements

            return (kws_ele, kws_bl)
        """
        kws_ele = []
        kws_bl  = []
        for ele in self.all_elements:
            if ele == '_prefixstr':
                continue
            elif self.getElementType(ele).lower() == u'beamline':
                kws_bl.append(ele)
            else:
                kws_ele.append(ele)

        return tuple((kws_ele, kws_bl))

    def showBeamlines(self):
        """ show all defined beamlines
        """
        cnt = 0
        blidlist = []
        for k in self.all_elements:
            try:
                if self.all_elements.get(k).has_key('beamline'):
                    cnt += 1
                    blidlist.append(k)
            except:
                pass
        retstr = '{total:<3d}beamlines: {allbl}'.format(total = cnt,
                allbl = ';'.join(blidlist))
        print(retstr)

        return retstr

    def getElementType(self, elementKw):
        """ return type name for given element keyword,
            e.g. getElementType('Q01') should return string: 'QUAD'
        """
        try:
            etype = self.all_elements.get(elementKw.upper()).keys()[0]
        except:
            etype = self.all_elements.get(elementKw.upper())
        return etype.upper()

    def getElementConf(self, elementKw, raw = False):
        """ return configuration for given element keyword,
            e.g. getElementConf('Q01') should return dict: {u'k1': 0.0, u'l': 0.05}
        """
        if raw == True:
            try:
                econf = self.all_elements.get(elementKw.upper())
            except:
                return {}
        else:
            try:
                econf = self.all_elements.get(elementKw.upper()).values()[0]
            except:
                return {}
        return econf

    def formatElement(self, kw, format = 'elegant'):
        """ convert json/dict of element configuration into elegant/mad format
        """
        etype = self.getElementType(kw) 
        econf_dict = self.getElementConf(kw)
        econf_str = ''
        for k,v in econf_dict.items():
            econf_str += (k + ' = ' + '"' + str(v) + '"' + ', ')
        
        if format == 'elegant':
            fmtstring = '{eid:<6s}:{etype:>10s}, {econf}'.format(eid   = kw.upper(),
                                                                 etype = etype.upper(),
                                                                 econf = econf_str[:-2]) # [:-2] slicing to remove trailing space and ','
        elif format == 'mad':
            pass

        return fmtstring

    def generateLatticeLine(self, latname = 'newline', line = None):
        """ construct a new lattice line
        """
        latticeline = []
        for e in line:
            if isinstance(e, list):
                latticeline.extend(e)
            else:
                latticeline.append(e)

        newblele = {latname.upper():{'beamline':{'lattice':'('+' '.join(latticeline)+')'}}}
        self.all_elements.update(newblele)
        self.kws_bl.append(latname.upper())
        return newblele

    def generateLatticeFile(self, beamline, filename, format = 'elegant'):
        """ generate simulation files for lattice analysis,
            e.g. ".lte" for elegant, ".madx" for madx

            input parameters:
            beamline: keyword for beamline
            filename: name of lte/mad file
            format: madx, elegant, 
                    'elegant' by default, generated lattice is for elegant tracking
        """

        """
        if not self.isBeamline(beamline):
            print("%s is a valid defined beamline, do not process." % (beamline))
            return False
        """

        f = open(os.path.expanduser(filename), 'w')

        # write filehead, mainly resolving prefix string lines
        cl1 = "This file is automatically generated by 'generateLatticeFile()' method,"
        cl2 = 'could be used as ' + format + ' lattice file.'
        cl3 = 'Author: Tong Zhang (zhangtong@sinap.ac.cn)'
        cl4 = 'Generated Date: ' + time.strftime('%Y-%m-%d %H:%M:%S %Z',time.localtime())

        f.write('!{str1:<73s}!\n'.format(str1='-'*73))
        f.write('!{str1:^73s}!\n'.format(str1=cl1))
        f.write('!{str1:^73s}!\n'.format(str1=cl2))
        f.write('!{str1:^73s}!\n'.format(str1='-'*24))
        f.write('!{str1:^73s}!\n'.format(str1=cl3))
        f.write('!{str1:^73s}!\n'.format(str1=cl4))
        f.write('!{str1:<73s}!\n'.format(str1='-'*73))
        f.write('\n')
        
        """ do not need to dump stoed variables now, 2016-03-21
        # write global variables
        f.write('! {str1:<73s}\n'.format(str1= 'Global variable definitions:'))
        f.write('\n'.join(self.all_elements['_prefixstr']))
        f.write('\n')
        f.write('\n')
        """
        
        # write element definitions and lattice
        f.write('! {str1:<72s}\n'.format(str1= 'Element definitions:'))
        elelist = self.getFullBeamline(beamline, extend = True)
        if self.getElementType(elelist[0]) != 'CHARGE':
            elelist.insert(0, self.getChargeElement())
        for ele in sorted(set(elelist)):
            elestring = self.rinseElement(ele)['name']
            f.write(self.formatElement(elestring, format = 'elegant') + '\n')

        # write beamline lattice definition
        f.write('\n')
        f.write('! {str1:<72s}\n'.format(str1= 'Beamline definitions:'))
        f.write('{bl:<6s}: line = ({lattice})'.format(bl      = beamline.upper(), 
                                                      lattice = ', '.join(elelist)))
        f.close()

        # if everything's OK, return True
        return True

    def rinseElement(self, ele):
        """ resolve element case with multiply format,
            e.g. rinseElement('10*D01') should return dict {'num': 10; 'name' = 'D01'}
        """
        if '*' in ele:
            tmplist = ''.join(ele.split()).split('*')
            tmplist_num = tmplist[[x.isdigit() for x in tmplist].index(True)]
            tmplist_ele = tmplist[[x.isdigit() for x in tmplist].index(False)]
            return dict(zip(('num','name'), (int(tmplist_num), tmplist_ele)))
        else:
            return dict(zip(('num','name'),(1, ele)))

    def orderLattice(self, beamline):
        """ ordering element type appearance sequence for each element of beamline
            e.g. after getFullBeamline, 
            lattice list ['q','Q01', 'B11', 'Q02', 'B22'] will return:
            [(u'q',   u'CHARGE',   1), 
             (u'q01', u'QUAD',     1), 
             (u'b11', u'CSRCSBEN', 1), 
             (u'q02', u'QUAD',     2), 
             (u'b12', u'CSRCSBEN', 2)]

        """ 
        ele_name_list = self.getFullBeamline(beamline, extend = True)
        ele_type_list = [self.getElementType(ele) for ele in ele_name_list]
        order_list   = [0] * len(ele_name_list)
        ele_type_dict_uniq = dict(zip(ele_type_list, order_list))
        for idx in xrange(len(ele_name_list)):
            etype = ele_type_list[idx]
            ele_type_dict_uniq[etype] += 1
            order_list[idx] = ele_type_dict_uniq[etype]

        return zip(ele_name_list, ele_type_list, order_list)

    def getChargeElement(self):
        """ return charge element name
        """
        for k in self.getAllEle():
            if self.getElementType(k) == 'CHARGE':
                return k
        return ''

    def getElementByOrder(self, beamline, type, irange):
        """ return element list by appearance order in beamline, 
            which could be returned by orderLattice(beamline)

        possible irange definitions:
            irange = 0,      first one 'type' element;
            irange = -1,     last one
            irange = 0,2,3,  the first, third and fourth 'type' element
            irange = 2:10:1, start:end:setp range
            irange = 'all',    all
        """
        try:
            assert beamline.upper() in self.kws_bl
        except AssertionError:
            print('%s is not a defined beamline.' % beamline)
            return ''

        try:
            orderedLattice_list = self.orderLattice(beamline)
            allmatchedlist = [val for idx, val in enumerate(orderedLattice_list) if val[1] == type.upper()]
            if ',' in str(irange):
                retlist = [allmatchedlist[int(num)] for num in str(irange).split(',')]
            elif ':' in str(irange):
                idxlist = map(int, irange.split(':'))
                if len(idxlist) == 2:
                    idxlist.append(1)
                idx_start, idx_stop, idx_step = idxlist[0], idxlist[1], idxlist[2]
                retlist = allmatchedlist[slice(idx_start, idx_stop, idx_step)]
            elif str(irange) == 'all':
                retlist = allmatchedlist[:]
            else:
                retlist = [allmatchedlist[int(irange)]]
            return retlist
        except: 
            #print('Can not find %s in %s.' % (type, beamline))
            return ''

    def getElementByName(self, beamline, name):
        """ return element list by literal name in beamline
            each element is tuple like (name, type, order)
        """
        try:
            assert beamline.upper() in self.kws_bl
        except AssertionError:
            print('%s is not a defined beamline.' % beamline)
            return ''

        try:
            assert name.lower() in self.getFullBeamline(beamline, extend = True)
            orderedLattice_list = self.orderLattice(beamline)
            retlist = [val for idx, val in enumerate(orderedLattice_list) if val[0] == name.lower()]
            return retlist

        except AssertionError:
            print('%s is not in %s.' % (name, beamline))
            return ''
    
    def manipulateLattice(self, beamline, type = 'quad', 
                                irange = 'all', property = 'k1', 
                                opstr = '+0%'):
        """ manipulate element with type, e.g. quad

            input parameters:
            beamline: beamline definition keyword
            type    : element type, case insensitive
            irange  : slice index, see getElementByOrder()
            property: element property, e.g. 'k1' for 'quad' strength
            opstr   : operation, '+[-]n%' or '+[-*/]n'
        """
        #lattice_list = self.getFullBeamline(beamline, extend = True)
        #orderedLattice_list = self.orderLattice(beamline)
        opele_list = self.getElementByOrder(beamline, type, irange)

        opr = opstr[0]
        opn = float(opstr[1:].strip('%'))

        if  opstr[-1] == '%':
            opn /= 100.0
            opsdict = {'+': lambda a, p: a*(1+p), 
                       '-': lambda a, p: a*(1-p)}
        else:
            opsdict = {'+': lambda a, p: a + p, 
                       '-': lambda a, p: a - p,
                       '*': lambda a, p: a * p,
                       '/': lambda a, p: a / float(p)}
            
        for ename,etype,eid in opele_list:
            val0_old = self.all_elements[ename.upper()].values()[0].get(property.lower())
            val0_new = opsdict[opr](val0_old, opn)
            self.all_elements[ename.upper()].values()[0][property.lower()] = val0_new

        return True

    def getElementProperties(self, name):
        """ return element properties
        """
        try:
            allp = self.all_elements[name.upper()]
            if isinstance(allp, dict):
                type = allp.keys()[0]
                properties =  allp.values()[0]
                return {'type': type, 'properties': properties}
            else:
                type = allp
                return {'type': type, 'properties': None}
        except:
            pass
        
#===========================================================================

def test2():
    latticepath=os.path.join(os.getcwd(), '../lattice')
    infile = os.path.join(latticepath, 'linac.lte')

    #kw = 'B11'
    #kw = 'bl'
    #kw = 'BPM01'
    #kw = 'dp4fh'
    #kw = 'a1i'
    #kw = 'q'
    lpins = LteParser(infile)
    #print lpins.prestrdict
    #lpins.getKw(kw)
    #print lpins.confstr
    #lpins.getKw(kw).toDict().solve_rpn()
    #print lpins.confdict
    
    #print lpins.detectAllKws()
    # print the whole lte file into json format, to show by: cat output | jshon [pjson]
    #allLatticeElements_str = lpins.file2json(jsonfile = 'jfile.dat')
    allLatticeElements_str = lpins.file2json()
    #print type(allLatticeElements_str)
    #allLatticeElements_dict = json.loads(allLatticeElements_str)
    #print type(allLatticeElements_dict)
    #print allLatticeElements_dict.values()
    
    latins = Lattice(allLatticeElements_str)
    #print latins.getElementType('Q01')
    #print latins.getElementConf('q01')
    #print latins.all_elements['BL']['beamline']['lattice']
    
    #latins.showBeamlines()
    #print latins.getBeamline('doub1')
    #print latins.getBeamline('doub2')
    #print latins.getBeamline('chi')
    #print latins.getFullBeamline('chi')

    #print latins.getFullBeamline('bl')

    #print latins.formatElement('q01')
    #print latins.formatElement('q06')
    #print latins.formatElement('B11')
    #print latins.formatElement('BPM01')

    testingpath = os.path.join(os.getcwd(), '../tests/tracking')
    outlatfile = os.path.join(testingpath, 'tmp.lte')
    latins.generateLatticeFile('bl', outlatfile)

    #print latins.kws_ele
    #print latins.kws_bl

def main():
    test2()

if __name__ == '__main__':
    main()
