#!/usr/bin/env pyton
# -*- coding: utf-8 -*-

"""
This module is written for the purposes of elements modeling:
    1: interpret (EPICS databases)/(EPICS PVs) into dicts (json) objects
    2: update (EPICS databases)/(EPICS PVs) with new dicts (json) objects


Author      : Tong Zhang
Created     : 2016-03-18
Last updated: 2016-03-24
"""

import element
import json
import copy
import epics

class Models(object):
    """ make lattice configuration (json) for lattice.Lattice
        return instance as a json string file with all configuration.
        get lattice name by instance.name.
    """
    def __init__(self, name = 'BL', mode = 'simu'):
        """ create Models instance,
            :param name: lattice name, 'BL' by defualt
            :param mode: 'simu' or 'online' mode,
                if 'online' is defined, the lattice should be update the ctrl
                configuration before dumping configuration string by calling
                method: getCtrlConf()
        """
        self._mode             = mode.lower()   # 'simu' (simulation) or 'online' (online) mode
        self._lattice_name     = name.upper()   # lattice name
        self._lattice_elecnt   = 0      # lattice element counter
        self._lattice_elenamelist = []  # lattice element name list
        self._lattice_eleobjlist  = []  # lattice element object list
        self._lattice_confdict = {}     # lattice configuration dict
        self._lattice = element.ElementBeamline(
                            name   = self._lattice_name,
                            config = "lattice = ()") # initial lattice configuration

    @property
    def mode(self):
        return self._mode

    @property
    def name(self):
        return self._lattice_name.upper()

    @name.setter
    def name(self, name):
        self._lattice_name = name.upper()

    @mode.setter
    def mode(self, mode):
        self._mode = mode.lower()

    def addElement(self, *ele):
        """ add element to lattice element list
            input parameters:
            :param ele: magnetic element defined in element module
            return total element number
        """
        for el in list(Models.flatten(ele)):
            e = copy.deepcopy(el)
            self._lattice_eleobjlist.append(e)
            self._lattice_elenamelist.append(e.name)
            self._lattice_elecnt += 1
        # update lattice, i.e. beamline element
        self._lattice.setConf(Models.makeLatticeString(self._lattice_elenamelist))
        return self._lattice_elecnt
    
    def getCtrlConf(self, msgout=True):
        """ get control configurations regarding to the PV names,
            read PV value
            :param msgout: print information if True (be default)
            return updated element object list
        """
        _lattice_eleobjlist_copy = copy.deepcopy(self._lattice_eleobjlist)
        if self.mode == 'online':
            for e in _lattice_eleobjlist_copy:
                for k in (set(e.simukeys) & set(e.ctrlkeys)):
                    try:
                        if msgout:
                            print("Reading from %s..." % e.ctrlinfo[k]['pv'])
                        pvval = epics.caget(e.ctrlinfo[k]['pv'])
                        if not pvval is None:
                            e.simuinfo[k] = e.unitTrans(pvval, direction = '+')
                            if msgout:
                                print("  Done.") 
                        else: 
                            if msgout:
                                print("  Failed.")
                    except:
                        pass
        else: # self.mode is 'simu' do nothing
            pass
        return _lattice_eleobjlist_copy

    def putCtrlConf(self, eleobj, ctrlkey, val, type = 'raw'):
        """ put the value to control PV field
            :param eleobj: element object in lattice
            :param ctrlkey: element control property, PV name
            :param val: new value for ctrlkey
            :param type: set in 'raw' or 'real' mode, 'raw' by default
                         'raw': set PV with the value of 'val',
                         'real': set PV with the value translated from 'val'
        """
        if ctrlkey in eleobj.ctrlkeys:
            if type == 'raw':
                newval = val
            else: # val should be translated
                newval = eleobj.unitTrans(val, direction = '-')
            epics.caput(eleobj.ctrlinfo[ctrlkey]['pv'], newval)
            return True
        else:
            return False

    def getAllConfig(self, fmt = 'json'):
        """
            return all element configurations as json string file.
            could be further processed by beamline.Lattice class
            input parameter:
            :param fmt: 'json' (default) or 'dict'
        """
        for e in self.getCtrlConf(msgout=False):
            self._lattice_confdict.update(e.dumpConfig(type='simu'))
        self._lattice_confdict.update(self._lattice.dumpConfig())
        if fmt == 'json':
            return json.dumps(self._lattice_confdict)
        else:
            return self._lattice_confdict

    def updateConfig(self, eleobj, config, type = 'simu'):
        """ write new configuration to element
            input parameters:
            :param eleobj: define element object
            :param config: new configuration for element, string or dict
            :param type: 'simu' by default, could be online, misc, comm, ctrl
        """
        eleobj.setConf(config, type = type)

    @staticmethod
    def makeLatticeString(ele):
        """ return string like "lattice = (q b d)"
        """
        return 'lattice = (' + ' '.join(ele) + ')'

    @staticmethod
    def flatten(ele):
        """ flatten recursively defined list,
            e.g. [1,2,3, [4,5], [6,[8,9,[10,[11,'x']]]]]

            return generator object
        """
        for el in ele:
            if isinstance(el, list) or isinstance(el, tuple):
                for e in Models.flatten(el):
                    yield(e)
            else:
                yield(el)

    @property
    def LatticeList(self):
        """ show lattice element list
        """
        return self._lattice_elenamelist

    @property
    def LatticeDict(self):
        """ show lattice configuration
        """
        return self._lattice_confdict

    def __str__(self):
        return self.getAllConfig()

    def getElementsByName(self, name):
        """ get element with given name (exclusively)
            return element object regarding to 'name'
            :param name: element name, case sensitive
        """
        try:
            return filter(lambda x:x.name == name, self._lattice_eleobjlist)[0]
        except:
            return ''

    def printAllElements(self):
        """ print out all modeled elements
        """
        cnt = 1
        print("{id:<3s}: {name:<12s} {type:<10s} {classname:<10s}".format(id='ID',name='Name',type='Type',classname='Class Name'))
        for e in self._lattice_eleobjlist:
            print("{cnt:>03d}: {name:<12s} {type:<10s} {classname:<10s}".format(cnt=cnt,name=e.name,type=e.typename,classname=e.__class__.__name__))
            cnt += 1

