import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
"""
verts = [
    (0., 0.), # left, bottom
    (0., 1.), # left, top
    (1., 1.), # right, top
    (1., 0.), # right, bottom
    (0., 0.), # ignored
    ]

codes = [
         Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         Path.CLOSEPOLY,
        ]
"""
"""
codes = [
         Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         #Path.LINETO,
         Path.CLOSEPOLY,
        ]

path = Path(verts, codes)

fig   = plt.figure()
ax    = fig.add_subplot(111)
patch = patches.PathPatch(path, facecolor='blue', edgecolor = 'blue', lw=2)
ax.add_patch(patch)
ax.set_xlim(-2,2)
ax.set_ylim(-2,2)
plt.show()
"""

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
