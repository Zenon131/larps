"""
Force models for three candidate hull shapes.

All shapes are scaled to the same displaced volume as the box
(4.50 ft³), so the comparison shows what each shape costs in size,
drag, and crush load for equal payload.
"""

import numpy as np
import matplotlib.pyplot as plt

FT2_TO_M2 = 0.09290304
FT3_TO_M3 = 0.02831685
P_ATM = 101325

rho_water = 1025 # seawater kg/m^3
g = 9.81

# Envelope (m): the box's size, and the starting proportions for the rest
L, W, H = 3.0*0.3048, 1.0*0.3048, 1.5*0.3048

# NACA 4-digit upper surface, x as fraction of chord, result in fraction of chord
def naca_yt(x, t_over_c):
    return 5 * t_over_c * (
        0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4
    )


class RectangularPrism:
    """Blunt box: most internal volume, worst drag."""

    name = "Rectangular prism"
    cd = 1.05 # flat face, handbook value

    def __init__(self, l, w, h):
        self.l, self.w, self.h = l, w, h

    @property
    def volume(self):
        return self.l * self.w * self.h

    @property
    def wetted_area(self):
        return 2 * (self.w*self.h + self.l*self.h + self.l*self.w)

    @property
    def frontal_area(self):
        return self.w * self.h

    @property
    def cb_from_nose(self):
        return self.l / 2

    @property
    def dims(self):
        return self.l, self.w, self.h

    def drag(self, v, alpha_deg=0.0):
        return 0.5 * rho_water * v**2 * self.cd * self.frontal_area

    def lift(self, v, alpha_deg=0.0):
        return 0.0


class Ovoid:
    """Ellipsoid: slippery, but gives up a lot of volume."""

    name = "Ovoid (ellipsoid)"
    cd = 0.15 # streamlined body, handbook value

    def __init__(self, l, w, h):
        self.a, self.b, self.c = l/2, w/2, h/2 # semi-axes

    @property
    def volume(self):
        return 4/3 * np.pi * self.a * self.b * self.c

    @property
    def wetted_area(self):
        # Knud Thomsen's approximation (no exact formula for ellipsoids)
        p = 1.6075
        s = self.a**p*self.b**p + self.a**p*self.c**p + self.b**p*self.c**p
        return 4 * np.pi * (s/3) ** (1/p)

    @property
    def frontal_area(self):
        return np.pi * self.b * self.c

    @property
    def cb_from_nose(self):
        return self.a

    @property
    def dims(self):
        return 2*self.a, 2*self.b, 2*self.c

    def drag(self, v, alpha_deg=0.0):
        return 0.5 * rho_water * v**2 * self.cd * self.frontal_area

    def lift(self, v, alpha_deg=0.0):
        return 0.0


class WingBody:
    """Extruded airfoil: barely any drag at level trim, plus lift when pitched."""

    name = "Wing body"
    cd0 = 0.02        # thick section profile drag
    oswald = 0.7      # low AR hurts efficiency
    stall_deg = 20.0  # low-AR bodies stall late

    def __init__(self, l, w, h):
        self.chord = l
        self.span = w
        self.tc = h / l # thickness ratio (a chunky 0.5 here)
        self.x = np.linspace(1e-4, 1.0, 2000)

    @property
    def _profile(self):
        # (x, thickness) sampled along the chord, in meters
        return self.x * self.chord, naca_yt(self.x, self.tc) * self.chord

    @property
    def _section_area(self):
        xc, yt = self._profile
        return 2 * np.trapezoid(yt, xc)

    @property
    def planform(self):
        return self.chord * self.span

    @property
    def aspect_ratio(self):
        return self.span**2 / self.planform

    @property
    def volume(self):
        return self._section_area * self.span

    @property
    def wetted_area(self):
        xc, yt = self._profile
        slope = np.gradient(yt, xc)
        perimeter = 2 * np.trapezoid(np.sqrt(1 + slope**2), xc)
        return perimeter * self.span + 2 * self._section_area

    @property
    def frontal_area(self):
        # edge-on silhouette
        return self._section_area

    @property
    def cb_from_nose(self):
        xc, yt = self._profile
        return np.trapezoid(xc * yt, xc) / np.trapezoid(yt, xc)

    @property
    def dims(self):
        return self.chord, self.span, self.tc * self.chord

    def _cl(self, alpha_deg):
        # finite-wing corrected lift slope, no fancy stall model
        alpha = np.radians(min(alpha_deg, self.stall_deg))
        cl_alpha = 2*np.pi * self.aspect_ratio / (self.aspect_ratio + 2)
        return cl_alpha * alpha

    def _cd(self, alpha_deg):
        return self.cd0 + self._cl(alpha_deg)**2 / (np.pi * self.aspect_ratio * self.oswald)

    def drag(self, v, alpha_deg=0.0):
        return 0.5 * rho_water * v**2 * self._cd(alpha_deg) * self.planform

    def lift(self, v, alpha_deg=0.0):
        return 0.5 * rho_water * v**2 * self._cl(alpha_deg) * self.planform


