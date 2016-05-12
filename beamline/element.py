#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines all kinds of magnet components/elements.

Author      : Tong Zhang
Created     : 2016-03-22
"""

import json

import epics
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
from . import mathutils


class MagBlock(object):
    """ Super class of all elements, part of configuration parameters are
        defined here:
        objcnt: object counter, if create/add element one by one, objcnt
            will return the total element number by sumObjNum() method;
        comminfo: the shared common information for all elements, could be
            defined by calling setCommInfo() static method;
        __styleconfig_dict: style configurations for element drawing, could
            be defined by setStyleConfig() static method;

        New element should inherited MagBlock, and define following methods:
        __init__(), setStyle(), setDraw()
    """
    objcnt = 0  # object counter
    comminfo = {}  # common information
    __styleconfig_dict = {
        'quad':
            {'h': 0.6, 'fc': 'red', 'ec': 'red', 'alpha': 0.50,},
        'bend':
            {'h': 0.5, 'fc': 'blue', 'ec':'blue', 'alpha': 0.50,},
        'drift':
            {'h': 0.1, 'lw': 1, 'color': 'black', 'alpha': 0.75},
        'moni':
            {'lw': 1, 'color': '#FF9500', 'alpha': 0.75},
    }  # global configuration for element style, dict
    __styleconfig_json = json.dumps(__styleconfig_dict)

    def __init__(self, name=None):
        MagBlock.objcnt += 1
        self._name = name     # elementent name
        self.typename = None  # element type name
        self.comminfo = {k: v for k, v in MagBlock.comminfo.items()}  # common information

        self.simuinfo = {}  # simulation information
        self.ctrlinfo = {}  # control information
        self.miscinfo = {}  # other information

        self.simukeys = []  # keywords of simulation information
        self.ctrlkeys = []  # keywords of control information
        self.misckeys = []  # keywords of other information
        self.transfun = None  # unit translation function

        self.setConfDict = {'simu': self._setSimuConf,
                            'ctrl': self._setCtrlConf,
                            'misc': self._setMiscConf}

        self.prtConfigDict = {'simu': self._printSimuConf,
                              'ctrl': self._printCtrlConf,
                              'misc': self._printMiscConf,
                              'comm': self._printCommConf,
                              'all': self._printAllConf}

        self.dumpConfigDict = {'simu': self._dumpSimuConf,
                               'ctrl': self._dumpCtrlConf,
                               'misc': self._dumpMiscConf,
                               'comm': self._dumpCommConf,
                               'all': self._dumpAllConf,
                               'online': self._dumpOnlineConf}

        self.styledict = {}  # style dict
        self._patches = []   # patches list, empty
        self.next_inc_angle = 0  # for visualization, initial incremental angle

        self._spos = None # element position along beamline/lattice, in [m]
        self.transM = np.eye(6, 6, dtype = np.float64) # default element transport matrix
        self.transM_flag = False # if calcTransM() is called

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @staticmethod
    def rot(inputArray, theta=0, pc=(0, 0)):
        """ rotate input array with angle of theta
            :param inputArray: input array or list,
                e.g. np.array([[0,0],[0,1],[0,2]]) or [[0,0],[0,1],[0,2]]
            :param theta: rotation angle in degree
            :param pc: central point coords (x,y) regarding to rotation
            :return: rotated numpy array
        """
        if not isinstance(inputArray, np.ndarray):
            inputArray = np.array(inputArray)

        if not isinstance(pc, np.ndarray):
            pc = np.array(pc)

        theta = theta/180.0*np.pi  # degree to rad
        mr = np.array([
                [np.cos(theta), -np.sin(theta)],
                [np.sin(theta),  np.cos(theta)],
                ])
        return np.dot(mr, (inputArray-pc).transpose()).transpose() + pc.transpose()

    @staticmethod
    def copy_patches(ptches0):
        """ return a list of copied input matplotlib patches 
            
            :param ptches0: list of matploblib.patches objects
        """
        if not isinstance(ptches0, list):
            ptches0 = list(ptches0)
        copyed_ptches = []
        for pt in ptches0:
            pth = pt.get_path().deepcopy()
            ptch = patches.PathPatch(pth,
                                     lw=pt.get_lw(),
                                     fc=pt.get_fc(),
                                     ec=pt.get_ec(),
                                     alpha=pt.get_alpha())
            copyed_ptches.append(ptch)
        return copyed_ptches

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
            for k, v in infostr.items():
                MagBlock.comminfo[k] = v
        elif isinstance(infostr, str):
            for k, v in MagBlock.str2dict(infostr).items():
                MagBlock.comminfo[k] = v
        else:
            print("Information string ERROR.")

    @staticmethod
    def str2dict(istr):
        if 'lattice' not in istr.lower():
            tmpstr = istr.replace(',', '=').split('=')
        else:
            tmpstr = istr.split('=')
        k = [i.strip() for i in tmpstr[0::2]]
        v = [i.strip() for i in tmpstr[1::2]]
        return dict(zip(k, v))

    @staticmethod
    def setStyleConfig(config=None, showhelp=False):
        """ set/update global style configurations for magblock elements
            update Magblock._styleconfig_dict and _styleconfig_json
        :param config: configuration dict or json
        :param showhelp: if True, print showhelp information, default is False
        :return: new style config dict
        """
        if showhelp:
            print("The input configuration string should be with the format like:")
            print(MagBlock._MagBlock__styleconfig_json)
            print("with all or part of new properties, e.g.")
            print(json.dumps({'quad': {'fc': 'blue'}}))
        else:
            if config is None:
                config = MagBlock._MagBlock__styleconfig_dict
            if isinstance(config, dict):
                for k in set(config.keys()) & set(MagBlock._MagBlock__styleconfig_dict.keys()):
                    for k1 in set(config[k].keys()) & set(MagBlock._MagBlock__styleconfig_dict[k].keys()):
                        MagBlock._MagBlock__styleconfig_dict[k][k1] = config[k][k1]
                MagBlock._MagBlock__styleconfig_json = json.dumps(MagBlock._MagBlock__styleconfig_dict)
            elif isinstance(config, str):
                config = json.loads(config)
                for k in set(config.keys()) & set(MagBlock._MagBlock__styleconfig_dict.keys()):
                    for k1 in set(config[k].keys()) & set(MagBlock._MagBlock__styleconfig_dict[k].keys()):
                        MagBlock._MagBlock__styleconfig_dict[k][k1] = config[k][k1]
                MagBlock._MagBlock__styleconfig_json = json.dumps(MagBlock._MagBlock__styleconfig_dict)
            else:
                print("Information string ERROR.")

            return MagBlock._MagBlock__styleconfig_dict

    def setConf(self, conf, type='simu'):
        """ set information for different type dict,
            :param conf: configuration information, str or dict
            :param type: simu, ctrl, misc
        """
        if conf is None:
            return
        else:
            if isinstance(conf, str):
                conf = MagBlock.str2dict(conf)
            self.setConfDict[type](conf)

    def setStyle(self, **style):
        """ set element style configuration
            :param style: dict of keys: 'color', 'h', 'alpha'
        """
        pass

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
        :param angle: rotation angle
        :param p0: start drawing point coords, (x, y)
        :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        self.next_p0 = p0

    def printConfig(self, type='simu'):
        """ print information about element
            :param type: comm, simu, ctrl, misc, all
        """
        print("{s1}{s2:^22s}{s1}".format(s1="-" * 10, s2="Configuration START"))
        print("Element name: {en} ({cn})".format(en=self.name, cn=self.__class__.__name__))
        if self._spos is not None:
            print("Position: s = {pos:.3f} [m]".format(pos=float(self._spos)))
        self.prtConfigDict[type]()
        print("{s1}{s2:^22s}{s1}".format(s1="-" * 10, s2="Configuration END"))

    def dumpConfig(self, type='online', format='elegant'):
        """ dump element configuration to given format,
            inpurt parameters:
            :param type: comm, simu, ctrl, misc, all, online (default)
            :param format: elegant/mad, elegant by default
        """
        return self.dumpConfigDict[type](format)

    def getConfig(self, type='online', format='elegant'):
        """ only dump configuration part, dict
            :param type: comm, simu, ctrl, misc, all, online (default)
            :param format: elegant/mad, elegant by default
        """
        return self.dumpConfigDict[type](format).values()[0].values()[0]

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
            for k, v in sorted(self.simuinfo.items(), reverse=True):
                print("  {k:6s} = {v:6s}".format(k=str(k), v=str(v)))

    def _printCommConf(self):
        if self.comminfo:
            print("Common configs:")
            for k, v in sorted(self.comminfo.items(), reverse=True):
                print("  {k:6s} = {v:6s}".format(k=str(k), v=str(v)))

    def _printCtrlConf(self):
        """ get PV value and print out
        """
        if self.ctrlinfo:
            print("Control configs:")
            for k, v in sorted(self.ctrlinfo.items(), reverse=True):
                pv = v['pv']
                rval = epics.caget(pv)
                if rval is None:
                    val = ''
                else:
                    val = self.unitTrans(rval, direction='+')
                print("  {k:6s} = {pv:6s}, raw: {rval:>6s}, real: {val:>6s}".format(k=str(k),
                                                                                    pv=str(pv),
                                                                                    rval=str(rval),
                                                                                    val=str(val)))

    def _printMiscConf(self):
        if self.miscinfo:
            print("Miscellaneous configs:")
            for k, v in sorted(self.miscinfo.items(), reverse=True):
                print("  {k:6s} = {v:6s}".format(k=str(k), v=str(v)))

    def _printAllConf(self):
        # allinfo = {}
        # map(allinfo.update, [self.comminfo, self.ctrlinfo, self.miscinfo, self.simuinfo])
        # for k,v in sorted(allinfo.items(), reverse=True):
        #    print("{k:6s} = {v:6s}".format(k=k,v=v))
        self._printCommConf()
        self._printSimuConf()
        self._printCtrlConf()
        self._printMiscConf()

    def _dumpSimuConf(self, format):
        return {self.name.upper(): {self.typename: {k: self.simuinfo[k] for k in self.simukeys}}}

    def _dumpMiscConf(self, format):
        return {self.name.upper(): {self.typename: {k: self.miscinfo[k] for k in self.misckeys}}}

    def _dumpCtrlConf(self, format):
        return {self.name.upper(): {self.typename: {k: self.ctrlinfo[k] for k in self.ctrlkeys}}}

    def _dumpCommConf(self, format):
        return {self.name.upper(): {self.typename: {k: self.comminfo[k] for k in self.comminfo.keys()}}}

    def _dumpAllConf(self, format):
        allinfo = {}
        map(allinfo.update, [self.comminfo, self.miscinfo, self.simuinfo, self.ctrlinfo])
        return {self.name.upper(): {self.typename: {k: allinfo[k] for k in allinfo.keys()}}}

    def _dumpOnlineConf(self, format):
        """ dump element configuration json string for online modeling,
            in which control configuration should be overwritten simulation conf,
            e.g. in simuinfo: {'k1':10,'l':1}, ctrlinfo: {'k1':pv_name,...}
            the k1 value should be replaced by pv_name, and from which 
            the value read into, take note the simuinfo and ctrlinfo
            would not be changed.
        """
        oinfod = {k: v for k, v in self.simuinfo.items()}
        for k in (set(oinfod.keys()) & set(self.ctrlkeys)):
            oinfod[k] = self.ctrlinfo[k]
        return {self.name.upper(): {self.typename: oinfod}}

    def unitTrans(self, inval, direction='+', transfun=None):
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

    def showDraw(self, fignum=1):
        """ show the element drawing
        """
        if self._patches == []:
            print "Please setDraw() before showDraw(), then try again."
            return
        else:
            fig = plt.figure(fignum)
            fig.clear()
            ax = fig.add_subplot(111, aspect='equal')
            [ax.add_patch(i) for i in self._patches]
            bbox = self._patches[0].get_path().get_extents()
            x0 = 2.0*min(bbox.xmin, bbox.ymin)
            x1 = 2.0*max(bbox.xmax, bbox.ymax)
            ax.set_xlim(x0, x1)
            ax.set_ylim(x0, x1)
            # x1,y1=tuple(self.nextp0)
            # x2,y2=tuple(self.nextp1)
            # x3,y3=tuple(self.nextpc)
            # ax.plot([x1,x2,x3], [y1,y2,y3], 'o')#, ms=5, fc='b', ec='b')
            x, y = tuple(self.next_p0)
            ax.plot(x, y, 'o', ms=10, c='b')

            ax.annotate(s=self._anote['name'],
                        xy=self._anote['xypos'],
                        xytext=self._anote['textpos'],
                        textcoords='data',
                        arrowprops=dict(arrowstyle='->'),
                        rotation=-90,
                        fontsize='small')

            fig.canvas.draw()
            plt.grid()
            plt.show()

    def getPosition(self):
        """ return the element position along beamline/lattice, in [m]
            should be initialized in Models.initPos() method first 
            (by default, will complete after Models.addElement() method)
            i.e. valid position in [m] would return after lattice modeled.
        """
        return self._spos
    
    def setPosition(self, s):
        """ set element position along beamline/lattice, in [m]
        """
        self._spos = s

    def getLength(self):
        """ return element length if valid, or return 0.0
        """
        try:
            l = float(self.getConfig(type='simu')['l'])
        except:
            l = 0.0

        return l

    def getMatrix(self):
        """ return 6 x6 dims transport matrix
        """
        if self.transM_flag is not True:
            print("warning: invoke calcTransM() to update transport matrix.")
        return self.transM
    
    def getR(self, i, j):
        """ return transport matrix element, indexed by i(row) and j(col),
            with the initial index of 1
            :param i: row index
            :param j: col index
        """
        return self.transM[i-1,j-1]

class ElementCharge(MagBlock):
    """ charge element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'CHARGE'
        self.setConf(config)

