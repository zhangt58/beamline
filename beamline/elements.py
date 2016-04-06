#!/usr/bin/env python
# -*- coding: utf8 -*-

import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.pyplot as plt
import numpy as np

"""
definition for magnetic elements
Created Time: Sep. 22nd, 2014
Author: Tong Zhang
"""

class Drift(object):
    """
    element: drift section, input parameters:
    _length: drift length, [m]
    _angle:  angle between drawing line and horizontal plane, [deg]
    _linkNode: (x,y) coordinates that drawing begins or linked to another element
    """
    def __init__(self,
                 length = 2.0,
                 angle = 0.0,
                 link_node = (0.0, 0.0),
                 line_color = 'black',
                 line_width = 1.5,
                 _alpha =0.8):

        x1, y1 = link_node
        x2, y2 = x1 + length * np.cos(angle / 180.0 * np.pi), y1 + length * np.sin(angle / 180.0 * np.pi)

        verts = [(x1, y1), (x2, y2), ]
        codes = [path.Path.MOVETO,
                 path.Path.LINETO, ]
        pathall = path.Path(verts, codes)
        self.patch = []
        patch = patches.PathPatch(pathall,
                                  facecolor= line_color,
                                  edgecolor= line_color,
                                  lw=line_width,
                                  alpha=_alpha)

        self.patch.append(patch)
        self.link_node = x2, y2
        self.maxy = max(y1, y2)
        self.maxx = max(x1, x2)
        self.miny = min(y1, y2)
        self.minx = min(x1, x2)

    def show(self, fignum=1):
        fig = plt.figure(fignum)
        ax = fig.add_subplot(111)
        [ax.add_patch(inspatch) for inspatch in self.patch]
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        plt.show()

class Rbend(object):
    """
    element: rectangle bend, input parameters:
    _width: bend width, [m]
    _height: bend hight, [m]
    _angle: bend angle, [deg]
    _linkNode: (x,y) coordinates that drawing begins or linked to another element
    """
    def __init__(self,
                 width=1.0,
                 height=2.0,
                 angle=0.0,
                 link_node=(0.0, 1.0),
                 face_color='red',
                 edge_color='red',
                 line_width=0.1,
                 _alpha=0.8):

        x0, y0 = (link_node[0], link_node[1] - height * 0.5)
        x1, y1 = (x0, y0 + height)
        x2, y2 = (x0 + width, y1)
        x3, y3 = (x0 + width, y0)

        verts = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x0, y0)]
        codes = [path.Path.MOVETO,
                 path.Path.LINETO,
                 path.Path.LINETO,
                 path.Path.LINETO,
                 path.Path.CLOSEPOLY, ]
        pathall = path.Path(verts, codes)
        self.patch = []
        patch = patches.PathPatch(pathall,
                                  facecolor=face_color,
                                  edgecolor=edge_color,
                                  lw=line_width,
                                  alpha=_alpha, )

        self.patch.append(patch)
        self.link_node = (x3 + x2)/2.0, (y3 + y2)/2.0
        self.angle = angle
        self.maxy = max(y0, y1, y2, y3)
        self.maxx = max(x0, x1, x2, x3)
        self.miny = min(y0, y1, y2, y3)
        self.minx = min(x0, x1, x2, x3)

    def show(self, fignum=1):
        fig = plt.figure(fignum)
        ax = fig.add_subplot(111)
        [ax.add_patch(inspatch) for inspatch in self.patch]
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        plt.show()

    def info(self):
        pass

