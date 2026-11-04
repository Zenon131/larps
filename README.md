# Low-disturbance Aquatic Reef Platform for Surveying (LARPS)

This repository contains the development and design files for the LARPS project. The goal of this project is to create a low-disturbance aquatic platform capable of surveying reef environments with minimal impact on the ecosystem.

## Project Overview
The LARPS project focuses on combining efficient underwater propulsion, reliable computer vision for navigation and surveying, and a low-impact physical design to ensure the preservation of delicate reef structures.

## Repository Structure
- `submarine/`: Contains the core compute, mathematics, and simulation files for the submarine's operation.
    - `hardware_specs.md`: Detailed hardware specifications for compute, vision, and actuation.
    - `sub_math.py`: Core mathematical models for the vehicle.

## Hardware Goals
- **Low Disturbance:** Optimized thruster configurations and movement patterns to minimize sediment disturbance.
- **Efficient CV:** Utilizing edge AI (e.g., Raspberry Pi 5 + NPU or Jetson) for real-time reef surveying.
- **High Reliability:** Industrial-grade sensors for depth and orientation in challenging underwater environments.