class ElementCenter(MagBlock):
    """ center element
    """
    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'CENTER'
        self.setConf(config)

class ElementCsrcsben(MagBlock):
    """ csrcsben element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'CSRCSBEN'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['bend'].items()}
        self._style['lw'] = MagBlock._MagBlock__styleconfig_dict['drift']['lw']

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: rotation angle [deg] of drawing central point,
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        self._style['w'] = float(sconf['l'])  # element width
        self._style['angle'] = float(sconf['angle'])/np.pi*180  # bending angle, [deg]
        _width = self._style['w']
        _height = self._style['h']
        _fc = self._style['fc']
        _ec = self._style['ec']
        _alpha = self._style['alpha']
        _angle = self._style['angle']
        _lw = self._style['lw']

        if mode == 'plain':
            # _angle >= 0:
            #     p1---p2
            #     |    |
            #     |    |
            #   --p0---p3--
            # 
            # _angle < 0:
            #   --p0---p3--
            #     |    |
            #     |    |
            #     p1---p2
            x0, y0 = p0
            pc = x0 + _width*0.5, y0

            if _angle >= 0:
                x1, y1 = x0, y0 + _height
            else:  # _angle < 0
                x1, y1 = x0, y0 - _height
            
            x2, y2 = x0 + _width, y1
            x3, y3 = x2, y0
            vs = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x0, y0)]
            cs = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, fc=_fc, ec=_ec, alpha=_alpha, lw=_lw)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x3, y3
            self.next_inc_angle = 0
        else:  # fancy mode
            #   p1---p6---p2
            #   |         |
            # --p0   pc   p3-- 
            #   |         |
            #   p5---p7---p4

            x0, y0 = p0
            x1, y1 = x0, y0 + _height*0.5
            x6, y6 = x1 + _width*0.5, y1
            x2, y2 = x0 + _width, y1
            x3, y3 = x2, y0
            x4, y4 = x3, y0 - _height*0.5
            x7, y7 = x6, y4
            x5, y5 = x0, y4
            pc = x0 + _width*0.5, y0

            vs0 = [
                    (x0, y0),
                    (x1, y1),
                    (x6, y6),
                    (x2, y2),
                    (x3, y3),
                    (x4, y4),
                    (x7, y7),
                    (x5, y5),
                    (x0, y0),
                ]
            vs = MagBlock.rot(vs0, theta=angle, pc=p0)
            cs = [
                    Path.MOVETO,
                    Path.CURVE3,
                    Path.CURVE3,
                    Path.CURVE3,
                    Path.CURVE3,
                    Path.CURVE3,
                    Path.CURVE3,
                    Path.CURVE3,
                    Path.CURVE3,
                ]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, fc=_fc, ec=_ec, alpha=_alpha, lw=_lw)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = tuple(MagBlock.rot((x3, y3), theta=angle, pc=p0).tolist())
            self.next_inc_angle = _angle

        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

    def calcTransM(self, gamma=None, type='simu', incsym=-1):
        sconf = self.getConfig(type=type)
        bend_length = sconf['l']
        theta = sconf['angle']
        rho = bend_length/np.sin(theta)
        #rho = np.sqrt(gamma**2-1)*m0*c0/bend_field/e0
        #theta = np.arcsin(bend_length/rho)
        self.transM = mathutils.transRbend(theta, rho, gamma, incsym)
        if gamma is not None:
            m0 = 9.10938215e-31
            e0 = 1.602176487e-19
            c0 = 299792458.0
            self._bend_field = np.sqrt(gamma**2-1)*m0*c0/rho/e0
            self._rho = rho
            self.setConf({'rho':self._rho, 'field':self._bend_field}, type='misc')
        self.transM_flag = True
        return self.transM

    @property
    def field(self):
        return self._bend_field

    @property
    def rho(self):
        return self._rho

class ElementCsrdrift(MagBlock):
    """ csrdrift element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'CSRDRIFT'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

        pc = x0 + 0.5*_length, (y0 + y1)*0.5
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

    def calcTransM(self, gamma=None):
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            l = float(sconf['l'])
        else:
            l = 0
        self.transM = mathutils.transDrift(l, gamma)
        self.transM_flag = True
        return self.transM

