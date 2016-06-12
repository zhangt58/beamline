import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

import numpy as np
from test_rot import rot
import matplotlib as mpl

verts1 = [
    (0., 0.), # left, bottom
    (0., 1.), # left, top
    (1., 1.), # right, top
    (1., 0.), # right, bottom
    (0., 0.), # ignored
    ]


codes1 = [
         Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         Path.CLOSEPOLY,
        ]
path1 = Path(verts1, codes1)

x0, y0 = 2.5, 2.5
w , h  = 0.4, 2.0
verts2 = [
    (x0 - w/2, y0),
    (x0      , y0 + h/2),
    (x0 + w/2, y0),
    (x0      , y0 - h/2),
    (x0 - w/2, y0),
    ]
codes2 = [
         Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         #Path.CURVE3,
         #Path.CURVE3,
         #Path.CURVE3,
         #Path.CURVE3,
        ]
path2 = Path(verts2, codes2)

verts2_rot = rot(np.array(verts2), theta=45, pc=np.array((x0, y0)))
path2_rot = Path(verts2_rot, codes2)


x = np.linspace(-2,2,100)
y = np.sin(x)

fig   = plt.figure()
ax    = fig.add_subplot(111)
line1 = ax.plot(x,y)
patch1 = patches.PathPatch(path1, facecolor='red', edgecolor = 'blue', alpha=0.3, lw=2)
patch2 = patches.PathPatch(path2, facecolor='red', edgecolor = 'blue', alpha=0.3, lw=2)
patch2_rot = patches.PathPatch(path2_rot, facecolor = 'red', edgecolor = 'blue', alpha = 0.3, lw=2)

pc = x0,y0
epatch1 = patches.Ellipse(pc, w, h, angle=0,  ec='blue', fc='blue', alpha=0.2)
epatch2 = patches.Ellipse(pc, w, h, angle=45, ec='blue', fc='blue', alpha=0.2)

epatch3 = patches.FancyBboxPatch((0,0), w, h)

for a,b in path1.iter_segments():
    print a,b

ax.add_patch(epatch1)
ax.add_patch(epatch2)
ax.add_patch(epatch3)
ax.add_patch(patch1)
ax.add_patch(patch2)
ax.add_patch(patch2_rot)
ax.set_xlim(-5,5)
ax.set_ylim(-5,5)
plt.show()


verts = [
        (0.0,0.0), # P0
        (0.2,1.0), # P1
        (1.0,0.8), # P2
        (0.8,0.0), # P3
        ]

codes = [Path.MOVETO,
         Path.CURVE4,
         Path.CURVE4,
         Path.CURVE4,
         ]

path = Path(verts, codes)

fig   = plt.figure()
ax    = fig.add_subplot(111)
patch = patches.PathPatch(path, facecolor = 'red', edgecolor = 'red', alpha = 0.5)
ax.add_patch(patch)

xs, ys = zip(*verts)
ax.plot(xs, ys, 'x--', lw = 2, color='black', ms = 10)

ax.text(-0.05, -0.05, '$P_0$')
ax.text( 0.15,  1.05, '$P_1$')
ax.text( 1.05,  0.85, '$P_2$')
ax.text( 0.85, -0.05, '$P_3$')

ax.set_xlim(-0.1,1.1)
ax.set_ylim(-0.1,1.1)

x = np.linspace(-1,1,10)
y = np.sin(x)
ax.add_line(mpl.lines.Line2D(x,y))

plt.show()

"""
import numpy as np
data    = np.random.randn(1000)
n, bins = np.histogram(data,100)

left   = np.array(bins[:-1])
right  = np.array(bins[1:])
bottom = np.zeros(len(left))
top    = bottom + n

nrects = len(left)
nverts = nrects*(1+3+1)
verts = np.zeros((nverts,2))
codes = np.ones(nverts, int) * Path.LINETO
codes[0::5] = Path.MOVETO
codes[4::5] = Path.CLOSEPOLY
verts[0::5,0]=left
verts[0::5,1]=bottom
verts[1::5,0]=left
verts[1::5,1]=top
verts[2::5,0]=right
verts[2::5,1]=top
verts[3::5,0]=right
verts[3::5,1]=bottom

fig     = plt.figure()
ax      = fig.add_subplot(111)
barpath = Path(verts, codes)
patch   = patches.PathPatch(barpath, facecolor = 'blue', 
                            edgecolor = 'red', alpha = 0.5)
ax.add_patch(patch)
ax.set_xlim(left[0],right[-1])
ax.set_ylim(bottom.min(), top.max()*1.2)
plt.show()
"""
