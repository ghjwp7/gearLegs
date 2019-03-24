#!/usr/bin/env python3

# tooth.py, makes a gear of k teeth by rotating a tooth profile k
# times to get a polygon outline, then extruding that polygon.  Note,
# in openscad preview mode, some polyhedron sides may look
# transparent; if so, press f6 to render the gear.

# Note, this code does not yet radius (or fillet) the base angles of
# the gear teeth.

# Ref: https://www.engineersedge.com/gears/externalgears.pdf
# Ref: https://www.sdp-si.com/D805/D805_PDFS/Technical/8050T034.pdf
# Also see: https://www.thingiverse.com/thing:1919326 by Greg Frost

from solid import linear_extrude, cylinder, polygon, scad_render_to_file
from math import sqrt, pi, sin, cos, atan2

def rad(deg): return deg*pi/180.0
def deg(rad): return rad*180.0/pi

def spurGear(nT=12, gmodule=3, holeDiam=6.35, gthick=4, pressAngle=28):
    '''Return CSG of a cylindrical spur gear having center-hole
    diameter=holeDiam, thickness=gthick, module=gmodule, pressure
    angle=pressAngle, #teeth=nT.  In more detail:

    module: A metric gear's module (mm) is its reference diameter (its
    pitch diameter) divided by its tooth count.  For example, a
    module-3 gear with 30 teeth is 90 mm across.  "Circular pitch",
    equal to pi*module, is tooth-to-tooth circumferential distance at
    pitch diameter.  "Diametral pitch" is the number of tooth
    intervals per inch at pitch diameter.

    Pressure angle (degrees) is profile angle at pitch diameter; also
    equals angle between normal to tooth surface and angle of force
    when gear contact point is at the pitch diameter.

    Coefficient of profile shift: [Not in this version; may add in
    future] Use 0 if #teeth is large; as #teeth gets smaller, use a
    larger shift to avoid tooth undercutting.  See Table 4, p. T-40 in
    SDP-SI 8050T034.pdf

    '''
    cyl = cylinder(h=gthick*1.1, d=holeDiam, center=True)
    nTeeth  = float(nT)
    gmodule = float(gmodule)
    pitchDiam = gmodule * nTeeth
    baseDiam = pitchDiam * cos(rad(pressAngle))
    rootDiam = pitchDiam - 2.5 * gmodule
    tipDiam  = pitchDiam + 2 * gmodule
    #addendum, dedendum  = gmodule, gmodule*1.25
    rp, rb, rr, rt = pitchDiam/2., baseDiam/2., rootDiam/2., tipDiam/2.
    rm = max(rb, rr)
    #print ('rp {:8.2f}   rb {:8.2f}   rr {:8.2f}  rt {:8.2f}'.format(rp, rb, rr, rt)) 

    def round3(v):  return int(1000*v+0.5)/1000.0
    def rotated(pl, ra):
        '''Return point list pl, rotated by ra radians, rounded
        to a few decimal places for compactness.  '''
        s, c = sin(ra), cos(ra)
        return [[round3(x*c-y*s), round3(x*s+y*c)] for x,y in pl]

    def invo(r): # Compute involute at radius r, return its (x,y)
        ia = sqrt((r/rb)**2 - 1) # Radians for involute to reach radius r
        ix = rb*(cos(ia) + ia*sin(ia))
        iy = rb*(sin(ia) - ia*cos(ia)) # x,y coords of point on involute 
        return (ix,-iy)

    # Make set of points for outline of one tooth along +y axis
    # Compute point at pitch radius, for use as alignment angle  
    x, y = invo(rp)           # (x,y) when involute crosses pitch circle
    alan = atan2(-y, x)        # angle from origin to x,y
    tang = pi/nTeeth          # angle subtended by one tooth or one gap
    htan = tang/2             # half-tooth angle: 1/4 of pitch angle
    pang = 2*tang             # angle subtended by one tooth + one gap
    nradii = 6
    rstep = (rt-rm)/float(nradii)
    points = [invo(rm + j*rstep) for j in range(nradii)]
    
    # Rotate half-tooth for proper tooth thickness at pitch circle
    points = rotated(points, alan+htan)
    #print ('Half-tooth points after adjust: ',points)
    # Mirror tooth top side to bottom
    bepo = points + [[x,-y] for x,y in reversed(points)]
    repo = list(reversed(bepo))   # draw up not down
    polyli = []
    for i in range(nT):
        polyli +=  rotated(repo, i*pang)
    return linear_extrude(gthick, True)(polygon(polyli)) - cyl

#---------------------------------------------
if __name__ == '__main__':
    from sys import argv
    arn = 0
    arn+=1; nT  = int(argv[arn]) if len(argv)>arn else 20
    arn+=1; gM  = float(argv[arn]) if len(argv)>arn else 3.0
    print ('Making spurGear(nT:{}, gM:{})'.format(nT,gM))
    g = spurGear(nT, gM)
    scad_render_to_file(g, 'tooth.scad', include_orig_code=False)
    #print ('Wrote scads to tooth.scad')
