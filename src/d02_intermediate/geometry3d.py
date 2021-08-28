import math
import jdcal
import datetime as dt
from math import radians as rd

from math import tan, asin, degrees, radians


def sunheight(  lat=51.218606,
            lon=6.79393,
            datetime='2021-09-20 12:00'):
    '''
    returns the sunheight in degrees at given date, time and location
    defaults to Düsseldorf Main Station, 2021-09-20, 12:00 pm, CET
    :param lat: latitude of a location
    :param lon: longitude of a location
    :param datetime: date and time in format 'YYYY-MM-DD hh:mm'
    '''
    # source for formula: http://www.geoastro.de/SME/tk/index1.htm 
    # change type of datetime to datetime.datetime if necessary
    if type(datetime)==str:
        fmt = '%Y-%m-%d %H:%M'
        datetime = dt.datetime.strptime(datetime, fmt)
    
    # set constants, 
    # ecl is ecliptic of the earth in degrees, 
    # d2r is factor to convert degrees to radians
    ecl = 23.44
    d2r = .01745
    pi2 = 2*math.pi

    # =INT(365,25*(IF(E2>2;F2;F2-1)+4716))
    # +INT(30,6001*(IF(E2>2;E2;E2+12)+1))
    # +D2+C2/24+2-INT(F2/100)+INT(INT(F2/100)/4)-1524,5-2451545

    # =INT(365,25*(IF(E2>2;F2;F2-1)+4716))
    if datetime.month > 2:
        h1 = datetime.year
    else:
        h1 = datetime.year-1
    h1 = int(365.25*(h1+4716))

    # INT(30,6001*(IF(E2>2;E2;E2+12)+1))
    # is correct
    if datetime.month > 2:
        h2 = datetime.month+1
    else:
        h2=datetime.month+13
    h2=int(30.6001*h2)

    UT = datetime.hour + datetime.minute/60
    # +D2+C2/24+2-INT(F2/100)+INT(INT(F2/100)/4)-1524,5-2451545
    h3 = datetime.day+UT/24+2-int(datetime.year/100) + int(int(datetime.year/100)/4)-1524.5-2451545

    JDM = h1+h2+h3

    # =J2/36525
    T=JDM/36525
    # = 2*PI()*(0,993133 + 99,997361*K3-INT(0,993133 + 99,997361*K3))
    M = pi2*   (0.993133 + 99.997361*T-int(0.993133 + 99.997361*T))
    # =6893*SIN(M2) + 72*SIN(2*M2)
    DL = 6893*math.sin(M)+72*math.sin(2*M)
    #=2*PI()*(0,7859453+M2/(2*PI())+(6191,2*K2+N2)/1296000-INT(0,7859453+M2/(2*PI())+(6191,2*K2+N2)/1296000))
    L= pi2 * (0.7859453+M/ (pi2)+   (6191.2*T+ DL)/1296000-int(0.7859453+M /pi2    )+(6191.2*T +DL)/1296000)
    SL = math.sin(L)
    Z = math.sin(d2r*ecl)*SL
    X = math.cos(L)
    Y = math.cos(ecl*d2r)*SL
    R = (1-Z**2)**.5
    # =IF(24*ATAN(U2/(T2+R2))/PI()>0;24*ATAN(U2/(T2+R2))/PI();24*ATAN(U2/(T2+R2))/PI()+24)
    RA = 24*math.atan(Y/(X+R))/math.pi
    if RA <= 0:
        RA += 24
    # =MOD(280,46061837+360,98564736629*J2   +0,000387933*K2^2-K2^3/38710000+$H$2;360)
    theta = (280.46061837+360.98564736629*JDM+0.000387933*(T**2)-(T**3)/38710000+lon)%360
    # =IF(L2-15*V2>0;L2-15*V2;360+L2-15*V2)
    tau = theta-15*RA
    if tau <= 0:
        tau += 360
    
    DEC = math.atan(Z/R)/d2r
    # height sin is correct
    height_sin = math.cos(lat*d2r)*math.cos(DEC*d2r)*math.cos(tau*d2r)+math.sin(d2r*lat)*math.sin(d2r*DEC)
    height = math.asin(height_sin)/d2r
    return height


import math
import jdcal
import datetime as dt
from math import radians as rd

from math import tan, asin, degrees, radians


