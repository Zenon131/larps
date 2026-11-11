import finmodel
import numpy as np
import matplotlib.pyplot as plt

inchtometer = 0.0254
degtorad = np.pi / 180

waterDensity = 1000

if __name__ == '__main__':
    rpmv = np.linspace(0, 200, 50)
    terminalVs = []
    terminalVNoDrags = []
    thrustvs = []
    maxtorquevs = []
    torquevs = []

    for rpm in rpmv:
        print(rpm)
        fin = finmodel.Fin(rpm)

        thrustvs.append(finmodel.netFinThrust(fin, 0, np.array([0, 0, 0])))
        nettorque, maxtorque, maxforce, netwheeltorque = finmodel.finTorque(fin, 0, np.array([0, 0, 0]))
        maxtorquevs.append(maxtorque)
        torquevs.append(netwheeltorque)

        lo = 0.0
        hi = 1.2

        for it in range(10):
            v = (lo + hi) / 2
            thrust = finmodel.netFinThrust(fin, 0, np.array([-v, 0, 0]))
            drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer) ** 2 * np.pi * v ** 2
            # drag = 0
            if thrust > drag:
                lo = v
            else:
                hi = v

        terminalVs.append((lo + hi)/2)

        lo = 0.0
        hi = 1.2

        for it in range(10):
            v = (lo + hi) / 2
            thrust = finmodel.netFinThrust(fin, 0, np.array([-v, 0, 0]))
            # drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer) ** 2 * np.pi * v ** 2
            drag = 0
            if thrust > drag:
                lo = v
            else:
                hi = v

        terminalVNoDrags.append((lo + hi)/2)

    # print(terminalVs)
    print(np.array(terminalVs) / np.array(terminalVNoDrags))
    plt.plot(rpmv, terminalVs)
    plt.plot(rpmv, terminalVNoDrags)
    plt.xlabel("rpm")
    plt.ylabel("terminal velocity (m/s)")
    plt.grid(True)
    plt.savefig("outputs/graph_velocity.png", dpi=600)

    # print(thrustvs)
    plt.figure()
    plt.plot(rpmv, thrustvs)
    plt.xlabel("rpm")
    plt.ylabel("thrust (N)")
    plt.grid(True)
    plt.savefig("outputs/graph_thrust.png", dpi=600)

    # print(thrustvs)
    plt.figure()
    plt.plot(rpmv, torquevs)
    plt.xlabel("rpm")
    plt.ylabel("torque (Nm)")
    plt.grid(True)
    plt.savefig("outputs/graph_torque.png", dpi=600)

    plt.figure()
    plt.plot(rpmv, np.array(torquevs) * rpmv / 60 * 2 * np.pi)
    plt.xlabel("rpm")
    plt.ylabel("power (w)")
    plt.grid(True)
    plt.savefig("outputs/graph_power.png", dpi=600)

    plt.show()