class Undulator(object):
    """
    element: undulator, input parameters:
    period_length: undulator period length, [m]
    period_number: undulator period number
    north_color  : color of north pole
    south_color  : color of south pole
    link_node    : (x,y) coordinates that drawing begins or linked to another element   
    ratio        : ratio of pole_height v.s. pole_width, and gap v.s pole_width
    spacing      : spacing between pole, measured by pole_width,
    gap          : undulator gap only for visualization, not true magnetic gap
    """
    def __init__(self,
                 period_length = 2.0,
                 period_number = 10,
                 north_color   = 'red',
                 south_color   = 'blue',
                 link_node     = (0, 0),
                 ratio         = [2.5,1.5],
                 spacing       = 1.5,
                 _alpha        = 0.8):
        pole_width  = 0.5 * period_length
        pole_height = ratio[0] * pole_width
        gap         = ratio[1] * pole_width

        self.patch = []
        maxx, maxy, minx, miny = 0, 0, 1e100, 1e100
        _x0, _y0 = link_node
        for inum in range(period_number*2):
            x0, y0 = (_x0, _y0 + 0.5 * gap)
            x1, y1 = (x0, y0 + pole_height)
            x2, y2 = (x1 + pole_width, y1)
            x3, y3 = (x2, y0)
            verts1 = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x0, y0)]
            codes1 = [path.Path.MOVETO,
                      path.Path.LINETO,
                      path.Path.LINETO,
                      path.Path.LINETO,
                      path.Path.CLOSEPOLY, ]
            pole_color = north_color
            patch1 = patches.PathPatch(path.Path(verts1,codes1),
                                       facecolor=pole_color,
                                       edgecolor=pole_color,
                                       alpha=_alpha,)
            maxy = max(maxy, y0, y1, y2, y3)
            maxx = max(maxx, x0, x1, x2, x3)
            miny = min(miny, y0, y1, y2, y3)
            minx = min(minx, x0, x1, x2, x3)
            
            x01, y01 = x0, 2.0 * _y0 - y0
            x11, y11 = x1, 2.0 * _y0 - y1
            x21, y21 = x2, 2.0 * _y0 - y2
            x31, y31 = x3, 2.0 * _y0 - y3
 
            verts2 = [(x01, y01), (x11, y11), (x21, y21), (x31, y31), (x01, y01)]
            codes2 = [path.Path.MOVETO,
                      path.Path.LINETO,
                      path.Path.LINETO,
                      path.Path.LINETO,
                      path.Path.CLOSEPOLY, ]
            pole_color = south_color
            patch2 = patches.PathPatch(path.Path(verts2,codes2),
                                       facecolor=pole_color,
                                       edgecolor=pole_color,
                                       alpha=_alpha,)
            _x0 += pole_width * spacing
            _y0 = _y0
            north_color,south_color = south_color, north_color
 
            maxy = max(maxy, y01, y11, y21, y31)
            maxx = max(maxx, x01, x11, x21, x31)
            miny = min(miny, y01, y11, y21, y31)
            minx = min(minx, x01, x11, x21, x31)

            self.patch.append(patch1)
            self.patch.append(patch2)

        # endfor
        # draw horizon line
        verts3 = [link_node, (_x0, _y0),]
        codes3 = [path.Path.MOVETO, path.Path.LINETO,]
        patch3 = patches.PathPatch(path.Path(verts3,codes3),
                                   facecolor='black',
                                   edgecolor='black',
                                   lw    = 1.5,
                                   alpha = 0.8,)
        self.patch.append(patch3)
        self.link_node  = _x0, _y0
        self.maxx = max(maxx, _x0)
        self.maxy = max(maxy, _y0)
        self.minx = min(minx, _x0)
        self.miny = min(miny, _y0)

    def show(self, fignum=1):
        fig = plt.figure(fignum)
        ax = fig.add_subplot(111)
        [ax.add_patch(inspatch) for inspatch in self.patch]
        ax.set_xlim(-10, 40)
        ax.set_ylim(-10, 10)
        plt.show()

class Quadrupole(object):
    """
    element: quadrupole, input parameters:
    width: quad width, [m]
    angle: angle, [deg]
    xy_sign: 'x': x-focusing, K1>0; 'y': y-focusing, K1<0 
    link_node: (x,y) coordinates that drawing begins or linked to another element
    """
    def __init__(self,
                 width=1.0,
                 angle=75,
                 xysign='x',
                 link_node=(0.0, 1.0),
                 face_color='blue',
                 edge_color='blue',
                 line_width=0.1,
                 _alpha=0.8):

        if xysign == "x":
            x0, y0 = link_node
            x1, y1 = x0 + 0.5 * width, y0 + 0.5 * width * np.tan(angle / 180.0 * np.pi)
            x2, y2 = x1 + 0.5 * width, y0
            x3, y3 = x1, 2 * y0 - y1

            verts = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x0, y0)]
            codes = [path.Path.MOVETO,
                     path.Path.LINETO,
                     path.Path.LINETO,
                     path.Path.LINETO,
                     path.Path.CLOSEPOLY, ]
            pathall = path.Path(verts, codes)

            self.link_node = x2, y2
            self.maxy = max(y0, y1, y2, y3)
            self.maxx = max(x0, x1, x2, x3)
            self.miny = min(y0, y1, y2, y3)
            self.minx = min(x0, x1, x2, x3)

        elif xysign == "y":
            x0, y0 = link_node
            x1, y1 = x0 - 0.5 * width, y0 + 0.5 * width * np.tan(angle / 180.0 * np.pi)
            x2, y2 = x1 + width, y1
            x3, y3 = x1, 2 * y0 - y1 
            x4, y4 = x2, 2 * y0 - y2

            verts = [(x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x0, y0), (x0, y0)]
            codes = [path.Path.MOVETO,
                     path.Path.LINETO,
                     path.Path.LINETO,
                     path.Path.LINETO,
                     path.Path.LINETO,
                     path.Path.LINETO,
                     path.Path.CLOSEPOLY, ]
            pathall = path.Path(verts, codes)

            self.link_node = x0, y0
            self.maxy = max(y0, y1, y2, y3, y4)
            self.maxx = max(x0, x1, x2, x3, x4)
            self.miny = min(y0, y1, y2, y3, y4)
            self.minx = min(x0, x1, x2, x3, x4)
        
        self.patch = []
        patch = patches.PathPatch(pathall,
                                  facecolor=face_color,
                                  edgecolor=edge_color,
                                  lw=line_width,
                                  alpha=_alpha, )
        self.patch.append(patch)

    def show(self, fignum=1):
        fig = plt.figure(fignum)
        ax = fig.add_subplot(111)
        [ax.add_patch(inspatch) for inspatch in self.patch]
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        plt.show()
 
def test():
    a = Quadrupole()
    a.show()

if __name__ == '__main__':
    test()
