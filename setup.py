from setuptools import setup, find_packages
import os

scriptnames = ['runElegant.sh', 
               'sddsprintdata.sh', 
               'renametolower.sh',
               'file2lower.sh']

setup(
        name     = "beamline",
        version  = "1.1.4",
        description = "beamline plot module",
        author   = "Tong Zhang",
        author_email = "warriorlance@gmail.com",
        platforms = ["Linux"],
        license  = "MIT",
        packages = find_packages(),
        url = "https://github.com/Archman/beamline",
        scripts  = [os.path.join('scripts',sn) for sn in scriptnames],
     )

