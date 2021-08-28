from math import radians, degrees, sin, cos, tan, asin, acos, atan

def radiation_incidence_on_panel(
        global_rad, 
        direct_rad, 
        diffuse_rad, 
        solar_rad_toa, 
        sunheight,
        panel_tilt,
        albedo,
        angle_of_incidence):
    '''
    returns estimated value for the radiation on a PV panel in W/m²
    :param global_rad: global radiation in W/m²
    :param direct_rad: direct radiation in W/m²
    :param diffuse_rad: diffuse radiation in W/m²
    :aram solar_rad_toa: radiation at the top of atmosphere, reference func 'get_solar_irradiance' for value
    :param sunheight: sunheight angle/altitude in degrees
    :param panel_tilt: tilt of the panel in degrees
    :param albedo: albedo of surrounding area, reference estimate_albedo func for value
    :param angle_of_incidence: angle of incidence of the sun beams on the solar panel in degrees
    '''
    # check if a computation is worth it
    if (global_rad >0):
        # rename some vars fo better access
        gd = diffuse_rad
        gb = direct_rad
        g = global_rad
        gon = solar_rad_toa
        beta = panel_tilt
        phi = albedo
        theta = angle_of_incidence

        # compute zenith angle
        theta_z = 90-sunheight
        # compute extraterrestial horizontal radiation: g0
        g0 = gon * cos(radians(theta_z))

        # compute ratio of beam radiation on tilted surface to the beam radiation on horizontal surface: rb
        if theta < 90:
            rb = cos(radians(theta))/cos(radians(theta_z))
        else:
            rb=0
        # compute anisotropy index (measure for amount of circumsolar diffuse radiation): ai
        ai = gb/g0
        # compute a factor for horizon brightening: f
        f= (gb/g)**.5

        # compute the global radiation incidence: gt
        gt1 = (gb+gd*ai)*rb
        gt2 = gd*(1-ai)*(.5+cos(radians(beta))/2)
        gt3 = 1+f*sin(radians(beta/2))**3
        gt4 = g*phi*(.5-cos(radians(beta))/2)
        gt = gt1+gt2*gt3+gt4
    else:
        gt=0
    return gt