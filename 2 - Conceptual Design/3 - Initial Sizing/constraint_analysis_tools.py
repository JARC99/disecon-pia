import numpy as np
from ambiance import Atmosphere

#%% Rotorcraft constraint analysis

def get_Hvr_PW_rat(design_brief, concept, DL):
    
    h_TO = design_brief['T-O altitude']
    
    FoM = concept['Figure of merit']
    eta_e = concept['Powertrain efficiency']
    
    g = Atmosphere(0).grav_accel # m/s^2 
    rho = Atmosphere(h_TO).density # kg/m^3
    
    DL = DL*g
    
    PW_rat = np.sqrt(DL/(2*rho))/(FoM*eta_e)
    
    return PW_rat*g # W/kg

def get_vRoC_PW_rat(design_brief, concept, DL):

    h_cr = design_brief['Cruise altitude']
    h_TO = design_brief['T-O altitude']
    vRoC = design_brief['Vertical rate of climb']
    
    FoM = concept['Figure of merit']
    k_i = concept['Induced power correction factor']
    eta_e = concept['Powertrain efficiency']
    
    g = Atmosphere(0).grav_accel
    rho = Atmosphere((h_TO + h_cr)/2).density # kg/m^3
    
    DL = DL*g
    
    PW_rat = (vRoC - k_i*vRoC/2 + k_i/2*np.sqrt(vRoC**2 + 2*DL/rho) 
              + (1/FoM - 1)*(- k_i*vRoC/2 + k_i/2*np.sqrt(vRoC**2 + 2*DL/rho)))/eta_e
 
    return PW_rat*g # kg/W

def get_vSC_PW_rat(design_brief, concept, DL):
    
    h_vSC = design_brief['Hover service ceiling']
    vRoC_SC = design_brief['Vertical rate of climb at hover service ceiling']
    
    FoM = concept['Figure of merit']
    k_i = concept['Induced power correction factor']
    eta_e = concept['Powertrain efficiency']
    
    g = Atmosphere(0).grav_accel
    rho = Atmosphere(h_vSC).density # kg/m^3
    
    DL = DL*g
    
    PW_rat = (vRoC_SC - k_i*vRoC_SC/2 + k_i/2*np.sqrt(vRoC_SC**2 + 2*DL/rho) + 
             (1/FoM - 1)*(- k_i*vRoC_SC/2 + k_i/2*np.sqrt(vRoC_SC**2 + 2*DL/rho)))/eta_e
    
    return PW_rat*g # kg/W

#%% Transition constraint analysis

def get_Tr_PW_rat(design_brief, concept, DL, WL):

    h_TO = design_brief['T-O altitude']
    V_S = design_brief['Stall speed']
    theta_TR = concept['Transition tilt angle']
    eta_e = concept['Powertrain efficiency']
    eta_p = concept['Propulsive efficiency']
    
    AR = concept['Wing aspect ratio']
    CDmin = concept['Minimum drag coefficient']
    FoM = concept['Figure of merit']
    k_i = concept['Induced power correction factor']
    
    g = Atmosphere(0).grav_accel # m/s^2 
    rho = Atmosphere(h_TO).density # kg/m^3
    
    DL = DL*g
    WL = WL*g
    
    e = 1.78*(1 - 0.45*AR**0.68) - 0.64
    k = 1/(np.pi*AR*e)
    eta_o = eta_e*eta_p
    V_TR = 1.2*V_S # m/s
    q = 1/2 * rho * V_TR**2 # Pa
    
    PW_rat = ((k_i/np.sin(np.deg2rad(theta_TR))
             *np.sqrt(-V_TR**2/2 + np.sqrt((V_TR**2/2)**2 
                                           + (DL/(2*rho*np.sin(theta_TR)))**2)) 
             + (1/FoM - 1)
             *(k_i/np.sin(np.deg2rad(theta_TR))*np.sqrt(-V_TR**2/2 + np.sqrt((V_TR**2/2)**2
                                     + (DL/(2*rho*np.sin(np.deg2rad(theta_TR))))**2))))/eta_e
             + (q*V_TR*CDmin/ WL + k*WL/q)/eta_o)
    
    return PW_rat*g # kg/W

#%% Fixed-wing constraint analysis

def get_TO_PW_rat(design_brief, concept, WL):
    
    h_TO = design_brief['T-O altitude']
    S_G = design_brief['Ground run']
    V_S = design_brief['Stall speed']
    
    CL_TO = concept['Lift coefficient at T-O']
    CD_TO = concept['Drag coefficient at T-O']
    eta_e = concept['Powertrain efficiency']
    eta_p = concept['Propulsive efficiency']
    mu = concept['Ground friction coefficient']
    
    g = Atmosphere(0).grav_accel # m/s^2 
    rho = Atmosphere(h_TO).density # kg/m^3
    
    WL = WL*g
    V_LOF = 1.1*V_S # m/s
    q = 1/2 * rho * V_LOF**2/2 # Pa
    eta_o = eta_e*eta_p
    
    TW_rat =  V_LOF**2 / (2*g*S_G) + q*CD_TO/WL + mu*(1 - q*CL_TO/WL) # N/N
    
    PW_rat = TW_rat*(V_LOF/np.sqrt(2))/eta_o # N/W
    
    return PW_rat*g # kg/W

