import numpy as np
from cuttlefish_model import CuttlefishRobot
from sub_shapes import rho_water

def calculate_average_power(freq, amp, wavelength=0.1):
    robot = CuttlefishRobot()
    
    # Wave parameters
    k = 2 * np.pi / wavelength
    omega = 2 * np.pi * freq
    
    # Space and time discretization
    x = np.linspace(0, robot.fin_span, 50)
    t = np.linspace(0, 2*np.pi/omega, 20)
    X, T = np.meshgrid(x, t, indexing='ij')
    
    # Local vertical velocity: vz = -amp * omega * cos(kx - wt)
    v_z_fin = -amp * omega * np.cos(k*X - omega*T)
    
    # Instantaneous Power per slice = Force * Velocity
    # P = (0.5 * rho * Cd * v_z^2 * Area) * v_z
    dx = x[1] - x[0]
    area_strip = robot.fin_width * dx
    
    # P_inst = 0.5 * rho * Cd * |v_z|^3 * Area
    p_inst = 0.5 * rho_water * robot.Cd_fin * np.abs(v_z_fin**3) * area_strip
    
    # Average over time (axis 1) and sum over space (axis 0)
    avg_power = np.sum(np.mean(p_inst, axis=1))
    
    # Since we have two fins (port and starboard)
    return avg_power * 2

frequencies = [1.0, 1.5, 2.0, 2.5, 3.0]
amplitudes = [0.01, 0.02, 0.03]

print(f"{'Freq \\ Amp':<12} | {'0.01m':<10} | {'0.02m':<10} | {'0.03m':<10}")
print("-" * 45)
for f in frequencies:
    row = []
    for a in amplitudes:
        p_avg = calculate_average_power(f, a)
        row.append(f"{p_avg:.2f} W")
    print(f"{f' {f} Hz':<12} | {' | '.join(row)}")
