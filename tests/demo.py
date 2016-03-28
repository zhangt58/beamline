#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" workflow example for online modeling.
    
    Author: Tong Zhang
    Dated : 2016-03-25
"""

import beamline
import os

def modelWorkflow():
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
    beamline.MagBlock.setCommInfo(comminfo)
    
    ## STEP 2: create element

    # charge
    chconf = {'total':1e-9}
    q = beamline.ElementCharge(name = 'q', config = chconf)

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

    B1 = beamline.ElementCsrcsben(name = 'b1', config = {'angle':angle, 'e1':0, 'e2':angle})
    B1.setConf(simconf, type = 'simu')
    #B1.setConf("pv=sxfel:lattice:b1",  type = 'ctrl')
    
    B2 = beamline.ElementCsrcsben(name = 'b2', config = {'angle':-angle, 'e1':-angle, 'e2':0})
    B3 = beamline.ElementCsrcsben(name = 'b3', config = {'angle':-angle, 'e1':0,      'e2':-angle})
    B4 = beamline.ElementCsrcsben(name = 'b4', config = {'angle': angle, 'e1':angle,  'e2':0})
    B2.setConf(simconf, type = 'simu')
    B3.setConf(simconf, type = 'simu')
    B4.setConf(simconf, type = 'simu')

    # drift
    D0 = beamline.ElementDrift(name = 'D0', config = "l=1.0")

    # quad
    Q1 = beamline.ElementQuad(name = 'Q1', config = "k1 = 10, l = 0.1")
    dftconf = {'tilt':"pi 4 /"}
    Q1.setConf(dftconf, type = 'simu')


    ## STEP 3: make lattice beamline
    # METHOD 1: CANNOT get all configurations
    # use 'ElementBeamline' class of 'element' module
    #
    # beamline
    latele = [obj.name for obj in [q, D0, Q1, D0, B1, D0, B2, D0, D0, B3, D0, B4, D0, Q1, D0]]
    latstr = '(' + ' '.join(latele) + ')'
    
    bl = beamline.ElementBeamline(name = 'bl', config = {'lattice':latstr})
    #bl = beamline.ElementBeamline(name = 'bl1', config = "lattice = (q d0 q1)")
    #bl.setConf("lattice = (d,q,b)", type = 'simu')
    #print bl

    # METHOD 2: CAN get all configurations
    # use 'Models' class of 'models' module
    latline = beamline.Models(name = 'blchi')
    qline = (D0, Q1, D0)
    chi   = (B1, D0, B2, D0, D0, B3, D0, B4)
    latline.addElement(q, qline, chi, qline)
    #print latline.LatticeList
    #print latline.LatticeDict[latline.name]
    #print latline
    
    # show defined elements number
    #print beamline.MagBlock.sumObjNum()

    ## STEP 4: create Lattice instance, make simulation required input files
    # e.g. '.lte' for elegant tracking, require all configurations
    latins = beamline.Lattice(latline.getAllConfig())
    latfile = os.path.join(os.getcwd(), 'tracking/test.lte')
    latins.generateLatticeFile(latline.name, latfile)

    ## STEP 5: simulation with generated lattice file
    simpath = os.path.join(os.getcwd(), 'tracking')
    elefile = os.path.join(simpath, 'test.ele')
    h5out   = os.path.join(simpath, 'tpout.h5')
    elesim = beamline.Simulator()
    elesim.setMode('elegant')
    elesim.setScript('runElegant.sh')
    elesim.setExec('elegant')
    elesim.setPath(simpath)
    elesim.setInputfiles(ltefile = latfile, elefile = elefile)
    elesim.doSimulation()
    data = elesim.getOutput(file = 'test.out', data = ('t', 'p'), dump = h5out)

if __name__ == '__main__':
    modelWorkflow()

