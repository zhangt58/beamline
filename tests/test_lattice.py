#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tong Zhang
# 2016-03-03
#

import beamline
import os
import unittest

class BeamlineLteParserTest(unittest.TestCase):
    def setUp(self):
        latticePath = os.path.join(os.getcwd(), '../lattice')
        infilename  = os.path.join(latticePath, 'linac.lte')
        self.pins = beamline.LteParser(infilename)

class BeamlineLatticeTest(unittest.TestCase):
    def setUp(self):
        latticePath = os.path.join(os.getcwd(), '../lattice')
        infilename  = os.path.join(latticePath, 'linac.lte')
        pins = beamline.LteParser(infilename)
        self.lins  = beamline.Lattice(pins.file2json())

class DetectAllKwsTest(BeamlineLteParserTest):
    # detect all keywords
    def runTest(self):
        all_kws = self.pins.detectAllKws()
        all_kws_list = ['q', 'A1i', 'A1p', 'A1e', 'A2i', 'A2p', 'A2e', 
                'A3i', 'A3p', 'A3e', 'A4i', 'A4p', 'A4e', 'B11', 'B12', 
                'B13', 'B14', 'DB11', 'DB12', 'DB13', 'DB14', 'B0', 'DQD1', 
                'DQD2', 'DQD3', 'DBD', 'DBdm', 'D1', 'D2', 'D3', 'DF1', 
                'DF2', 'DF3', 'DF4', 'DF5', 'DBLL1', 'DBLL2', 'DBLL3', 
                'DBLL4', 'DBLL5', 'DBPM1', 'DBPM2', 'DBPM3', 'DICT', 
                'DP1FH', 'DP1SH', 'DP2FH', 'DP2SH', 'DP3FH', 'DP3SH', 
                'DP4FH', 'DP4SH', 'DP5FH', 'DP5SH', 'DP6FH', 'DP6SH', 
                'DS1FH', 'DS1SH', 'DVALV', 'DAM', 'Q01', 'Q02', 'Q03', 
                'Q04', 'Q05', 'Q06', 'Q07', 'Q08', 'Q09', 'Q10', 'PF1', 
                'PF2', 'PSTN1', 'PSTN2', 'BPM01', 'BPM02', 'BPM03', 
                'PRL1', 'PRL2', 'PRL3', 'PRL4', 'PRL5', 'PRL6', 'PRL7', 
                'wA1i', 'wA1p', 'wA1e', 'wA2i', 'wA2p', 'wA2e', 'wA3i', 
                'wA3p', 'wA3e', 'wA4i', 'wA4p', 'wA4e', 'w00', 'w01', 'w02', 
                'w03', 'w04', 'w05', 'w06', 'w07', 'w08', 'w09', 'A1', 'A2', 
                'A3', 'A4', 'bi2s', 'bi2b', 'doub1', 'doub2', 'trip3', 'chi', 
                'bl']
        self.assertEqual(all_kws, all_kws_list)

class GetKwTest(BeamlineLteParserTest):
    # get configuration of one keyword
    def runTest(self):
        # show string
        kw = 'q01'
        self.assertEqual(self.pins.getKw(kw).confstr, 'Q01 : QUAD, L = 5.000000000E-02, K1 = 0')

        # string to dict
        self.assertEqual(self.pins.getKw(kw).toDict().confdict, {'Q01': {'QUAD': {'K1': '0', 'L': '5.000000000E-02'}}})

        # resolve rpn expression
        self.assertEqual(self.pins.getKw(kw).toDict().solve_rpn().confdict, {'Q01': {'QUAD': {'K1': 0.0, 'L': 0.05}}})

class GetKwAsDictTest(BeamlineLteParserTest):
    # get keyword as dict
    def runTest(self):
        self.assertEqual(self.pins.getKwAsDict('q02'), {'Q02': {'QUAD': {'K1': '-0', 'L': '5.000000000E-02'}}})
        # str2dict
        self.assertEqual(self.pins.getKwAsDict('q01'), self.pins.str2dict('Q01 : QUAD, L = 5.000000000E-02, K1 = 0'))

