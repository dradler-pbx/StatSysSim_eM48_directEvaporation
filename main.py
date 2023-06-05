import VCSpbx as vcs
from CoolProp.CoolProp import PropsSI as CPPSI

# Parameters declatarion
ref = "R290"
air = "AIR"
cpr_speed = 6500.
T_amb = 30. + 273.15
superheat = 5.
mdot_air_cond = 0.75
mdot_air_evap = 0.5
T_box = -20 + 273.15
h_air_box = CPPSI('H', 'P', 1e5, 'T', T_box, 'AIR')
p_air_box = 1e5


# initial guesses
T0_init = -30 + 273.15
Tc_init = 45 + 273.15
p0_init = CPPSI('P', 'T', T0_init, 'Q', 0, ref)
pc_init = CPPSI('P', 'T', Tc_init, 'Q', 0, ref)
mdot_init = 8.E-3
h1_init = CPPSI('H', 'P', p0_init, 'T', T0_init + superheat + 5., ref)
h2_init = CPPSI('H', 'P', pc_init, 'T', 100+273.15, ref)
h3_init = CPPSI('H', 'P', pc_init, 'T', Tc_init-.1, ref)
h4_init = CPPSI('H', 'P', pc_init, 'T', Tc_init-4., ref)
h5_init = CPPSI('H', 'P', p0_init, 'T', T0_init + superheat, ref)
h_air_out_guess = CPPSI('H', 'P', p_air_box, 'T', T_box - 5., air)

# System and components
system = vcs.System('system', 0.1)
cpr = vcs.Compressor_MasterfluxAlpine('cpr', system, cpr_speed)
cond = vcs.Condenser(id='cond', system=system, k=[450., 450., 450.], area=1., subcooling=0.1, T_air_in=T_amb, mdot_air_in=mdot_air_cond)
ihx = vcs.IHX(id='ihx', system=system, UA=2.3)
evap = vcs.Evaporator(id='evap', system=system, k=[420., 420.], area=1., superheat=superheat, boundary_switch=True, limit_temp=True)
srccold = vcs.Source(id='srccold', system=system, mdot=mdot_air_evap, p=1e5, h=h_air_box)
snkcold = vcs.Sink(id='snkcold', system=system)

# Junctions
cpr_cond = vcs.Junction(id='cpr_cond', system=system, medium=ref, upstream_component=cpr, upstream_port_id='outlet_A', downstream_component=cond, downstream_port_id='inlet_A', mdot_init=mdot_init, p_init=pc_init, h_init=h2_init)
cond_ihx = vcs.Junction(id='cond_ihx', system=system, medium=ref, upstream_component=cond, upstream_port_id='outlet_A', downstream_component=ihx, downstream_port_id='inlet_A', mdot_init= mdot_init, p_init=pc_init, h_init=h3_init)
ihx_evap = vcs.Junction(id='ihx_evap', system=system, medium=ref, upstream_component=ihx, upstream_port_id='outlet_A', downstream_component=evap, downstream_port_id='inlet_A', mdot_init= mdot_init, p_init=p0_init, h_init=h4_init)
evap_ihx = vcs.Junction(id='evap_ihx', system=system, medium=ref, upstream_component=evap, upstream_port_id='outlet_A', downstream_component=ihx, downstream_port_id='inlet_B', mdot_init=mdot_init, p_init=p0_init, h_init=h5_init)
ihx_cpr = vcs.Junction(id='ihx_cpr', system=system, medium=ref, upstream_component=ihx, upstream_port_id='outlet_B', downstream_component=cpr, downstream_port_id='inlet_A', mdot_init=mdot_init, p_init=p0_init, h_init=h1_init)
srcSL_evap = vcs.Junction(id='srcSL_evap', system=system, medium=air, upstream_component=srccold, upstream_port_id='outlet_A', downstream_component=evap, downstream_port_id='inlet_B', mdot_init=mdot_air_evap, p_init=p_air_box, h_init=h_air_box)
evap_snkSL = vcs.Junction(id='evap_snkSL', system=system, medium=air, upstream_component=evap, upstream_port_id='outlet_B', downstream_component=snkcold, downstream_port_id='inlet_A', mdot_init=mdot_air_evap, p_init=p_air_box, h_init=h_air_out_guess)

