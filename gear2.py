#!/usr/bin/env python3

# Use PyQt spinboxes to set parameters for a SolidPython program which
# generates OpenSCAD code for a gear.  jiw 20 March 2019.

# Whenever you click Produce, this program will output a file
# 'gear1.scad' with .scad code modeling an object.  If AutoProd is
# green (turned on) Produce will occur whenever you change a value in
# a spinbox or click Produce.

import sys
from math import sqrt, pi, sin, cos
from PyQt5.QtWidgets import QGridLayout, QSpinBox, QLabel
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

from solid import circle, color, cube, cylinder, text
from solid import rotate, scad_render_to_file, translate
from solid.utils import up, down, left, right, forward, back
from solid.utils import Black, Cyan, Green, Red, Magenta

#---------------------------------------------
class CallData:
    '''Provide methods to make callback closures.  All methods of this
    class are @classmethod or @staticmethod items.    '''
    def __init__(self):
        pass
    autoProduce = False
    #---------------------------------------------
    @staticmethod
    def buttonLabels():    return ['Quit', 'Produce', 'AutoProd']
    #---------------------------------------------
    @classmethod
    def makeClickFunc(c, bu,bun):
        return lambda x: c.on_buttonClick(bu, bun)
    #---------------------------------------------
    @classmethod
    def makeSpinBoxFunc(c, base, sl, slN):
        return lambda x: c.on_spinbox(x, widget, sl, slN)
    #---------------------------------------------
    @classmethod
    def on_spinbox(c, v, base, sl, slN):
        '''Handle changes in spinbox values
        
        Params: base = main display widget
        v = new value,   sl = QSpinBox object,   slN = spinbox number
        '''
        ap = base.armParam
        # This a,g,h,m,n,p,s order matches the order in spinsets
        data = [ap.a, ap.g, ap.h, ap.m, ap.n, ap.p, ap.s]
        data[slN] = v
        ap.a, ap.g, ap.h, ap.m, ap.n, ap.p, ap.s = data
        # At any spinbox change, run Produce if AutoProd is on
        if c.autoProduce:  produceOutput(ap)
    #---------------------------------------------
    @classmethod
    def on_buttonClick(c, bu, bun):
        '''Handle buttons like 'Quit','Load','Produce'
        
        Params:
        bu  = button object of button that was clicked
        bun = button number of button that was clicked
        '''
        bt = c.buttonLabels()[bun]
        if   bt=='Quit':      sys.exit()
        elif bt=='Produce':   produceOutput(bu.parentWidget().armParam)
        elif bt=='AutoProd':
            c.autoProduce = not c.autoProduce
            color = 'green' if c.autoProduce else 'khaki'
            bu.setStyleSheet('QPushButton {background-color: %s;}'%color)
        else:
            print ('B{} {} {} click'.format(bun, bt, bu.text()))
#---------------------------------------------
class GearAssembly:
    '''Class for Gear Assembly data.  Data items include:
    a, Pressure angle, degrees
    m, Module, pitch diam/pi, mm*10
    g, Gear Thickness, mm*10, eg 26 -> 2.6 mm thick
    h, Center hole diameter, mm*10
    s, Sun gear tooth count
    t, Planet gear tooth count
    n, Number of planets
    '''        
    def __init__(self, a,g,h,m,n,p,s):
        self.ready = False
        self.a = a
        self.g = g
        self.h = h
        self.m = m
        self.n = n
        self.p = p
        self.s = s

    def makeAssembly(self):
        sun = Gear(self.s, 0, self)
        asm = sun.makeGear(None, self)
        for i in range(self.n):
            plan = Gear(self.p, 1+i, self)
            asm += plan.makeGear(sun, self)
        return asm
    