# Helpers -------------------------------------------------------------

def crush_force(shape, depth_m):
    # absolute pressure over the whole wetted surface, same method as sub_math
    p_abs = P_ATM + rho_water * g * depth_m
    return p_abs * shape.wetted_area

def restoring_torque(shape, pitch_deg, cg_below_cb=0.05):
    # self-righting moment, CG hung 5 cm below the CB (neutral buoyancy assumed)
    buoyancy = rho_water * g * shape.volume
    return buoyancy * cg_below_cb * np.sin(np.radians(pitch_deg))

def scaled_to_volume(make_shape, target_v):
    # uniform scaling: volume grows as k^3, proportions are preserved
    base = make_shape(L, W, H)
    k = (target_v / base.volume) ** (1/3)
    return make_shape(L*k, W*k, H*k), k


# Comparison ----------------------------------------------------------

# Everyone carries the box's displaced volume, so payload is equal
V_REF = RectangularPrism(L, W, H).volume
SHAPES = [scaled_to_volume(make, V_REF) for make in (RectangularPrism, Ovoid, WingBody)]

print("=== SHAPE FORCE MODELS (equal volume) ===")
print(f"Every shape displaces {V_REF:.3f} m³ ({V_REF/FT3_TO_M3:.2f} ft³), "
      f"neutral mass {rho_water*V_REF:.1f} kg\n")

for s, k in SHAPES:
    l, w, h = s.dims
    print(s.name)
    print(f"  Scale vs envelope:   x{k:.2f}")
    print(f"  Size (L x W x H):    {l/0.3048:.2f} x {w/0.3048:.2f} x {h/0.3048:.2f} ft")
    print(f"  Wetted area:         {s.wetted_area:.2f} m² ({s.wetted_area/FT2_TO_M2:.1f} ft²)")
    print(f"  Frontal area:        {s.frontal_area:.3f} m²")
    print(f"  CB from nose:        {s.cb_from_nose:.3f} m ({s.cb_from_nose/l*100:.0f}% of length)")
    print(f"  Crush force @10 m:   {crush_force(s, 10)/1000:.0f} kN")
    for v in (0.5, 1.0, 2.0):
        print(f"  Drag @{v:.1f} m/s:         {s.drag(v):7.1f} N")
    print(f"  Lift @1 m/s, 5 deg:  {s.lift(1.0, 5.0):.1f} N")
    print(f"  Lift @1 m/s, 10 deg: {s.lift(1.0, 10.0):.1f} N")
    print()

print("Self-righting torque (CG 5 cm below CB, 10 deg pitch):")
for s, _ in SHAPES:
    print(f"  {s.name:<20} {restoring_torque(s, 10):.1f} N·m")
print("  -> identical: with equal volume it only depends on the CG-CB gap")

# Drag vs speed -------------------------------------------------------

speeds = np.linspace(0.1, 2.0, 100)
plt.figure()
for s, _ in SHAPES:
    plt.plot(speeds, [s.drag(v) for v in speeds], label=s.name)
plt.xlabel('Speed (m/s)')
plt.ylabel('Drag (N)')
plt.title('Drag vs speed, equal volume')
plt.legend()
plt.grid(True)
plt.show()