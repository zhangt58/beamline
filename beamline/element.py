#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines all kinds of magnet components/elements.

Author      : Tong Zhang
Created     : 2016-03-22
Last updated: 2016-03-24
"""

import json
import epics

class MagBlock(object):
    objcnt = 0      # object counter
    comminfo = {}
    def __init__(self, name = None):
        MagBlock.objcnt += 1
        self._name = name # element name
        self.comminfo = {k:v for k,v in MagBlock.comminfo.items()} # common information

        self.simuinfo = {} # simulation information
        self.ctrlinfo = {} # control information
        self.miscinfo = {} # other information

        self.simukeys = [] # keywords of simulation information
        self.ctrlkeys = [] # keywords of control information
        self.misckeys = [] # keywords of other information
        self.transfun = None # unit translation function
        
        self.setConfDict = {'simu': self._setSimuConf, 
                            'ctrl': self._setCtrlConf, 
                            'misc': self._setMiscConf}

        self.prtConfigDict = {'simu': self._printSimuConf, 
                              'ctrl': self._printCtrlConf, 
                              'misc': self._printMiscConf,
                              'comm': self._printCommConf,
                              'all' : self._printAllConf}

        self.dumpConfigDict = {'simu': self._dumpSimuConf, 
                               'ctrl': self._dumpCtrlConf, 
                               'misc': self._dumpMiscConf,
                               'comm': self._dumpCommConf,
                               'all' : self._dumpAllConf,
                               'online': self._dumpOnlineConf}

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @staticmethod
    def sumObjNum():
        return MagBlock.objcnt
    
    @staticmethod
    def setCommInfo(infostr):
        """ set common information, to dict: info
            input parameter:
            :param infostr:
                1 infostr is a dict
                2 infostr with format like: "k1=v1, k2=v2"
        """
        if isinstance(infostr, dict):
            for k,v in infostr.items():
                MagBlock.comminfo[k] = v
        elif isinstance(infostr, str):
            for k,v in MagBlock.str2dict(infostr).items():
                MagBlock.comminfo[k] = v
        else:
            print("Information string ERROR.")

    @staticmethod
    def str2dict(istr):
        if not 'lattice' in istr.lower():
            tmpstr = istr.replace(',','=').split('=')
        else:
            tmpstr = istr.split('=')
        k = [i.strip() for i in tmpstr[0::2]]
        v = [i.strip() for i in tmpstr[1::2]]
        return dict(zip(k,v))

    def setConf(self, conf, type = 'simu'):
        """ set information for different type dict,
            :param conf: configuration information, str or dict
            :param type: simu, ctrl, misc
        """
        if conf == None:
            return
        else:
            if isinstance(conf, str):
                conf = MagBlock.str2dict(conf)
            self.setConfDict[type](conf)

    def printConfig(self, type = 'simu'):
        """ print information about element
            :param type: comm, simu, ctrl, misc, all
        """
        print("{s1}{s2:^22s}{s1}".format(s1="-"*10,s2="Configuration START"))
        print("class name: " + self.__class__.__name__)
        self.prtConfigDict[type]()
        print("{s1}{s2:^22s}{s1}".format(s1="-"*10,s2="Configuration END"))
   
    def dumpConfig(self, type = 'online', format = 'elegant'):
        """ dump element configuration to given format,
            inpurt parameters:
            :param type: comm, simu, ctrl, misc, all, online (default)
            :param format: elegant/mad, elegant by default
        """
        return self.dumpConfigDict[type](format)

    def _setSimuConf(self, conf):
        self.simuinfo.update(conf)
        self.simukeys.extend(conf.keys())
        self.simukeys = list(set(self.simukeys))

    def _setCtrlConf(self, conf):
        self.ctrlinfo.update(conf)
        self.ctrlkeys.extend(conf.keys())
        self.ctrlkeys = list(set(self.ctrlkeys))

    def _setMiscConf(self, conf):
        self.miscinfo.update(conf)
        self.misckeys.extend(conf.keys())
        self.misckeys = list(set(self.misckeys))

    def _printSimuConf(self):
        if self.simuinfo:
            print("Simulation configs:")
            for k,v in sorted(self.simuinfo.items(), reverse=True):
                print("  {k:6s} = {v:6s}".format(k=str(k),v=str(v)))

    def _printCommConf(self):
        if self.comminfo:
            print("Common configs:")
            for k,v in sorted(self.comminfo.items(), reverse=True):
                print("  {k:6s} = {v:6s}".format(k=str(k),v=str(v)))

    def _printCtrlConf(self):
        """ get PV value and print out
        """
        if self.ctrlinfo:
            print("Control configs:")
            for k,v in sorted(self.ctrlinfo.items(), reverse=True):
                pv  = v['pv']
                rval = epics.caget(pv)
                if rval is None:
                    val = ''
                else:
                    val = self.unitTrans(rval,direction = '+')
                print("  {k:6s} = {pv:6s}, raw: {rval:>6s}, real: {val:>6s}".format(k   = str(k),
                                                                                    pv  = str(pv),
                                                                                    rval= str(rval),
                                                                                    val = str(val)))

    def _printMiscConf(self):
        if self.miscinfo:
            print("Miscellaneous configs:")
            for k,v in sorted(self.miscinfo.items(), reverse=True):
                print("  {k:6s} = {v:6s}".format(k=str(k),v=str(v)))

    def _printAllConf(self):
        #allinfo = {}
        #map(allinfo.update, [self.comminfo, self.ctrlinfo, self.miscinfo, self.simuinfo])
        #for k,v in sorted(allinfo.items(), reverse=True):
        #    print("{k:6s} = {v:6s}".format(k=k,v=v))
        self._printCommConf()
        self._printSimuConf()
        self._printCtrlConf()
        self._printMiscConf()

    def _dumpSimuConf(self, format):
        return {self.name.upper(): {self.typename: {k:self.simuinfo[k] for k in self.simukeys}}}

    def _dumpMiscConf(self, format):
        return {self.name.upper(): {self.typename: {k:self.miscinfo[k] for k in self.misckeys}}}

    def _dumpCtrlConf(self, format):
        return {self.name.upper(): {self.typename: {k:self.ctrlinfo[k] for k in self.ctrlkeys}}}

    def _dumpCommConf(self, format):
        return {self.name.upper(): {self.typename: {k:self.comminfo[k] for k in self.comminfo.keys()}}}

    def _dumpAllConf(self, format):
        allinfo = {}
        map(allinfo.update, [self.comminfo, self.miscinfo, self.simuinfo, self.ctrlinfo])
        return {self.name.upper(): {self.typename: {k:allinfo[k] for k in allinfo.keys()}}}

    def _dumpOnlineConf(self, format):
        """ dump element configuration json string for online modeling,
            in which control configuration should be overwritten simulation conf,
            e.g. in simuinfo: {'k1':10,'l':1}, ctrlinfo: {'k1':pv_name,...}
            the k1 value should be replaced by pv_name, and from which 
            the value read into, take note the simuinfo and ctrlinfo
            would not be changed.
        """
        oinfod = {k:v for k,v in self.simuinfo.items()}
        for k in (set(oinfod.keys()) & set(self.ctrlkeys)):
            oinfod[k] = self.ctrlinfo[k]
        return {self.name.upper(): {self.typename: oinfod}}

    def unitTrans(self, inval, direction = '+', transfun = None):
        """ unit translation between EPICS PV and physical values,
            :param inval: input val,
            :param direction: '+': PV->physical, '-': physical->PV, '+' by default,
            :param transfun: userdefined translation function, None by default,
                             could be defined through creating obj.transfun
        """
        outval = inval
        return outval

    def __str__(self):
        """ return simulation configuration dict as json string format
        """
        return json.dumps(self.dumpConfig())

class ElementCharge(MagBlock):
    """ charge element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'CHARGE'
        self.setConf(config)

