#!/usr/bin/env python
#
# -*- coding: utf8 -*-
#

"""
functions for matplotlib plotting.

Re-organized: Oct. 8, 2015
Author: Tong Zhang
"""

import elements
import matplotlib.pyplot as plt
import numpy as np

def plotLattice(beamlinepatchlist, 
                fignum = 1, fig_size = 20, fig_ratio = 0.5,
                xranges = (-10, 10), yranges = (-10, 10), 
                zoomfac = 1.5):
    """
    function plot beamline defined by beamlinepatchlist, which is a set of patches for all elements
    :param beamlinepatchlist: generated by function makeBeamline
    """
    fig = plt.figure(fignum,figsize=(fig_size,fig_size*fig_ratio))
    ax = fig.add_subplot(111)
    for ins in beamlinepatchlist:
        [ax.add_patch(inspatch) for inspatch in ins.patch]
    x1, x2 = xranges
    y1, y2 = yranges
    minx = 0.5 * (x2 + x1) - 0.5 * zoomfac * (x2 - x1)
    maxx = 0.5 * (x2 + x1) + 0.5 * zoomfac * (x2 - x1)
    miny = 0.5 * (y2 + y1) - 0.5 * zoomfac * (y2 - y1)
    maxy = 0.5 * (y2 + y1) + 0.5 * zoomfac * (y2 - y1)
    ax.set_xlim([minx, maxx])
    ax.set_ylim([miny, maxy])
    plt.show()

def makeBeamline(beamlinelist, startpoint=(0, 0)):
    """
    function to construct patches for 'plotLattice', from different elements like
    'rbend','quadrupole',etc. parsing from lattice file, mad/lte.
    drift sections are calculated from other elements.

    Input parameters:
    :param beamlinelist: list, which elements are dict, each dict is the description for magnetic element,
                  should be returned from module 'blparser', function madParser
    """
    latticelist = []
    anglenow = 0.0
    maxx, maxy = startpoint
    minx, miny = startpoint

    for i in range(len(beamlinelist)):
        element = beamlinelist[i]
        elementtype = element["type"][0:4].lower()
        if elementtype == "rben":
            newelement = elements.Rbend(width=float(element["l"]), height=1.5 * float(element["l"]),
                                        angle=float(element["angle"]),
                                        link_node=startpoint,)
            anglenow += newelement.angle
            minx = min(minx, newelement.minx)
            miny = min(miny, newelement.miny)
            maxx = max(maxx, newelement.maxx)
            maxy = max(maxy, newelement.maxy)

        elif elementtype == "drif":
            newelement = elements.Drift(length=float(element["l"]), angle=anglenow,
                                        link_node=startpoint,)
            minx = min(minx, newelement.minx)
            miny = min(miny, newelement.miny)
            maxx = max(maxx, newelement.maxx)
            maxy = max(maxy, newelement.maxy)

        elif elementtype == "quad":
            xory = "x"
            if float(element["k1"]) < 0: xory = "y"
            newelement = elements.Quadrupole(width=float(element["l"]),
                                             angle=float(element["angle"]),
                                             xysign=xory,
                                             link_node=startpoint,)
            minx = min(minx, newelement.minx)
            miny = min(miny, newelement.miny)
            maxx = max(maxx, newelement.maxx)
            maxy = max(maxy, newelement.maxy)
        
        elif elementtype == "undu":
            newelement = elements.Undulator(period_length = float(element["xlamd"]), 
                                            period_number = int(element["nwig"]),
                                            link_node=startpoint,)
            minx = min(minx, newelement.minx)
            miny = min(miny, newelement.miny)
            maxx = max(maxx, newelement.maxx)
            maxy = max(maxy, newelement.maxy)

        else:
            print "unknown element\n"

        startpoint = newelement.link_node
        latticelist.append(newelement)

    return latticelist, np.array([minx, maxx]), np.array([miny, maxy])

def main():
    try:
        import blparser
        beamlinelist = blparser.madParser('../lattice/ele.list')
        beamlineplot, xlim, ylim = makeBeamline(beamlinelist, startpoint=(5, 5))
        plotLattice(beamlineplot, xranges = xlim, yranges = ylim, zoomfac = 2.0, fig_size = 8, fig_ratio = 0.4)
    except ImportError:
        print "Import blparser error!"

if __name__ == '__main__':
    main()