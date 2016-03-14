from setuptools import setup, find_packages
import os

setup(
        name     = "beamline",
        version  = "1.1.3",
        description = "beamline plot module",
        author   = "Tong Zhang",
        author_email = "warriorlance@gmail.com",
        platforms = ["Linux"],
        license  = "MIT",
        packages = find_packages(),
        scripts  = [os.path.join('scripts',sn) for sn in ['runElegant.sh', 'sddsprintdata.sh']],
     )

