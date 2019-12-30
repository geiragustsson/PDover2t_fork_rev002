import pprint
import numpy as np
#import pdover2t

####################################################################
# Pipe collapse (local buckling - system collapse) according to DNVGL-ST-F101.
####################################################################

alpha_fab = 0.85
alpha_U = 1.00
D = 0.660
D_max = D
D_min = D
E = 207.*10**9
g = 9.81
h_l = -410.
material = "CMn"
nu = 0.3
rho_water = 1027.
SMYS = 450.e6
t = 0.0212
t_corr = 0.0005
t_fab = 0.001
T = 60

# t-min
t_1 = t - t_corr - t_fab
print(f"Minimum pipe wall thickness: {t_1}")

# ovality
O_0 = pdover2t.dnvgl_st_f101.pipe_ovality(D, D_max, D_min)
print(f"Pipe ovality: {O_0}")

# material strength, with temperature de-rating
f_y = pdover2t.dnvgl_st_f101.char_mat_strength(SMYS, T, material, alpha_U=alpha_U)
print(f"Pipe material strength, with temperature de-rating: {f_y:.1f}")

# external pressure
p_e = rho_water * g * abs(h_l) 
print(f"External pressure due to water depth: {p_e:.1f}")

# characteristic elastic pressure
p_el = pdover2t.dnvgl_st_f101.pipe_char_elastic_pressure(t_1, D, nu, E)
print(f"Pipe characteristic elastic pressure: {p_el:.1f}")

# characteristic plastic pressure
p_p = pdover2t.dnvgl_st_f101.pipe_char_plastic_pressure(t_1, D, f_y, alpha_fab)
print(f"Pipe characteristic plastic pressure: {p_p:.1f}")

# collapse pressure (numerical)
p_c_0 =  1025*9.81*1 # initial value for numerical calculation of pipe collapse pressure
p_c = pdover2t.dnvgl_st_f101.char_collapse_pressure_num(p_el, p_p, O_0, D, t_1, p_c_0=p_c_0)
print(f"Pipe collapse pressure (numerical): {p_c:.1f}")

# collapse unity check (numerical)
pipe_collapse_uty = pdover2t.dnvgl_st_f101.pipe_collapse_unity(p_e, p_c)
print(f"Pipe collapse unity check (numerical): {pipe_collapse_uty:.3f}")

# collapse pressure (analytic)
p_c = pdover2t.dnvgl_st_f101.char_collapse_pressure(p_el, p_p, O_0, D, t_1)
print(f"Pipe collapse pressure (analytic): {p_c:.1f}")

# collapse unity check (analytic)
pipe_collapse_uty = pdover2t.dnvgl_st_f101.pipe_collapse_unity(p_e, p_c)
print(f"Pipe collapse unity check (analytic): {pipe_collapse_uty:.3f}")

####################################################################
# Pipe pressure containment (bursting) according to DNVGL-ST-F101.
#
# Reference:
# DNVGL-ST-F101 (2017-12)
# sec:5.4.2.1, eq:5.6, page:93; 
# sec:5.4.2.1, eq:5.7, page:94;
####################################################################

parameters = {
    "alpha_U": 1.0,
    "D": 0.660,
    "g": 9.81,
    "gamma_inc": 1.1,
    "gamma_SCPC": 1.138,
    "h_ref": 30.,
    "h_l": 0.,
    "material": "CMn",
    "p_d": 240e5, 
    "rho_cont": 275.,
    "rho_water": 1027.,
    "rho_t": 1027.,
    "SC": "medium",
    "SMYS": 450.e6,
    "SMTS": 535.e6,
    "t": 0.0212,
    "t_corr": 0.0005,
    "t_fab": 0.001,
    "T": 60,
}

p_cont_overall = pdover2t.dnvgl_st_f101.press_contain_all(ret="all", **parameters)
pprint.pprint(p_cont_overall)

# Pressure containment unity check
print("Pressure containment unity check result: {:.2f}".format(p_cont_overall["p_cont_uty"]))

####################################################################
# Pipe propagation buckling according to DNVGL-ST-F101.
####################################################################

alpha_fab = 0.85
alpha_U = 1.00
D = 0.660
g = 9.81
h_l = -410.   # np.linspace(0,500,10)  
material = "CMn"
rho_water = 1027.
SMYS = 450.e6
t = 0.0212
t_corr = 0.0005
T = 60

# wall thickness for propagation
t_2 = t - t_corr # np.array([t, t - t_corr])
print(f"Pipe wall thickness for propagation: {t_2}")

# external pressure
p_e = pdover2t.misc.water_depth_press(h_l, rho_water, g)
print(f"External pressure due to water depth: {p_e:.1f}")

# material strength, with temperature de-rating
f_y = pdover2t.dnvgl_st_f101.char_mat_strength(SMYS, T, material, alpha_U=alpha_U)
print(f"Pipe material strength, with temperature de-rating: {f_y:.1f}")

# characteristic propagation pressure
p_pr = pdover2t.dnvgl_st_f101.propbuck_char_pressure(t_2, D, f_y, alpha_fab)
print(f"Characteristic propagation pressure: {p_pr:.1f}")

# pipe propagation buckling unity check
propbuck_uty = pdover2t.dnvgl_st_f101.propbuck_unity(p_e, p_pr)
print(f"Pipe propagation buckling unity check: {propbuck_uty:.3f}")

# critical water depth for propagating buckling
propbuck_crit_wd = pdover2t.dnvgl_st_f101.propbuck_critical_wd(t_2, D, p_pr, rho_water, SMYS, 
    T=T, material=material, alpha_U=alpha_U, alpha_fab=alpha_fab )
print(f"Critical water depth for propagating buckling: {propbuck_crit_wd:.2f}")

# buckle arrestor properties
L_BA = 12.2
t = 0.0319
t_2 = t - t_corr

# characteristic propagation pressure for buckle arrestor
p_prBA = pdover2t.dnvgl_st_f101.propbuck_char_pressure(t_2, D, f_y, alpha_fab)
print(f"Characteristic propagation pressure for buckle arrestor: {p_prBA:.1f}")

# crossover pressure for buckle arrestor
p_x = pdover2t.dnvgl_st_f101.propbuck_crossover_press(p_pr, p_prBA, D, t_2, L_BA)
print(f"Crossover pressure for buckle arrestor: {p_x:.1f}")

# buckle arrestor propagation buckling unity check
propbuck_arrestor_uty = pdover2t.dnvgl_st_f101.propbuck_arrestor_unity(p_e, p_x)
print(f"Buckle arrestor propagation buckling unity check: {propbuck_arrestor_uty:.3f}")

# critical water depth for buckle arrestor
BA_propbuck_crit_wd = pdover2t.dnvgl_st_f101.propbuck_critical_wd(t_2, D, p_pr, rho_water, SMYS, 
    T=T, material=material, alpha_U=alpha_U, alpha_fab=alpha_fab )
print(f"Critical water depth for buckle arrestor: {BA_propbuck_crit_wd:.2f}")


















