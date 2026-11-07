"""
Submarine preliminary math
"""

import numpy as np
import matplotlib.pyplot as plt

FT2_TO_M2 = 0.09290304 # ft^2 to m^2
FT3_TO_M3 = 0.02831685 # ft^3 to m^3
P_ATM = 101325 # 1 atm (Pa)

# Hull dimensions (ft)
w_1, h_1 = 1.0, 1.5
csa_1 = w_1 * h_1
perimeter_1 = 2 * (w_1 + h_1)

csa_2 = 1.25 * 1.25
csa_3 = 1.5 * 1.5

# Hull length (ft)
sub_length_ft = 3.0

# Total surface area (ft^2)
surface_area_1_ft2 = 2 * csa_1 + perimeter_1 * sub_length_ft

# Gauge pressure (Pa)
def pressure(rho, g, h):
    return rho * g * h

# Absolute pressure (Pa)
def absolute_pressure(rho, g, h, p_atm=P_ATM):
    return pressure(rho, g, h) + p_atm

# Force from pressure (N)
def pressure_force(pressure_pa, area_ft2):
    return pressure_pa * (area_ft2 * FT2_TO_M2)

# Buoyancy force (N)
def buoyant_force(rho, g, volume_ft3):
    volume_m3 = volume_ft3 * FT3_TO_M3
    return rho * g * volume_m3

# Neutral mass (kg)
def neutral_buoyancy_mass(rho, volume_ft3):
    volume_m3 = volume_ft3 * FT3_TO_M3
    return rho * volume_m3

# Net buoyancy (N)
def net_buoyancy(f_buoyant, weight_sub_n):
    return f_buoyant - weight_sub_n

# Constants
rho_water = 1025 # seawater kg/m³
g = 9.81 # m/s^2
h = 0 # m

# Buoyancy (CSA 1)
v_displaced_ft3 = csa_1 * sub_length_ft
f_buoyancy = buoyant_force(rho_water, g, v_displaced_ft3)
m_neutral = neutral_buoyancy_mass(rho_water, v_displaced_ft3)

print("=== BUOYANCY ANALYSIS ===")
print(f"Submarine Length:              {sub_length_ft} ft")
print(f"Displaced Volume (CSA 1):      {v_displaced_ft3:.2f} ft³ ({v_displaced_ft3 * FT3_TO_M3:.2f} m³)")
print(f"Total Buoyant Force:           {f_buoyancy:.2f} N ({f_buoyancy/1000:.2f} kN)")
print(f"Required Neutral Mass:        {m_neutral:.2f} kg ({m_neutral * 2.20462:.2f} lbs)\n")

# Graphing data
depth_list = []
gauge_p_list = []
abs_p_list = []
hydro_force_list = []
crush_force_list = []

print("PRESSURE & FORCE VS DEPTH")
# Depth loop (0-50m)
while h <= 50:
    p_gauge = pressure(rho_water, g, h)
    p_abs = absolute_pressure(rho_water, g, h)
    
    f_hydro = pressure_force(p_gauge, surface_area_1_ft2)
    f_crush = pressure_force(p_abs, surface_area_1_ft2)
    
    depth_list.append(h)
    gauge_p_list.append(p_gauge / 1000.0)    # kPa
    abs_p_list.append(p_abs / 1000.0)        # kPa
    hydro_force_list.append(f_hydro / 1000.0) # kN
    crush_force_list.append(f_crush / 1000.0) # kN
    
    if h % 10 == 0:  # print every 10 meters for conciseness
        print(f"Depth: {h} m")
        print(f"  Gauge Pressure:    {p_gauge:.2f} Pa ({p_gauge/1000:.2f} kPa)")
        print(f"  Absolute Pressure: {p_abs:.2f} Pa ({p_abs/1000:.2f} kPa)")
        print(f"  Hydrostatic Force: {f_hydro:.2f} N ({f_hydro/1000:.2f} kN)")
        print(f"  Buoyancy:          {f_buoyancy:.2f} N ({f_buoyancy/1000:.2f} kN)")
        print(f"  Crushing Force:    {f_crush:.2f} N ({f_crush/1000:.2f} kN)\n")
    
    h += 1

# Pressure/Force vs Depth plot
def graph_pressure_force(depths, hydro_forces, crush_forces):
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Depth (m)')
    ax1.set_ylabel('Hydrostatic Force (kN)', color=color)
    ax1.plot(depths, hydro_forces, color=color, label='Hydrostatic Force (Net)')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:red'
    ax2.set_ylabel('Crushing Force (kN)', color=color)
    ax2.plot(depths, crush_forces, color=color, linestyle='--', label='Crushing Force (Total)')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.title(f'Submarine Force vs. Depth (Surface Area = {surface_area_1_ft2:.1f} ft^2)')
    plt.show()


# =====================================================================
# Vector Math
# =====================================================================

def rotation_matrix_pitch_roll(roll_rad, pitch_roll):
    """Rotation matrix for roll/pitch"""
    phi, theta = roll_rad, pitch_roll
    
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(phi), -np.sin(phi)],
        [0, np.sin(phi), np.cos(phi)]
    ])
    
    R_y = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    
    return R_y @ R_x