class ElementDrift(MagBlock):
    """ drift element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'DRIFT'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

        pc = x0 + 0.5*_length, (y0 + y1)*0.5
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}
        
    def calcTransM(self, gamma=None):
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            l = float(sconf['l'])
        else:
            l = 0
        self.transM = mathutils.transDrift(l, gamma)
        self.transM_flag = True
        return self.transM

class ElementKicker(MagBlock):
    """ kicker element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'KICKER'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

        pc = x0 + 0.5*_length, (y0 + y1)*0.5
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

class ElementLscdrift(MagBlock):
    """ lscdrift element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'LSCDRIFT'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['lemgth'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

        pc = x0 + 0.5*_length, (y0 + y1)*0.5
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

    def calcTransM(self, gamma=None):
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            l = float(sconf['l'])
        else:
            l = 0
        self.transM = mathutils.transDrift(l, gamma)
        self.transM_flag = True
        return self.transM

class ElementMark(MagBlock):
    """ mark element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'MARK'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

        pc = x0 + 0.5*_length, (y0 + y1)*0.5
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

class ElementMoni(MagBlock):
    """ moni element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'MONI'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['moni'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _fancyc = self._style['color']
        _alpha = self._style['alpha']
        _plainc = MagBlock._MagBlock__styleconfig_dict['drift']['color']
        
        #
        #   |
        # --p0--p1--
        #   |
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            pc = x0 + 0.5*_length, (y0 + y1)*0.5
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_plainc, ec=_plainc, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            #x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            #pc = x0 + 0.5*_length, (y0 + y1)*0.5

            x1, y1 = x0, y0 + 0.5 * _length
            x2, y2 = x1 + 1./3.0 * _length, y1
            x3, y3 = x2 + 1./3.0 * _length, y1
            x4, y4 = x3 + 1./3.0 * _length, y1
            x5, y5 = x4, y0
            x6, y6 = x5, y5 - 0.5 * _length
            x7, y7 = x3, y6
            x8, y8 = x3, y7 + 1./3.0 * _length
            x9, y9 = x2, y8
            x10, y10 = x9, y7
            x11, y11 = x0, y7
            pc = (x0 + x5) *0.5, (y0 + y5) * 0.5

            verts1 = [
                    (x0, y0),
                    (x1, y1),
                    (x2, y2),
                    pc,
                    (x3, y3),
                    (x4, y4),
                    (x5, y5),
                    (x6, y6),
                    (x7, y7),
                    (x8, y8),
                    (x9, y9),
                    (x10, y10),
                    (x11, y11),
                    (x0, y0),
                ]

            codes1 = [
                     Path.MOVETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.LINETO,
                     Path.CLOSEPOLY,
                    ]
            pth = Path(verts1, codes1)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_fancyc, ec=_fancyc, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            #self.next_p0 = x1, y1
            self.next_p0 = x5, y5
            self.next_inc_angle = 0

        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

class ElementQuad(MagBlock):
    """ quad element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'QUAD'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['quad'].items()}
        self._style['lw'] = MagBlock._MagBlock__styleconfig_dict['drift']['lw']

    def unitTrans(self, inval, direction='+', transfun=None):
        transfun = self.transfun
        if transfun is not None:
            outval = transfun(inval, direction)
        else:  # use builtin translation rules
            if direction == '+':  # PV->physical
                outval = 2 * inval
            elif direction == '-':  # physical->PV
                outval = 0.5 * inval
        return outval

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: rotation angle [deg] of drawing central point,
                angle is rotating from x-axis to be '+' or '-',
                '+': anticlockwise, '-': clockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """

        sconf = self.getConfig(type='simu')
        self._style['w'] = float(sconf['l'])  # element width
        _width = self._style['w']
        _height = self._style['h']
        _fc = self._style['fc']
        _ec = self._style['ec']
        _alpha = self._style['alpha']
        _kval = float(sconf['k1'])
        _lw = self._style['lw']

        if mode == 'plain':
            # _kval >= 0:
            #    p1---p2
            #    |    |
            #    |    |
            # ---p0---p3---
            #
            # _kval < 0:
            # ---p0---p3---
            #    |    |
            #    |    |
            #    p1---p2

            x0, y0 = p0

            if _kval >= 0:
                x1, y1 = x0, y0 + _height
            else:
                x1, y1 = x0, y0 - _height

            x2, y2 = x0 + _width, y1
            x3, y3 = x2, y0

            vs = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x0, y0)]
            cs = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, fc=_fc, ec=_ec, alpha=_alpha, lw=_lw)

            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x3, y3
            self.next_inc_angle = 0
        else:  # fancy mode
            #       p1
            #     /    \
            # --p0  pc  p2(nextp0)---
            #     \    /
            #       p3

            x0, y0 = p0
            x1, y1 = x0 + _width*0.5, y0 + _height*0.5
            x2, y2 = x1 + _width*0.5, y0
            x3, y3 = x1, y0 - _height*0.5
            pc = x0 + _width*0.5, y0

            vs0 = [
                  (x0, y0),
                  (x1, y1), 
                  (x2, y2), 
                  (x3, y3), 
                  (x0, y0)
                  ]
            vs = MagBlock.rot(vs0, theta=angle, pc=p0)
            cs = [
                  Path.MOVETO,
                  Path.CURVE3,
                  Path.CURVE3,
                  Path.CURVE3,
                  Path.CURVE3
                  ]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, fc=_fc, ec=_ec, alpha=_alpha, lw=_lw)

            self._patches = []
            self._patches.append(ptch)
            pout = x0+_width, y0   # the right most point in x-axis
            self.next_p0 = tuple(MagBlock.rot(pout, theta=angle, pc=p0).tolist())
            self.next_inc_angle = 0

        pc = x0 + 0.5*_width, y0
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

    def calcTransM(self, gamma=None, type='simu'):
        sconf = self.getConfig(type=type)
        l = float(sconf['l'])
        k1 = self.getK1(type='ctrl')
        self.transM = mathutils.transQuad(l, k1, gamma)
        self.transM_flag = True
        return self.transM

    def getK1(self, type='simu'):
        if type == 'ctrl':
            pv = self.ctrlinfo.get('k1')['pv']
            rval = epics.caget(pv)
            if rval is None:
                val = self.getConfig(type='simu')['k1']
            else:
                val = self.unitTrans(rval, direction = '+')
            return val
        else:
            return self.getConfig(type='simu')['k1']

class ElementRfcw(MagBlock):
    """ rfcw element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'RFCW'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        _height = self._style['h']
        if 'freq' in sconf:
            freqi = int(float(sconf['freq'])/2856.0e6)
        else:
            freqi = 0
        
        if freqi == 1:
            _fancyc = '#FFDDBB' # S band
            _text = 'S'
        elif freqi == 2:
            _fancyc = '#5E5EFF' # C band
            _text = 'C'
        elif freqi == 4:
            _fancyc = '#8800FF' # X band
            _text = 'X'
        else:
            _fancyc = '#FFBB00' # other
            _text = '..'
        
        #
        #   p1-------p2
        #   |        |
        # --p0       p3--
        #   |        |
        #   p5-------p4
        #
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0, y0 + 0.5*_height
            x2, y2 = x0 + _length, y1
            x3, y3 = x2, y0
            x4, y4 = x3, y0 - 0.5*_height
            x5, y5 = x0, y4
            vs = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x0, y0)]
            cs = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc='w', ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x3, y3
            self.next_inc_angle = 0
            pc = (x0 + x3)*0.5, (y0 + y3)*0.5
        else:  # fancy mode, 
            x0, y0 = p0
            x1, y1 = x0, y0 + 0.5*_height
            x2, y2 = x0 + _length, y1
            x3, y3 = x2, y0
            x4, y4 = x3, y0 - 0.5*_height
            x5, y5 = x0, y4
            vs = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x0, y0)]
            cs = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_fancyc, ec=_fancyc, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x3, y3
            self.next_inc_angle = 0
            pc = (x0 + x3)*0.5, (y0 + y3)*0.5

        self._atext = {'xypos': pc, 'text': _text}
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename,
                       'atext': self._atext}

