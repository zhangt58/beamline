#!/usr/bin/env pyton
# -*- coding: utf-8 -*-

"""
This module is written for the purposes of elements modeling for accelerator:
    1: manually define magnetic elements one by one and model the machine;
    2: interpret lattice file (.lte file) to be modeled elements;
    2: update (EPICS databases)/(EPICS PVs) with new configuration.


Author      : Tong Zhang
Created     : 2016-03-18
"""

import copy
import json

import epics
import matplotlib.pyplot as plt

from . import element


class Models(object):
    """ make lattice configuration (json) for lattice.Lattice
        return instance as a json string file with all configuration.
        get lattice name by instance.name.
    """
    def __init__(self, name='BL', mode='simu'):
        """ create Models instance,
            :param name: lattice name, 'BL' by defualt
            :param mode: 'simu' or 'online' mode,
                if 'online' is defined, the lattice should be update the ctrl
                configuration before dumping configuration string by calling
                method: getCtrlConf()
        """
        self._mode = mode.lower()           # 'simu' (simulation) or 'online' (online) mode
        self._lattice_name = name.upper()   # lattice name
        self._lattice_elecnt = 0            # lattice element counter
        self._lattice_elenamelist = []      # lattice element name list
        self._lattice_eleobjlist = []       # lattice element object list
        self._lattice_confdict = {}         # lattice configuration dict
        self._lattice = element.ElementBeamline(
                            name=self._lattice_name,
                            config="lattice = ()")  # initial lattice configuration

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

        #self._lattice.setConf(Models.makeLatticeString(self._lattice_elenamelist))
        self._lattice.setConf(Models.makeLatticeDict(self._lattice_elenamelist))

        # positioning elements
        self.initPos()

        return self._lattice_elecnt
    
    def initPos(self, startpos=0.0):
        """ initialize the elements position [m] in lattice, the starting
            point is 0 [m] for the first element by default.

            :param startpos: starting point, 0 [m] by default
        """
        spos = startpos
        for ele in self._lattice_eleobjlist:
            #print("{name:<10s}: {pos:<10.3f}".format(name=ele.name, pos=spos))
            ele.setPosition(spos)
            spos += ele.getLength()

    
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
                        if pvval is not None:
                            e.simuinfo[k] = e.unitTrans(pvval, direction='+')
                            if msgout:
                                print("  Done.") 
                        else: 
                            if msgout:
                                print("  Failed.")
                    except:
                        pass
        else:  # self.mode is 'simu' do nothing
            pass
        return _lattice_eleobjlist_copy

    def putCtrlConf(self, eleobj, ctrlkey, val, type='raw'):
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
            else:  # val should be translated
                newval = eleobj.unitTrans(val, direction='-')
            epics.caput(eleobj.ctrlinfo[ctrlkey]['pv'], newval)
            return True
        else:
            return False

    def getAllConfig(self, fmt='json'):
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

    def updateConfig(self, eleobj, config, type='simu'):
        """ write new configuration to element
            input parameters:
            :param eleobj: define element object
            :param config: new configuration for element, string or dict
            :param type: 'simu' by default, could be online, misc, comm, ctrl
        """
        eleobj.setConf(config, type=type)

    @staticmethod
    def makeLatticeString(ele):
        """ return string like "lattice = (q b d)"
        :param ele: element list
        """
        return 'lattice = (' + ' '.join(ele) + ')'
    
    @staticmethod
    def makeLatticeDict(ele):
        """ return lattice dict conf like {"lattice": "(q b d)"}
        :param ele: element list
        """
        return {"lattice": '(' + ' '.join(ele) + ')'}

    @staticmethod
    def flatten(ele):
        """ flatten recursively defined list,
            e.g. [1,2,3, [4,5], [6,[8,9,[10,[11,'x']]]]]
            :param ele: recursive list, i.e. list in list in list ...
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
        """ get element with given name,
            return list of element objects regarding to 'name'
            :param name: element name, case sensitive, if elements are
                auto-generated from LteParser, the name should be lower cased.
        """
        try:
            return filter(lambda x: x.name == name, self._lattice_eleobjlist)
        except:
            return []

    def printAllElements(self):
        """ print out all modeled elements
        """
        cnt = 1
        print("{id:<3s}: {name:<12s} {type:<10s} {classname:<10s}"
              .format(id='ID', name='Name', type='Type', classname='Class Name'))
        for e in self._lattice_eleobjlist:
            print("{cnt:>03d}: {name:<12s} {type:<10s} {classname:<10s}"
                  .format(cnt=cnt, name=e.name, type=e.typename, classname=e.__class__.__name__))
            cnt += 1

    def draw(self, startpoint=(0, 0), mode='plain', showfig=False):
        """ lattice visualization
            
            :param startpoint: start drawing point coords, default: (0, 0)
            :param showfig: show figure or not, default: False
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
            :return: patchlist, anotelist, (xmin0, xmax0), (ymin0, ymax0)
                patchlist: list of element patches
                anotelist: list of annotations
                (xmin0, xmax0) and (ymin0, ymax0) are ploting range
        """
        p0 = startpoint
        angle = 0.0
        patchlist = []
        anotelist = []
        xmin0, xmax0, ymin0, ymax0 = 0, 0, 0, 0
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        for ele in self._lattice_eleobjlist:
            ele.setDraw(p0=p0, angle=angle, mode=mode)
            angle += ele.next_inc_angle
            #print ele.name, ele.next_inc_angle, angle
            patchlist.extend(ele._patches)
            if hasattr(ele, '_anote'): anotelist.append(ele._anote)
            try:
                p0 = ele.next_p0
                xyrange = ele._patches[0].get_path().get_extents()
                xmin, xmax = xyrange.xmin, xyrange.xmax
                ymin, ymax = xyrange.ymin, xyrange.ymax
            except:
                pass
            xmin0 = min(xmin, xmin0)
            xmax0 = max(xmax, xmax0)
            ymin0 = min(ymin, ymin0)
            ymax0 = max(ymax, ymax0)
        
        # show figure or not
        if showfig:
            fig = plt.figure()
            ax = fig.add_subplot(111, aspect='equal')
            [ax.add_patch(i) for i in patchlist]
            [ax.annotate(s=i['name'],
                         xy=i['xypos'],
                         xytext=i['textpos'],
                         arrowprops=dict(arrowstyle='->'),
                         rotation=-90,
                         fontsize='small') 
                         for i in anotelist]
            ax.set_xlim([xmin0*2, xmax0*2])
            ax.set_ylim([ymin0*2, ymax0*2])
            plt.show()

        return patchlist, anotelist, (xmin0, xmax0), (ymin0, ymax0)

    @staticmethod
    def plotElements(ax, patchlist):
        """ plot elements' drawings to axes
            
            :param ax: matplotlib axes object
            :param patchlist: element patch object list
        """
        [ax.add_patch(ptch) for ptch in patchlist]

    @staticmethod
    def anoteElements(ax, anotelist, showAccName=False, efilter=None, textypos=None, **kwargs):
        """ annotate elements to axes
            
            :param ax: matplotlib axes object
            :param anotelist: element annotation object list
            :param showAccName: tag name for accelerator tubes? default is False, 
                show acceleration band type, e.g. 'S', 'C', 'X', or for '[S,C,X]D' for cavity
            :param efilter: element type filter, default is None, annotate all elements
                could be defined to be one type name or type name list/tuple, e.g.
                filter='QUAD' or filter=('QUAD', 'CSRCSBEN')
            :param textypos: y coordinator of annotated text string
            :param kwargs:
                alpha=0.8, arrowprops=dict(arrowstyle='->'), rotation=-60, fontsize='small'

            return list of annotation objects
        """
        defaultstyle = {'alpha': 0.8, 'arrowprops': dict(arrowstyle='->'), 
                        'rotation': -60, 'fontsize': 'small'}
        defaultstyle.update(kwargs)
        anote_list = []
        if efilter is None:
            for anote in anotelist:
                if textypos is None:
                    textxypos = tuple(anote['textpos'])
                else:
                    textxypos = tuple((anote['textpos'][0], textypos))
                if not showAccName and anote['type'] in ('RFCW', 'RFDF'):
                    kwstyle = {k:v for k,v in defaultstyle.items()}
                    kwstyle.pop('arrowprops')
                    note_text = ax.text(anote['atext']['xypos'][0], anote['atext']['xypos'][1],
                            anote['atext']['text'], **kwstyle)
                else:
                    note_text = ax.annotate(s=anote['name'], xy=anote['xypos'], xytext=textxypos, **defaultstyle)
                anote_list.append(note_text)
        else:
            if not isinstance(efilter, tuple):
                filter = tuple(efilter)
            for anote in anotelist:
                if anote['type'] in efilter:
                    if textypos is None:
                        textxypos = tuple(anote['textpos'])
                    else:
                        textxypos = tuple((anote['textpos'][0], textypos))
                    if not showAccName and anote['type'] in ('RFCW', 'RFDF'):
                        kwstyle = {k:v for k,v in defaultstyle.items()}
                        kwstyle.pop('arrowprops')
                        note_text = ax.text(anote['atext']['xypos'][0], anote['atext']['xypos'][1],
                                anote['atext']['text'], **kwstyle)
                    else:
                        note_text = ax.annotate(s=anote['name'], xy=anote['xypos'], xytext=textxypos, **defaultstyle) 
                    anote_list.append(note_text)
        return anote_list

def test():
    #pvs = ('sxfel:lattice:Q01', 'sxfel:lattice:Q02')
    #A = Models(*pvs)
    latline = Models(name='BL')
 
    ch = element.ElementCharge(name='q',  config="total = 1e-9")
    d1 = element.ElementDrift(name='d1', config="l = 1.0")
    q1 = element.ElementQuad(name='Q1', config="l = 1.0, k1 = 10")
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
    print latins.getElementConf('c', raw=True)
    print latins.getElementProperties('c')

    """
    newbl1 = latins.generateLatticeLine(latname = 'nl1', line = ['2*l0','l0'])
    newbl2 = latins.generateLatticeLine(latname = 'nl2', line = ['2*nl1'])
    latins.generateLatticeFile('nl2', outlatfile)
    """


if __name__ == '__main__':
    #test1()
    test()
