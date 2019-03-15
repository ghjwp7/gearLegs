$fn = 90;

union() {
	union() {
		difference() {
			difference() {
				intersection() {
					translate(v = [0, -40, 0]) {
						cylinder(h = 1, r = 70);
					}
					translate(v = [0, 100, 0]) {
						cylinder(h = 1, r = 110);
					}
				}
				translate(v = [-243.6445017525, -7.4287556331, -0.0500000000]) {
					cube(size = [220, 32.2625677500, 1.1000000000]);
				}
			}
			translate(v = [43.3498264779, -1.0979354109, -0.0500000000]) {
				cube(size = [220, 14.2688698742, 1.1000000000]);
			}
		}
		color(c = [0, 1, 0]) {
			translate(v = [40, 6.7143344046, -0.0500000000]) {
				cylinder(h = 1.1000000000, r = 8.5001704160);
			}
		}
	}
	color(c = [1, 0, 0]) {
		translate(v = [-20, 9.1300322100, -0.0500000000]) {
			cylinder(h = 1.1000000000, r = 16.9551127350);
		}
	}
}