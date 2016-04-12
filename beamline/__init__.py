from .elements   import Drift, Rbend, Undulator, Quadrupole
from .pltutils   import plotLattice, makeBeamline
from .blparser   import madParser
from .lattice    import Lattice, LteParser
from .simulation import Simulator
from .datautils  import DataExtracter, DataVisualizer, DataStorage
from .element    import MagBlock
from .element    import ElementCharge
from .element    import ElementCsrcsben, ElementQuad
from .element    import ElementCsrdrift, ElementDrift, ElementLscdrift
from .element    import ElementKicker
from .element    import ElementMark, ElementWatch, ElementMoni
from .element    import ElementRfcw, ElementRfdf, ElementWake
from .element    import ElementBeamline
from .element    import ElementCsrdrift as ElementCsrdrif
from .element    import ElementLscdrift as ElementLscdrif
from .element    import ElementDrift as ElementDrif
from .models     import Models


__version__ = "1.2"
__author__ = "Tong Zhang"

__doc__ = """
    lattice operation/online module

    Version: %s
    Author: Tong Zhang (zhangtong@sinap.ac.cn)

    This python package is created for lattice online modeling, 
    manipulating and visualising.
""" % (__version__)

allElements = [ElementCharge,   ElementCsrcsben, ElementQuad, 
               ElementCsrdrift, ElementCsrdrif,  ElementDrift,    
               ElementDrif,     ElementLscdrift, ElementLscdrif,
               ElementKicker,   ElementMark,     ElementWatch, 
               ElementMoni,     ElementRfcw,     ElementRfdf, 
               ElementWake,     ElementBeamline]

__all__ = [
           Drift, Rbend, Undulator, Quadrupole, 
           plotLattice, makeBeamline, madParser, 
           Lattice, LteParser,
           Simulator,
           DataExtracter, DataVisualizer, DataStorage,
           Models,
           ].extend(allElements)