class ElementRfdf(MagBlock):
    """ rfdf element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'RFDF'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        _height = self._style['h']
        if 'freq' in sconf:
            freqi = int(float(sconf['freq'])/2856.0e6)
        elif 'frequency' in sconf:
            freqi = int(float(sconf['frequency'])/2856.0e6)
        else:
            freqi = 0
        
        if freqi == 1:
            _fancyc = '#FFDDBB' # S band
            _text = 'SD'
        elif freqi == 2:
            _fancyc = '#5E5EFF' # C band
            _text = 'CD'
        elif freqi == 4:
            _fancyc = '#8800FF' # X band
            _text = 'XD'
        else:
            _fancyc = '#FFBB00' # other
            _text = '..'
        
        #
        #   p1-------p2
        #   |        |
        # --p0       p3--
        #   |        |
        #   p5-------p4
        #
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0, y0 + 0.5*_height
            x2, y2 = x0 + _length, y1
            x3, y3 = x2, y0
            x4, y4 = x3, y0 - 0.5*_height
            x5, y5 = x0, y4
            vs = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x0, y0)]
            cs = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc='w', ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x3, y3
            self.next_inc_angle = 0
            pc = (x0 + x3)*0.5, (y0 + y3)*0.5
        else:  # fancy mode, 
            x0, y0 = p0
            x1, y1 = x0, y0 + 0.5*_height
            x2, y2 = x0 + _length, y1
            x3, y3 = x2, y0
            x4, y4 = x3, y0 - 0.5*_height
            x5, y5 = x0, y4
            vs = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x0, y0)]
            cs = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_fancyc, ec=_fancyc, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x3, y3
            self.next_inc_angle = 0
            pc = (x0 + x3)*0.5, (y0 + y3)*0.5

        self._atext = {'xypos': pc, 'text': _text}
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename,
                       'atext': self._atext}

class ElementWake(MagBlock):
    """ wake element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'WAKE'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

