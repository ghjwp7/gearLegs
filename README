This directory contains applications using SolidPython to make
OpenSCAD models of mostly-planar parts like gears and legs.

spinboxLegs.py uses PyQt (Python Qt5 API) to set up a GUI window for
inputting via spinboxes (see below) six parameters that control the
shape of a leg, in this case an ovoid shape bounded by four
arcs-of-circles.  Large upper and lower circles intersect to form a
lens; small circles are created in the lens and tangent to it.

The 'Produce' button in the GUI tells the program to write a file,
legs1.scad, using current values of parameters.  If the 'AutoProd'
button has a green background, auto-produce is turned on.  In this
mode, when you change any value, Produce will happen automatically.
If AutoProd is not on, Produce happens only when you click the Produce
button.  Clicking AutoProd toggles the auto-produce setting.

You can view model results using `openscad legs1.scad` or a similar
command.  To get OpenSCAD to automatically refresh its view whenever
the legs1.scad file changes, turn on the "Automatic Reload and
Preview" feature on OpenSCAD's 'Design' tab.  Thereafter, each time
Produce occurs, the file will be reloaded and redrawn -- except that
when file rewrites occur quite rapidly, some of them may be missed.

A spinbox (a QSpinBox Qt widget) as used here has a data entry box for
a number, and up/down arrowheads.  Numbers in specified ranges can be
typed into the box, or the arrowheads can be clicked or held, or
up/down arrows on the keypad can be used to change spinbox contents.
Note, this program sets ranges of 0 to 999 for three boxes, and -999
to 0 for its other three.  If you type digits that are out of range
into a box, nothing happens -- the digits don't echo.