class File2jsonTest(BeamlineLteParserTest):
    # dump file content into json string format
    # dump to file: pins.file2json('jfile.json')
    def runTest(self):
        self.assertEqual(self.pins.file2json(), open('jfile.json','r').read())

"""
class GetAllKwsTest(BeamlineLatticeTest):
    # get all keywords
    # magnetic elements: kws_ele
    # other elements: kws_bl (beamline and prefix strings)
    def runTest(self):
        kws_ele, kws_bl = self.lins.getAllKws()
        self.assertEqual(kws_ele, [u'DS1FH', u'DP3FH', u'W03', u'DP2SH', u'A4P', u'DBLL5', u'DBLL4', u'DBLL3', u'DBLL2', u'DBLL1', u'BPM02', u'BPM03', u'DP5FH', u'BPM01', u'DBD', u'DVALV', u'B0', u'DP1FH', u'B13', u'DBDM', u'A4E', u'W08', u'W09', u'W04', u'W05', u'W06', u'W07', u'W00', u'W01', u'W02', u'A4I', u'WA1E', u'WA1I', u'DP3SH', u'PRL2', u'PRL3', u'PRL1', u'PRL6', u'PRL7', u'PRL4', u'PRL5', u'DP6SH', u'DP4SH', u'Q03', u'_prefixstr', u'Q', u'WA2E', u'WA3P', u'Q05', u'A2P', u'DP2FH', u'B14', u'B12', u'A2E', u'B11', u'A2I', u'DB14', u'DB11', u'DB13', u'DB12', u'DF5', u'DF4', u'DF1', u'DF3', u'DF2', u'WA3I', u'Q10', u'WA3E', u'A3P', u'A3E', u'A3I', u'DP5SH', u'DP6FH', u'WA2P', u'Q08', u'Q09', u'WA2I', u'Q02', u'DP1SH', u'Q01', u'Q06', u'Q07', u'Q04', u'DP4FH', u'DS1SH', u'DQD1', u'DQD3', u'DQD2', u'PF1', u'PF2', u'PSTN2', u'DBPM1', u'DBPM2', u'DBPM3', u'DAM', u'PSTN1', u'A1P', u'A1E', u'WA1P', u'A1I', u'WA4I', u'WA4E', u'D2', u'DICT', u'WA4P', u'D3', u'D1'])
        self.assertEqual(kws_bl,  [u'BL', u'CHI', u'TRIP3', u'BI2S', u'BI2B', u'A1', u'A3', u'A2', u'A4', u'DOUB2', u'DOUB1'])

class GetBeamlineTest(BeamlineLatticeTest):
    # get beamline
    def runTest(self):
        self.assertEqual(self.lins.getBeamline('bl'), [u'q', u'w00', u'a1', u'bi2s', u'a2', u'w01', u'chi', u'w02', u'a3', u'dbll1', u'a4', u'w03', u'dbll2', u'trip3', u'dbpm3', u'bpm03', u'dict', u'dbll3', u'dvalv', u'd1', u'dam', u'prl7', u'pstn2', u'w04'])

class GetFullBeamlineTest(BeamlineLatticeTest):
    # get expanded beamline
    def runTest(self):
        self.assertEqual(self.lins.getFullBeamline('bl'), 
                [u'q', u'w00', u'a1i', u'18*a1p', u'a1e', u'dbll2', u'dqd1', u'q01', u'dqd2', u'q02', u'dbpm2', u'dbdm', u'dp2fh', u'dp2sh', u'dbll2', u'a2i', u'18*a2p', u'a2e', u'w01', u'dbll2', u'dqd3', u'q05', u'dqd2', u'q06', u'dqd3', u'dp4fh', u'dp4sh', u'dbll5', u'dbd', u'b11', u'db11', u'b12', u'db12', u'pf2', u'db13', u'b13', u'db14', u'b14', u'dbd', u'dbll5', u'dqd3', u'q07', u'dqd2', u'q08', u'dqd3', u'dp5fh', u'dp5sh', u'dbll2', u'pstn1', u'w02', u'a3i', u'18*a3p', u'a3e', u'dbll1', u'a4i', u'18*a4p', u'a4e', u'w03', u'dbll2', u'dqd1', u'q09', u'dqd2', u'q10', u'dqd2', u'q09', u'dqd1', u'dbpm3', u'bpm03', u'dict', u'dbll3', u'dvalv', u'd1', u'dam', u'prl7', u'pstn2', u'w04'])
        self.assertEqual(self.lins.getFullBeamline('bl', extend = True), 
                [u'q', u'w00', u'a1i', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1p', u'a1e', u'dbll2', u'dqd1', u'q01', u'dqd2', u'q02', u'dbpm2', u'dbdm', u'dp2fh', u'dp2sh', u'dbll2', u'a2i', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2p', u'a2e', u'w01', u'dbll2', u'dqd3', u'q05', u'dqd2', u'q06', u'dqd3', u'dp4fh', u'dp4sh', u'dbll5', u'dbd', u'b11', u'db11', u'b12', u'db12', u'pf2', u'db13', u'b13', u'db14', u'b14', u'dbd', u'dbll5', u'dqd3', u'q07', u'dqd2', u'q08', u'dqd3', u'dp5fh', u'dp5sh', u'dbll2', u'pstn1', u'w02', u'a3i', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3p', u'a3e', u'dbll1', u'a4i', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4p', u'a4e', u'w03', u'dbll2', u'dqd1', u'q09', u'dqd2', u'q10', u'dqd2', u'q09', u'dqd1', u'dbpm3', u'bpm03', u'dict', u'dbll3', u'dvalv', u'd1', u'dam', u'prl7', u'pstn2', u'w04'])

class GetElementTypeTest(BeamlineLatticeTest):
    # get element type by keyword name
    def runTest(self):
        self.assertEqual(self.lins.getElementType('b11'), 'CSRCSBEN')

class GetElementConfTest(BeamlineLatticeTest):
    # get element configuration by keyword name
    def runTest(self):
        self.assertEqual(self.lins.getElementConf('b11'), {u'hgap': 0.015, u'integration_order': 4.0, u'nonlinear': 1.0, u'angle': 0.17872171540423112, u'n_kicks': 100.0, u'l': 0.20106869612225164, u'edge1_effects': 1.0, u'edge2_effects': 1.0, u'block_csr': 0.0, u'sg_halfwidth': 1.0, u'e2': 0.17872171540423112, u'e1': 0.0, u'bins': 512.0, u'csr': u'csr_on_off'})

class IsBeamlineTest(BeamlineLatticeTest):
    # test if keyword is beamline
    def runTest(self):
        self.assertTrue(self.lins.isBeamline('bl'))
        self.assertFalse(self.lins.isBeamline('bl01'))
        self.assertFalse(self.lins.isBeamline('q02'))

class ShowBeamlinesTest(BeamlineLatticeTest):
    # show all beamlines
    def runTest(self):
        self.assertEqual(self.lins.showBeamlines(), 
                "11 beamlines: BL;CHI;TRIP3;BI2S;BI2B;A1;A3;A2;A4;DOUB2;DOUB1")

class GenerateLatticeFileTest(BeamlineLatticeTest):
    # generateLatticeFile by beamline keyword
    def runTest(self):
        latticefile = os.path.join(os.getcwd(), 'tracking/newlat.lte')
        self.assertTrue(self.lins.generateLatticeFile('bl', latticefile, format = 'elegant'))

class RinseElementTest(BeamlineLatticeTest):
    # rinse element test
    def runTest(self):
        self.assertEqual(self.lins.rinseElement('18*aip'), {'name':'aip', 'num':18})
        self.assertEqual(self.lins.rinseElement('q01'),    {'num':1, 'name':'q01'})

class OrderLatticeTest(BeamlineLatticeTest):
    def runTest(self):
        chi_ordered = [(u'dbll2', u'LSCDRIF', 1), (u'dqd3', u'LSCDRIF', 2), (u'q05', u'QUAD', 1), (u'dqd2', u'LSCDRIF', 3), (u'q06', u'QUAD', 2), (u'dqd3', u'LSCDRIF', 4), (u'dp4fh', u'LSCDRIF', 5), (u'dp4sh', u'LSCDRIF', 6), (u'dbll5', u'LSCDRIF', 7), (u'dbd', u'LSCDRIF', 8), (u'b11', u'CSRCSBEN', 1), (u'db11', u'CSRDRIF', 1), (u'b12', u'CSRCSBEN', 2), (u'db12', u'CSRDRIF', 2), (u'pf2', u'PFILTER', 1), (u'db13', u'CSRDRIF', 3), (u'b13', u'CSRCSBEN', 3), (u'db14', u'CSRDRIF', 4), (u'b14', u'CSRCSBEN', 4), (u'dbd', u'LSCDRIF', 9), (u'dbll5', u'LSCDRIF', 10), (u'dqd3', u'LSCDRIF', 11), (u'q07', u'QUAD', 3), (u'dqd2', u'LSCDRIF', 12), (u'q08', u'QUAD', 4), (u'dqd3', u'LSCDRIF', 13), (u'dp5fh', u'LSCDRIF', 14), (u'dp5sh', u'LSCDRIF', 15), (u'dbll2', u'LSCDRIF', 16), (u'pstn1', u'MARK', 1)]
        self.assertEqual(self.lins.orderLattice('chi'), chi_ordered)

class GetElementByNameTest(BeamlineLatticeTest):
    def runTest(self):
        self.assertEqual(self.lins.getElementByName('chi','dbll2'), 
                [(u'dbll2', u'LSCDRIF', 1), (u'dbll2', u'LSCDRIF', 16)])

class GetElementByOrderTest(BeamlineLatticeTest):
    def runTest(self):
        bl   = 'chi'
        type = 'lscdrif'
        # single index
        self.assertEqual(self.lins.getElementByOrder(bl, type, -1), [(u'dbll2', u'LSCDRIF', 16)])
        # multi index
        self.assertEqual(self.lins.getElementByOrder(bl, type, '0,1,2'), [(u'dbll2', u'LSCDRIF', 1), (u'dqd3', u'LSCDRIF', 2), (u'dqd2', u'LSCDRIF', 3)])
        # index range
        self.assertEqual(self.lins.getElementByOrder(bl, type, '1:5:2'), [(u'dqd3', u'LSCDRIF', 2), (u'dqd3', u'LSCDRIF', 4)])
        self.assertEqual(self.lins.getElementByOrder(bl, type, 'all'),[(u'dbll2', u'LSCDRIF', 1), (u'dqd3', u'LSCDRIF', 2), (u'dqd2', u'LSCDRIF', 3), (u'dqd3', u'LSCDRIF', 4), (u'dp4fh', u'LSCDRIF', 5), (u'dp4sh', u'LSCDRIF', 6), (u'dbll5', u'LSCDRIF', 7), (u'dbd', u'LSCDRIF', 8), (u'dbd', u'LSCDRIF', 9), (u'dbll5', u'LSCDRIF', 10), (u'dqd3', u'LSCDRIF', 11), (u'dqd2', u'LSCDRIF', 12), (u'dqd3', u'LSCDRIF', 13), (u'dp5fh', u'LSCDRIF', 14), (u'dp5sh', u'LSCDRIF', 15), (u'dbll2', u'LSCDRIF', 16)])

class GetElementPropertiesTest(BeamlineLatticeTest):
    def runTest(self):
        kw = 'bpm02'
        self.assertEqual(self.lins.getElementProperties(kw), 
                         {'type':'moni', 'properties':None})

        kw = 'q01'
        self.assertEqual(self.lins.getElementProperties(kw)['properties'],
                         {u'k1': 0.0, u'l': 0.05})

class ManipulateLatticeTest(BeamlineLatticeTest):
    def runTest(self):
        ele = self.lins.getElementByOrder('chi', type = 'quad', irange = 0)[0][0]
        k1_old = self.lins.getElementProperties(ele)['properties']['k1']
        self.lins.manipulateLattice('chi', type = 'quad', irange = 0, 
                                     property = 'k1', opstr = '+100%')
        k1_new = self.lins.getElementProperties(ele)['properties']['k1']
        self.assertEqual(k1_new, 2.0*k1_old)
        
    def genltefileTest(self):
        latticefile1 = os.path.join(os.getcwd(), 'tracking/newlat1.lte')
        latticefile2 = os.path.join(os.getcwd(), 'tracking/newlat2.lte')
        self.lins.generateLatticeFile('bl', latticefile1, format = 'elegant')
        self.lins.manipulateLattice('chi', type = 'quad', property = 'k1', irange = 'all', opstr = '+100%')
        self.lins.generateLatticeFile('bl', latticefile2, format = 'elegant')
"""

