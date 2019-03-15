#!/usr/bin/env python

# Use PyQt spinboxes to set parameters for a SolidPython program which
# generates OpenSCAD code for a leg assembly.  jiw 14 March 2019.

# Whenever you click Produce, this program will output a file
# 'legs1.scad' with .scad code modeling an object.  If AutoProd is
# green (turned on) Produce will occur whenever you change a value in
# a spinbox or click Produce.

# Note, although openscad's 2nd orthogonal view shows the y axis as
# positive-up on the screen, y axis coordinates seem to act
# oppositely.  Result: odd spinbox labels like "bigger=lower" and
# "neg. thickness above origin" in the application window, and in
# comments, "top" and "up" referring to higher on the screen and
# more-negative y values.

import sys
from math import sqrt
from PyQt5.QtWidgets import QGridLayout, QSpinBox, QLabel
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

from solid import color, cube, cylinder, text
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
class ArmParams:
    '''Class with data and methods to make an oval arm.

    Let C(r,x,y) stand for a circle with radius r and center (x,y).
    Also, let p > q > 0 > s > t, and u > 0 > w. In this program, an
    Arm is a truncated-crescent shape, bounded by arcs of four
    circles: an upper arc, part of C(p-s, 0, p); a lower arc, part of
    C(q-t, 0, t); a left arc, part of C(rl, w, vl); and a right arc,
    part of C(rr, u, vr).  For the left and right arcs, rr, rl, vr, vl
    are chosen so that the left and right circles are tangent to the
    lens formed by the intersection of the upper and lower circles.'''
    def __init__(self, p,q,s,t,u,w):
        self.ready = False
        self.p = p
        self.q = q
        self.s = s
        self.t = t
        self.u = u
        self.w = w
        #print ('p {}  q {}  s {}  t {}  u {}  w {}'.format(p,q,s,t,u,w))

    def solveArcArc(self, p,q,s,t,u):
        '''Solve for a circle R tangent to two arcs C1 and C2.  Return radius,
        v, tphi, tplo, ie, the radius of R, its center y coordinate, and
        two tangency points, tp hi and tp lo.

        The arcs are portions of circles with radii r1 = p-s and r2 =
        q-t, with centers at (0,p) and (0,t) respectively, while
        circle R has radius r and center (u,v).  We are given p, q, s,
        t, u with p > q > 0 > s > t.  r and v are unknowns.  Method:
        Let radii from (0,p) and (0,t) intersect at (u,v).  Let a and
        b be the lengths of the radii left over after intersection.
        So a = r1 - sqrt(u^2+(p-v)^2) and b = r2 - sqrt(u^2+(t-v)^2).
        We want a(v0) = b(v0).  We solve using Newton iteration then
        compute r = a(v0).  Note, if f(v) = c - sqrt(u^2+(d-v)^2),
        then f'(v) = (v-d)/sqrt(u^2+(d-v)^2). Note, closed-form
        (non-iterative) solutions exist but seem complicated; see eg
        <https://math.stackexchange.com/q/3145832>        '''
        r1, r2, uu = p-s, q-t, u*u
        r1s, r2s = r1**2, r2**2
        # Make initial estimate of v, halfway between y1(u) and y2(u)
        if r1s<uu or r2s<uu: return 5,0 # u too big means no solution
        y1u, y2u = p - sqrt(r1s-uu), t + sqrt(r2s-uu)
        v = (y1u+y2u)/2
        for i in range(9):     # Usually takes about 3 iterations
            av = sqrt(uu+(p-v)**2);  ar=r1-av;  adf=(v-p)/av
            bv = sqrt(uu+(t-v)**2);  br=r2-bv;  bdf=(v-t)/bv
            if abs(adf-bdf) < 1e-5: break # Avoid div by 0
            v = v + (ar-br)/(adf-bdf)
            if abs(ar-br) < 1e-12: break
        # Compute intersection points by similar triangles
        r = ar; n1, n2 = r1/(r1-r), r2/(r2-r)
        tphi = (u*n1, p-(p-v)*n1)
        tplo = (u*n2, t+(v-t)*n2)
        return ar, v, tphi, tplo

    def getOblongArm(self):
        '''Return a SolidPython object modeling an oblong arm (per specs in
        ArmParams object) bounded by four arcs of circles.        '''
        eps =  0.01
        p,q,s,t,u,w = self.p, self.q, self.s, self.t, self.u, self.w
        r1, r2 = p-s, q-t
        domis, chi, dhi = 2*max(r1,r2), 1.1, -0.05
        arc1 = back(r1+s)(cylinder(r=r1, h=1))
        arc2 = back(q-r2)(cylinder(r=r2, h=1))
        rl, vl, p1, p2 = self.solveArcArc(p,q,s,t,u)
        rr, vr, p3, p4 = self.solveArcArc(p,q,s,t,w)
        rightcircle = color(Green)(translate([u,-vl,dhi])(cylinder(r=rl,h=chi)))
        leftcircle = color(Red) (translate([w,-vr,dhi])(cylinder(r=rr,h=chi)))
        yrhi, yrlo, ylhi, yllo = p1[1], p2[1], p3[1], p4[1]
        xr, xl = min(p1[0], p2[0]), max(p3[0], p4[0])
        dominol = translate([xl-domis,-yllo, dhi])(cube([domis,yllo-ylhi,chi]))
        dominor = translate([xr,      -yrlo, dhi])(cube([domis,yrlo-yrhi,chi]))
        return (arc1*arc2-dominol-dominor) + rightcircle + leftcircle
#---------------------------------------------
def produceOutput(ap):
    if not ap.ready: return
    asm = ap.getOblongArm()
    cylSegments, version, title = 90, 1, 'legs'
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
    p,q,s,t,u,w  = 40, 10, -30, -100, 40, -20
    aarm = ArmParams(p,q,s,t,u,w)
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
    spinsets = [
        # Range; Initial Value; VarName; and Legend for each spinbox
        [0,  999, p, 'p',  'Center 1 (bigger=lower)'],
        [-999, 0, s, 's',  'Circle 1 neg. thickness above origin'],
        [-999, 0, t, 't',  'Center 2 (bigger neg.=higher)'],
        [0,  999, q, 'q',  'Circle 2 thickness below origin'],
        [0,  999, u, 'u',  'Right-end distance from origin'],
        [-999, 0, w, 'w',  'Left-end neg. distance from origin'],
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
