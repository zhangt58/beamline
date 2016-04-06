#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module designed for online modeling:
*elegant tracking with lte/ele files*:
    1: lte file should be generated from lattice.Lattice.generateLatticeFile() method;
    2: take ele file as initialization parameter, but could be changed;
    3: output tracking results as hdf5 file (hard drive) and numpy array (memory);
    

Author      : Tong Zhang
Created     : 2016-03-08
Last updated: 2016-03-08
"""

import os
import subprocess

from . import datautils


class Simulator(object):
    def __init__(self, infile=''):
        self.mode = 'mad'           # call setMode(mode = 'elegant') to change mode, or 'mad' by default
        self.lattice_file = infile  # .lte file for elegant mode, or .mad[x] file for mad mode
        self.elegant_file = ''
        self.set_file = {
                        'elegant': self._setElegant,
                        'mad': self._setMad
                        }

        self.sim_case = {
                        'elegant': self._doElegant,
                        'mad': self._doMad
                        }

        self.get_output = {
                          'elegant': self._getOutputElegant,
                          'mad': self._getOutputMad
                          }
        self.sim_exec = 'mad'
        self.sim_path = os.path.expanduser('~')

    def setMode(self, mode='elegant'):
        """ set simulation mode, define mode parameter of 'elegant' or 'mad'
        :param mode: simulation mode
        """
        self.mode = mode.lower()

    def setScript(self, fullname):
        """ set bash shell script full path name for simulation
        :param fullname: set 'runElegant.sh', which should be available after installed beamline package
        """
        self.sim_script = fullname

    def setExec(self, execpath):
        """ set executable for simulation
        :param execpath: elegant or madx full path
        """
        self.sim_exec = execpath

    def setPath(self, simpath):
        """ set simulation path where data should be put into
        :param simpath: where simulations take place, all data files should be found there
        """
        self.sim_path = simpath

    def _setElegant(self, **infiles):
        """ set input parameters for elegant tracking, available keys: 'ltefile', 'elefile'
        """
        ltefile, elefile = infiles['ltefile'], infiles['elefile']
        self.lattice_file = ltefile
        self.elegant_file = elefile

    def _setMad(self, **infiles):
        """ set input parameters for mad calculation, available keys: 'madfile'
        """
        self.lattice_file = infiles['madfile']

    def _doElegant(self):
        """ perform elegant tracking
        """
        cmdlist = ['bash', self.sim_script, self.elegant_file, self.sim_path, self.sim_exec]
        subprocess.call(cmdlist)

    def _doMad(self):
        """ perform mad calculation
        """
        pass

    def _getOutputElegant(self, **kws):
        """ get results from elegant output according to the given keywords,
            input parameter format: key = sdds field name tuple, e.g.:
            available keywords are:
             - 'file': sdds fielname, file = test.sig
             - 'data': data array,    data = ('s','Sx')
             - 'dump': h5file name, if defined, dump data to hdf5 format
        """
        datascript = "sddsprintdata.sh"
        datapath = self.sim_path
        trajparam_list = kws['data']
        sddsfile = os.path.expanduser(os.path.join(self.sim_path, kws['file']))
        dh = datautils.DataExtracter(sddsfile, *trajparam_list)
        dh.setDataScript(datascript)
        dh.setDataPath(datapath)
        if 'dump' in kws:
            dh.setH5file(kws['dump'])
            dh.extractData().dump()
        data = dh.extractData().getH5Data()
        return data

    def _getOutputMad(self, **kws):
        pass

    def setInputfiles(self, **infiles):
        """ input parameters: 
        (elegant mode)
            1: lte file
            2: ele file
        (mad mode)
            1: mad file
        """
        self.set_file[self.mode](**infiles)
        
    def doSimulation(self):
        self.sim_case[self.mode]()

    def getOutput(self, **kws):
        return self.get_output[self.mode](**kws)

    def __str__(self):
        return ('mode = {mode:5s}\n' 
                'lat file = {lattice_file:5s}\n'
                'ele file = {elegant_file:5s}\n'
                'sim exec = {sscript_path:5s}\n').format(
                    mode=self.mode,
                    lattice_file=self.lattice_file,
                    elegant_file=self.elegant_file,
                    sscript_path=self.sim_script)

#----------------------------------------------------------------------------------------


def test():
    import os

    # elegant workflow
    simtestpath = os.path.join(os.getcwd(), '../tests/tracking/')
    ltefile = os.path.join(simtestpath, 'newlat.lte')
    elefile = os.path.join(simtestpath, 'test.ele')
    #print ltefile, elefile

    A = Simulator()
    A.setMode('elegant')
    A.setScript(os.path.join(os.getcwd(), '../scripts/runElegant.sh'))
    A.setExec('/home/tong/APS/epics/../oag/apps/bin/linux-x86_64/elegant')
    A.setPath(simtestpath)
    A.setInputfiles(ltefile=ltefile, elefile=elefile)
    A.doSimulation()
    data = A.getOutput(file='test.sig', data=('s', 'Sx'))
    data = A.getOutput(file='test.sig', data=('s', 'Sx'), dump='test.h5')

    """
    # mad workflow 1
    A = Simulator()
    A.setMode('mad')
    A.setScript('/home/tong/bin/madx64r')
    A.setInputfiles(madfile = 'test.mad')
    print A

    # mad workflow 2
    A = Simulator('test.mad')
    A.setScript('/home/tong/bin/madx64r')
    print A
    """

if __name__ == '__main__':
    test()
