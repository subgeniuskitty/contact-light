import math
import time
import krpc

# Configuration

conn = krpc.connect(name='To orbit', address='192.168.1.11')
vessel = conn.space_center.active_vessel

target_alt = 100000

# Telemetery streams

alt = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apo = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
per = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

stg1_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
stg1_fuel = conn.add_stream(stg1_resources.amount, 'SolidFuel')

# Vehicle setup

vessel.control.sas = True
vessel.control.rcs = True
vessel.control.throttle = 1.0

# Launch

vessel.control.throttle = 0.0
vessel.control.activate_next_stage()
print('Launching')

vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90,90)

# Suborbital ascent

while stg1_fuel() > 0.01:
    pass

vessel.control.activate_next_stage()
vessel.control.throttle = 1.0
print('SRB separation')

turn_start = alt()
while apo() < target_alt:
    percent_complete = (alt() - turn_start) / (target_alt - turn_start)
    turn_angle = 90 * percent_complete
    vessel.auto_pilot.target_pitch_and_heading(90-turn_angle, 90)

vessel.control.throttle = 0.0
print('Coasting to apoapsis')

while alt() < target_alt - 5000:
    pass

# Circularizing

vessel.auto_pilot.target_pitch_and_heading(0, 90)
vessel.control.throttle = 1.0
print('Circularizing')

while per() < target_alt:
    pass

vessel.control.throttle = 0.0
print('Orbit achieved')
