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
from .ui import ui_main
from .mathutils import funTransQuadF, funTransQuadD
from .mathutils import funTransDrift
from .mathutils import funTransUnduH, funTransUnduV
from .mathutils import funTransEdgeX, funTransEdgeY
from .mathutils import funTransSectX, funTransSectY
from .mathutils import funTransChica
from .mathutils import transDrift
from .mathutils import transQuad
from .mathutils import transSect
from .mathutils import transRbend
from .mathutils import transFringe
from .mathutils import transChicane
from .mathutils import Chicane
from .matchutils import ParseParams, BeamMatch, FELSimulator, parseLattice

__version__ = "1.3.5"
__author__ = "Tong Zhang"

__doc__ = """Python package created for lattice generation, operation, 
manipulation, visualization and accelerator online modeling, distributed
with both console and graphical user interfaces environment.

To evoke the GUI app:

1. run ``lv`` or ``latticeviewer`` in terminal after ``beamline`` 
   package is installed;
2. ``beamline.ui_main.run()`` in [i]python terminal after ``beamline``
   is imported.

:Version: %s
:Author: Tong Zhang (zhangtong@sinap.ac.cn)
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
           ui_main,
           ParseParams, BeamMatch, FELSimulator, parseLattice,
           funTransQuadF, funTransQuadD, funTransDrift, funTransUnduH, 
           funTransUnduV, funTransEdgeX, funTransEdgeY, funTransSectX, 
           funTransSectY, funTransChica, 
           transDrift, transQuad, transSect, transRbend, transFringe,
           transChicane, Chicane,
           ].extend(allElements)
