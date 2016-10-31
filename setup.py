from setuptools import setup, find_packages
import os

scriptnames = ['runElegant.sh',
               'sddsprintdata.sh',
               'renametolower.sh',
               'file2lower.sh',
               'lte2json',
               'json2lte',
               'latticeviewer',
               'lv']

def readme():
    with open('README.rst') as f:
        return f.read()

requiredpackages = ['pyrpn', 'h5py', 'numpy', 'matplotlib', 'pyepics']

setup(
        name     = "beamline",
        version  = "1.3.6",
        description = "online model package for electron accelerator",
        long_description = readme() + '\n\n',
        author   = "Tong Zhang",
        author_email = "warriorlance@gmail.com",
        platforms = ["Linux"],
        license  = "MIT",
        packages = find_packages(),
        url = "http://archman.github.io/beamline/",
        scripts  = [os.path.join('scripts',sn) for sn in scriptnames],
        requires = requiredpackages,
        extras_require = {'sdds': ['sddswhl']},
)
