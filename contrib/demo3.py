#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Demonstration to modeling accelerator with the lte file.
    DCLS

    Author       : Tong Zhang
    Created      : 2016-04-12 10:11:06 AM CST
    Last updated : 2016-04-14 09:02:50 AM CST
"""

import beamline
import os
import matplotlib.pyplot as plt

### STEP 0: global configurations
beamline.MagBlock.setStyleConfig(
        config={'drift':{'lw':2}}
        )

### STEP 1: read lattice configurations from .lte file
ltefile = os.path.join(os.getcwd(), 'dcls/dcls.lte')
lpins   = beamline.LteParser(ltefile)

# generate lte file with all the element-definitions regarding to beamline
blname = 'bl'
newltefile = os.path.join(os.getcwd(), 'dcls/om.lte')
latins = beamline.Lattice(lpins.file2json())
latins.generateLatticeFile(blname, newltefile)

# use the concise version of lte file
newlpins = beamline.LteParser(newltefile)
newlatins = beamline.Lattice(newlpins.file2json())
# 
## print all keywords and types
#allkws = newlpins.detectAllKws()
#for kw in allkws:
#    print("{k:<10s}: {t:>10s}".format(k=kw.upper(),
#                                      t=newlpins.getKwType(kw)))

# demonstrate to create a new element from keyword name,
# there are two approaches to create:
#   1: use element classes from element module
#   2: use makeElement() method from LteParser class or Lattice class

kw_name   = 'B11'

## create element approach 1:
#kw_dict   = newlpins.getKwAsDict(kw_name)
#kw_type   = newlpins.getKwType(kw_name)
#kw_config = newlpins.getKwConfig(kw_name)
#kw_name_eobj = beamline.ElementQuad(name=kw_name, config=kw_config)

## create element approach 2:
kw_eobj_name = newlpins.makeElement(kw_name)
#kw_eobj_name = newlatins.makeElement(kw_name)

## show element drawing:
kw_eobj_name.setDraw(mode='fancy') # or mode='plain'
#kw_eobj_name.showDraw()

### STEP 2: initialise all element objects for beamline model
#for ele in beamline.Models.flatten(newlatins.getAllKws()):
latmodel = beamline.Models(name=blname, mode='simu')
ele_name_list = newlatins.getElementList(blname)
ele_eobj_list = []
for ele in ele_name_list:
    eobj = newlatins.makeElement(ele)
    ele_eobj_list.append(eobj)

latmodel.addElement(*ele_eobj_list)
# show all configurations | pjson
#print latmodel.getAllConfig()

# find element by name
Q11BI1H_list = latmodel.getElementsByName('Q01'.lower())

# add other configurations, e.g. control configurations, etc.
Q11BI1H_list[0].printConfig(type='all')

# csrcsben example: 
B1LH_list = latmodel.getElementsByName('B11'.lower())
B1LH_list[0].printConfig()

### STEP 3: do tracking with the modeled lattice
finlatins = beamline.Lattice(latmodel.getAllConfig())
finltefile = os.path.join(os.getcwd(), 'dcls/om.lte')
finlatins.generateLatticeFile(latmodel.name, finltefile)

simpath = os.path.join(os.getcwd(), 'dcls')
elefile = os.path.join(simpath, 'om.ele')
elesim  = beamline.Simulator()
elesim.setMode('elegant')
elesim.setScript('runElegant.sh')
elesim.setExec('elegant')
elesim.setPath(simpath)
elesim.setInputfiles(ltefile=finltefile, elefile=elefile)
elesim.doSimulation()

# data columns could be extracted from simulation output files, to memory or h5 files.
data_tp    = elesim.getOutput(file = 'om.out', data = ('t', 'p'  ))#, dump = h5out)
data_sSx   = elesim.getOutput(file = 'om.sig', data = ('s', 'Sx' ))
data_setax = elesim.getOutput(file = 'om.twi', data = ('s', 'etax'))


# #### visualize data

fig = plt.figure(1)
ax1 = fig.add_subplot(221)
ax1.plot(data_tp[:,0],data_tp[:,1],'.')
ax1.set_xlabel('$t\,[s]$')
ax1.set_ylabel('$\gamma$')


ax2 = fig.add_subplot(222)
ax2.plot(data_sSx[:,0],data_sSx[:,1],'-')
ax2.set_ylabel('$\sigma_x\,[\mu m]$')
ax2.set_xlabel('$s\,[m]$')


ax3 = fig.add_subplot(223)
ax3.plot(data_setax[:,0],data_setax[:,1],'r-', lw=3,)
ax3.set_ylabel('$\eta_{x}\,[m]$')
ax3.set_xlabel('$s\,[m]$')


"""
# Scan parameter: final Dx v.s. angle of B1
import numpy as np
dx = []
thetaArray = np.linspace(0.05,0.3,20)
for theta in thetaArray:
    eleb1.setConf({'angle':theta}, type = 'simu')
    latins = beamline.Lattice(latline_online.getAllConfig())
    latins.generateLatticeFile(latline_online.name, latfile)
    elesim.doSimulation()
    data = elesim.getOutput(file = 'test.twi', data = (['etax']))
    dx.append(data[-1])
