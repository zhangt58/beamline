# beamline

Accelerator online model and lattice visualization modules developed by <code>Python</code>.

Developing language: <code>Python 2.7</code>

Author: Tong Zhang &copy; 2015-2016

### Main Features:

1. Parsing <code>elegant</code> (electron accelerator tracking code) lattice file (.lte) to be
   python dict or json string for further operations.
2. Modeling accelerator magnetic elements, such as dipole, quadrupole, drift, etc. to be python
   objects, from EPICS control environment to OOP level.
3. Modeling lattice beamline from modeled elements, constructing Lattice instance, 
   dumping .lte file for code tracking.
4. Feeding defined elements with new configuration, interfacing with EPICS environment, to form
   the close-loop online system.
5. Visualizing the lattice layout by predefined elements' style.
