#!/usr/bin/env python2

"""
plot beamline from MAD-8 definition file
----
Tong Zhang, Sep.23,2014
"""

import elements
import parse_beamline
         
#beamlinelist = parse_beamline.parse_mad('/home/tong/work/TGU/SIOM/beamline/20140909.txt')
#beamlinelist = parse_beamline.parse_mad('/home/tong/work/python/drawing/visualattice/ele.list', 'BL4')
beamlinelist = parse_beamline.parse_mad('/home/tong/work/python/drawing/visualattice/LPA.list', 'BL1')
beamlineplot, xlim, ylim = elements.make_beamline_for_plot(beamlinelist, startpoint=(5, 5))
elements.plot_lattice(beamlineplot, fig_size = 10, fig_ratio = 0.3, xranges=xlim, yranges=ylim, zoomfac=2)
