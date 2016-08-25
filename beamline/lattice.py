#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Classes and routines to handle lattice issues for online modeling and runtime calculations.

* class ``LteParser``: parse ``ELEGANT`` lattice definition files for simulation:

    1. convert lte file into dict/json format for further usage;
    2. resolve rpn expressions within element definitions;
    3. retain prefixed information of lte file as '_prefixstr' key in json/dict;

* class ``Lattice``: handle lattice issues from json/dict definitions:

    1. instantiate with json/dict lattice definition, e.g. from ``LteParser.file2json()``;
    2. generate lte file for elegant simulation;
    3. iteratively expand the beamline definition in lte file;
    4. generate lte file after manipulations.

.. Author      : Tong Zhang
.. Created     : 2016-01-28
"""

import json
import os
import time
import ast
import sys
import cStringIO

from pyrpn import rpn

from . import element


class LteParser(object):
    """
    :param infile: lte filename or list of lines of lte file
    :param mode: 'f': treat infile as file,
                 's': (else) treat as list of lines
    """
    def __init__(self, infile, mode='f'):
        if mode == 'f':  # read lines from infile
            self.file_lines = open(infile, 'r').readlines()
        elif mode == 's': # infile is the output of generateLatticeFile(bl,'sio')
            self.file_lines = infile.split('\n')  # string to list of lines

        self.confstr = ''        # configuration string line for given element excluding control part
        self.confstr_epics = ''  # configuration string line for given element, epics control part
        self.ctrlconf_dict = {}  # epics control config dict
        self.confdict = {}  # configuration string line to dict
        self.confjson = {}  # configuration string line to json
        self.prestrdict = {}  # prefix string line to dict, e.g. line starts with '%'

        self.stodict = {}  # sto key-value dict
        self.resolvePrefix()  # sto string information
        self.resolveEPICS()   # handle line starts with !!epics

    def resolvePrefix(self):
        """ extract prefix information into dict with the key of '_prefixstr'
        """
        tmpstrlist = []
        tmpstodict = {}
        for line in self.file_lines:
            if line.startswith('%'):
                stolist = line.replace('%', '').split('sto')
                rpnexp = stolist[0].strip()  # rpn expression
                rpnvar = stolist[1].strip()  # rpn variable
                tmpstodict[rpnvar] = rpnexp
                # bug: rpnval in rpnexp 
                # raises error when converting string convert to float
                # Found: 2016-06-08 22:29:25 PM CST
                # Fixed: 2016-06-12 11:51:01 AM CST
                # e.g.
                # a sto 0.1
                # a sto b
                # then b should be 0.1,
                # i.e. b -> a -> 0.1
                # solve the 'sto chain' assignment issue.
        
        self.stodict = self.resolve_rpn(tmpstodict)
        for k,v in self.stodict.items():
            stostr = '% {val} sto {var}'.format(val=v, var=k)
            tmpstrlist.append(stostr)
        self.prestrdict['_prefixstr'] = tmpstrlist

    def get_rpndict_flag(self, rpndict):
        """ calculate flag set, the value is True or False,
            if rpndict value is not None, flag is True, or False
            
            if a set with only one item, i.e. True returns, 
            means values of rpndict are all valid float numbers,
            then finally return True, or False
        """
        flag_set = set([rpn.Rpn.solve_rpn(str(v)) is not None for v in rpndict.values()])
        if len(flag_set) == 1 and flag_set.pop():
            return True
        else:
            return False

    def rinse_rpnexp(self, rpnexp, rpndict):
        """ replace valid keyword of rpnexp from rpndict
            e.g. rpnexp = 'b a /', rpndict = {'b': 10}
            then after rinsing, rpnexp = '10 a /'

            return rinsed rpnexp
        """
        for wd in rpnexp.split():
            if wd in rpndict:
                try:
                    val = float(rpndict[wd])
                    rpnexp = rpnexp.replace(wd, str(val))
                except:
                    pass
        return rpnexp

    def resolve_rpn(self, rpndict):
        """ solve dict of rpn expressions to pure var to val dict
        :param rpndict: dict of rpn expressions
        return pure var to val dict
        """
        if rpndict == {}:
            return {}

        retflag = self.get_rpndict_flag(rpndict)
        cnt = 0
        tmpdict = {k:v for k,v in rpndict.items()}
        while not retflag:
            # update rpndict
            cnt += 1
            tmpdict = self.update_rpndict(tmpdict)
            # and flag
            retflag = self.get_rpndict_flag(tmpdict)
        return tmpdict

    def update_rpndict(self, rpndict):
        """ update rpndict, try to solve rpn expressions as many as possible,
            leave unsolvable unchanged.
    
            return new dict
        """
        tmpdict = {k:v for k,v in rpndict.items()}
        for k,v in rpndict.items():
            v_str = str(v)
            if rpn.Rpn.solve_rpn(v_str) is None:
                tmpdict[k] = self.rinse_rpnexp(v_str, tmpdict)
            else:
                tmpdict[k] = rpn.Rpn.solve_rpn(v_str)
        return tmpdict

    def resolveEPICS(self):
        """ extract epics control configs into 
        """
        kw_name_list = []
        kw_ctrlconf_list = []
        for line in self.file_lines:
            if line.startswith('!!epics'):
                el = line.replace('!!epics','').replace(':',';;',1).split(';;')
                kw_name_list.append(el[0].strip())
                kw_ctrlconf_list.append(json.loads(el[1].strip()))
        self.ctrlconf_dict = dict(zip(kw_name_list, kw_ctrlconf_list))

    def getKw(self, kw):
        """ Extract doc snippet for element configuration,
            :param kw: element name
            :return: instance itself
                1 call getKwAsDict() to return config as a dict
                2 call getKwAsJson() to return config as json string
                3 call getKwAsString() to return config as a raw string

        USAGE: getKw('Q10')
        """
        ikw = kw.lower()
        line_continue_flag = ''
        appendflag = False
        try:
            for line in self.file_lines:
                if line.strip() == '':
                    continue
                line = ' '.join(line.strip().split()).strip('\n; ')
                if line.startswith('!'):
                    continue
                if line.lower().startswith(ikw + ' :') or line.lower().startswith(ikw + ':'):
                    conflist = []  # list to put into element configuration
                    conflist.append(line)
                    appendflag = True
                elif appendflag and line_continue_flag == '&':
                    conflist.append(line)
                line_continue_flag = line[-1]
                if line_continue_flag != '&':
                    appendflag = False
            conf_str = ''.join(conflist).replace('&', ',')
            if 'line' in conf_str.lower().split('=')[0]:  # if bl defines lattice
                conf_str = conf_str.lower().replace(',', ' ')[::-1].replace('enil', 'beamline,lattice'[::-1], 1)[
                           ::-1]  # avoid the case with bl keyword has 'line'
        except:
            conf_str = ''
        
        #print conf_str

        # split('!epics'): second part is epics control conf
        splitedparts = conf_str.split('!epics')
        self.confstr = splitedparts[0]
        try:
            self.confstr_epics = splitedparts[1].strip()
        except IndexError:
            self.confstr_epics = ''

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
        :param rawstr: raw configuration string of element
        """
        kw_list = []
        sp1 = rawstr.split(':')
        kw_name = sp1[0].strip().upper()
        kw_desc = sp1[1:]
        sp2 = kw_desc[0].replace(',', ';;', 1).split(';;')
        kw_type = sp2[0].strip()
        try:
            kw_vals = sp2[1].replace(",", '=').split('=')
            [(not (i.isspace() or i == '')) and kw_list.append(i) for i in kw_vals]
            ks = [k.strip() for k in kw_list[0::2]]
            vs = [v.strip().replace('"', '').replace("'", '') for v in kw_list[1::2]]
            kw_vals_dict = dict(zip(ks, vs))
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
        :param kw: element keyword
        """
        return self.dict2json(self.getKwAsDict(kw))

    def getKwAsDict(self, kw):
        """ return keyword configuration as a dict

        Usage: rdict = getKwAsDict(kw)
        """
        self.getKw(kw)
        return self.str2dict(self.confstr)

    def getKwCtrlConf(self, kw, fmt='dict'):
        """ return keyword's control configuration, followed after '!epics' notation
        :param kw: keyword name
        :param fmt: return format, 'raw', 'dict', 'json', default is 'dict'
        """
        try:
            confd = self.ctrlconf_dict[kw]
            if fmt == 'dict':
                retval = confd
            else: # 'json' string for other options
                retval = json.dumps(confd)
        except KeyError:
            # try to get from raw line string
            self.getKw(kw)
            if self.confstr_epics != '':
                if fmt == 'dict':
                    retval = ast.literal_eval(self.confstr_epics)
                elif fmt == 'json':
                    retval = json.dumps(ast.literal_eval(self.confstr_epics))
                else:  # raw string
                    retval = self.confstr_epics
            else:
                retval = None 

        return retval

    def getKwAsString(self, kw):
        """ return keyword configuration as a string

        Usage: rstr = getKwAsString(kw)
        """
        return self.getKw(kw).confstr

    def detectAllKws(self):
        """ Detect all keyword from infile, return as a list
        
        USAGE: kwslist = detectAllKws()
        """
        kwslist = []
        for line in self.file_lines:
            # if line.strip() == '': continue
            line = ''.join(line.strip().split())
            if line.startswith("!"):
                continue
            # if ':' in line and not "line" in line:
            if ':' in line:
                kw_name = line.split(':')[0]
                if set(kw_name).difference(set(['=','-','*','/','+'])) == set(kw_name):
                    kwslist.append(kw_name)
        return kwslist

    def file2json(self, jsonfile=None):
        """ Convert entire lte file into json like format
        
        USAGE: 1: kwsdictstr = file2json()
               2: kwsdictstr = file2json(jsonfile = 'somefile')

        show pretty format with pipeline: | jshon, or | pjson
        if jsonfile is defined, dump to defined file before returning json string
        :param jsonfile: filename to dump json strings
        """
        kwslist = self.detectAllKws()
        kwsdict = {}
        idx = 0
        for kw in sorted(kwslist, key=str.lower):
            #print kw
            idx += 1
            tdict = self.getKwAsDict(kw)
            self.rpn2val(tdict)
            kwsdict.update(tdict)
            if kw not in self.ctrlconf_dict:
                ctrlconf = self.getKwCtrlConf(kw, fmt='dict')
                if ctrlconf is not None:
                    self.ctrlconf_dict.update({kw:ctrlconf})
        kwsdict.update(self.prestrdict)
        ctrlconfdict = {'_epics':self.ctrlconf_dict} # all epics contrl config in self.ctrlconfdict
        kwsdict.update(ctrlconfdict)
        try:
            with open(os.path.expanduser(jsonfile), 'w') as outfile:
                json.dump(kwsdict, outfile)
        except:
            pass
        return json.dumps(kwsdict)

    def getKwType(self, kw):
        """ return the type of kw, upper cased string

        USAGE: rtype = getKwType(kw)
        """
        return self.getKwAsDict(kw).values()[0].keys()[0].upper()

    def getKwConfig(self, kw):
        """ return the configuration of kw, dict

        USAGE: rdict = getKwConfig(kw)
        """
        confd = self.getKwAsDict(kw).values()[0].values()[0]
        return {k.lower():v for k,v in confd.items()}

    def makeElement(self, kw):
        """ return element object regarding the keyword configuration
        """
        kw_name = kw
        kw_type = self.getKwType(kw_name)
        kw_config = {k.lower():v for k,v in self.getKwConfig(kw_name).items()}
        objtype='Element' + kw_type.capitalize()
        retobj = getattr(element, objtype)(name=kw_name, config=kw_config)
        # set up EPICS control configs
        ctrlconf = self.getKwCtrlConf(kw_name)
        if ctrlconf != {}:
            retobj.setConf(ctrlconf, type='ctrl')

        return retobj

    def scanStoVars(self, strline):
        """ scan input string line, replace sto parameters with calculated results.
        """
        for wd in strline.split():
            if wd in self.stodict:
                strline = strline.replace(wd, str(self.stodict[wd]))
        return strline

    def rpn2val(self, rdict):
        """ Resolve the rpn string into calulated float number

        USAGE: rpn2val(rdict)
            :param rdict: json like dict
        """

        kw_name = rdict.keys()[0]  # b11
        kw_val = rdict[kw_name]
        try:
            kw_type = kw_val.keys()[0]  # csrcsben
            kw_param = kw_val.values()[0]
            if kw_type != 'beamline':
                for k, v in kw_param.items():
                    v = self.scanStoVars(v)
                    rpnval = rpn.Rpn.solve_rpn(v)
                    if rpnval is not None:
                        kw_param[k] = rpnval# update rpn string to float if not None
        except:
            pass  # element that only has type name, e.g. {'bpm01': 'moni'}

    def solve_rpn(self):
        """ solve rpn string in self.confdict, and update self.confdict
        
        USAGE: ins = LteParser(infile)
               ins.getKw(kw).toDict().solve_rpn()
        """
        self.rpn2val(self.confdict)
        return self


# ===========================================================================

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
        else:  # elements is dict already
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
        :param beamlineKw: keyword of beamline
        """
        lattice_string = self.all_elements.get(beamlineKw.upper()).values()[0].get('lattice')
        return lattice_string[1:-1].split()  # drop leading '(' and trailing ')' and split into list

    def getFullBeamline(self, beamlineKw, extend=False):
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
            getBeamline('chi') = [u'dbll2', u'doub1', u'dp4fh', u'dp4sh', u'dbll5', u'dbd', u'b11', u'db11', u'b12',
                                  u'db12', u'pf2', u'db13', u'b13', u'db14', u'b14', u'dbd', u'dbll5', u'doub2',
                                  u'dp5fh', u'dp5sh', u'dbll2', u'pstn1']

            thus: getFullBeamline('chi') should return:
            [u'dbll2', A, u'dp4fh', u'dp4sh', u'dbll5', u'dbd', u'b11', u'db11', u'b12', u'db12', u'pf2', u'db13',
             u'b13', u'db14', u'b14', u'dbd', u'dbll5', B, u'dp5fh', u'dp5sh', u'dbll2', u'pstn1']

            :param extend: if extend mode should be envoked, by default False
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
                    else:  # if not beamline, do not expand
                        fullbl.append(ele)
            else:  # extend
                for ele in rawbl:
                    ele_num_name_dict = self.rinseElement(ele)
                    elename = ele_num_name_dict['name']
                    elenum = ele_num_name_dict['num']
                    if self.isBeamline(elename):
                        fullbl.extend(self.getFullBeamline(elename, extend=True) * elenum)
                    else:
                        fullbl.extend([elename] * elenum)
            return fullbl
        except AssertionError:
            print('ERROR: %s is not a right defined beamline.' % beamlineKw)

    def isBeamline(self, kw):
        """ test if kw is a beamline
        :param kw: keyword
        """
        return kw.upper() in self.kws_bl

    def getAllKws(self):
        """ extract all keywords into two categories
            
            kws_ele: magnetic elements
            kws_bl: beamline elements

            return (kws_ele, kws_bl)
        """
        kws_ele = []
        kws_bl = []
        for ele in self.all_elements:
            if ele == '_prefixstr' or ele == '_epics':
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
                if 'beamline' in self.all_elements.get(k):
                    cnt += 1
                    blidlist.append(k)
            except:
                pass
        retstr = '{total:<3d}beamlines: {allbl}'.format(total=cnt,
                                                        allbl=';'.join(blidlist))
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

    def getElementConf(self, elementKw, raw=False):
        """ return configuration for given element keyword,
            e.g. getElementConf('Q01') should return dict: {u'k1': 0.0, u'l': 0.05}
            :param elementKw: element keyword
        """
        if raw is True:
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

    def getElementCtrlConf(self, elementKw):
        """ return keyword's EPICS control configs, 
            if not setup, return {}
        """
        try:
            retval = self.all_elements['_epics'][elementKw.upper()]
        except KeyError:
            retval = {}

        return retval

    def formatElement(self, kw, format='elegant'):
        """ convert json/dict of element configuration into elegant/mad format
        :param kw: keyword
        """
        etype = self.getElementType(kw)
        econf_dict = self.getElementConf(kw)
        econf_str = ''
        for k, v in econf_dict.items():
            econf_str += (k + ' = ' + '"' + str(v) + '"' + ', ')

        if format == 'elegant':
            fmtstring = '{eid:<10s}:{etype:>10s}, {econf}'.format(eid=kw.upper(),
                                                                 etype=etype.upper(),
                                                                 econf=econf_str[
                                                                       :-2])
            # [:-2] slicing to remove trailing space and ','
        elif format == 'mad':
            pass

        return fmtstring

    def generateLatticeLine(self, latname='newline', line=None):
        """ construct a new lattice line
        :param latname: name for generated new lattice
        """
        latticeline = []
        for e in line:
            if isinstance(e, list):
                latticeline.extend(e)
            else:
                latticeline.append(e)

        newblele = {latname.upper(): {'beamline': {'lattice': '(' + ' '.join(latticeline) + ')'}}}
        self.all_elements.update(newblele)
        self.kws_bl.append(latname.upper())
        return newblele

    def generateLatticeFile(self, beamline, filename=None, format='elegant'):
        """ generate simulation files for lattice analysis,
            e.g. ".lte" for elegant, ".madx" for madx

            input parameters:
            :param beamline: keyword for beamline
            :param filename: name of lte/mad file, 
                if None, output to stdout;
                if 'sio', output to a string as return value;
                other cases, output to filename;
            :param format: madx, elegant,
                'elegant' by default, generated lattice is for elegant tracking
        """

        """
        if not self.isBeamline(beamline):
            print("%s is a valid defined beamline, do not process." % (beamline))
            return False
        """

        if filename is None:
            f = sys.stdout
        elif filename == 'sio':
            f = cStringIO.StringIO()
        else:
            f = open(os.path.expanduser(filename), 'w')

        # write filehead, mainly resolving prefix string lines
        cl1 = "This file is automatically generated by 'generateLatticeFile()' method,"
        cl2 = 'could be used as ' + format + ' lattice file.'
        cl3 = 'Author: Tong Zhang (zhangtong@sinap.ac.cn)'
        cl4 = 'Generated Date: ' + time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime())

        f.write('!{str1:<73s}!\n'.format(str1='-' * 73))
        f.write('!{str1:^73s}!\n'.format(str1=cl1))
        f.write('!{str1:^73s}!\n'.format(str1=cl2))
        f.write('!{str1:^73s}!\n'.format(str1='-' * 24))
        f.write('!{str1:^73s}!\n'.format(str1=cl3))
        f.write('!{str1:^73s}!\n'.format(str1=cl4))
        f.write('!{str1:<73s}!\n'.format(str1='-' * 73))
        f.write('\n')

        """ do not need to dump stoed variables now, 2016-03-21
        # write global variables
        f.write('! {str1:<73s}\n'.format(str1= 'Global variable definitions:'))
        f.write('\n'.join(self.all_elements['_prefixstr']))
        f.write('\n')
        f.write('\n')
        """
        
        # write EPICS control configuration part if contains '_epics' key
        if '_epics' in self.all_elements:
            f.write('! {str1:<73s}\n'.format(str1= 'EPICS control definitions:'))
            for k,v in self.all_elements['_epics'].items():
                f.write('!!epics {k:<10s}:{v:>50s}\n'.format(k=k,v=json.dumps(v)))
            f.write('\n')

        # write element definitions and lattice
        f.write('! {str1:<72s}\n'.format(str1='Element definitions:'))
        elelist = self.getFullBeamline(beamline, extend=True)
        if self.getElementType(elelist[0]) != 'CHARGE':
            elelist.insert(0, self.getChargeElement())
        for ele in sorted(set(elelist)):
            elestring = self.rinseElement(ele)['name']
            f.write(self.formatElement(elestring, format='elegant') + '\n')

        # write beamline lattice definition
        f.write('\n')
        f.write('! {str1:<72s}\n'.format(str1='Beamline definitions:'))
        f.write('{bl:<10s}: line = ({lattice})'.format(bl=beamline.upper(),
                                                      lattice=', '.join(elelist)))
        if filename == 'sio':
            retval = f.getvalue()
        else:
            retval = True
        f.close()

        # if everything's OK, return True or string ('sio') mode
        return retval

    def getElementList(self, bl):
        """ return the elements list according to the appearance order 
            in beamline named 'bl'

            :param bl: beamline name
        """
        return self.getFullBeamline(bl, extend=True)

    def rinseElement(self, ele):
        """ resolve element case with multiply format,
            e.g. rinseElement('10*D01') should return dict {'num': 10; 'name' = 'D01'}
            :param ele: element string
        """
        if '*' in ele:
            tmplist = ''.join(ele.split()).split('*')
            tmplist_num = tmplist[[x.isdigit() for x in tmplist].index(True)]
            tmplist_ele = tmplist[[x.isdigit() for x in tmplist].index(False)]
            return dict(zip(('num', 'name'), (int(tmplist_num), tmplist_ele)))
        else:
            return dict(zip(('num', 'name'), (1, ele)))

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
        ele_name_list = self.getFullBeamline(beamline, extend=True)
        ele_type_list = [self.getElementType(ele) for ele in ele_name_list]
        order_list = [0] * len(ele_name_list)
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

            :param beamline: beamline name
            :param type: element type name
            :param irange: selected element range

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
            # print('Can not find %s in %s.' % (type, beamline))
            return ''

    def getElementByName(self, beamline, name):
        """ return element list by literal name in beamline
            each element is tuple like (name, type, order)
            :param beamline: beamline name
            :param name: element literal name
        """
        try:
            assert beamline.upper() in self.kws_bl
        except AssertionError:
            print('%s is not a defined beamline.' % beamline)
            return ''

        try:
            assert name.lower() in self.getFullBeamline(beamline, extend=True)
            orderedLattice_list = self.orderLattice(beamline)
            retlist = [val for idx, val in enumerate(orderedLattice_list) if val[0] == name.lower()]
            return retlist

        except AssertionError:
            print('%s is not in %s.' % (name, beamline))
            return ''

    def manipulateLattice(self, beamline, type='quad',
                          irange='all', property='k1',
                          opstr='+0%'):
        """ manipulate element with type, e.g. quad

            input parameters:
            :param beamline: beamline definition keyword
            :param type: element type, case insensitive
            :param irange: slice index, see getElementByOrder()
            :param property: element property, e.g. 'k1' for 'quad' strength
            :param opstr: operation, '+[-]n%' or '+[-*/]n'
        """
        # lattice_list = self.getFullBeamline(beamline, extend = True)
        # orderedLattice_list = self.orderLattice(beamline)
        opele_list = self.getElementByOrder(beamline, type, irange)

        opr = opstr[0]
        opn = float(opstr[1:].strip('%'))

        if opstr[-1] == '%':
            opn /= 100.0
            opsdict = {'+': lambda a, p: a * (1 + p),
                       '-': lambda a, p: a * (1 - p)}
        else:
            opsdict = {'+': lambda a, p: a + p,
                       '-': lambda a, p: a - p,
                       '*': lambda a, p: a * p,
                       '/': lambda a, p: a / float(p)}

        for ename, etype, eid in opele_list:
            val0_old = self.all_elements[ename.upper()].values()[0].get(property.lower())
            val0_new = opsdict[opr](val0_old, opn)
            self.all_elements[ename.upper()].values()[0][property.lower()] = val0_new

        return True

    def getElementProperties(self, name):
        """ return element properties
        :param name: element name
        """
        try:
            allp = self.all_elements[name.upper()]
            if isinstance(allp, dict):
                type = allp.keys()[0]
                properties = allp.values()[0]
                return {'type': type, 'properties': properties}
            else:
                type = allp
                return {'type': type, 'properties': None}
        except:
            pass

    def makeElement(self, kw):
        """ return element object regarding the keyword configuration
        """
        kw_name = kw
        kw_type = self.getElementType(kw_name)
        kw_config = {k.lower():v for k,v in self.getElementConf(kw_name).items()}
        objtype='Element' + kw_type.capitalize()
        retobj = getattr(element, objtype)(name=kw_name, config=kw_config)
        # set up EPICS control configs
        ctrlconf = self.getElementCtrlConf(kw)
        if ctrlconf != {}:
            retobj.setConf(ctrlconf, type='ctrl')

        return retobj


