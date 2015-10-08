#!/usr/bin/env python

#
# -*- coding: utf8 -*-
#

#import sys
#sys.path.append('../dist/beamline-1.1-py2.7.egg')

import beamline

beamlinelist = beamline.blparser.madParser('../lattice/LPA.list', 'BL2')
blplot, xlim, ylim = beamline.makeBeamline(beamlinelist, startpoint = (5, 5))
beamline.plotLattice(blplot, fig_size = 8, fig_ratio = 0.5, xranges = xlim, yranges = ylim, zoomfac = 1.8)