def testfun():
    latticePath = os.path.join(os.getcwd(), '../lattice')
    infilename  = os.path.join(latticePath, 'linac.lte')
    pins = beamline.LteParser(infilename)
    lins = beamline.Lattice(pins.file2json())
    
    #latticefile = os.path.join(os.getcwd(), 'tracking/newlat.lte')
    #lins.generateLatticeFile('bl', latticefile, format = 'elegant')

#    tl = lins.manipulateLattice('bl')
#    print tl

#    print lins.orderLattice('chi')

#    for (ename,etype,eid) in lins.orderLattice('chi'):
#        print('{x:10s}:{y:10s}:{z:3d}'.format(x=ename,y=etype,z=eid))
#    print lins.getFullBeamline('bl')
#    print lins.getFullBeamline('a1', extend = True)
#    print lins.getFullBeamline('l1')
#    print lins.getFullBeamline('2l1', extend = True)
#    print lins.getFullBeamline('bltest')
#    print lins.getFullBeamline('bltest', extend = True)
    
#    print lins.getFullBeamline('chi', extend = True)
#    print lins.getElementByName('chi','dbll2')
#    # single index
#    print lins.getElementByOrder('chi','lscdrif', -1)
#    # multi index
#    print lins.getElementByOrder('chi','lscdrif', '0,1,2')
#    # index range
#    print lins.getElementByOrder('chi','lscdrif', '1:5:2')
#    print lins.getElementByOrder('chi','lscdrif', 'all')

