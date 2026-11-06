import numpy as np
from cuttlefish_model import CuttlefishRobot

def find_terminal_velocity(freq, amp, wavelength=0.1):
    robot = CuttlefishRobot()
    dt = 0.1
    # Simulate for 100 seconds to reach steady state
    for _ in range(1000):
        robot.step(dt, freq, amp, wavelength)
    return robot.state[3]

frequencies = [1.0, 1.5, 2.0, 2.5, 3.0]
amplitudes = [0.01, 0.02, 0.03]

print(f"{'Freq \\ Amp':<12} | {'0.01m':<10} | {'0.02m':<10} | {'0.03m':<10}")
print("-" * 45)
for f in frequencies:
    row = []
    for a in amplitudes:
        v_term = find_terminal_velocity(f, a)
        row.append(f"{v_term:.3f} m/s")
    print(f"{f' {f} Hz':<12} | {' | '.join(row)}")
