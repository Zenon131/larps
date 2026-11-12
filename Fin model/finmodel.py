import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy
from numba import int32, float32
from numba.experimental import jitclass

inchtometer = 0.0254
degtorad = np.pi / 180

waterDensity = 1000


spec = [
    ('hulllength', float32),
    ('finwidth', float32),
    ('articulationangle', float32),
    ('finclockangle', float32),
    ('f_spatial', float32),
    ('f_temporal', float32),
    ('numfins', int32),
    ('finconnectorlength', float32)
]


@jitclass(spec)
class Fin:
    def __init__(self, rpm=200, spatialfreq=None, fins=6):
        self.hulllength = 24 * inchtometer
        self.finwidth = 6 * inchtometer
        self.articulationangle = 15 * degtorad  # divide by 2?
        self.finclockangle = 120 * degtorad
        self.numfins = fins
        self.finconnectorlength = 1.5 * inchtometer  # design variable

        #  _   _
        # / \_/ \_

        self.f_spatial = spatialfreq if spatialfreq is not None else self.finclockangle * self.numfins / self.hulllength
        self.f_temporal = rpm / 60 * 2 * np.pi

    def finFunction(self, x, y, t):
        # y is axis along fin rods (moving outwards)
        return y * self.articulationangle * np.sin(x * self.f_spatial + t * self.f_temporal)

    def finFunction_dt(self, x, y, t):
        # y is axis along fin rods (moving outwards)
        return y * self.articulationangle * self.f_temporal * np.cos(x * self.f_spatial + t * self.f_temporal)

    def finFunction_dx(self, x, y, t):
        # y is axis along fin rods (moving outwards)
        return y * self.articulationangle * self.f_spatial * np.cos(x * self.f_spatial + t * self.f_temporal)

    def finFunction_dy(self, x, y, t):
        # y is axis along fin rods (moving outwards)
        return self.articulationangle * np.sin(x * self.f_spatial + t * self.f_temporal)

    def pointForces_dx_dy(self, x, y, t, waterspeed):
        # gives the instantaneous force on the robot per xy differentiable element
        # very optimistic - assumes only the water where the fin is moving is displaced, and it's displaced reflected to the fin at a cst accel
        # (commented parts swap between vector mode & JIT mode) (redo pending)
        finSpeed = self.finFunction_dt(x, y, t)
        angleOfAttack = self.finFunction_dx(x, y, t)
        angleOfFin = self.finFunction_dy(x, y, t)

        # finNormalVector = np.array([-angleOfAttack, -angleOfFin, np.full_like(angleOfAttack, 1)])
        finNormalVector = np.array([-angleOfAttack, -angleOfFin, 1])
        # finNormalVector = finNormalVector / np.linalg.norm(finNormalVector, axis=0)
        finNormalVector = finNormalVector / np.linalg.norm(finNormalVector)

        # note: it's actually negative fin speed. sorry
        # finSpeedVector = np.array([np.full_like(finSpeed, 0), np.full_like(finSpeed, 0), -finSpeed])
        finSpeedVector = np.array([0, finSpeed * np.sin(angleOfFin), -finSpeed * np.cos(angleOfFin)])
        # finSpeedVector = np.array([0, 0, -finSpeed])

        # reps = (*np.array(x).shape, 1)
        # waterVector = np.tile(waterspeed, reps).T + finSpeedVector
        waterVector = waterspeed + finSpeedVector

        # waterReflect = waterVector - 2 * np.einsum("i...,i...->...", waterVector, finNormalVector) * finNormalVector
        waterReflect = waterVector - 2 * np.dot(waterVector, finNormalVector) * finNormalVector

        waterMovementVector = waterReflect - finSpeedVector

        waterMassToDisplace = np.abs(finSpeed) * waterDensity * 2  # times 2 for pushing and pulling

        # waterAccel = waterMovementVector - np.tile(waterspeed, reps).T
        waterAccel = waterMovementVector - waterspeed

        waterForce = waterMassToDisplace * waterAccel

        # returns force on robot!
        return -waterForce

    def pointTorque_dx_dy(self, x, y, t, waterspeed):
        forces = self.pointForces_dx_dy(x, y, t, waterspeed)
        angleOfFin = np.atan(self.finFunction_dy(x, y, t))
        return y * (np.sin(angleOfFin) * forces[1] - np.cos(angleOfFin) * forces[2])


def netFinThrust(findef, t, waterspeed):
    resx, _ = scipy.integrate.dblquad(lambda y, x: findef.pointForces_dx_dy(x, y, t, waterspeed)[0],
                                      0, findef.hulllength,
                                      lambda x: 0, lambda x: findef.finwidth)

    return resx