dxArray = np.array(dx)

plt.plot(thetaArray, dxArray, 'r')
"""

# #### Lattice layout visualization

# generate lattice drawing plotting objects
ptches, anotes, xr, yr = latmodel.draw(mode='fancy', showfig=False)

# show drawing 
fig3 = plt.figure(2)
ax3 = fig3.add_subplot(111)
ax3.plot(data_setax[:,0],data_setax[:,1],'r-', lw=3,)
ax3.set_ylabel('$\eta_{x}\,[m]$')
ax3.set_xlabel('$s\,[m]$')

ax3t = ax3.twinx()
[ax3t.add_patch(i) for i in ptches]
xr3 = ax3.get_xlim() 
yr3 = ax3.get_ylim() 
x0, x1 = min(xr[0],xr3[0]), max(xr[1], xr3[1])
y0, y1 = min(yr[0],yr3[0]), max(yr[1], yr3[1])
ax3t.set_xlim(x0, x1)
ax3t.set_ylim(y0, y1*3)
ax3.set_xlim(x0, x1)
ax3.set_ylim(y0, y1)
ax3.grid()


# show lattice drawing in a single plot
newptches = beamline.MagBlock.copy_patches(ptches)
#for i,val in enumerate(newptches):
#    print id(newptches[i]), id(ptches[i])
fig4 = plt.figure(4, figsize=(20,6), dpi=90)
ax4 = fig4.add_subplot(111,aspect=2)
#[ax4.add_patch(i) for i in newptches]
#beamline.Models.plotElements(ax4, newptches)
beamline.Models.plotElements(ax4, newptches)
beamline.Models.anoteElements(ax4, anotes, efilter='QUAD', 
        textypos=0.45, color='m', rotation=60, fontsize='small')
beamline.Models.anoteElements(ax4, anotes, efilter='CSRCSBEN', 
        textypos=0.55, color='b', rotation=60, fontsize='small')
beamline.Models.anoteElements(ax4, anotes, showAccName=True, 
        efilter=('RFCW','RFDF'), 
        textypos=None, arrowprops=None, color='k', 
        rotation=0, fontsize=None)
"""
[ax4.annotate(s=i['name'],
              xy=i['xypos'],
              xytext=(i['textpos'][0], -0.1),
              arrowprops=dict(arrowstyle='->'),
              alpha = 0.8,
              color='m',
              rotation=-60,
              fontsize='x-small')
              for i in anotes if i['type'] == 'QUAD']

[ax4.annotate(s=i['name'],
              xy=i['xypos'],
              xytext=(i['textpos'][0], 0.15),
              arrowprops=dict(arrowstyle='->', alpha=0.5),
              alpha = 0.8,
              color='b',
              rotation=-60,
              fontsize='x-small')
              for i in anotes if i['type'] == 'CSRCSBEN']

[ax4.annotate(s=i['name'],
              xy=i['xypos'],
              xytext=(i['textpos'][0], i['textpos'][1] - 0.1),
              arrowprops=dict(arrowstyle='->', alpha=0.5),
              alpha = 0.8,
              color='k',
              rotation=-60,
              fontsize='x-small')
              for i in anotes if i['type'] == 'CSRDRIFT']

"""

ax4.set_yticks([])
ax4.set_xlim(-1,40)
ax4.set_ylim(y0, y1*1.3)
ax4.set_xlabel('$s\,\mathrm{[m]}$')
fig4.tight_layout()
ax4.set_title('DCLS Lattice Layout', fontsize=24, color='m', fontweight='bold')

plt.show()
