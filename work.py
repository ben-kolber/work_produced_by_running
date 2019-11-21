import math
import pandas as pd
import time

# ratio of mass of body to mass of leg and arm
# for male and females (KG)
male_leg_mass_ratio = 0.1668
male_arm_mass_ratio = 0.057
female_leg_mass_ratio = 0.1847
female_arm_mass_ratio = 0.0497

# ratio of height to length of arm and leg
# for male and female (KG)
male_arm_length_ratio = 0.6
male_leg_length_ratio = 0.6
female_arm_length_ratio = 0.6
female_leg_length_ratio = 0.6

# gravitational constant
G = 9.81  # m/sec^2
Delta_time = 15  # sec

# Instance of a runner


class Human:

    def __init__(self, weight, height):  # weight in kg and height in cm
        self.mass = weight
        self.height = height*0.56/100.0  # Center of gravity vertical height, in meters
        self.arm_mass = weight * male_arm_mass_ratio  # kg
        self.arm_length = height * male_arm_length_ratio / 2.0 / 100.0  # meters
        self.leg_mass = weight * male_leg_mass_ratio  # kg
        self.leg_length = height * male_leg_length_ratio / 2.0 / 100.0  # meters

        # couples of mass (part i center mass) and arm legnth/2 (radius of gyration)
        self.parts = [
            [self.arm_mass, self.arm_length],
            [self.arm_mass, self.arm_length],
            [self.leg_mass, self.leg_length],
            [self.leg_mass, self.leg_length]]

    # added work for running uphill.
    # theta is angle between 0-DEG and hill gradient.
    def get_gradient(self, gradient, distance):
        gradient = gradient / distance
        theta = math.atan(gradient)
        return self.mass * G * distance * math.sin(theta)

    # External work done by the runner
    # c.m = center mass
    #####################################################################################
    # Mass * G * H(c.m) + 1/2 * Mass * Velocity(c.m) + Mass * G * Distance * sin(theta)
    #####################################################################################
    def external_work(self, gradient, velocity, distance):
        velocity = velocity / 3.6  # km/g -> m/sec
        potential = self.mass * self.height * G  # jouls
        gradient = self.get_gradient(gradient, distance)
        return (((self.mass * velocity * velocity)/2.0) + potential + gradient)

    # Internal work done by the runner calculated for each leg and arm.
    # this segment can be even more specific by calculating work of each limb at work.
    # b.p = body part, so the work of each part and the summation for total work.
    ################################################################################
    # SIGMA     [(1/2 * mass(b.p) * gyration(c.m of b.p)^2 * angular_vel(b.p)^2) +
    # <1 - N>    (1/2 * mass(b.p) * velocity(b.p relative to c.m)^2)]
    ################################################################################
    def internal_work(self, velocity, distance):
        work_total = 0
        velocity = velocity / 3.6  # km/h -> m/s
        speed = distance / Delta_time
        # radians / sec
        w = speed / (self.leg_length * 2)  # angular velocity, leg and arm length are the same.
        # velocity relative to center mass
        v_part = (self.mass * velocity) / (4*((2 * self.arm_mass) + (2 * self.leg_mass)))
        for part in self.parts:  # add to power work of each part
            work_total += (part[0]*part[1]*part[1]*w*w)/2.0 + (part[0] * v_part * v_part)/2.0
        return work_total


##############
### Driver ###
##############
if __name__ == "__main__":
    # importing the data
    data = pd.read_csv('/Users/benjaminkolber/Desktop/guy_data.csv', encoding="ISO-8859-1")
    #data = pd.read_csv('/Users/guyg/desktop/guy_data.csv', encoding="ISO-8859-1")
    height = list(data['A'])[0]  # cm
    weight = list(data['B'])[0]  # kg
    times = list(data['C'])  # sec
    distances = list(data['D'])  # meters
    gradients = list(data['E'])  # 0 - 1 ratio
    velocities = list(data['F'])  # km / h

    # create an instance of a runner
    human = Human(weight, height)
    print('New runner! -> Weight: {} kg. Height = {} cm'.format(weight, height))
    # start computing output of power in watts every second.(power = work/time)
    # please take into account this is pure wattage, not including the additional
    # 97.2 watts a human generates every second.
    total = 0
    kilojouls = 0
    total_distance = 0
    for i in range(len(times)):

        if times[i] == 0:
            pass
        else:
            external_work = human.external_work(gradients[i], velocities[i], distances[i])
            internal_work = human.internal_work(velocities[i], distances[i])
            clean_watts = (external_work + internal_work)/Delta_time
            watts = clean_watts + 97.2
            total_session_watts = external_work + internal_work
            print('====')
            print('velocity: {}'.format(velocities[i]))
            print('distance: {}'.format(distances[i]))
            print('times: {}'.format(times[i]))
            print('gradient: {}'.format(gradients[i]/distances[i]))
            print('pure avg. watts generated: {} watts'.format(clean_watts))
            print('with organs taken into account: {} watts'.format(watts))
            print('total watts generated in 15SEC: {} watts'.format(total_session_watts))
            human_watts = 4 * clean_watts
            kilojouls += human_watts / 1000 * 15
            total += total_session_watts
            total_distance += distances[i]
            print('----------------------------------------')
            time.sleep(0.01)
    print('================================================')
    print('REPORT:')
    print('Total Session watts: {} watts'.format(total))
    print('Total distance: {} meters'.format(total_distance))
    calories = kilojouls / 4.184
    print('Total calorie burn: {} calories'.format(calories))
    print('----------------------------------------')
