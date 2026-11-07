import numpy as np
import matplotlib.pyplot as plt
from sub_shapes import Ovoid, rho_water, g

class CuttlefishRobot:
    def __init__(self, length=0.9144, width=0.3048, height=0.3048):
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
        # Wave physics
        k = 2 * np.pi / wavelength 
        omega = 2 * np.pi * freq   
        
        x = np.linspace(0, self.fin_span, 50)
        t = np.linspace(0, 2*np.pi/omega, 20)
        X, T = np.meshgrid(x, t, indexing='ij')
        
        # Local slope (Angle of Attack)
        slope = amp * k * np.cos(k*X - omega*T)
        theta = np.arctan(slope)
        
        # --- STALL LIMIT ---
        # Cap theta at 15 degrees (approx 0.26 rad) to prevent unrealistic lift
        stall_angle = np.radians(15)
        theta_clamped = np.clip(theta, -stall_angle, stall_angle)
        
        # Local vertical velocity
        v_z_fin = -amp * omega * np.cos(k*X - omega*T)
        v_rel = np.sqrt(v_z_fin**2 + self.state[3]**2)
        
        # LIFT-BASED MODEL:
        cl = 2 * np.pi * theta_clamped 
        
        dx = x[1] - x[0]
        ar = self.fin_width / dx
        cd = 0.1 + (cl**2 / (np.pi * ar * 0.7)) 
        
        area_strip = self.fin_width * dx
        
        # F = 0.5 * rho * v^2 * Area * Coeff
        f_lift = 0.5 * rho_water * (v_rel**2) * area_strip * cl
        f_drag = 0.5 * rho_water * (v_rel**2) * area_strip * cd
        
        # Thrust (X) = L*sin(theta) - D*cos(theta)
        thrust_matrix = f_lift * np.sin(theta) - f_drag * np.cos(theta)
        
        avg_thrust_x = np.sum(np.mean(thrust_matrix, axis=1))
        return np.array([avg_thrust_x, 0, 0])

    def get_dynamics(self, freq, amp, wavelength):
        # Multiply by 2 because we have both port and starboard fins
        thrust = self.calculate_fin_thrust(freq, amp, wavelength) * 2
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
