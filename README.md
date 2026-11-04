# Low-disturbance Aquatic Reef Platform for Surveying (LARPS)

This repository contains the development and design files for the LARPS project. The goal of this project is to create a low-disturbance aquatic platform capable of surveying reef environments with minimal impact on the ecosystem.

## Project Overview
The LARPS project focuses on combining efficient underwater propulsion, reliable computer vision for navigation and surveying, and a low-impact physical design to ensure the preservation of delicate reef structures.

## Preliminary Technical Specifications

### Physical Design & Buoyancy
Based on preliminary calculations in `submarine/sub_math.py`:
- **Hull Dimensions:** Approx. 1.0' x 1.5' x 3.0'
- **Displaced Volume:** $\sim 4.5\text{ ft}^3$ ($\sim 0.13\text{ m}^3$)
- **Neutral Buoyancy Mass:** $\sim 133\text{ kg}$ (Required mass for neutral buoyancy in seawater)
- **Total Buoyant Force:** $\sim 1.27\text{ kN}$

### Hydrostatics & Stability
- **Stability Strategy:** Passive stability is achieved by offsetting the Center of Gravity (CG) below the Center of Buoyancy (CB).
- **Analysis:** Restoration torques are calculated for pitch and roll to ensure the platform naturally returns to a level state.
- **Pressure Analysis:** Structural integrity is analyzed against hydrostatic crushing forces (calculated up to 50m depth).

### Propulsion & Control
- **Thruster Configuration:** 4-thruster allocation matrix for Surge, Heave, Pitch, and Yaw control.
- **Control Logic:** Implementation of a 6-DOF wrench mapping to translate desired movement into individual thruster commands.

## Repository Structure
- `submarine/`: Contains the core compute, mathematics, and simulation files for the submarine's operation.
    - `hardware_specs.md`: Detailed hardware specifications for compute, vision, and actuation.
    - `sub_math.py`: Core mathematical models for buoyancy, pressure, and stability.
    - `sim_robot.py`: Robotics simulation and control testing.

## Hardware Goals
- **Low Disturbance:** Optimized thruster configurations and movement patterns to minimize sediment disturbance.
- **Efficient CV:** Utilizing edge AI (e.g., Raspberry Pi 5 + NPU) for real-time reef surveying.
- **High Reliability:** Industrial-grade sensors for depth and orientation in challenging underwater environments.