def get_RoC_PW_rat(design_brief, concept, WL):
    
    h_cr = design_brief['Cruise altitude']
    h_TO = design_brief['T-O altitude']
    RoC = design_brief['Rate of climb']

    AR = concept['Wing aspect ratio']
    CDmin = concept['Minimum drag coefficient']
    eta_e = concept['Powertrain efficiency']
    eta_p = concept['Propulsive efficiency']
    
    g = Atmosphere(0).grav_accel
    rho = Atmosphere((h_TO + h_cr)/2).density # kg/m^3
    
    WL = WL*g
    e = 1.78*(1 - 0.045*AR**0.68) - 0.64
    k = 1/(np.pi*AR*e)
    V_Y = np.sqrt(2/rho*WL*np.sqrt(k/(3*CDmin)))
    q = 1/2 * rho * V_Y**2 # Pa
    eta_o = eta_e*eta_p

    TW_rat = RoC/V_Y + q/WL*CDmin + k/q*WL # N/N
    PW_rat = TW_rat*V_Y/eta_o # N/W
    
    return PW_rat*g, V_Y # kg/W, m/s


def get_V_cr_PW_rat(design_brief, concept, WL):
    h_cr = design_brief['Cruise altitude']
    
    AR = concept['Wing aspect ratio']
    CDmin = concept['Minimum drag coefficient']
    n = concept['Peukert exponent']
    eta_e = concept['Powertrain efficiency']
    eta_p = concept['Propulsive efficiency']
    
    g = Atmosphere(0).grav_accel
    rho = Atmosphere(h_cr).density # kg/m^3
    
    WL = WL*g
    e = 1.78*(1 - 0.045*AR**0.68) - 0.64
    k = 1/(np.pi*AR*e)
    b_rat_Rmax = ((n + 1)/(3*n - 1))**(1/4) 
    V_cr = b_rat_Rmax*np.sqrt(2/rho*WL*np.sqrt(k/CDmin))
    V_L = np.sqrt(2/rho*WL*np.sqrt(k/(3*CDmin)))
    q = 1/2 * rho * V_cr**2 # Pa
    eta_o = eta_e*eta_p
    
    TW_rat = q*CDmin/WL + k/q*WL # N/N
    PW_rat = TW_rat*V_cr/eta_o # N/W
    
    return PW_rat*g, V_cr # kg/W, m/s

def get_Turn_PW_rat(design_brief, concept, WL):
    h_cr = design_brief['Cruise altitude']
    n = design_brief['Load factor']
    
    AR = concept['Wing aspect ratio']
    CDmin = concept['Minimum drag coefficient']
    PC = concept['Peukert exponent']
    eta_e = concept['Powertrain efficiency']
    eta_p = concept['Propulsive efficiency']
    
    g = Atmosphere(0).grav_accel
    rho = Atmosphere(h_cr).density # kg/m^3
    
    WL = WL*g
    e = 1.78*(1 - 0.045*AR**0.68) - 0.64
    k = 1/(np.pi*AR*e)
    b_rat_Rmax = ((PC + 1)/(3*PC - 1))**(1/4) 
    V_cr = b_rat_Rmax*np.sqrt(2/rho*WL*np.sqrt(k/CDmin))
    q = 1/2 * rho * V_cr**2 # Pa
    eta_o = eta_e*eta_p
    
    TW_rat = q*(CDmin/WL + k*(n/q)**2*WL) # N/N
    PW_rat = TW_rat*V_cr/eta_o # N/W
    
    return PW_rat*g # kg/W

def get_SC_PW_rat(design_brief, concept, WL):
    h_SC = design_brief['Service ceiling']
    RoC_SC = design_brief['Rate of climb at service ceiling']
    
    AR = concept['Wing aspect ratio']
    CDmin = concept['Minimum drag coefficient']
    eta_e = concept['Powertrain efficiency']
    eta_p = concept['Propulsive efficiency']
    
    g = Atmosphere(0).grav_accel
    rho = Atmosphere(h_SC).density # kg/m^3
    
    WL = WL*g
    e = 1.78*(1 - 0.045*AR**0.68) - 0.64
    k = 1/(np.pi*AR*e)
    V_Y = np.sqrt(2/rho*WL*np.sqrt(k/(3*CDmin)))
    eta_o = eta_e*eta_p

    TW_rat = RoC_SC/(np.sqrt(2/rho*WL*np.sqrt(k/(3*CDmin)))) + 4*np.sqrt(k*CDmin/3) # N/N
    PW_rat = TW_rat*V_Y/eta_o # N/W
    
    return PW_rat*g # kg/W

def get_S_WL(design_brief, concept):
    
    h_TO = design_brief['T-O altitude']
    V_S = design_brief['Stall speed']
    
    CLmax = concept['Maximum lift coefficient']
    
    g = Atmosphere(0).grav_accel # m/s^2 
    rho = Atmosphere(h_TO).density # kg/m^3
    
    q = 1/2*rho*V_S**2 # Pa
    
    WL_S = q*CLmax
    
    return (WL_S/g)[0], V_S