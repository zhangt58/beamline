#!/usr/bin/env python
# -*- coding: utf-8 -*-

import h5py
import numpy as np
import subprocess
import os


class DataExtracter(object):
    """ extract required data from a sdds formated file, 
        to put into hdf5 formated file or just RAM

        Author: Tong Zhang
        Date  : 2016-03-10
    """
    def __init__(self, sddsfile, *kws):
        self.sddsfile = sddsfile
        self.kwslist = kws

        self.precision = '%.16e'
        self.dcmdline = 'sddsprintout {fn} -notitle -nolabel'.format(fn=self.sddsfile)

        self.h5data = ''

    def getAllCols(self, sddsfile=None):
        """ return all data collum names
        :param sddsfile: sdds file name
        """
        if sddsfile is None:
            sddsfile = self.sddsfile
        return subprocess.check_output(['sddsquery', '-col',  sddsfile]).split()

    def extractData(self):
        """ extract data as numpy array, with given required fields
        """
        for k in self.kwslist:
            self.dcmdline += ' -col={kw},format={p}'.format(kw=k, p=self.precision)
        cmdlist = ['bash', self.dscript, self.dpath, self.dcmdline]
        retlist = []
        proc = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
        for line in proc.stdout:
            retlist.append([float(i) for i in line.split()])
        self.h5data = np.array(retlist)
        return self

    def getH5Data(self):
        """ return extracted data as numpy array
        """
        return self.h5data

    def getKws(self):
        """ return data fields
        """
        return self.kwslist

    def setDataScript(self, fullscriptpath):
        self.dscript = os.path.expanduser(fullscriptpath)

    def setDataPath(self, path):
        """ set full dir path of data files
        :param path: data path
        """
        self.dpath = os.path.expanduser(path)

    def setH5file(self, h5filepath):
        """ set h5file full path name
        :param h5filepath: path for hdf5 file
        """
        self.h5file = os.path.expanduser(h5filepath)

    def setKws(self, *kws):
        """ set keyword list, i.e. sdds field names
        """
        self.kwslist = kws

    def dump(self):
        """ dump extracted data into a single hdf5file
        """
        f = h5py.File(self.h5file, 'w')
        for i, k in enumerate(self.kwslist):
            v = self.h5data[:, i]
            dset = f.create_dataset(k, shape=v.shape, dtype=v.dtype)
            dset[...] = v
        f.close()


class DataVisualizer(object):
    """ for data visualization purposes

        Author: Tong Zhang
        Date  : 2016-03-14
    """
    def __init__(self, data):
        self.data = data

    def inspectDataFile(self):
        """ inspect hdf5 data file
        """
        pass

    def illustrate(self, xlabel, ylabel):
        """ plot x, y w.r.t. xlabel and ylabel
        :param ylabel: xlabel
        :param xlabel: ylabel
        """
        pass

    def saveArtwork(self, name='image', fmt='jpg'):
        """ save figure by default name of image.jpg
        :param name: image name, 'image' by default
        :param fmt: image format, 'jpg' by default
        """
        pass


class DataStorage(object):
    """ for data storage management, 
        communicate with database like mongodb, mysql, sqlite, etc.

        Author: Tong Zhang
        Date  : 2016-03-14
    """
    def __init__(self, data):
        self.data = data

    def configDatabase(self):
        """ configure database
        """
        pass

    def putData(self):
        """ put data into database 
        """
        pass

    def getData(self):
        """ get data from database
        """
        pass

#--------------------------------------------------------------------------------------


def test():
    # workflow
    datafields = ['s', 'Sx', 'Sy', 'enx', 'eny']
    datascript = '~/Programming/projects/beamline/scripts/sddsprintdata.sh'
    datapath   = '~/Programming/projects/beamline/tests/tracking'
    hdf5file   = os.path.join(os.path.expanduser(datapath), 'test.h5')
    A = DataExtracter('test.sig', *datafields)
    A.setDataScript(datascript)
    A.setDataPath  (datapath)
    A.setH5file    (hdf5file)
    A.extractData().dump()

    fd = h5py.File(hdf5file, 'r')
    d_s  = fd['s'][:]
    d_sx = fd['Sx'][:]

    import matplotlib.pyplot as plt
    plt.figure(1)
    plt.plot(d_s, d_sx, 'r-')
    plt.show()

if __name__ == '__main__':
    test()