def sun_geo(lat=48.1,
            lon=11.6,
            datetime='2006-08-06 06:00'):
    '''
    returns a dict with azimut and altitude values of the sun for a given time, date and location
    returned faulty azimuth values in the past, please beware
    defaults to Munich, 2006-08-06, 06:00 am, CET
    :param lat: latitude of a location
    :param lon: longitude of a location
    :param datetime: date and time in format 'YYYY-MM-DD hh:mm'
    '''
    # change type of datetime to datetime.datetime if necessary
    if type(datetime)==str:
        fmt = '%Y-%m-%d %H:%M'
        datetime = dt.datetime.strptime(datetime, fmt)

    # source for formula: https://physik.cosmos-indirekt.de/Physik-Schule/Sonnenstand
    # compute time variable n
    n = datetime.date().toordinal() -2451545  + 1721424.5 + datetime.hour/24 + datetime.minute/(24*60)
    # compute mean ecliptical length of the sun: L
    L = 280.460 + .9856474*n
    L = L%360
    # compute mean anomaly: g
    g = 357.528 + .9856003*n
    g = math.radians(g%360)
    # compute actual ecliptical length of the sun: A
    A= math.radians(L + 1.915*math.sin(g)+.01997*math.sin(2*g))
    # compute ecliptic: e
    e = math.radians(23.439 - 0.0000004*n)
    # compute right ascension: alpha
    alpha = math.degrees(math.atan(math.cos(e)*math.tan(A)))
    if math.cos(A) <0:
        alpha = alpha +180
        
    # compute declination of the sun: delta
    delta = math.degrees(math.asin(math.sin(e)*math.sin(A)))
    # compute julian centuries: T0
    T0 = n/36525

    # compute time in hours: T
    T = datetime.hour + datetime.minute/60
    # compute mean sidereal time for greenwich: theta_hg
    theta_hg = (6.697376 + 2400.05134*T0 + 1.002738*T)%24

    # compute greenwich hour angle: theta_g
    theta_g = theta_hg*15
    # compute sidereal time for given lon: theta
    theta = theta_g+lon
    # compute hour angel of the sun: tau
    tau = theta - alpha
    # compute azimut: azimut
    sintau = math.sin(rd(tau))
    costau = math.cos(rd(tau))
    sinphi = math.sin(rd(lat))
    tandelta = math.tan(rd(delta))
    cosphi = math.cos(rd(lat))
    azimut = math.degrees(math.atan(sintau/(costau*sinphi-tandelta*cosphi)))
    # compute sunheight: sunheight
    cosdelta = math.cos(rd(delta))
    sindelta = math.sin(rd(delta))
    sunheight = math.degrees(math.asin(cosdelta*costau*cosphi+sindelta*sinphi))
    # compute mean refraction: R
    ri = rd(sunheight + 10.3/(sunheight+5.11))
    R = 1.02/math.tan(ri)
    # compute refracted sunheight: sunheight_ref
    sunheight_ref = sunheight + R/60
    # correct azimut
    if (costau*sinphi-tandelta*cosphi)<0:
        if azimut > 0:
            azimut = azimut-180
        else:
            azimut = azimut+180
    # collect data in a dict
    sun_geo = {'azimut':azimut,'sunheight':sunheight,'sunheight refracted':sunheight_ref}
    return sun_geo


from math import tan, asin, degrees, radians, cos, sin, acos

def inc_angle_by_gradients(azimut, sunheight_refracted, ns_grad, ew_grad):
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

def inc_angle_by_degrees(azimut,sunheight_refracted,tilt,alignment):
    '''
    returns the effective angle of incidence of the sun rays relative to the solar panel in degrees
    :param azimut: azimut of the sun in degrees
    :param sunheight_refracted: sunheight in degrees
    :param tilt: tilt of the panel
    :param alignment: alignment of the panel 
    '''
    # formula created based on the formula for angles between 3d vectors
    # use some variables for easier formula construction
    a = (radians(azimut+180))
    s1 = sin(a)
    s2 = cos(a)
    s3 = tan(radians(sunheight_refracted))
    
    p1 = -sin(radians(alignment))*tan(radians(tilt))
    p2 = -cos(radians(alignment))*tan(radians(tilt))
    p3 = (cos(radians(alignment)))**2 + (sin(radians(alignment)))**2 
     
    # construct the upper part
    upper = s1*p1+s2*p2+s3*p3
    # construct the vector lengths
    vl_sun = (s1**2 + s2**2 + s3**2)**.5
    vl_panel = (p1**2 + p2**2 + p3**2)**.5
    # compute the angle of incidence
    angle = acos(upper/(vl_sun*vl_panel))
    return degrees(angle)