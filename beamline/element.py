#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module defines all kinds of magnet components/elements.

Author      : Tong Zhang
Created     : 2016-03-22
Last updated: 2016-03-22
"""

class MagBlock(object):
    objcnt = 0
    info = {}
    def __init__(self):
        MagBlock.objcnt += 1
        self.info = {k:v for k,v in MagBlock.info.items()}

    @staticmethod
    def sumObjNum():
        return MagBlock.objcnt
    
    @staticmethod
    def setCommInfo(infostr):
        """ set common information,
            input parameter:
            :param infostr:
                1 infostr is a dict
                2 infostr with format like: "k1=v1, k2=v2"
        """
        if isinstance(infostr, dict):
            for k,v in infostr.items():
                MagBlock.info[k] = v
        elif isinstance(infostr, str):
            for k,v in MagBlock.str2dict(infostr).items():
                MagBlock.info[k] = v
        else:
            print("Information string ERROR.")

    def setConf(self, conf):
        if isinstance(conf, str):
            self.info.update(MagBlock.str2dict(conf))
        else:
            self.info.update(conf)

    @staticmethod
    def str2dict(istr):
        tmpstr = istr.replace(',','=').split('=')
        k = [i.strip() for i in tmpstr[0::2]]
        v = [i.strip() for i in tmpstr[1::2]]
        return dict(zip(k,v))

    def printConfig(self):
        print("\n")
        print("{s1}{s2:^22s}{s1}".format(s1="-"*10,s2="Configuration START"))
        for k,v in sorted(self.info.items(), reverse=True):
            print("{k} is {v}".format(k=k,v=v))
        print("{s1}{s2:^22s}{s1}".format(s1="-"*10,s2="Configuration END"))

    def dumpConfig(self, elename, format = 'elegant'):
        """ dump element configuration to given format,
            inpurt parameters:
            :param format: elegant/mad, elegant by default
        """
        return {elename: {self.typename: {k:self.info[k] for k in self.keylist}}}

class ElementCharge(MagBlock):
    """ charge element
    """
    def __init__(self):
        MagBlock.__init__(self)
        self.typename = 'CHARGE'
        self.keylist = ['total']

    def dumpConfig(self, elename, format = 'elegant'):
        return {elename: {self.typename: {k:self.info[k] for k in self.keylist}}}

class ElementCsrcsben(MagBlock):
    """ csrcsben element
    """
    def __init__(self):
        MagBlock.__init__(self)
        self.typename = 'CSRCSBEN'
        self.keylist = ['l','angle']

class ElementCsrdrift(MagBlock):
    """ csrdrift element
    """
    def __init__(self):
        MagBlock.__init__(self)
        self.typename = 'CSRDRIFT'
        self.keylist = ['l']

class ElementDrift(MagBlock):
    """ drift element
    """
    def __init__(self):
        MagBlock.__init__(self)
        self.typename = 'DRIFT'
        self.keylist = ['l']

class ElementKicker(MagBlock):
    """ kicker element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementLscdrift(MagBlock):
    """ lscdrift element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementMark(MagBlock):
    """ mark element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementMoni(MagBlock):
    """ moni element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementQuad(MagBlock):
    """ quad element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementRfcw(MagBlock):
    """ rfcw element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementRfdf(MagBlock):
    """ rfdf element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementWake(MagBlock):
    """ wake element
    """
    def __init__(self):
        MagBlock.__init__(self)

class ElementWatch(MagBlock):
    """ watch element
    """
    def __init__(self):
        MagBlock.__init__(self)

def test():
    #dinfo = {'DATE': '2016-03-22', 'AUTHOR': 'Tong Zhang'}
    dinfo = 'DATE = 2016-03-22, AUTHOR = Tong Zhang'
    MagBlock.setCommInfo(dinfo)

    CH = ElementCharge()
    chconf = {'total':1e-9}
    CH.setConf(chconf)

    D0 = ElementDrift()
    d0conf = {'l':1.0}
    D0.setConf(d0conf)

    B1 = ElementCsrcsben()
    b1conf = {'l':0.5,'angle':5}
    B1.setConf(b1conf)

    D1 = ElementCsrdrift()
    B2 = ElementCsrcsben()
    D2 = ElementCsrdrift()
    B3 = ElementCsrcsben()
    D3 = ElementCsrdrift()
    B4 = ElementCsrcsben()
    D4 = ElementCsrdrift()
    Q1 = ElementQuad()
    D5 = ElementDrift()
    Q2 = ElementQuad()
    D6 = ElementDrift()
    Q3 = ElementQuad()
    D7 = ElementDrift()

    #print MagBlock.sumObjNum()
    #CH.printConfig()
    #D0.printConfig()
    #B1.printConfig()
    dconf1 = CH.dumpConfig('C')
    dconf2 = D0.dumpConfig('D0')
    dconf3 = B1.dumpConfig('B1')

    dconf = {}
    for i in [dconf1, dconf2, dconf3]:
        dconf.update(i)

    import json
    print json.dumps(dconf)

    

if __name__ == '__main__':
    test()


