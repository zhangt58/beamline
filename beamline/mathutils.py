#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
functions for mathematical calculations
    1: transfer matrix for quad, drift, undulator, chicane, etc.

Tong Zhang
Aug. 11, 2015

Revised: 2016-05-11 11:12:20 AM CST
    1: expand 2 x 2 transport matrice to 6 x 6
"""

import numpy as np

def funTransQuadF(k, s):
    """ Focusing quad in X, defocusing in Y
        :param k: k1, in [T/m]
        :param s: width, in [m]
    """
    sqrtk=np.sqrt(complex(k))
    a =  np.cos(sqrtk*s)
    b =  np.sin(sqrtk*s)/sqrtk
    c = -sqrtk*np.sin(sqrtk*s)
    d =  np.cos(sqrtk*s)
    return np.matrix([[a.real, b.real], [c.real, d.real]], dtype = np.double)

def funTransQuadD(k, s):
    """ Defocusing quad in X, focusing in Y
        :param k: k1, in [T/m]
        :param s: width, in [m]
    """
    sqrtk=np.sqrt(complex(k))
    a = np.cosh(sqrtk*s)
    b = np.sinh(sqrtk*s)/sqrtk
    c = sqrtk*np.sinh(sqrtk*s)
    d = np.cosh(sqrtk*s)
    return np.matrix([[a.real, b.real], [c.real, d.real]], dtype = np.double)

def funTransDrift(s):
    """ Drift
        :param s: drift length, in [m]
    """
    return np.matrix([[1, s], [0, 1]], dtype = np.double)

def funTransUnduV(k, s):
    """ Planar undulator transport matrix in vertical direction
        :param k: equivalent k1, in [T/m], i.e. natural focusing
        :param s: horizontal width, in [m]
    """
    m = funTransQuadF(k, s)
    return m

def funTransUnduH(s):
    """ Planar undulator transport matrix in horizontal direction 
        :param s: horizontal width, in [m]
    """
    return np.matrix([[1, s], [0, 1]], dtype = np.double)

def funTransEdgeX(theta, rho):
    """ Fringe matrix in X
        :param theta: fringe angle, in [rad]
        :param rho: bend radius, in [m]
    """
    return np.matrix([[1, 0], [np.tan(theta)/rho, 1]], dtype = np.double)

def funTransEdgeY(theta, rho):
    """ Fringe matrix in Y
        :param theta: fringe angle, in [rad]
        :param rho: bend radius, in [m]
    """
    return np.matrix([[1, 0], [-np.tan(theta)/rho, 1]], dtype = np.double)

def funTransSectX(theta, rho):
    """ Sector matrix in X
        :param theta: bend angle, in [rad]
        :param rho: bend radius, in [m]
    """
    return np.matrix([[np.cos(theta), rho*np.sin(theta)], [-np.sin(theta)/rho, np.cos(theta)]], dtype = np.double)

def funTransSectY(theta, rho):
    """ Sector matrix in Y
        :param theta: bend angle, in [rad]
        :param rho: bend radius, in [m]
    """
    return np.matrix([[1, rho*theta], [0, 1]], dtype = np.double)

def funTransChica(imagl, idril, ibfield, gamma0, xoy='x'):
    """ Chicane matrix, composed of four rbends, seperated by drifts
        :param imagl: rbend width, in [m]
        :param idril: drift length between two adjacent rbends, in [m]
        :param ibfield: rbend magnetic strength, in [T]
        :param gamma0: electron energy, gamma
        :param xoy: 'x' or 'y', matrix in X or Y direction, 'x' by default
    """
    m0 = 9.10938215e-31
    e0 = 1.602176487e-19
    c0 = 299792458
    rho = np.sqrt(gamma0**2-1)*m0*c0/ibfield/e0
    theta = np.arcsin(imagl/rho)
    ld = idril
    mx = reduce(np.dot, [funTransDrift(idril), 
                         funTransSectX(theta, rho), funTransEdgeX(theta, rho),
                         funTransDrift(ld),
                         funTransEdgeX(-theta, -rho), funTransSectX(-theta, -rho),
                         funTransDrift(ld),
                         funTransSectX(-theta, -rho), funTransEdgeX(-theta, -rho), 
                         funTransDrift(ld),
                         funTransEdgeX(theta, rho), funTransSectX(theta, rho), 
                         funTransDrift(idril)])
    my = reduce(np.dot, [funTransDrift(idril),
                         funTransSectY(theta, rho), funTransEdgeY(theta, rho),
                         funTransDrift(ld),
                         funTransEdgeY(-theta, -rho), funTransSectY(-theta, -rho),
                         funTransDrift(ld),
                         funTransSectY(-theta, -rho), funTransEdgeY(-theta, -rho),
                         funTransDrift(ld),
                         funTransEdgeY(theta, rho), funTransSectY(theta, rho),
                         funTransDrift(idril)])
    if xoy == 'x':
        m = mx
    else:
        m = my

    return m

# 6 x 6 transport matrice
def transDrift(length=0.0, gamma=None):
    """ Transport matrix of drift
        :param length: drift length in [m]
        :param gamma: electron energy, gamma value
    """
    m = np.eye(6, 6, dtype = np.float64)
    if length == 0.0:
        print("warning: 'length' should be a positive float number.")
    elif gamma is not None and gamma != 0.0:
        m[0,1] = m[2,3] = length
        m[4,5] = float(length)/gamma/gamma
    else:
        print("warning: 'gamma' should be a positive float number.")
    return m

def transQuad(length=0.0, k1=0.0, gamma=None):
    """ Transport matrix of quadrupole
        :param length: quad width in [m]
        :param k1: quad k1 strength in [T/m]
        :param gamma: electron energy, gamma value
    """
    m = np.eye(6, 6, dtype = np.float64)
    if length == 0.0:
        print("warning: 'length' should be a positive float number.")
    elif gamma is not None and gamma != 0.0:
        if k1 == 0:
            print("warning: 'k1' should be a positive float number.")
            m[0,1] = m[2,3] = 1.0
            m[4,5] = float(length)/gamma/gamma
        else:
            sqrtk = np.sqrt(complex(k1))
            sqrtkl = sqrtk * length
            m[0,0] = m[1,1] = (np.cos(sqrtkl)).real
            m[0,1] = (np.sin(sqrtkl)/sqrtk).real
            m[1,0] = (-np.sin(sqrtkl)*sqrtk).real
            m[2,2] = m[3,3] = (np.cosh(sqrtkl)).real
            m[2,3] = (np.sinh(sqrtkl)/sqrtk).real
            m[3,2] = (-np.sinh(sqrtkl)*sqrtk).real
            m[4,5] = float(length)/gamma/gamma
    else:
        print("warning: 'gamma' should be a positive float number.")
    return m

def transSect(theta=None, rho=None, gamma=None):
    """ Transport matrix of sector dipole
        :param theta: bending angle in [RAD]
        :param rho: bending radius in [m]
        :param gamma: electron energy, gamma value
    """
    m = np.eye(6, 6, dtype = np.float64)
    if None in (theta, rho, gamma):
        print("warning: 'theta', 'rho', 'gamma' should be positive float numbers.")
        return m
    else:
        rc = rho * np.cos(theta)
        rs = rho * np.sin(theta)
        m[0,0] = m[1,1] = rc/rho
        m[0,1] = rs
        m[0,5] = rho-rc
        m[1,0] = -np.sin(theta)/rho
        m[1,5] = rs/rho
        m[2,3] = rho*np.sin(theta)
        m[4,0] = m[1,5]
        m[4,1] = m[0,5]
        m[4,5] = rho*np.sin(theta)/gamma/gamma - rho*theta + rs
        return m

def transRbend(theta=None, rho=None, gamma=None, incsym=-1):
    """ Transport matrix of rectangle dipole
        :param theta: bending angle in [RAD]
        :param incsym: incident symmetry, -1 by default, options:
                       -1: left half symmetry, 0: full symmetry, 1: right half symmetry
        :param rho: bending radius in [m]
        :param gamma: electron energy, gamma value
    """
    if None in (theta, rho, gamma):
        print("warning: 'theta', 'rho', 'gamma' should be positive float numbers.")
        m = np.eye(6, 6, dtype = np.float64)
        return m
    else:
        beta12d = {'-1':(0, theta), '0':(theta*0.5, theta*0.5), '1':(theta, 0)}
        (beta1, beta2) = beta12d[str(incsym)]
        mf1 = transFringe(beta=beta1, rho=rho)
        mf2 = transFringe(beta=beta2, rho=rho)
        ms = transSect(theta=theta, rho=rho, gamma=gamma)
        m = reduce(np.dot, [mf1, ms, mf2])
        return m

def transFringe(beta=None, rho=None):
    """ Transport matrix of fringe field
        :param beta: angle of rotation of pole-face in [RAD]
        :param rho: bending radius in [m]
    """
    m = np.eye(6, 6, dtype = np.float64)
    if None in (beta, rho):
        print("warning: 'theta', 'rho' should be positive float numbers.")
        return m
    else:
        m[1,0] = np.tan(beta)/rho
        m[3,2] = -np.tan(beta)/rho
        return m

def transChicane(bend_length=None, bend_field=None, drift_length=None, gamma=None):
    """ Transport matrix of chicane
        composed of four rbends and three drifts between them
        :param bend_length: rbend width in [m]
        :param bend_field: rbend magnetic field in [T]
        :param drift_length: drift length, list or tuple of three elements, in [m]
                             single float number stands for same length for three drifts
        :param gamma: electron energy, gamma value
    """
    if None in (bend_length, bend_field, drift_length, gamma):
        print("warning: 'bend_length', 'bend_field', 'drift_length', 'gamma' should be positive float numbers.")
        m = np.eye(6, 6, dtype = np.float64)
        return m
    else:
        if isinstance(drift_length, tuple) or isinstance(drift_length, list):
            if len(drift_length) == 1:
                dflist = drift_length * 3
            elif len(drift_length) == 2:
                dflist = []
                dflist.extend(drift_length)
                dflist.append(drift_length[0])
            elif len(drift_length) >= 3:
                dflist = drift_length[0:3]
                if dflist[0] != dflist[-1]:
                    print("warning: chicane is not symmetric.")
            else:
                print("drift_length is not a valid list or tuple.")
        else:
            dflist = []
            dflist.extend([drift_length, drift_length, drift_length])

        m0 = 9.10938215e-31
        e0 = 1.602176487e-19
        c0 = 299792458.0
        rho = np.sqrt(gamma**2-1)*m0*c0/bend_field/e0
        theta = np.arcsin(bend_length/rho)

        m_rb_1 = transRbend( theta,  rho, gamma, -1)
        m_rb_2 = transRbend(-theta, -rho, gamma,  1)
        m_rb_3 = transRbend(-theta, -rho, gamma, -1)
        m_rb_4 = transRbend( theta,  rho, gamma,  1)
        m_df_12 = transDrift(dflist[0], gamma)
        m_df_23 = transDrift(dflist[1], gamma)
        m_df_34 = transDrift(dflist[2], gamma)

        m = reduce(np.dot, [m_rb_1, m_df_12, m_rb_2, m_df_23, m_rb_3, m_df_34, m_rb_4])
        return m
        
class Chicane(object):
    """ Chicane class
    """
    def __init__(self, bend_length=None, bend_field=None, drift_length=None, gamma=None):
        self.transM = np.eye(6, 6, dtype = np.float64)
        self.setParams(bend_length, bend_field, drift_length, gamma)
        self.mflag = True # if calculate m or return eye matrix
    
    def setParams(self,bend_length, bend_field, drift_length, gamma):
        if None in (bend_length, bend_field, drift_length, gamma):
            print("warning: 'bend_length', 'bend_field', 'drift_length', 'gamma' should be positive float numbers.")
            self.mflag = False
        else:
            self.setDriftList(drift_length)
            self.gamma = gamma
            self.bend_length = bend_length
            self.bend_field = bend_field

    def setDriftList(self, drift_length):
        """ set drift length list of three elements
            :param drift_length: input drift_length in [m]
        """
        if isinstance(drift_length, tuple) or isinstance(drift_length, list):
            if len(drift_length) == 1:
                self.dflist = drift_length * 3
            elif len(drift_length) == 2:
                self.dflist = []
                self.dflist.extend(drift_length)
                self.dflist.append(drift_length[0])
            elif len(drift_length) >= 3:
                self.dflist = drift_length[0:3]
                if self.dflist[0] != self.dflist[-1]:
                    print("warning: chicane is not symmetric.")
            else:
                print("drift_length is not a valid list or tuple.")
                self.mflag = False
        else:
            self.dflist = []
            self.dflist.extend([drift_length, drift_length, drift_length])

    def getMatrix(self):
        if self.mflag:
            m0 = 9.10938215e-31
            e0 = 1.602176487e-19
            c0 = 299792458.0
            rho = np.sqrt(self.gamma**2-1)*m0*c0/self.bend_field/e0
            theta = np.arcsin(self.bend_length/rho)
            self.bangle = theta

            m_rb_1 = transRbend( theta,  rho, self.gamma, -1)
            m_rb_2 = transRbend(-theta, -rho, self.gamma,  1)
            m_rb_3 = transRbend(-theta, -rho, self.gamma, -1)
            m_rb_4 = transRbend( theta,  rho, self.gamma,  1)
            m_df_12 = transDrift(self.dflist[0], self.gamma)
            m_df_23 = transDrift(self.dflist[1], self.gamma)
            m_df_34 = transDrift(self.dflist[2], self.gamma)

            self.transM = reduce(np.dot, [m_rb_1, m_df_12, m_rb_2, m_df_23, m_rb_3, m_df_34, m_rb_4])
     
            return self.transM
            
    def getAngle(self, mode='deg'):
        """ return bend angle
            :param mode: 'deg' or 'rad'
        """
        if self.mflag:
            if mode == 'deg':
                return self.bangle / np.pi * 180
            else: # rad
                return self.bangle
        else:
            return 0

    def getR(self,i=5,j=6):
        """ return transport matrix element, indexed by i, j,
            be defaut, return dispersion value, i.e. getR(5,6) in [m]
            :param i: row index, with initial index of 1
            :param j: col indx, with initial index of 1
        """
        return self.transM[i-1,j-1]

    def setBendLength(self, x):
        self.bend_length = x

    def setBendField(self, x):
        self.bend_field = x

    def setDriftLength(self, x):
        self.setDriftList(x)

    def setGamma(self, x):
        self.gamma = x

def test():
    k = -10
    s = 1
    
    theta   = 2
    rho     = 9
    imagl   = 0.5
    idril   = 1.0
    ibfield = 0.8
    gamma0  = 500
    xoy     = 'y'

    f1 = funTransQuadF(k, s)
    f2 = funTransQuadD(k, s)
    f3 = funTransUnduV(k, s)
    f4 = funTransChica(imagl, idril, ibfield, gamma0, xoy)
    print f1
    print f2
    print f3
    print("-"*40)
    print f1.dot(f2).dot(f3)
    print reduce(np.dot, [f1, f2, f3])
    print("-"*40)
    print f4
    print("-"*40)
    print funTransQuadF(k, s) - funTransQuadD(-k, s)

if __name__ == "__main__":
    test()
