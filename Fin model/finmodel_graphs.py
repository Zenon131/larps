import finmodel
import numpy as np
import matplotlib.pyplot as plt

inchtometer = 0.0254
degtorad = np.pi / 180

waterDensity = 1000


def plotrpm():
    rpmv = np.linspace(0, 400, 50)
    terminalVs = []
    terminalVNoDrags = []
    thrustvs = []
    maxtorquevs = []
    torquevs = []
    stabletorquevs = []
    stablethrusts = []

    for rpm in rpmv:
        print(rpm)
        fin = finmodel.Fin(rpm)

        thrustvs.append(finmodel.netFinThrust(fin, 0, np.array([0, 0, 0])))
        nettorque, maxtorque, maxforce, netwheeltorque = finmodel.finTorque(fin, 0, np.array([0, 0, 0]))
        maxtorquevs.append(maxtorque)
        torquevs.append(netwheeltorque)

        lo = 0.0
        hi = 4.0

        for it in range(11):
            v = (lo + hi) / 2
            thrust = finmodel.netFinThrust(fin, 0, np.array([-v, 0, 0]))
            drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer) ** 2 * np.pi * v ** 2
            # drag = 0
            if thrust > drag:
                lo = v
            else:
                hi = v

        terminalVs.append((lo + hi) / 2)

        stablethrusts.append(finmodel.netFinThrust(fin, 0, np.array([-(lo + hi) / 2, 0, 0])))
        snettorque, smaxtorque, smaxforce, snetwheeltorque = finmodel.finTorque(fin, 0, np.array([-(lo + hi) / 2, 0, 0]))
        stabletorquevs.append(snetwheeltorque)

        lo = 0.0
        hi = 4.0

        for it in range(11):
            v = (lo + hi) / 2
            thrust = finmodel.netFinThrust(fin, 0, np.array([-v, 0, 0]))
            # drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer) ** 2 * np.pi * v ** 2
            drag = 0
            if thrust > drag:
                lo = v
            else:
                hi = v

        terminalVNoDrags.append((lo + hi) / 2)

    # print(terminalVs)
    # print(np.array(terminalVs) / np.array(terminalVNoDrags))
    plt.figure(figsize=(18, 6))
    plt.suptitle("RPM dependence (mode = 2)")

    plt.subplot(2, 3, 1)
    plt.plot(rpmv, terminalVs, label="with drag")
    plt.plot(rpmv, terminalVNoDrags, label="without drag")
    plt.xlabel("rpm")
    plt.ylabel("terminal velocity (m/s)")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_rpm_velocity.png", dpi=400)

    # print(thrustvs)
    plt.subplot(2, 3, 2)
    plt.plot(rpmv, thrustvs, label="start")
    plt.plot(rpmv, stablethrusts, label="terminal")
    plt.xlabel("rpm")
    plt.ylabel("thrust (N)")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_rpm_thrust.png", dpi=400)

    # print(thrustvs)
    plt.subplot(2, 3, 3)
    plt.plot(rpmv, torquevs, label="start")
    plt.plot(rpmv, stabletorquevs, label="terminal")
    plt.xlabel("rpm")
    plt.ylabel("torque (Nm)")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_rpm_torque.png", dpi=400)

    plt.subplot(2, 3, 4)
    plt.plot(rpmv, np.array(torquevs) * rpmv / 60 * 2 * np.pi, label="start")
    plt.plot(rpmv, np.array(stabletorquevs) * rpmv / 60 * 2 * np.pi, label="terminal")
    plt.xlabel("rpm")
    plt.ylabel("power")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_rpm_power.png", dpi=400)

    plt.subplot(2, 3, 5)
    plt.plot(rpmv, np.array(stablethrusts) * np.array(terminalVs) / (np.array(stabletorquevs) * rpmv / 60 * 2 * np.pi))
    plt.xlabel("rpm")
    plt.ylabel("efficiency, with drag, terminal")
    plt.ylim(0, 1)
    plt.grid(True)
    # plt.savefig("outputs/graph_rpm_efficiency.png", dpi=400)

    plt.subplot(2, 3, 6)
    plt.plot(rpmv, (np.array(stabletorquevs) * rpmv / 60 * 2 * np.pi) / 22 / 9.8 / np.array(terminalVs))
    plt.xlabel("rpm")
    plt.ylabel("Cost of Transport")
    plt.grid(True)
    # plt.savefig("outputs/graph_rpm_COT.png", dpi=400)

    plt.tight_layout()
    plt.savefig("outputs/graph_rpm.png", dpi=300)


