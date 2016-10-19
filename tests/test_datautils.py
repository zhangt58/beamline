import beamline
import numpy as np
import unittest
import os


class DataUtilsTest(unittest.TestCase):
    def setUp(self):
        datafields = ['s','Sx','Sy','enx', 'eny']
        sddsfile   = 'test.sig'
        hdf5file   = 'test.h5'
        package_path = os.path.join(*os.path.split(beamline.__path__[0])[:-1])
        datascript   = os.path.join(package_path, 'scripts/sddsprintdata.sh')
        datapath     = os.path.join(package_path, 'tests/tracking')
        self.hdf5fullpath = os.path.join(os.path.expanduser(datapath), hdf5file)
        self.sddsfullpath = os.path.join(os.path.expanduser(datapath), sddsfile)

        self.A = beamline.DataExtracter(self.sddsfullpath, *datafields)
        self.A.setDataScript(datascript)
        self.A.setDataPath  (datapath)
        self.A.setH5file    (self.hdf5fullpath)

        self.s = np.array([[0.], [0.], [1.], [1.5], [2.5], [3.], [4.], [4.5],
                           [5.5], [6.5], [7.], [8.], [8.5], [9.5], [10.], [11.]])
        self.sNamelist = [['0.0', 'MARK'], ['0.0', 'CHARGE'], ['1.0', 'DRIF'], ['1.5', 'QUAD'],
                          ['2.5', 'DRIF'], ['3.0', 'CSRCSBEND'], ['4.0', 'DRIF'], ['4.5', 'CSRCSBEND'],
                          ['5.5', 'DRIF'], ['6.5', 'DRIF'], ['7.0', 'CSRCSBEND'], ['8.0', 'DRIF'],
                          ['8.5', 'CSRCSBEND'], ['9.5', 'DRIF'], ['10.0', 'QUAD'], ['11.0', 'DRIF']]

        self.colnames = ['s', 'ElementName', 'ElementOccurence', 'ElementType',
                         's1', 's12', 's13', 's14', 's15', 's16', 's17',
                         's2', 's23', 's24', 's25', 's26', 's27',
                         's3', 's34', 's35', 's36', 's37',
                         's4', 's45', 's46', 's47',
                         's5', 's56', 's57',
                         's6', 's67',
                         's7',
                         'ma1', 'ma2', 'ma3', 'ma4', 'ma5', 'ma6', 'ma7',
                         'minimum1', 'minimum2', 'minimum3', 'minimum4', 'minimum5', 'minimum6', 'minimum7',
                         'maximum1', 'maximum2', 'maximum3', 'maximum4', 'maximum5', 'maximum6', 'maximum7',
                         'Sx', 'Sxp', 'Sy', 'Syp', 'Ss', 'Sdelta', 'St',
                         'ex', 'enx', 'ecx', 'ecnx', 'ey', 'eny', 'ecy', 'ecny',
                         'betaxBeam', 'alphaxBeam', 'betayBeam', 'alphayBeam']

    def test_extractData(self):
        self.A.kwslist = ['s']
        ret1 = self.A.extractData()

        self.assertIsInstance(ret1, beamline.datautils.DataExtracter)
        self.assertIsInstance(ret1.h5data, np.ndarray)
        self.assertListEqual(list(ret1.h5data), list(self.s))

        self.A.kwslist = ['s', 'ElementType']
        ret2 = self.A.extractData()

        self.assertListEqual(ret2.h5data.tolist(), self.sNamelist)

        ret3 = beamline.datautils.DataExtracter(self.sddsfullpath, *('s'))
        self.assertIsInstance(ret3, beamline.datautils.DataExtracter)
        ret3.extractData()
        self.assertListEqual(list(ret3.h5data), list(self.s))

    def test_getAllPars(self):
        ret = self.A.getAllPars()
        self.assertListEqual(ret, ['Step'])

    def test_getAllCols(self):
        ret = self.A.getAllCols()
        self.assertListEqual(ret, self.colnames)

class GetAllColsTest(DataUtilsTest):
    def runTest(self):
        self.assertEqual(self.A.getAllCols(), ['s', 'ElementName', 'ElementOccurence', 'ElementType', 's1', 's12', 's13', 's14', 's15', 's16', 's17', 's2', 's23', 's24', 's25', 's26', 's27', 's3', 's34', 's35', 's36', 's37', 's4', 's45', 's46', 's47', 's5', 's56', 's57', 's6', 's67', 's7', 'ma1', 'ma2', 'ma3', 'ma4', 'ma5', 'ma6', 'ma7', 'minimum1', 'minimum2', 'minimum3', 'minimum4', 'minimum5', 'minimum6', 'minimum7', 'maximum1', 'maximum2', 'maximum3', 'maximum4', 'maximum5', 'maximum6', 'maximum7', 'Sx', 'Sxp', 'Sy', 'Syp', 'Ss', 'Sdelta', 'St', 'ex', 'enx', 'ecx', 'ecnx', 'ey', 'eny', 'ecy', 'ecny', 'betaxBeam', 'alphaxBeam', 'betayBeam', 'alphayBeam'])

class WorkflowTest(DataUtilsTest):
    def runTest(self):
        self.A.extractData().dump()

        import h5py
        fd = h5py.File(self.hdf5fullpath, 'r')
        d_s  = fd['s'][:]
        d_sx = fd['Sx'][:]

        import matplotlib.pyplot as plt
        plt.figure(1)
        plt.plot(d_s, d_sx, 'r-')
        plt.show()

if __name__ == '__main__':
    unittest.main()
