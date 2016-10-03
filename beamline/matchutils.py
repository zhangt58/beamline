#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
classes to do beam optics matching
Tong Zhang
Aug. 10, 2015
"""

import re
import numpy as np
from numpy import sqrt
from numpy.linalg import inv
import mathutils

import os

class ParseParams(object):
    def __init__(self, *infilename):
        self.infilename = infilename
        self.onParseFile()

    def onParseFile(self):
        self.aw0        = 0.0
        self.xlamds     = 0.0
        self.xlamd      = 0.0
        self.gamma      = 0.0
        self.emitx      = 0.0
        self.imagl      = 0.0
        self.idril      = 0.0
        self.ibfield    = 0.0
        self.unitlength = 0.0

        fids = (open(file) for file in self.infilename)
        for curfid in fids:
            for line in curfid:
                line = line.lower()
                # aw0
                if 'aw0' in line:
                    self.aw0 = float(line.strip().split('=')[-1])
                # xlamds
                if 'xlamds' in line:
                    self.xlamds = float(line.strip().split('=')[-1])
                # xlamd
                mxlamd = re.match(' *xlamd[^s].*', line)
                if mxlamd:
                    self.xlamd = float(mxlamd.group().split('=')[-1])
                # gamma
                if 'gamma0' in line:
                    self.gamma = float(line.strip().split('=')[-1])
                # emitx
                if 'emitx' in line:
                    self.emitx = float(line.strip().split('=')[-1])
                # imagl
                if 'imagl' in line:
                    self.imagl = float(line.strip().split('=')[-1])
                # idril
                if 'idril' in line:
                    self.idril = float(line.strip().split('=')[-1])
                # ibfield
                if 'ibfield' in line:
                    self.ibfield = float(line.strip().split('=')[-1])
                # unitlength, i.e. undulator period
                if 'unit' in line:
                    self.unitlength = float(line.strip().split('=')[-1])

    def getUndulatorParameter(self):
        return self.aw0

    def getUndulatorPeriod(self):
        return self.xlamd
    
    def getUndulatorUnitlength(self):
        return self.unitlength

    def getFELwavelength(self):
        return self.xlamds

    def getElectronGamma(self):
        return self.gamma

    def getElectronEmitx(self):
        return self.emitx
    
    def getChicaneMagnetLength(self):
        return self.imagl

    def getChicaneDriftLength(self):
        return self.idril
 
    def getChicaneMagnetField(self):
        return self.ibfield

def parseLattice(latlengthname = 'fullat.hghg'):
    for line in open(latlengthname):
        if line.startswith('!'):
            newlist = line.replace('!','').strip().split(' ')
            return [float(i) for i in newlist]

class BeamMatch(object):
    def __init__(self, infile_mod, infile_rad, 
                 latfile_mod, latfile_rad, 
                 infile_mod_new, infile_rad_new,
                 latfile_rad_new, qfval, qdval):

        self.infile_mod      = infile_mod
        self.infile_rad      = infile_rad
        self.latfile_mod     = latfile_mod
        self.latfile_rad     = latfile_rad

        self.infile_mod_new  = infile_mod_new
        self.infile_rad_new  = infile_rad_new

        self.latfile_rad_new = latfile_rad_new

        self.qfval = qfval
        self.qdval = qdval

        self.alphax_mod = 0.0
        self.alphay_mod = 0.0
        self.sigmax_mod = 0.0
        self.sigmay_mod = 0.0

        self.alphax_rad = 0.0
        self.alphay_rad = 0.0
        self.sigmax_rad = 0.0
        self.sigmay_rad = 0.0

        self.matchOK = True

    def matchPerform(self, qf_linenum = 11, qd_linenum = 13):
        fid_infile_mod_new = open(self.infile_mod_new, 'w')
        fid_infile_rad_new = open(self.infile_rad_new, 'w')
        
        fid_latfile_rad_new = open(self.latfile_rad_new, 'w')

        linenum = 0
        for line in open(self.latfile_rad):
            linenum += 1
            if not line.startswith('?!'):
                if linenum == qf_linenum:
                    tmpline = line.lower().split()
                    tmpline[1] = '%.2f' % self.qfval
                    line = ' '.join(tmpline) + '\n'
                elif linenum == qd_linenum:
                    tmpline = line.lower().split()
                    tmpline[1] = '%.2f' % self.qdval
                    line = ' '.join(tmpline) + '\n'
                else:
                    line = "%s%s" % (' '.join(line.lower().split()), '\n')
            fid_latfile_rad_new.write(line)

        for line in open(self.infile_mod):
            line = line.lower()
            if 'alphax' in line:
                line = ' alphax = %.3f\n' % self.alphax_mod
            if 'alphay' in line:
                line = ' alphay = %.3f\n' % self.alphay_mod
            if 'rxbeam' in line:
                line = ' rxbeam = %.4e\n' % self.sigmax_mod
            if 'rybeam' in line:
                line = ' rybeam = %.4e\n' % self.sigmay_mod
            fid_infile_mod_new.write(line)

        for line in open(self.infile_rad):
            line = line.lower()
            if 'alphax' in line:
                line = ' alphax = %.3f\n' % self.alphax_rad
            if 'alphay' in line:
                line = ' alphay = %.3f\n' % self.alphay_rad
            if 'rxbeam' in line:
                line = ' rxbeam = %.4e\n' % self.sigmax_rad
            if 'rybeam' in line:
                line = ' rybeam = %.4e\n' % self.sigmay_rad
            if 'maginfile' in line:
                line = " maginfile = '%s'\n" % self.latfile_rad_new
            fid_infile_rad_new.write(line)

        fid_infile_mod_new.close()
        fid_infile_rad_new.close()
        fid_latfile_rad_new.close()

    def matchCalculate(self, latlengthname = 'fullat.hghg'):
        m0 = 9.10938215e-31
        e0 = 1.602176487e-19
        c0 = 299792458

        modparams = ParseParams(self.infile_mod, self.latfile_mod)
        gamma0  = modparams.getElectronGamma     ()
        emitn   = modparams.getElectronEmitx     ()
        am      = modparams.getUndulatorParameter()
        lambdam = modparams.getUndulatorPeriod   ()

        radparams = ParseParams(self.infile_rad, self.latfile_rad)
        au      = radparams.getUndulatorParameter ()
        lambdau = radparams.getUndulatorPeriod    ()
        imagl   = radparams.getChicaneMagnetLength()
        idril   = radparams.getChicaneDriftLength ()
        ibfield = radparams.getChicaneMagnetField ()

        lo1, lum, lo2, lo3, lf, lo4, lur, lo5, ld = parseLattice(latlengthname)

        kp, kn = self.qfval, self.qdval
        Kp = e0*kp/m0/c0/sqrt(gamma0**2-1)
        Kn = e0*kn/m0/c0/sqrt(gamma0**2-1)

        lambdas = lambdau/2.0/gamma0**2*(1+au**2)*1.0e9

        ku      = 2.0*np.pi/lambdau
        Ku      = sqrt(2.0)*au
        Kbetau  = 0.5*(Ku*ku/gamma0)**2

        Km      = sqrt(2.0)*am
        km      = 2.0*np.pi/lambdam
        Kbetam  = 0.5*(Km*km/gamma0)**2

        #print Kp,Kn,lambdas,ku,Ku,Kbetau,Km,km,Kbetam,lambdau,lambdam

        N = np.array([lo3, lf*0.5, lo4, lur, lo5, ld, lo4, lur, lo5, 0.5*lf])
        # one FODO period: N[1:], N[0]: drift length before QF

        mx = mathutils.funTransQuadF(Kp, N[1]*lambdau)*mathutils.funTransDrift(N[2]*lambdau)*mathutils.funTransUnduH(N[3]*lambdau)*mathutils.funTransDrift(N[4]*lambdau)*mathutils.funTransQuadF(Kn, N[5]*lambdau)*mathutils.funTransDrift(N[6]*lambdau)*mathutils.funTransUnduH(N[7]*lambdau)*mathutils.funTransDrift(N[8]*lambdau)*mathutils.funTransQuadF(Kp, N[9]*lambdau)
        if (mx[0,0] + mx[1,1])**2 > 4 or mx[0,1] <= 0:
            self.matchOK = False
            return self.matchOK
            
        my = mathutils.funTransQuadF(-Kp, N[1]*lambdau)*mathutils.funTransDrift(N[2]*lambdau)*mathutils.funTransUnduV(Kbetau, N[3]*lambdau)*mathutils.funTransDrift(N[4]*lambdau)*mathutils.funTransQuadF(-Kn, N[5]*lambdau)*mathutils.funTransDrift(N[6]*lambdau)*mathutils.funTransUnduV(Kbetau, N[7]*lambdau)            *mathutils.funTransDrift(N[8]*lambdau)*mathutils.funTransQuadF(-Kp, N[9]*lambdau)
        if (my[0,0] + my[1,1])**2 > 4 or my[0,1] <= 0:
            self.matchOK = False
            return self.matchOK
        
        #print mx
        #print my

        ## twiss parameters of FODO
        # mx
        alphax_FODO = (mx[0,0]-mx[1,1])/sqrt(4.0-(mx[0,0]+mx[1,1])**2)
        betax_FODO  = 2.0*mx[0,1]/sqrt(4.0-(mx[0,0]+mx[1,1])**2)
        gammax_FODO = (1.0+alphax_FODO**2)/betax_FODO
        # my
        alphay_FODO = (my[0,0]-my[1,1])/sqrt(4.0-(my[0,0]+my[1,1])**2)
        betay_FODO  = 2.0*my[0,1]/sqrt(4.0-(my[0,0]+my[1,1])**2)
        gammay_FODO = (1.0+alphay_FODO**2)/betay_FODO

        ## match to the entrance of radiator
        # forward match to 'O + QF/2'
        AX = mathutils.funTransQuadF( Kp, N[1]*lambdau)*mathutils.funTransDrift(N[0]*lambdau)
        AY = mathutils.funTransQuadF(-Kp, N[1]*lambdau)*mathutils.funTransDrift(N[0]*lambdau)
        AX = inv(AX)
        AY = inv(AY)
        Nx = np.matrix([[ AX[0,0]**2,     -2*AX[0,0]*AX[0,1],     AX[0,1]**2     ],
                        [-AX[0,0]*AX[1,0], 1+2*AX[0,1]*AX[1,0],  -AX[0,1]*AX[1,1]],
                        [ AX[1,0]**2,     -2*AX[1,0]*AX[1,1],     AX[1,1]**2     ]])
        Ny = np.matrix([[ AY[0,0]**2,     -2*AY[0,0]*AY[0,1],     AY[0,1]**2     ],
                        [-AY[0,0]*AY[1,0], 1+2*AY[0,1]*AY[1,0],  -AY[0,1]*AY[1,1]],
                        [ AY[1,0]**2,     -2*AY[1,0]*AY[1,1],     AY[1,1]**2     ]])

        Bx = Nx*np.matrix([[betax_FODO],[alphax_FODO],[gammax_FODO]])
        By = Ny*np.matrix([[betay_FODO],[alphay_FODO],[gammay_FODO]])

        betax_rad  = Bx[0,0]
        betay_rad  = By[0,0]
        alphax_rad = Bx[1,0]
        alphay_rad = By[1,0]
        gammax_rad = Bx[2,0]
        gammay_rad = By[2,0]
        sigmax_rad = sqrt(betax_rad*emitn/gamma0)
        sigmay_rad = sqrt(betay_rad*emitn/gamma0)

        # matched beam for radiator input 
        self.alphax_rad = alphax_rad
        self.alphay_rad = alphay_rad
        self.sigmax_rad = sigmax_rad
        self.sigmay_rad = sigmay_rad

        ## forward match to mod + chicane, find configurations for mod input
        AX = mathutils.funTransChica(imagl, idril, ibfield, gamma0, 'x')*mathutils.funTransDrift(lo2*lambdam)*mathutils.funTransUnduH(lum*lambdam)*mathutils.funTransDrift(lo1*lambdam)
        AY = mathutils.funTransChica(imagl, idril, ibfield, gamma0, 'y')*mathutils.funTransDrift(lo2*lambdam)*mathutils.funTransUnduV(Kbetam, lum*lambdam)*mathutils.funTransDrift(lo1*lambdam)
        AX = inv(AX)
        AY = inv(AY)
        Nx = np.matrix([[ AX[0,0]**2,     -2*AX[0,0]*AX[0,1],     AX[0,1]**2     ],
                        [-AX[0,0]*AX[1,0], 1+2*AX[0,1]*AX[1,0],  -AX[0,1]*AX[1,1]],
                        [ AX[1,0]**2,     -2*AX[1,0]*AX[1,1],     AX[1,1]**2     ]])
        Ny = np.matrix([[ AY[0,0]**2,     -2*AY[0,0]*AY[0,1],     AY[0,1]**2     ],
                        [-AY[0,0]*AY[1,0], 1+2*AY[0,1]*AY[1,0],  -AY[0,1]*AY[1,1]],
                        [ AY[1,0]**2,     -2*AY[1,0]*AY[1,1],     AY[1,1]**2     ]])
        Bx = Nx*np.matrix([[betax_rad],[alphax_rad],[gammax_rad]])
        By = Ny*np.matrix([[betay_rad],[alphay_rad],[gammay_rad]])

        betax_mod  = Bx[0,0]
        betay_mod  = By[0,0]
        alphax_mod = Bx[1,0]
        alphay_mod = By[1,0]
        gammax_mod = Bx[2,0]
        gammay_mod = By[2,0]
        sigmax_mod = sqrt(betax_mod*emitn/gamma0)
        sigmay_mod = sqrt(betay_mod*emitn/gamma0)

        # matched beam for modulator input 
        self.alphax_mod = alphax_mod
        self.alphay_mod = alphay_mod
        self.sigmax_mod = sigmax_mod
        self.sigmay_mod = sigmay_mod

        """
        print("gamma0 : %.4e" % gamma0 )
        print("emitn  : %.4e" % emitn  )
        print("aw0m   : %.4f" % am     )
        print("xlamdm : %.4f" % lambdam)
        print("aw0r   : %.4f" % au     )
        print("xlamdr : %.4f" % lambdau)
        print("imagl  : %.4f" % imagl  )
        print("idril  : %.4f" % idril  )
        print("ibfield: %.4f" % ibfield)
        """

        return self.matchOK

    def matchPrintout(self):
        print("\nModulator:")
        print("---------------------------")
        print("alphax = %.3f" % self.alphax_mod)
        print("alphay = %.3f" % self.alphay_mod)
        print("rxbeam = %.4e" % self.sigmax_mod)
        print("rybeam = %.4e" % self.sigmay_mod)

        print("\nRadiator:")
        print("---------------------------")
        print("alphax = %.3f" % self.alphax_rad)
        print("alphay = %.3f" % self.alphay_rad)
        print("rxbeam = %.4e" % self.sigmax_rad)
        print("rybeam = %.4e" % self.sigmay_rad)

class FELSimulator(object):
    def __init__(self, mode = 'HGHG', 
                    modinfile = 'mod.in', 
                    radinfile = 'rad.in',
                    modlatfile = 'mod.lat', 
                    radlatfile = 'rad.lat'):
        self.mode       = mode
        self.modinfile  = modinfile
        self.modlatfile = modlatfile
        self.radinfile  = radinfile
        self.radlatfile = radlatfile

        self.data = np.zeros([1, 1])

    def run(self):
        cmd1 = 'echo' + ' ' + self.modinfile + ' | ' + 'genesis > /dev/null'
        cmd2 = 'echo' + ' ' + self.radinfile + ' | ' + 'genesis > /dev/null'
        os.system(cmd1)
        os.system(cmd2)

    def postProcess(self, outfile = 'rad.out'):
        #datfile = 'tmp.dat'
        fout = open(outfile, 'r')
        #fdat = open(datfile, 'w')

        entries = self.grepParam(param='entries')

        line = ' '.join(fout.readline().lower().strip().split())
        while not line.startswith('z[m]'):
            line = ' '.join(fout.readline().lower().strip().split())
        
        data0 = np.zeros([entries, 3])
        for i in xrange(entries):
            elements = fout.readline().lower().strip().split()
            line = ' '.join(elements)
            #fdat.write("%s\n" % line)
            data0[i, 0:3] = [float(strnum) for strnum in elements]

        line = ' '.join(fout.readline().lower().strip().split())
        while not line.startswith('power'):
            line = ' '.join(fout.readline().lower().strip().split())
        
        elements = fout.readline().lower().strip().split()
        fieldnum = elements.__len__()
        data1 = np.zeros([entries, fieldnum])
        data1[0, 0:fieldnum] = [float(strnum) for strnum in elements]
        for i in xrange(1, entries):
            elements = fout.readline().lower().strip().split()
            line = ' '.join(elements)
            #fdat.write("%s\n" % line)
            data1[i, 0:fieldnum] = [float(strnum) for strnum in elements]

        fout.close()
        #fdat.close()

        self.data = np.concatenate((data0, data1), axis = 1)
        
    def getMaxPower(self):
        return self.data[:,3].max()

    def grepParam(self, param = 'entries', outfile = 'rad.out'):
        for line in open(outfile):
            if param in line:
                return int(line.strip().split()[0])

    def plotPower(self):
        import matplotlib.pyplot as plt
        plt.plot(self.data[:,0], self.data[:,3], 'r-')
        plt.show()

def test():
    testParse = ParseParams('rad.in', 'rad.lat')
    aw0        = testParse.getUndulatorParameter ()
    xlamd      = testParse.getUndulatorPeriod    ()
    unitlength = testParse.getUndulatorUnitlength()
    xlamds     = testParse.getFELwavelength      ()
    gamma0     = testParse.getElectronGamma      ()
    emitx      = testParse.getElectronEmitx      ()
    imagl      = testParse.getChicaneMagnetLength()
    idril      = testParse.getChicaneDriftLength ()
    ibfield    = testParse.getChicaneMagnetField ()
    """
    print("aw0    = %.3f" % aw0   )
    print("xlamd  = %.3f" % xlamd )
    print("xlamds = %.3e" % xlamds)
    print("gamma0 = %.3f" % gamma0)
    print("emitx  = %.3e" % emitx )
    print("imagl  = %.3f" % imagl )
    print("idril  = %.3f" % idril )
    print("ibfield= %.3f" % ibfield)
    print("unit   = %.3f" % unitlength)

    print parseLattice('fullat.hghg')
    """
    
    qf, qd = -1, 2

    testMatch = BeamMatch('mod.in', 'rad.in', 
                          'mod.lat', 'rad.lat',
                          'newmod.in', 'newrad.in',
                          'newrad.lat', qf, qd)
    if testMatch.matchCalculate():
        testMatch.matchPerform()
        #testMatch.matchPrintout()
        fel = FELSimulator()
        fel.run()
        fel.postProcess()
        print fel.getMaxPower()

if __name__ == '__main__':
    test()
    
