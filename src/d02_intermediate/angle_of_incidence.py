from math import tan, asin, degrees, radians, cos, sin, acos

def inc_angle(azimut, sunheight_refracted, ns_grad, ew_grad):
    '''
    returns the effective angle of incidence of the sun rays relative to the solar panel in degrees
    :param azimut: azimut of the sun in degrees
    :param sunheight_refracted: sunheight in degrees
    :param ns_grad: north-south gradient of the panel, positive if the panel is facing south
    :param ew_grad: east-west gradient of the panel, positive if the panel is facing west 
    '''
    # formula created based on the formula for angles between 3d vectors
    # use some variables for easier formula construction
    a = (radians(azimut+180))
     
    # construct the upper part
    nn = ew_grad*sin(a) - ns_grad*cos(a)+tan(radians(sunheight_refracted))
    # compute the length of the normal vector of the panel
    npl = (ew_grad**2+ns_grad**2+1)**.5
    # compute the length of the mirrored vector of the sun beam
    nsl = ((sin(a))**2+(cos(a))**2+(tan(radians(sunheight_refracted)))**2)**.5
    # compute the angle of incidence
    angle = acos(nn/(npl*nsl))
    return degrees(angle)