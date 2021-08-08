import math
import jdcal
import datetime as dt

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