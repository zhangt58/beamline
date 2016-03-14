from .elements  import Drift, Rbend, Undulator, Quadrupole
from .pltutils  import plotLattice, makeBeamline
from .blparser  import madParser
from .lattice   import Lattice, LteParser
from .datautils import DataExtracter

__version__ = "1.1.1"
__author__ = "Tong Zhang"

__doc__ = """
    lattice operation module

    Version: %s
    Author: Tong Zhang (zhangtong@sinap.ac.cn)

    This python package is created for lattice objectification, 
    manipulation and visualization.
""" % (__version__)

def testf(arg1, arg2='arg2'):
    """test function

    test test test
    """
    return arg1 + arg2

__all__ = [Drift, Rbend, Undulator, Quadrupole, 
           plotLattice, makeBeamline, madParser, 
           Lattice, LteParser,
           DataExtracter]
