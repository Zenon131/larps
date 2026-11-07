# Compute & Hardware Specification - Submarine Project

## General Constraints
- **Cost:** No single component > $200.
- **Performance:** Efficient and reliable Computer Vision (CV).
- **Environment:** Underwater (requires waterproof housing and specialized optics).

---

## Option 1: High-Performance AI Stack (NVIDIA Jetson)
*Best for: Complex CV tasks and high frame rates.*
**⚠️ BUDGET WARNING:** The full Developer Kit typically exceeds $200. This option may require special funding or a custom carrier board.

### Hardware Components
- **Compute Unit:** **NVIDIA Jetson Orin Nano Dev Kit** ($\sim \$499$)
- **Motor Control:** **Teensy 4.1 / Pixhawk** ($\sim \$100$)
- **Actuation:** **BLHeli_32 ESCs** ($\sim \$30/ea$) + **T200 Thrusters** ($\sim \$210/ea$)
- **Vision:** **Arducam Global Shutter Camera** ($\sim \$70$) + **Wide-angle Lens** ($\sim \$30$)
- **Sensors:** **BNO055 IMU** ($\sim \$35$) + **MS5837 Depth Sensor** ($\sim \$60$)

---

## Option 2: Versatile AI Stack (Raspberry Pi + NPU)
*Best for: Staying within the $200 per-item limit while maintaining AI power.*

### Hardware Components
- **Compute Unit:** **Raspberry Pi 5 (8GB)** ($\sim \$80$) + **Hailo-8 AI Kit** ($\sim \$90$)
    - **Why:** Stays under budget while providing dedicated NPU acceleration for CV.
- **Motor Control:** **Teensy 4.1 / Pixhawk** ($\sim \$100$)
- **Actuation:** **BLHeli_32 ESCs** ($\sim \$30/ea$) + **T200 Thrusters** ($\sim \$210/ea$)
- **Vision:** **Arducam Global Shutter Camera** ($\sim \$70$) + **Wide-angle Lens** ($\sim \$30$)
- **Sensors:** **BNO055 IMU** ($\sim \$35$) + **MS5837 Depth Sensor** ($\sim \$60$)

---

## Comparison Table (Compute Only)

| Feature | Jetson Orin Nano (Dev Kit) | R-Pi 5 + Hailo-8 |
| :--- | :--- | :--- |
| **Est. Compute Cost** | $\sim \$499$ | $\sim \$170$ |
| **Budget Constraint** | ❌ Exceeds $200 | ✅ Within Limit |
| **CV Acceleration** | GPU (CUDA) | NPU (Hailo) |
| **OS/Environment** | Linux (Ubuntu/JetPack) | Raspberry Pi OS / Debian |

## Next Steps for Team Discussion
1. **Budget Review:** Confirm if the Jetson's cost can be approved or if we commit to the R-Pi 5 + AI Kit.
2. **Thruster Cost:** Note that Blue Robotics T200s are right at the $200 limit ($\sim \$210$); check if we need a cheaper generic alternative.
3. **Power Budget:** Calculate total mAh required for the chosen compute option.