class ElementWatch(MagBlock):
    """ watch element
    """

    def __init__(self, name=None, config=None):
        MagBlock.__init__(self, name)
        self.typename = 'WATCH'
        self.setConf(config)
        self._style = {k: v for k, v in MagBlock._MagBlock__styleconfig_dict['drift'].items()}

    @property
    def style(self):
        return self._style

    def setStyle(self, **style):
        for k in set(style.keys()) & set(self._style.keys()):
            self._style[k] = style[k]

    def setDraw(self, p0=(0, 0), angle=0, mode='plain'):
        """ set element visualization drawing
            
            :param p0: start drawing position, (x,y)
            :param angle: angle [deg] between x-axis
                angle is rotating from x-axis to be '+' or '-',
                '+': clockwise, '-': anticlockwise
            :param mode: artist mode, 'plain' or 'fancy', 'plain' by default
        """
        sconf = self.getConfig(type='simu')
        if 'l' in sconf:
            self._style['length'] = float(sconf['l'])
        else:
            self._style['length'] = 0
        self._style['angle'] = angle
        _theta = angle/180.0*np.pi  # deg to rad
        _length = self._style['length']
        _lw = self._style['lw']
        _color = self._style['color']
        _alpha = self._style['alpha']
        
        #
        # --p0-------p1--
        # 
        if mode == 'plain':
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0
        else:  # fancy mode, same as plain, could be more fancy(Apr.08, 2016)
            x0, y0 = p0
            x1, y1 = x0 + _length, y0 + _length * np.tan(_theta)
            vs = [(x0, y0), (x1, y1)]
            cs = [Path.MOVETO, Path.LINETO]
            pth = Path(vs, cs)
            ptch = patches.PathPatch(pth, lw=_lw, fc=_color, ec=_color, alpha=_alpha)
            self._patches = []
            self._patches.append(ptch)
            self.next_p0 = x1, y1
            self.next_inc_angle = 0

        pc = x0 + 0.5*_length, (y0 + y1)*0.5
        self._anote = {'xypos': pc, 'textpos': pc, 'name': self.name.upper(), 'type': self.typename}

