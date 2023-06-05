import VCSpbx as vcs
from CoolProp.CoolProp import PropsSI as CPPSI

# parameters
ref = 'R290'
mdot = 17.6/3600
p_in = 2.764E5  # Pa
p_out = 20.666E5  # Pa
T_in = 18.456 + 273.15
h_in = CPPSI('H', 'P', p_in, 'T', T_in, ref)
speed = 3000.

# components
system = vcs.System('system', 0.1)
cpr = vcs.Compressor_MasterfluxAlpine(id='cpr', system=system, speed=speed)
inlet = vcs.Source('inlet', system, mdot, p_in, h_in)
outlet = vcs.Sink('sink', system, mdot, p_out, h_in)

# connections
inlet_cpr = vcs.Junction('inlet_cpr', system, ref, inlet, 'outlet_A', cpr, 'inlet_A',mdot, p_in, h_in)
cpr_outlet = vcs.Junction('cpr_outlet',system, ref, cpr, 'outlet_A', outlet, 'inlet_A', mdot, p_out, h_in)

system.initialize()
system.run()

print('Pel: {} W \nmdot: {} kg/s\nTD: {} °C'.format(cpr.Pel, cpr_outlet.get_massflow(), cpr_outlet.get_temperature()-273.15))