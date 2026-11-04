import numpy as np
import matplotlib.pyplot as plt
from sub_shapes import Ovoid, rho_water, g

# THIS MODEL IS SUBJECT TO CHANGE BASED ON FIN CALCS FROM HW AND HZ

class CuttlefishRobot:
    def __init__(self, length=0.9, width=0.3, height=0.2):
        self.hull = Ovoid(length, width, height)
        self.mass = rho_water * self.hull.volume
        
        a, b, c = self.hull.dims[0]/2, self.hull.dims[1]/2, self.hull.dims[2]/2
        self.I = np.diag([
            0.2 * self.mass * (b**2 + c**2),
            0.2 * self.mass * (a**2 + c**2),
            0.2 * self.mass * (a**2 + b**2)
        ])
        
        self.fin_span = width * 0.8
        self.fin_width = 0.1
        self.Cd_fin = 1.1
        self.state = np.zeros(12)

    def calculate_fin_thrust(self, freq, amp, wavelength):
        k = 2 * np.pi / wavelength
        omega = 2 * np.pi * freq
        
        x = np.linspace(0, self.fin_span, 50)
        t = np.linspace(0, 2*np.pi/omega, 20)
        
        # Use broadcasting to compute all x and t at once
        # X shape (50, 1), T shape (1, 20)
        X, T = np.meshgrid(x, t, indexing='ij')
        
        # Local slope: tan(theta) = amp * k * cos(kx - wt)
        slope = amp * k * np.cos(k*X - omega*T)
        theta = np.arctan(slope)
        
        # Local vertical velocity: vz = -amp * omega * cos(kx - wt)
        v_z_fin = -amp * omega * np.cos(k*X - omega*T)
        
        # F_normal = 0.5 * rho * Cd * v_z^2 * Area
        # Area per slice = fin_width * dx
        dx = x[1] - x[0]
        f_normal = 0.5 * rho_water * self.Cd_fin * (v_z_fin**2) * (self.fin_width * dx)
        
        # Thrust (X) = F_normal * sin(theta)
        thrust_matrix = f_normal * np.sin(theta)
        
        # Sum over X and average over T
        avg_thrust_x = np.sum(np.mean(thrust_matrix, axis=1))
        
        return np.array([avg_thrust_x, 0, 0])

    def get_dynamics(self, freq, amp, wavelength):
        thrust = self.calculate_fin_thrust(freq, amp, wavelength)
        v_vec = self.state[3:6]
        v_mag = np.linalg.norm(v_vec)
        drag_mag = self.hull.drag(v_mag)
        drag_vec = -drag_mag * (v_vec / (v_mag + 1e-6))
        f_net = thrust + drag_vec
        return f_net / self.mass

    def step(self, dt, freq, amp, wavelength):
        accel = self.get_dynamics(freq, amp, wavelength)
        self.state[3:6] += accel * dt
        self.state[0:3] += self.state[3:6] * dt