#    lins.manipulateLattice('chi', type = 'quad', irange = 0, opstr = '+100%')
#    for ename, etype, eid in lins.getElementByOrder('chi', type = 'quad', irange = 0):
#        print lins.getElementProperties(ename)['properties']

#    print lins.getElementProperties('q01')['properties']

    # double quad k1 in chi
    latticefile1 = os.path.join(os.getcwd(), 'tracking/newlat1.lte')
    latticefile2 = os.path.join(os.getcwd(), 'tracking/newlat2.lte')
    lins.generateLatticeFile('bl', latticefile1, format = 'elegant')
    lins.manipulateLattice('chi', type = 'quad', property = 'k1', irange = 'all', opstr = '+100%')
    lins.generateLatticeFile('bl', latticefile2, format = 'elegant')

    # use datautils and simulation modules
    simpath = os.path.join(os.getcwd(), 'tracking')
    ltefile = latticefile1
    elefile = os.path.join(simpath, 'test.ele')
    A = beamline.Simulator()
    A.setMode('elegant')
    A.setScript('runElegant.sh')
    A.setExec('elegant')
    A.setPath(simpath)
    A.setInputfiles(ltefile = ltefile, elefile = elefile)
    A.doSimulation()
    data = A.getOutput(file = 'test.out', data = ('t','p'), dump = 'test.h5')

def test1():
    latticePath = "/home/tong/Programming/projects/vFEL/simulation/SXFEL" 
    infilename  = os.path.join(latticePath, 'sxfel_v14b.lte')
    pins = beamline.LteParser(infilename)
    lins = beamline.Lattice(pins.file2json())

    print lins.dumpAllElements()
    #print lins.getChargeElement()
    #print lins.getElementByOrder('bl','charge',0)
    #newline = lins.generateLatticeLine('l0','l0')
    #print lins.getBeamline('bl')
    #print lins.getElementType('c')
    #print lins.getAllBl()
    #print lins.getFullBeamline('testline', extend = True)

if __name__ == '__main__':
    #testfun()
    #test1()
    unittest.main()
