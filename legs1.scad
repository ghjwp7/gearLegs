$fn = 90;

union() {
	union() {
		difference() {
			difference() {
				intersection() {
					translate(v = [0, -40, 0]) {
						cylinder(h = 1, r = 60);
					}
					translate(v = [0, 100, 0]) {
						cylinder(h = 1, r = 110);
					}
				}
				translate(v = [-242.4028853967, -7.6945250507, -0.0500000000]) {
					cube(size = [220, 22.2858983472, 1.1000000000]);
				}
			}
			translate(v = [41.0982751437, -2.0339736569, -0.0500000000]) {
				cube(size = [220, 4.8230074239, 1.1000000000]);
			}
		}
		color(c = [0, 1, 0]) {
			translate(v = [40, 0.6926949609, -0.0500000000]) {
				cylinder(h = 1.1000000000, r = 2.9395458905);
			}
		}
	}
	color(c = [1, 0, 0]) {
		translate(v = [-20, 3.8565585249, -0.0500000000]) {
			cylinder(h = 1.1000000000, r = 11.7983638696);
		}
	}
}