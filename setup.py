from setuptools import setup, find_packages

setup(
        name     = "beamline",
        version  = "1.1",
        description = "beamline plot module",
        author   = "Tong Zhang",
        author_email = "warriorlance@gmail.com",
        platforms = ["Linux"],
        license  = "MIT",
        packages = find_packages(),
        scripts  = ["parse_beamline.py", "elements.py"],
     )

