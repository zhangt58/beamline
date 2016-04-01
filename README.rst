beamline
=========

Accelerator online model and lattice visualization modules developed by Python.

Developing language: *Python 2.7*

Author: Tong Zhang 2015-2016

**Main Features:**

+  Parsing elegant (electron accelerator tracking code) lattice file (.lte) to be
   python dict or json string for further operations.
+  Modeling accelerator magnetic elements, such as dipole, quadrupole, drift, etc. to be python
   objects, from EPICS control environment to OOP level.
+  Support unit conversion between EPICS PV raw value and the physical real value of elements.
+  Modeling lattice beamline from modeled elements, constructing Lattice instance, 
   dumping .lte file for code tracking.
+  Feeding defined elements with new configuration, interfacing with EPICS environment, to form
   the close-loop online system.
+  Visualizing the lattice layout by predefined elements' style.
