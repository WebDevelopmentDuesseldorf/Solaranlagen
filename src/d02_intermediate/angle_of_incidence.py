from math import tan, asin, degrees, radians

def inc_angle(azimut, sunheight_refracted, ns_grad, ew_grad):
    '''
    returns the effective angle of incidence of the sun rays relative to the solar panel in degrees
    :param azimut: azimut of the sun in degrees
    :param sunheight_refracted: sunheight in degrees
    :param ns_grad: north-south gradient of the panel, positive if the panel is facing south
    :param ew_grad: east-west gradient of the panel, positive if the panel is facing west 
    '''
    sc = abs(ns_grad+ew_grad*(-tan(radians(azimut)))+tan(radians(sunheight_refracted)))
    l1 = (ns_grad**2+ew_grad**2+1)**.5
    l2= (1+(tan(radians(azimut)))**2+(tan(radians(sunheight_refracted)))**2)**.5
    angle = asin(sc/(l1*l2))
    return degrees(angle)