def finTorque(findef, t, waterspeed):
    curEnd = 0
    nettorque = 0
    maxtorque = 0
    maxforce = 0
    netwheeltorque = 0
    for i in range(findef.numfins):
        resx, _ = scipy.integrate.dblquad(lambda y, x: abs(findef.pointTorque_dx_dy(x, y, t, waterspeed)),
                                          curEnd, (i+0.5) * findef.hulllength/findef.numfins,
                                          lambda x: 0, lambda x: findef.finwidth)
        nettorque += np.abs(resx)
        maxtorque = max(maxtorque, np.abs(resx))

        flapForce = np.abs(resx) / findef.finconnectorlength
        maxforce = max(maxforce, flapForce)

        wheelrad = findef.finconnectorlength * np.sin(findef.articulationangle)
        wheelangle = i * findef.hulllength / findef.numfins * findef.f_spatial + t * findef.f_temporal

        wheeltorque = np.abs(flapForce * np.cos(wheelangle) * wheelrad)

        netwheeltorque += wheeltorque

        curEnd = (i+0.5) * findef.hulllength/findef.numfins

    # final segment
    resx, _ = scipy.integrate.dblquad(lambda y, x: findef.pointTorque_dx_dy(x, y, t, waterspeed),
                                      curEnd, findef.hulllength,
                                      lambda x: 0, lambda x: findef.finwidth)
    nettorque += np.abs(resx)
    maxtorque = max(maxtorque, np.abs(resx))

    flapForce = np.abs(resx) / findef.finconnectorlength
    maxforce = max(maxforce, flapForce)

    wheelrad = findef.finconnectorlength * np.sin(findef.articulationangle)
    wheelangle = findef.hulllength * findef.f_spatial + t * findef.f_temporal

    wheeltorque = np.abs(flapForce * np.cos(wheelangle) * wheelrad)

    netwheeltorque += wheeltorque

    return nettorque, maxtorque, maxforce, netwheeltorque


if __name__ == '__main__':
    fin = Fin()

    interval = 0.02
    frames = 100
    tv = np.linspace(0, interval * frames, frames)

    print(fin.pointForces_dx_dy(0, 0.5, 0.01, np.zeros(3)))

    robotspeed = 0
    robotx = 0
    robotmass = 22

    thrustv = []
    speedv = []
    robotxv = []
    torquev = []
    maxforcev = []
    powerv = []

    # print(0.5 * 0.83 * waterDensity * (6 * inchtometer)**2 * np.pi)

    for time in tv:
        print(time)
        thrust = netFinThrust(fin, time, np.array([-robotspeed, 0, 0]))
        # assuming the robot is roughly cylindrical shaped (flat front face) with H = 24in and D = 12in (conservative)
        # so cd ~ 0.83
        drag = 0.5 * 0.83 * waterDensity * (6 * inchtometer)**2 * np.pi * robotspeed**2
        netflaptorque, maxflaptorque, maxconnectorforce, netwheeltorque = finTorque(fin, time, np.array([-robotspeed, 0, 0]))

        robotspeed += (thrust-drag)/robotmass * interval
        robotx += robotspeed * interval

        thrustv.append(thrust)
        speedv.append(robotspeed)
        robotxv.append(robotx)
        torquev.append(netwheeltorque)
        powerv.append(netwheeltorque * fin.f_temporal)
        maxforcev.append(maxconnectorforce)

    plt.figure("robot thrust")
    plt.plot(tv, thrustv)
    plt.xlabel("time(s)")
    plt.grid(True)

    plt.figure("robot speed")
    plt.plot(tv, speedv)
    plt.xlabel("time(s)")
    plt.grid(True)

    plt.figure("driving torque")
    plt.plot(tv, torquev)
    plt.xlabel("time(s)")
    plt.grid(True)

    plt.figure("driving power")
    plt.plot(tv, powerv, label="drive power")
    plt.plot(tv, np.array(thrustv) * np.array(speedv), label="output power")
    plt.xlabel("time(s)")
    plt.legend()
    plt.grid(True)

    plt.figure("efficiency")
    plt.plot(tv, np.array(thrustv) * np.array(speedv) / powerv)
    plt.xlabel("time(s)")
    plt.legend()
    plt.grid(True)

    plt.figure("max connecting rod force")
    plt.plot(tv, maxforcev)
    plt.xlabel("time(s)")
    plt.grid(True)

    plt.show()

    # ~~~~~~~~~~ extra unused code below ~~~~~~~~~~~

    # line, = plt.plot(xv, fin.finFunction(xv, fin.finwidth, 0))

    # def update(frame):
    #     global robotspeed, robotx
    #     t = frame * interval
    #
    #     thrust = netFinThrust(fin, t, np.array([-robotspeed, 0, 0]))
    #     robotspeed += thrust * interval / 22
    #     robotx += robotspeed * interval
    #
    #     line.set_xdata(xv + robotx)
    #     line.set_ydata(fin.finFunction(xv, fin.finwidth, t))
    #     return line,
    #
    #
    # ani = animation.FuncAnimation(fig=fig, func=update, frames=400, interval=interval * 1000)

    # xv = np.linspace(0, fin.hulllength, 100)
    # for yv in np.linspace(0, fin.finwidth, 100):
    #     plt.plot(xv, fin.pointForces_dx_dy(xv, yv, 0, np.array([0, 0, 0]))[:, 0])

    # xv, yv = np.meshgrid(np.linspace(0, fin.hulllength, 100), np.linspace(0, fin.finwidth, 100))
    #
    # c = plt.contourf(xv, yv, fin.pointTorque_dx_dy(xv, yv, 0, np.array([0, 0, 0])), cmap='viridis', levels=20)
    # plt.colorbar(c, label='Point force')
    # print(netFinTorque(fin, 0, np.array([0, 0, 0])))
    # print(scipy.integrate.dblquad(lambda y, x: abs(fin.pointTorque_dx_dy(x, y, 0, np.array([0, 0, 0]))),
    #                                       0, 0.0061,
    #                                       lambda x: 0, lambda x: fin.finwidth))
    # plt.show()

    # plt.plot(xv, fin.finFunction(xv, fin.finwidth, 0))
    # plt.plot(xv, fin.finFunction(xv, fin.finwidth, 0.01))

    # print(finTorque(fin, 0, np.zeros(3)))