# ===========================================================================

def test2():
    latticepath = os.path.join(os.getcwd(), '../lattice')
    infile = os.path.join(latticepath, 'linac.lte')

    # kw = 'B11'
    # kw = 'bl'
    # kw = 'BPM01'
    # kw = 'dp4fh'
    # kw = 'a1i'
    # kw = 'q'
    lpins = LteParser(infile)
    # print lpins.prestrdict
    # lpins.getKw(kw)
    # print lpins.confstr
    # lpins.getKw(kw).toDict().solve_rpn()
    # print lpins.confdict

    # print lpins.detectAllKws()
    # print the whole lte file into json format, to show by: cat output | jshon [pjson]
    # allLatticeElements_str = lpins.file2json(jsonfile = 'jfile.dat')
    allLatticeElements_str = lpins.file2json()
    # print type(allLatticeElements_str)
    # allLatticeElements_dict = json.loads(allLatticeElements_str)
    # print type(allLatticeElements_dict)
    # print allLatticeElements_dict.values()

    latins = Lattice(allLatticeElements_str)
    # print latins.getElementType('Q01')
    # print latins.getElementConf('q01')
    # print latins.all_elements['BL']['beamline']['lattice']

    # latins.showBeamlines()
    # print latins.getBeamline('doub1')
    # print latins.getBeamline('doub2')
    # print latins.getBeamline('chi')
    # print latins.getFullBeamline('chi')

    # print latins.getFullBeamline('bl')

    # print latins.formatElement('q01')
    # print latins.formatElement('q06')
    # print latins.formatElement('B11')
    # print latins.formatElement('BPM01')

    testingpath = os.path.join(os.getcwd(), '../tests/tracking')
    outlatfile = os.path.join(testingpath, 'tmp.lte')
    latins.generateLatticeFile('bl', outlatfile)

    # print latins.kws_ele
    # print latins.kws_bl


def main():
    test2()


if __name__ == '__main__':
    main()