def hydrostatic_stability_analysis(mass_kg, volume_ft3, r_cg_body, r_cb_body, pitch_deg=10.0, roll_deg=5.0):
    """Stability analysis (force & torque)"""
    volume_m3 = volume_ft3 * FT3_TO_M3
    
    # Force vectors in world frame (Z-up)
    f_weight_world = np.array([0.0, 0.0, -mass_kg * g])
    f_buoyancy_world = np.array([0.0, 0.0, rho_water * g * volume_m3])
    
    f_net_world = f_weight_world + f_buoyancy_world
    
    # Convert pitch and roll to radians
    phi = np.radians(roll_deg)
    theta = np.radians(pitch_deg)
    R = rotation_matrix_pitch_roll(phi, theta)
    
    # CG and CB vectors in world frame
    r_cg_world = R @ r_cg_body
    r_cb_world = R @ r_cb_body
    
    # Restoring torque: tau = r_cg x W + r_cb x F_b
    tau_weight = np.cross(r_cg_world, f_weight_world)
    tau_buoyancy = np.cross(r_cb_world, f_buoyancy_world)
    tau_restoring_world = tau_weight + tau_buoyancy
    
    # Transform torque into body frame
    tau_restoring_body = R.T @ tau_restoring_world
    
    return f_net_world, tau_restoring_world, tau_restoring_body

def pressure_vector_integration(depth_m, width_ft=1.0, height_ft=1.5, length_ft=3.0):
    """Net force from face pressure integration"""
    w, h_dim, l = width_ft * np.sqrt(FT2_TO_M2), height_ft * np.sqrt(FT2_TO_M2), length_ft * np.sqrt(FT2_TO_M2)
    
    # 6 Faces defined by [center_offset_vector, normal_vector, area]
    faces = [
        # Top face (+z normal)
        (np.array([0, 0, h_dim/2]), np.array([0, 0, 1]), w * l),
        # Bottom face (-z normal)
        (np.array([0, 0, -h_dim/2]), np.array([0, 0, -1]), w * l),
        # Right face (+y normal)
        (np.array([0, np.array(w/2), 0]), np.array([0, 1, 0]), h_dim * l),
        # Left face (-y normal)
        (np.array([0, -w/2, 0]), np.array([0, -1, 0]), h_dim * l),
        # Front face (+x normal)
        (np.array([l/2, 0, 0]), np.array([1, 0, 0]), w * h_dim),
        # Back face (-x normal)
        (np.array([-l/2, 0, 0]), np.array([-1, 0, 0]), w * h_dim),
    ]
    
    f_total_vec = np.zeros(3)
    
    for offset, n_hat, area in faces:
        # z-depth of face center (z is positive downwards for depth)
        z_face = depth_m - offset[2]
        p_gauge = rho_water * g * z_face
        # Force vector on face: F = -P * A * n_hat
        f_face = -p_gauge * area * n_hat
        f_total_vec += f_face
        
    return f_total_vec

def thruster_allocation_matrix(u_thrusters):
    """Thruster force mapping"""
    # Matrix B (6x4)
    # Rows: [Fx, Fy, Fz, Tx, Ty, Tz]
    # Cols: [T_port, T_stbd, T_vert_bow, T_vert_stern]
    d_y = 0.2  # distance from center to port/stbd thrusters (m)
    d_x = 0.4  # distance from center to bow/stern thrusters (m)
    
    B = np.array([
        [1.0,  1.0,  0.0,  0.0],  # Fx (Surge)
        [0.0,  0.0,  0.0,  0.0],  # Fy (Sway)
        [0.0,  0.0,  1.0,  1.0],  # Fz (Heave)
        [0.0,  0.0,  0.0,  0.0],  # Tx (Roll)
        [0.0,  0.0, -d_x,  d_x],  # Ty (Pitch)
        [-d_y, d_y,  0.0,  0.0]   # Tz (Yaw)
    ])
    
    wrench_6dof = B @ u_thrusters
    return wrench_6dof

print("\n=== VECTOR MATH & HYDROSTATIC STABILITY ANALYSIS ===")
# Define CG and CB in body frame (origin at geometric center)
# CB placed 0.05m above CG for passive stability
r_cg = np.array([0.0, 0.0, -0.02]) # 2 cm below center
r_cb = np.array([0.0, 0.0,  0.03]) # 3 cm above center

f_net_w, tau_world, tau_body = hydrostatic_stability_analysis(
    mass_kg=m_neutral,
    volume_ft3=v_displaced_ft3,
    r_cg_body=r_cg,
    r_cb_body=r_cb,
    pitch_deg=10.0,
    roll_deg=5.0
)

print(f"CG Position (Body):            {r_cg} m")
print(f"CB Position (Body):            {r_cb} m")
print(f"Net Force Vector (World):      {f_net_w} N")
print(f"Restoring Torque (Pitch 10°, Roll 5°):")
print(f"  In World Frame:              {tau_world} N·m")
print(f"  In Body Frame:               {tau_body} N·m")

f_integrated = pressure_vector_integration(depth_m=10.0, width_ft=w_1, height_ft=h_1, length_ft=sub_length_ft)
print(f"\nSurface Pressure Vector Integration at 10m Depth:")
print(f"  Sum of Face Force Vectors:   {f_integrated} N")
print(f"  Notice +Z force equals buoyant force ({f_buoyancy:.2f} N), X/Y forces cancel out to 0!")

# Example Thruster Command: 10N forward port, 10N forward stbd, 5N bow up, 0N stern
u_cmd = np.array([10.0, 10.0, 5.0, 0.0])
wrench = thruster_allocation_matrix(u_cmd)
print(f"\nThruster Control Allocation (Input u={u_cmd} N):")
print(f"  Net Surge Force (Fx):        {wrench[0]:.2f} N")
print(f"  Net Heave Force (Fz):        {wrench[2]:.2f} N")
print(f"  Net Pitch Moment (Ty):       {wrench[4]:.2f} N·m")
print(f"  Net Yaw Moment (Tz):         {wrench[5]:.2f} N·m")


graph_pressure_force(depth_list, hydro_force_list, crush_force_list)
