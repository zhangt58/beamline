# beamline

Accelerator online model and lattice visualization package developed by <code>Python</code>.

Developing language: <code>Python 2.7 and 3.x</code>

As of release 2.0.0, Python 3.x is supported, (1.x.y supports Python 2.7).

Documentation: https://archman.github.io/beamline/

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
    <img src=/contrib/sxfel_lattice_layout.png?raw=true alt="sxfel lattice" width="800"></img>
</p>

* With annotations,
<p>
    <img src=/contrib/SXFEL_lattice_layout_anote.png?raw=true alt="sxfel lattice" width="800"></img>
    <img src=/contrib/DCLS_lattice_layout_anote.png?raw=true alt="dcls lattice with annotations" width="800"></img>
</p>


* GUI application: `latticeviewer`:
<p>
    <img src=/screenshots/01.png?raw=true alt="data viewer"              width="400"></img>
    <img src=/screenshots/02.png?raw=true alt="operation log"            width="400"></img>
    <img src=/screenshots/03.png?raw=true alt="beamline choose"          width="400"></img>
    <img src=/screenshots/04.png?raw=true alt="convert json to lte file" width="400"></img>
    <img src=/screenshots/05.png?raw=true alt="incremental search"       width="400"></img>
    <img src=/screenshots/06.png?raw=true alt="lattice visualization"    width="400"></img>
</p>

### Installation and Usage:

For the installation and the list of dependencies which partially need manual interaction see the [documentation](https://archman.github.io/beamline/), please.
