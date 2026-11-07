import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from cuttlefish_model import CuttlefishRobot

def run_simulation():
    # Initialize robot
    robot = CuttlefishRobot()
    
    # Simulation parameters
    dt = 0.1
    total_time = 20.0
    time_steps = np.arange(0, total_time, dt)
    
    # Control parameters (The 'Undulation' settings)
    freq = 2.0       # Hz
    amp = 0.02       # meters
    wavelength = 0.1 # meters
    
    velocities = []
    positions = []
    
    print("Simulating Cuttlefish Robot propulsion...")
    for t in time_steps:
        robot.step(dt, freq, amp, wavelength)
        velocities.append(robot.state[3]) # Surge velocity
        positions.append(robot.state[0])   # Surge position
        
    # Plotting results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    ax1.plot(time_steps, velocities, color='blue', linewidth=2)
    ax1.set_title('Surge Velocity over Time')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Velocity (m/s)')
    ax1.grid(True)
    
    ax2.plot(time_steps, positions, color='green', linewidth=2)
    ax2.set_title('Surge Position over Time')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Position (m)')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('/Users/jonathanwallace/meam_senior_design/submarine/simulation_result.png')
    print("Simulation complete. Result saved as simulation_result.png")

if __name__ == "__main__":
    run_simulation()