def test():
    #pvs = ('sxfel:lattice:Q01', 'sxfel:lattice:Q02')
    #A = Models(*pvs)
    latline = Models(name = 'BL')
 
    ch = element.ElementCharge(name = 'q',  config = "total = 1e-9")
    d1 = element.ElementDrift (name = 'd1', config = "l = 1.0")
    q1 = element.ElementQuad  (name = 'Q1', config = "l = 1.0, k1 = 10")
    lat1 = [d1, q1, q1] * 10
    latline.addElement(ch, lat1)
    latdict = latline.LatticeDict

    # generate lattice
    import lattice
    import json
    latins = lattice.Lattice(json.dumps(latdict))
    #print latins.getAllEle()
    #print latins.getAllBl()
    latfile = "/home/tong/Programming/projects/beamline/tests/test_models/fortest.lte"
    latins.generateLatticeFile(latline.name, latfile)

def test1():
    #
    import lattice
    import os
    #
    latticepath = os.path.join(os.getcwd(), '../lattice')
    ltefile = os.path.join(latticepath, 'linac.lte')
    latticepath = '/home/tong/Programming/projects/vFEL/simulation/SXFEL'
    ltefile = os.path.join(latticepath, 'sxfel_v14b.lte')
    lpins = lattice.LteParser(ltefile)
    allelements_str = lpins.file2json()
    #print allelements_str
    latins = lattice.Lattice(allelements_str)
    outlatfile = os.path.join(latticepath, 'tmp.lte')
    #latins.showBeamlines()
    
    #print latins.getFullBeamline('M1BI3', extend = True)
#    print latins.getAllBl()
#    print latins.getAllEle()
    #print latins.getBeamline('l0')
    #print latins.getFullBeamline('nl2', extend = True)
    
    #print lpins.getKwAsDict('Q01')
    #print lpins.getKwAsJson('BC1')
    #print lpins.getKwAsJson('testline')

    #for e in latins.getFullBeamline('bl', extend = True):
    #    print latins.getElementType(e)
    print latins.getElementConf('c', raw = True)
    print latins.getElementProperties('c')

    """
    newbl1 = latins.generateLatticeLine(latname = 'nl1', line = ['2*l0','l0'])
    newbl2 = latins.generateLatticeLine(latname = 'nl2', line = ['2*nl1'])
    latins.generateLatticeFile('nl2', outlatfile)
    """


if __name__ == '__main__':
    #test1()
    test()