#---------------------------------------------
class Gear:
    '''Class for one gear, including diameters and static mesh angles.
    The sun gear of an assembly has tooth 0 at mesh angle 0.  The kth
    planet of n planets has a mesh angle 180+fm(s,p,360*k/n), where s
    and p are sun and planet tooth counts, and fm is a function
    placing planet tooth 0 next to sun tooth [s*k/n] such that teeth
    mesh rather than clash.

    Gears have several diameters that are relevant, principally root,
    pitch, and tip diameters.  Drawings should show pitch circles of
    two meshing gears as tangent, their root circles separated by 2.5
    times the module, and their tip circles overlapped by twice the
    module.  At the pitch circle, tooth-to-tooth distance equals the
    module.  Hence, pitch circle circumference is an integer multiple
    of module.    '''
        
    def __init__(self, nT, pN, ap):
        '''Compute diameters and offsets for one gear.  It has nT teeth.  It
        is planet number pN if pN > 0, else it is the sun gear of an
        assembly.  Other data is in ap,
        a GearAssembly object.
        '''
        modul, sT, pT, nplanets = ap.m/10.0, ap.s, ap.p, ap.n
         # Compute pitch diameter from tooth count and module
        self.pd = nT * modul    # Gear pitch diameter, pd
        self.nT = nT
        # Compute root and tip diameters - per following:
        # https://khkgears.net/new/gear_knowledge/abcs_of_gears-b/basic_gear_terminology_calculation.html
        self.td = self.pd + 2  *modul # Gear tip diameter,  td
        self.rd = self.pd - 2.5*modul # Gear root diameter, rd
        loca = self.loca = (2*pi*(pN%nplanets))/nplanets # Line of centers angle, radians
        self.sma = 0
        def d(a): return a*180/pi
        if pN > 0:
            pDel = 2*pi/pT           # Angle between planet teeth
            sDel = 2*pi/sT           # Angle between sun teeth
            k = int(loca/sDel)       # Number of sun teeth to skip
            ta = k*sDel + sDel/2     # target angle
            self.sma = ta + pi if ta < pi else ta - pi
            print ('d {:6.2f}   k {:2}   kd {:6.2f}   la {:6.2f}   sa {:7.2f} e {:7.2f}'.format(d(sDel), k, d(k*sDel), d(loca), d(self.sma), self.sma/sDel))
        
    def makeGear(self, sg, ap):
        '''Produce CSG for one gear.  Parameter sg is None if this will be a
        sun gear, else is the sun Gear object.  Other data is in ap, a
        GearAssembly object.        '''
        hh, h0, h1, h2, h3 = 0.1, 1, 1.1, 1.2, 1.3
        nT, tLen, tRad = self.nT, (self.td-self.rd)*.3, self.rd/2
        asm  = cylinder(d=self.rd, h=h2)
        for i in range(nT):
            tAngle = self.sma + 2*i*pi/nT
            c = rotate(tAngle*180/pi)(cube([tLen, tLen/(6+i), h2]))
            dx, dy = tRad*cos(tAngle), tRad*sin(tAngle)
            asm += translate([dx, dy, 0])(c)
        asm = color(Black)(asm) + color(Magenta)(cylinder(d=self.pd, h=h1))
        centerHole = down(hh)(cylinder(d=ap.h/10, h=h3))
        asm = (asm + color(Green)(cylinder(d=self.td, h=h0))) - centerHole
        if sg:
            cDist = (sg.pd + self.pd)/2
            self.cx, self.cy = cDist*cos(self.loca), cDist*sin(self.loca)
            return translate([self.cx, self.cy, 0])(asm)
        else:
            self.cx, self.cy = 0, 0
            return asm    
#---------------------------------------------
# ref: "Public Domain
# in here, adapt some of the code from:
# Parametric Involute Spur Gear (and involute helical gear and
# involute rack) version 1.1 by Leemon Baird, 2011, Leemon@Leemon.com


#---------------------------------------------
def produceOutput(ap):
    if not ap.ready: return
    asm = ap.makeAssembly()
    cylSegments, version, title = 90, 1, 'gear'
    cylSet_fn = '$fn = {};'.format(cylSegments)
    asmFile = '{}{}.scad'.format(title, version)
    scad_render_to_file(asm, asmFile, file_header=cylSet_fn, include_orig_code=False)
    print ('Wrote scad code to {}'.format(asmFile))
#---------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)    # Create a Qt application, first thing
    widget = QWidget()
    widget.setWindowTitle('Some design')
    widget.setStyleSheet('QGridLayout {background-color: khaki; color: lightcyan}')
    widget.setStyleSheet('QPushButton {background-color: khaki;}')
    panes = QGridLayout(widget)
    a,g,h,m,n,p,s  = 20, 25, 31, 23, 5, 7, 13
    aarm = GearAssembly(a,g,h,m,n,p,s)
    # Make pushbuttons
    PBNames = CallData.buttonLabels()
    wib, hib, mb = 110, 60, 15
    for k, txt in enumerate(PBNames):
        bu = QPushButton(txt)
        panes.addWidget(bu, 0, k) # Button in row 0, column k
        bu.clicked.connect(CallData.makeClickFunc(bu, k))
        if txt=='AutoProd':
            CallData.on_buttonClick(bu, k) # Toggle AutoProd on

    widget.armParam = aarm      # Produce needs a link to aarm
    slo, shi = 0, 999
    spinsets = [
        # Range; Initial Value; VarName; and Legend for each spinbox
        [slo, shi, a, 'a', 'Pressure angle, degrees'],
        [slo, shi, g, 'g', 'Gear thickness,   mm*10'],
        [slo, shi, h, 'h', 'Center hole diam, mm*10'],
        [slo, shi, m, 'm', 'Module, diam/#t,  mm*10'],
        [slo, shi, n, 'n', 'Number of planets'],
        [slo, shi, p, 'p', 'Planet gear tooth count'],
        [slo, shi, s, 's', 'Sun gear tooth count'],
        ]
    ro = 2
    for sn, sset in enumerate(spinsets):
        rlo, rhi, rini, varn, legend = sset
        sb = QSpinBox()
        sb.valueChanged.connect(CallData.makeSpinBoxFunc(widget, sb, sn))
        sb.setRange(rlo, rhi)
        sb.setValue(rini)
        # Add legend, spinbox, and var name widgets into QGridLayout
        # Starting at cell (ro,0), use 1 row, 2 cols for legend
        panes.addWidget(QLabel(legend), ro, 0, 1, 2)
        panes.addWidget(sb, ro, 2)             # spinbox in cell (ro,2)
        panes.addWidget(QLabel(varn),   ro, 3) # var-name in cell (ro,3)
        ro += 1

    aarm.ready = True           # Now allow Produce to occur
    widget.show()               # Show the window
    app.exec_()                 # Run the app