class ElementCsrcsben(MagBlock):
    """ csrcsben element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'CSRCSBEN'
        self.setConf(config)

class ElementCsrdrift(MagBlock):
    """ csrdrift element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'CSRDRIFT'
        self.setConf(config)

class ElementDrift(MagBlock):
    """ drift element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'DRIFT'
        self.setConf(config)

class ElementKicker(MagBlock):
    """ kicker element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'KICKER'
        self.setConf(config)

class ElementLscdrift(MagBlock):
    """ lscdrift element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'LSCDRIFT'
        self.setConf(config)

class ElementMark(MagBlock):
    """ mark element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'MARK'
        self.setConf(config)

class ElementMoni(MagBlock):
    """ moni element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'MONI'
        self.setConf(config)

class ElementQuad(MagBlock):
    """ quad element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'QUAD'
        self.setConf(config)

    def unitTrans(self, inval, direction = '+', transfun = None):
        transfun = self.transfun
        if transfun != None:
            outval = transfun(inval, direction)
        else: # use builtin translation rules
            if direction == '+': # PV->physical
                outval = 2*inval
            elif direction == '-': # physical->PV
                outval = 0.5*inval
        return outval

class ElementRfcw(MagBlock):
    """ rfcw element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'RFCW'
        self.setConf(config)

class ElementRfdf(MagBlock):
    """ rfdf element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'RFDF'
        self.setConf(config)