class ElementBeamline(MagBlock):
    """ beamline element
    """

    def __init__(self, name='bl', config=None):
        MagBlock.__init__(self, name)
        self.typename = 'BEAMLINE'
        self.setConf(config)

ElementDrif = ElementDrift
ElementLscdrif = ElementLscdrift
ElementCsrdrif = ElementCsrdrift
ElementCsrcsbent = ElementCsrcsben


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

    # STEP 1: define common information, two different input parameter formats
    # commdinfo = {'DATE': '2016-03-22', 'AUTHOR': 'Tong Zhang'}
    comminfo = 'DATE = 2016-03-24, 16:05, AUTHOR = Tong Zhang'
    MagBlock.setCommInfo(comminfo)

    # STEP 2: create element

    # charge
    chconf = {'total': 1e-9}
    CH = ElementCharge(name='Q1', config=chconf)

    # csrcsben
    simconf = {"edge1_effects": 1,
               "edge2_effects": 1,
               "hgap": 0.015,
               "csr": 0,
               "nonlinear": 1,
               "n_kicks": 100,
               "integration_order": 4,
               "bins": 512,
               "sg_halfwidth": 1,
               "block_csr": 0,
               'l': 0.5, }
    angle = 0.2

    B1 = ElementCsrcsben(name='b1', config={'angle': angle, 'e1': 0, 'e2': angle})
    B1.setConf(simconf, type='simu')
    # B1.setConf("pv=sxfel:lattice:b1",  type = 'ctrl')

    B2 = ElementCsrcsben(name='b2', config={'angle': -angle, 'e1': -angle, 'e2': 0})
    B3 = ElementCsrcsben(name='b3', config={'angle': -angle, 'e1': 0, 'e2': -angle})
    B4 = ElementCsrcsben(name='b4', config={'angle': angle, 'e1': angle, 'e2': 0})
    B2.setConf(simconf, type='simu')
    B3.setConf(simconf, type='simu')
    B4.setConf(simconf, type='simu')

    # drift
    D0 = ElementDrift(name='D0', config="l=1.0")

    # quad
    Q1 = ElementQuad(name='Q1', config="k1 = 10, l = 0.1")
    dftconf = {'tilt': "pi 4 /"}
    Q1.setConf(dftconf, type='simu')

    # beamline
    latele = [obj.name for obj in [D0, Q1, D0, B1, D0, B2, D0, D0, B3, D0, B4, D0, Q1, D0]]
    latstr = '(' + ' '.join(latele) + ')'

    bl = ElementBeamline(name='bl', config={'lattice': latstr})
    # bl = ElementBeamline(name = 'bl1', config = "lattice = (q d0 q1)")
    # bl.setConf("lattice = (d,q,b)", type = 'simu')
    print bl

    # print MagBlock.sumObjNum()


if __name__ == '__main__':
    test()

