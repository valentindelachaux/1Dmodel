import math
import openpyxl as opxl
from thermo.chemical import Chemical
from thermo.chemical import Mixture
import numpy as np
import scipy.constants as scc

from matplotlib import pyplot as plt

coeff_downward_cool_surface = 1.2

def air_rho(T):
    return -0.00439881*T+2.500535714

def air_c_p(T):
    return 1006

def air_mu(T):
    return (0.004791667*T+0.4065)*1e-5

def air_nu(T):
    return (0.008894048*T-1.097178571)*1e-5

def air_k(T):
    return 7.2607*1e-5*T+0.004365714

def air_Pr(T):
    return 0.711


def back_h(T_abs,T_amb,theta,longueur,largeur,N_ailettes,a):
    DT = T_abs - T_amb
    T_mean = (T_abs+T_amb)/2

    g = scc.g

    rho = air_rho(T_mean)
    Cp = air_c_p(T_mean)
    mu = air_mu(T_mean)
    nu = air_nu(T_mean)
    lambd = air_k(T_mean)
    alpha = (lambd)/(rho*Cp)
    Pr = air_Pr(T_mean)
    beta = 1/T_mean
    
    """
    air = Mixture('air',T=T_mean,P=1e5)
    rho = air.rho
    Cp = air.Cp
    mu = air.mu
    nu = air.nu
    lambd = air.k
    alpha = (lambd)/(rho*Cp)
    Pr = (mu*Cp)/lambd
    beta = 1/T_mean
    """

    D = (largeur-N_ailettes*a)/(N_ailettes-1)
    
    Ra = ((rho**2)*g*math.cos(math.radians(theta))*beta*Cp*(D**4)*DT)/(mu*lambd*longueur)
    
    if DT > 0:
        Nu = (Ra/24)*(1-np.exp(-35/Ra))**(0.75)
    elif DT < 0:
        Nu = (-Ra/24)*(1-np.exp((coeff_downward_cool_surface*-35)/(-Ra)))**(0.75)

    h=(lambd/D)*Nu
    
    return h

def back_h_fins(T_abs,T_amb,theta,longueur,largeur,N_ailettes,a,L_a):
    DT = T_abs - T_amb
    T_mean = (T_abs+T_amb)/2

    g = scc.g

    rho = air_rho(T_mean)
    Cp = air_c_p(T_mean)
    mu = air_mu(T_mean)
    nu = air_nu(T_mean)
    lambd = air_k(T_mean)
    alpha = (lambd)/(rho*Cp)
    Pr = air_Pr(T_mean)
    beta = 1/T_mean


    D = (largeur-N_ailettes*a)/(N_ailettes-1)
    
    Ra = ((rho**2)*g*math.cos(math.radians(theta))*beta*Cp*(D**4)*DT)/(mu*lambd*longueur)

    Gr2=(g*beta*abs(DT)*D**3)*((L_a/longueur)**(1/2))*((D/L_a)**0.38)*(1/nu)**2
    Gr1=(g*beta*abs(DT)*D**4)/(math.sqrt(longueur*L_a)*nu**2)

    if DT<0 and theta<=30:
        crit=Gr2*Pr*math.sin((math.pi/2) - math.radians(theta))
        if crit<=20000:
            Nu = 0.0915*crit**0.436
            h = (lambd/D)*Nu
            return h
        else:
            return 2
    else:
        crit=Gr1*Pr*math.cos((math.pi/2)-math.radians(theta))
        if crit<=250:
            Nu = 0.0929*crit**0.5
            h = (lambd/D)*Nu
            return h
        elif crit<=1000000:
            Nu = 0.2413*crit**(1/3)
            h = (lambd/D)*Nu
            return h
        else:
            return 2

def back_h_simple(T_abs,T_amb,theta,longueur):
    
    h_back_mean = 2.

    DT = T_abs - T_amb

    T_mean = (T_abs+T_amb)/2

    g = scc.g

    rho = air_rho(T_mean)
    Cp = air_c_p(T_mean)
    mu = air_mu(T_mean)
    nu = air_nu(T_mean)
    lambd = air_k(T_mean)
    alpha = (lambd)/(rho*Cp)
    Pr = air_Pr(T_mean)
    beta = 1/T_mean

    if abs(DT)<=0.05:
        return 0.5

    if DT<0:
        if theta>45:
            Ra_L=(g*beta*math.cos(math.pi/2-math.radians(theta))*abs(DT)*(longueur**4))/(nu*alpha)
            if Ra_L >= 1e5 and Ra_L <= 2*1e10:
                Nu_L = 0.68+0.67*Ra_L**(1/4)*(1+(0.492/Pr)**(9/16))**(-4/9)
                h = (lambd/longueur)*Nu_L
                return h
            else:
                print('Ra_L',Ra_L)
                return h_back_mean
        
        elif theta<=45 and theta>=2:
            Ra_L=(g*beta*math.sin(math.pi/2-math.radians(theta))*abs(DT)*(longueur**4))/(nu*alpha)
            if Ra_L>=1e7 and Ra_L<=2*1e11:
                Nu_L = 0.14*Ra_L**(1/3)*((1+0.0107*Pr)/(1+0.01*Pr))
                h = (lambd/longueur)*Nu_L
                return h
            else:
                print('Ra_L',Ra_L)
                return h_back_mean

        else:
            print('theta',theta)
            return h_back_mean

    if DT>0:
        if theta>=2:
            Ra_L=(g*beta*math.cos(math.pi/2-math.radians(theta))*abs(DT)*(longueur**4))/(nu*alpha)
            if Ra_L >= 1e5 and Ra_L <= 1e11:
                Nu_L = 0.68+0.67*Ra_L**(1/4)*(1+(0.492/Pr)**(9/16))**(-4/9)
                h = (lambd/longueur)*Nu_L
                return h
        else:
            print('Ra_L',Ra_L)
            return h_back_mean

    print('DT',DT)
    return h_back_mean