system.initialize()
system.run(full_output=True)

# Plot the results
Qdot = evap_ihx.mdot*(evap_ihx.h - ihx_evap.h)
x_evap_in = CPPSI('Q', 'H', ihx_evap.get_enthalpy(), 'P', evap.p, ref)
Vdot_box = mdot_air_evap * CPPSI('D', 'T', T_box, 'P', p_air_box, 'AIR')
Vdot_air_cond = mdot_air_cond * CPPSI('D', 'T', T_amb, 'P', p_air_box, 'AIR')
Pel_evapfan = 200.  # estimation of evaporator fan power consumption (for COP)
Pel_condfan = 200.  # estimation of condenser fan power consumption (for COP)
Qloss = 50.  # estimation of heat losses in housing of system (for Qdot_ATP)
plot_dict = {
    'cycle': {
        'junctions':
            {
                'ihx_cpr':  {'component': ihx_cpr,  'position': [635, 215], 'ha': 'left', 'va': 'top', 'ref': True},
                'cpr_cond': {'component': cpr_cond, 'position': [635, 50], 'ha': 'left', 'va': 'top', 'ref': True},
                'cond_ihx': {'component': cond_ihx, 'position': [70, 20], 'ha': 'left', 'va': 'bottom', 'ref': True},
                'ihx_evap': {'component': ihx_evap, 'position': [155, 320], 'ha': 'left', 'va': 'top', 'ref': True},
                'evap_ixh': {'component': evap_ihx, 'position': [635, 400], 'ha': 'left', 'va': 'top', 'ref': True},
                'src_evap': {'component': srcSL_evap, 'position': [420, 640], 'ha': 'left', 'va': 'top'},
                'evap_snk': {'component': evap_snkSL, 'position': [260, 640], 'ha': 'right', 'va': 'top'}
            },
        'special':
            {
                'txv_evap': {'position': [80, 535], 'ha': 'left', 'va': 'top', 'text': 'T: {T:.2f} °C\np: {p:.2f} bar\nh:{h:.2f} J/kg\nmdot: {mdot:.2f} g/s\nx: {x:0.3f}'.format(T=evap.T0-273.15, p=evap.p*1e-5, h=ihx_evap.h, mdot=ihx_evap.mdot*1e3, x=x_evap_in)},
                'general': {'position': [240, 100], 'ha': 'left', 'va': 'top', 'text': 'T_box: {T_box: .2f} °C\nT_amb: {T_amb: .2f} °C\nPel: {Pel: .2f} W\nQdot_refCycle: {Qdot: .2f}\nCOP_refCycle: {COP_refCycle: .2f}\nQdot_ATP: {Qdot_ATP: .2f} W\nCOP_ATP: {COP_ATP: .2f}\nn_CPR: {n_CPR: .0f} rpm\nVdot_box: {Vbox:.0f} m3/h\nVdot_amb: {Vamb:.0f} m3/h'.format(Pel=cpr.Pel, Qdot=Qdot, n_CPR= cpr_speed, T_box=T_box - 273.15, T_amb=T_amb - 273.15, Vbox=Vdot_box * 3600, Vamb=Vdot_air_cond * 3600, COP_refCycle= Qdot/cpr.Pel, COP_ATP=(Qdot-Pel_evapfan)/(cpr.Pel+Pel_evapfan+Pel_condfan), Qdot_ATP=Qdot-Pel_evapfan-Qloss)}
            }
    },
    'refrigerant': ref,
    'compressor': cpr
}
system.plot_cycle(plot_dict=plot_dict, cycle_img_path=r'diagram.png')
