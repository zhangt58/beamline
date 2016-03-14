import beamline
import unittest
import os

class DataUtilsTest(unittest.TestCase):
    def setUp(self):
        datafields = ['s','Sx','Sy','enx','eny']
        sddsfile   = 'test.sig'
        hdf5file   = 'test.h5'
        datascript   = '~/Programming/projects/beamline/scripts/sddsprintdata.sh'
        datapath     = '~/Programming/projects/beamline/tests/tracking'
        self.hdf5fullpath = os.path.join(os.path.expanduser(datapath), hdf5file)
        sddsfullpath = os.path.join(os.path.expanduser(datapath), sddsfile) 
        
        self.A = beamline.DataExtracter(sddsfullpath, *datafields)
        self.A.setDataScript(datascript)
        self.A.setDataPath  (datapath)
        self.A.setH5file    (self.hdf5fullpath)

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