class ElementWake(MagBlock):
    """ wake element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'WAKE'
        self.setConf(config)

class ElementWatch(MagBlock):
    """ watch element
    """
    def __init__(self, name = None, config = None):
        MagBlock.__init__(self, name)
        self.typename = 'WATCH'
        self.setConf(config)

class ElementBeamline(MagBlock):
    """ beamline element
    """
    def __init__(self, name = 'bl', config = None):
        MagBlock.__init__(self, name)
        self.typename = 'BEAMLINE'
        self.setConf(config)

def test():
    """ For example, define lattice configuration for a 4-dipole chicane with quads
                    |-|---|-|  
                    /       \
          ---||---|-|       |-|---||---

        i.e.   drift + quad  + drift 
            + dipole + drift + dipole + drift 
            + dipole + drift + dipole
            + drift  + quad  + drift
    """
    # typical workflow:

    ## STEP 1: define common information, two different input parameter formats
    #commdinfo = {'DATE': '2016-03-22', 'AUTHOR': 'Tong Zhang'}
    comminfo = 'DATE = 2016-03-24, 16:05, AUTHOR = Tong Zhang'
    MagBlock.setCommInfo(comminfo)
    
    ## STEP 2: create element

    # charge
    chconf = {'total':1e-9}
    CH = ElementCharge(name = 'Q1', config = chconf)

    # csrcsben
    simconf = {"edge1_effects": 1,
               "edge2_effects":1,
               "hgap":0.015,
               "csr":0,
               "nonlinear":1,
               "n_kicks":100,
               "integration_order":4,
               "bins":512,
               "sg_halfwidth":1,
               "block_csr":0,
               'l':0.5,}
    angle = 0.2

    B1 = ElementCsrcsben(name = 'b1', config = {'angle':angle, 'e1':0, 'e2':angle})
    B1.setConf(simconf, type = 'simu')
    #B1.setConf("pv=sxfel:lattice:b1",  type = 'ctrl')
    
    B2 = ElementCsrcsben(name = 'b2', config = {'angle':-angle, 'e1':-angle, 'e2':0})
    B3 = ElementCsrcsben(name = 'b3', config = {'angle':-angle, 'e1':0,      'e2':-angle})
    B4 = ElementCsrcsben(name = 'b4', config = {'angle': angle, 'e1':angle,  'e2':0})
    B2.setConf(simconf, type = 'simu')
    B3.setConf(simconf, type = 'simu')
    B4.setConf(simconf, type = 'simu')

    # drift
    D0 = ElementDrift(name = 'D0', config = "l=1.0")

    # quad
    Q1 = ElementQuad(name = 'Q1', config = "k1 = 10, l = 0.1")
    dftconf = {'tilt':"pi 4 /"}
    Q1.setConf(dftconf, type = 'simu')

    # beamline
    latele = [obj.name for obj in [D0, Q1, D0, B1, D0, B2, D0, D0, B3, D0, B4, D0, Q1, D0]]
    latstr = '(' + ' '.join(latele) + ')'
    
    bl = ElementBeamline(name = 'bl', config = {'lattice':latstr})
    #bl = ElementBeamline(name = 'bl1', config = "lattice = (q d0 q1)")
    #bl.setConf("lattice = (d,q,b)", type = 'simu')
    print bl

    #print MagBlock.sumObjNum()

if __name__ == '__main__':
    test()


