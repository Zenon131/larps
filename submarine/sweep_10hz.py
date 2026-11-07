import numpy as np
from cuttlefish_model import CuttlefishRobot
from sub_shapes import rho_water

def simulate_terminal_state(freq, amp, wavelength=0.1):
    robot = CuttlefishRobot()
    dt = 0.1
    # Simulate until velocity stabilizes
    for _ in range(1000):
        robot.step(dt, freq, amp, wavelength)
    
    v_term = robot.state[3]
    
    # Power calculation at terminal state
    omega = 2 * np.pi * freq
    k = 2 * np.pi / wavelength
    x = np.linspace(0, robot.fin_span, 50)
    t = np.linspace(0, 2*np.pi/omega, 20)
    X, T = np.meshgrid(x, t, indexing='ij')
    v_z_fin = -amp * omega * np.cos(k*X - omega*T)
    
    dx = x[1] - x[0]
    area_strip = robot.fin_width * dx
    p_inst = 0.5 * rho_water * robot.Cd_fin * np.abs(v_z_fin**3) * area_strip
    avg_power = np.sum(np.mean(p_inst, axis=1)) * 2 # Two fins
    
    return v_term, avg_power

frequencies = [1.0, 2.0, 4.0, 6.0, 8.0, 10.0]
amplitudes = [0.01, 0.02, 0.03]

print(f"{'Freq':<8} | {'Amp':<8} | {'V_term (m/s)':<15} | {'Power (W)':<10}")
print("-" * 45)
for f in frequencies:
    for a in amplitudes:
        v, p = simulate_terminal_state(f, a)
        print(f"{f' {f} Hz':<8} | {f' {a}m':<8} | {v:<15.3f} | {p:<10.2f}")
