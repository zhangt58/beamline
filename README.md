# beamline

Accelerator online model and lattice visualization package developed by <code>Python</code>.

Developing language: <code>Python 2.7</code>

Author: Tong Zhang &copy; 2015-2016

### Main Features:

*  Parsing <code>elegant</code> (electron accelerator tracking code) lattice file (.lte) to be
   python dict or json string for further operations.
*  Modeling accelerator magnetic elements, such as dipole, quadrupole, drift, etc. to be python
   objects, from EPICS control environment to OOP level.
*  Automatic modeling from .lte lattice file definition with postfixed '!epics' anotation to 
   define EPICS control configurations.
*  Support unit conversion between EPICS PV raw value and the physical real value of elements.
*  Modeling lattice beamline from modeled elements, constructing Lattice instance, 
   dumping .lte file for code tracking.
*  Feeding defined elements with new configuration, interfacing with EPICS environment, to form
   the close-loop online system.
*  Visualizing the lattice layout by predefined elements' style.
*  Friendly native-look GUI application to facilitate these functionalities.

### Screenshots:

* Lattice visualization after modeling,

<p>
    <img src=/contrib/demo1_screenshot.png?raw=true alt="tracking output" width="400"></img>
</p>
<p>
    <img src=/contrib/sxfel_lattice_layout.png?raw=true alt="sxfel lattice" width="800"></img>
</p>
<p>
    <img src=/contrib/dcls_lattice_layout.png?raw=true alt="dcls lattice with annotations" width="800"></img>
</p>

* With annotations,
<p>
    <img src=/contrib/SXFEL_lattice_layout.png?raw=true alt="sxfel lattice" width="800"></img>
</p>
<p>
    <img src=/contrib/DCLS_lattice_layout.png?raw=true alt="dcls lattice with annotations" width="800"></img>
</p>

