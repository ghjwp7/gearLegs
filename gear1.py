#!/usr/bin/env python3

# Use PyQt spinboxes to set parameters for a SolidPython program which
# generates OpenSCAD code for a gear.  jiw 20 March 2019.

# Whenever you click Produce, this program will output a file
# 'gear1.scad' with .scad code modeling an object.  If AutoProd is
# green (turned on) Produce will occur whenever you change a value in
# a spinbox or click Produce.

import sys
from math import sqrt, pi
from PyQt5.QtWidgets import QGridLayout, QSpinBox, QLabel
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

from solid import circle, color, cube, cylinder, text
from solid import scad_render_to_file, translate
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
        # This p s t q u w order matches the order in spinsets
        data = [ap.p, ap.s, ap.t, ap.q, ap.u, ap.w]
        data[slN] = v
        ap.p, ap.s, ap.t, ap.q, ap.u, ap.w = data
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
class GearParams:
    '''Class for gear assembly data.  Data items include:
    p, Pressure angle, degrees
    s, Module, mm 
    t, Thickness, mm
    q, Center gear tooth count
    u, Planet gear tooth count
    w, Number of planets
    [v0 only draws the center gear]

    Gears have several diameters that are relevant, principally root,
    pitch, and tip diameters.  Drawings should show pitch circles of
    two meshing gears as tangent, their root circles separated by 2.5
    times the module, and their tip circles overlapped by twice the
    module.  At the pitch circle, tooth-to-tooth distance equals the
    module.  Hence, pitch circle circumference is an integer multiple
    of module.
    '''
        
    def __init__(self, p,q,s,t,u,w):
        self.ready = False
        self.p = p
        self.q = q
        self.s = s
        self.t = t
        self.u = u
        self.w = w
        #print ('p {}  q {}  s {}  t {}  u {}  w {}'.format(p,q,s,t,u,w))
        modul, cteeth, pteeth, pangle = s, q, u, p
         # Compute center-gear pitch diameter from tooth count
        self.cdp = (cteeth * modul)/pi
        # Compute root and tip diameters - per following:
        # https://khkgears.net/new/gear_knowledge/abcs_of_gears-b/basic_gear_terminology_calculation.html
        self.dt = self.cdp + 2  *modul # Gear tip diameter
        self.dr = self.cdp - 2.5*modul # Gear root diameter

    def makeGear(self):
        print ('Make gear')
        ccdr = color(Black)(cylinder(d=self.dr, h=1.2))
        ccdp = color(Magenta)(cylinder(d=self.cdp, h=1.1))
        cctp = color(Green)(cylinder(d=self.dt, h=1.0))
        return ccdr+ccdp+cctp
    
#     Cyan, Green, Red, Magenta
#---------------------------------------------
def produceOutput(ap):
    if not ap.ready: return
    asm = ap.makeGear()
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
    p,s,t,q,u,w  = 20, 2, 3, 32, 32, 1
    aarm = GearParams(p,q,s,t,u,w)
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
        [slo, shi, p, 'p',  'Pressure angle, degrees'],
        [slo, shi, s, 's',  'Module'],
        [slo, shi, t, 't',  'Thickness'],
        [slo, shi, q, 'q',  'Center gear tooth count'],
        [slo, shi, u, 'u',  'Planet gear tooth count'],
        [slo, shi, w, 'w',  'Number of planets'],
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