def plotfreq():
    modes = np.array(range(1, 10))
    terminalVs = []
    terminalVNoDrags = []
    thrustvs = []
    maxtorquevs = []
    torquevs = []
    stabletorquevs = []
    stablethrusts = []

    for m in modes:
        print(m)
        # fin = finmodel.Fin(spatialfreq=f)
        # fin.numfins = modes[ind] * 3
        fin = finmodel.Fin(fins=m*3)

        thrustvs.append(finmodel.netFinThrust(fin, 0, np.array([0, 0, 0])))
        nettorque, maxtorque, maxforce, netwheeltorque = finmodel.finTorque(fin, 0, np.array([0, 0, 0]))
        maxtorquevs.append(maxtorque)
        torquevs.append(netwheeltorque)

        lo = 0.0
        hi = 4.0

        for it in range(11):
            v = (lo + hi) / 2
            thrust = finmodel.netFinThrust(fin, 0, np.array([-v, 0, 0]))
            drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer) ** 2 * np.pi * v ** 2
            # drag = 0
            if thrust > drag:
                lo = v
            else:
                hi = v

        terminalVs.append((lo + hi) / 2)

        stablethrusts.append(finmodel.netFinThrust(fin, 0, np.array([-(lo + hi) / 2, 0, 0])))
        snettorque, smaxtorque, smaxforce, snetwheeltorque = finmodel.finTorque(fin, 0, np.array([-(lo + hi) / 2, 0, 0]))
        stabletorquevs.append(snetwheeltorque)

        lo = 0.0
        hi = 4.0

        for it in range(11):
            v = (lo + hi) / 2
            thrust = finmodel.netFinThrust(fin, 0, np.array([-v, 0, 0]))
            # drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer) ** 2 * np.pi * v ** 2
            drag = 0
            if thrust > drag:
                lo = v
            else:
                hi = v

        terminalVNoDrags.append((lo + hi) / 2)

    # print(terminalVs)
    print(np.array(terminalVs) / np.array(terminalVNoDrags))
    plt.figure(figsize=(18, 6))
    plt.suptitle("Mode dependence (RPM = 200)")

    plt.subplot(2, 3, 1)
    plt.plot(modes, terminalVs, label="with drag")
    plt.plot(modes, terminalVNoDrags, label="without drag")
    plt.xlabel("mode (amount of sin waves)")
    plt.ylabel("terminal velocity (m/s)")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_freq_velocity.png", dpi=400)

    # print(thrustvs)
    plt.subplot(2, 3, 2)
    plt.plot(modes, thrustvs, label="start")
    plt.plot(modes, stablethrusts, label="terminal")
    plt.xlabel("mode (amount of sin waves)")
    plt.ylabel("thrust (N)")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_freq_thrust.png", dpi=400)

    # print(thrustvs)
    plt.subplot(2, 3, 3)
    plt.plot(modes, torquevs, label="start")
    plt.plot(modes, stabletorquevs, label="terminal")
    plt.xlabel("mode (amount of sin waves)")
    plt.ylabel("torque (Nm)")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_freq_torque.png", dpi=400)

    plt.subplot(2, 3, 4)
    plt.plot(modes, np.array(torquevs) * 200 / 60 * 2 * np.pi, label="start")
    plt.plot(modes, np.array(stabletorquevs) * 200 / 60 * 2 * np.pi, label="terminal")
    plt.xlabel("mode (amount of sin waves)")
    plt.ylabel("power")
    plt.grid(True)
    plt.legend()
    # plt.savefig("outputs/graph_freq_power.png", dpi=400)

    plt.subplot(2, 3, 5)
    plt.plot(modes, np.array(stablethrusts) * np.array(terminalVs) / (np.array(stabletorquevs) * 200 / 60 * 2 * np.pi))
    plt.xlabel("mode (amount of sin waves)")
    plt.ylabel("efficiency, with drag, terminal")
    plt.ylim(0, 1)
    plt.grid(True)
    # plt.savefig("outputs/graph_freq_efficiency.png", dpi=400)

    plt.subplot(2, 3, 6)
    plt.plot(modes, (np.array(stabletorquevs) * 200 / 60 * 2 * np.pi) / 22 / 9.8 / np.array(terminalVs))
    plt.xlabel("mode (amount of sin waves)")
    plt.ylabel("Cost of Transport")
    plt.grid(True)
    # plt.savefig("outputs/graph_freq_COT.png", dpi=400)

    plt.tight_layout()
    plt.savefig("outputs/graph_freq.png", dpi=300)


if __name__ == '__main__':
    plotrpm()
    plotfreq()
    plt.show()
