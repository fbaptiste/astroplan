import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
# from astropy import units as u
# import astropy.units as u
# from astropy.time import Time
# from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun
#
# Assumptions:
#     Earth is a sphere
#     Earth's orbit is circular
#     Earth spins but does not precess
#     Sun is fixed in space
#     "Darkness" is when Sun's altitude at Lat, Lon < -12 deg
#     All distances are small compared with distance to a DSO
# Constants associated with Earth's orbit
pi = math.pi
psi = -23.4 * pi / 180.0  # Tilt of Earth's rotation axis relative to orbital plane
Tday = 23.0 + 56.0 / 60.0 + 4.0916 / 60.0 / 60.0  # Number of hours in a day
Om = 2.0 * pi / Tday  # Earth's rate of rotation about its axis
Trev = 365.25635 * Tday  # Number of hours in a year
w = 2 * pi / Trev  # Earth's orbital rate around the Sun


def dso(TargetName, lati: float, loni: float, horz, targ, ftype, csvw, hrLim, altLim, altMin, fdd):
    dt = 7.0/60.0  # Simulation time step in hours
    Nyr = 365  # Number of days in a year
    # Tname = ["SH2_", "NGC_", "IC_", "M_", "PGC_", "UGC_", "LDN_", "LBN_", "VdB", "C", "B", "RCW", "Cr", "Mel"]
    # nList = np.array([21, 16, 17, 18, 28, 29, 24, 25, 22, 19, 20, 23, 26, 27])
    Tname = ["M_", "SH2_", "NGC_", "IC_", "PGC_", "UGC_", "LDN_", "LBN_", "VdB", "C", "B", "RCW", "Cr", "Mel"]
    nList = np.array([18, 21, 16, 17, 28, 29, 24, 25, 22, 19, 20, 23, 26, 27])
    dayMonth = np.array([31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365, 396])
    month = 0
    hist = np.zeros(shape=(Nyr, 5))
    # Check if DSO is in first 4 catalogs (M, SH2, NGC, IC)
    number = 0
    for j in range(4):
        if int(targ[nList[j]]) > 0:
            number = max(number, nList[j])
    if number == 0:
        # print("Object "+targ[0]+" not in catalog")
        return 0  # Object not in first 4 catalogs
    # OK. DSO is in the selected catalog list so track its path
    ra = float(targ[1]) * pi / 180.0
    dec = float(targ[2]) * pi / 180.0
    R01 = np.array([
        [np.cos(psi), 0.0, -np.sin(psi)],
        [0.0, 1.0, 0.0],
        [np.sin(psi), 0.0, np.cos(psi)]
        ])
    R23 = np.array([
        [1.0, 0.0, 0.0],
        [0.0, np.cos(lati), np.sin(lati)],
        [0.0, -np.sin(lati), np.cos(lati)]
        ])
    t0 = 79.0*Tday  # Number of hours between Jan 1 and Spring Equinox
    t = 0.0 - t0  # January 1
    alt = altsun(t, loni, R23, R01)
    if alt > -12.0:  # It's daylight, so move clock forward to first dark
        t, alt, n1 = sunset(t, dt, alt, loni, R23, R01)
    else:
        while alt < -12.0:  # It's dark, so move clock back to first dark
            t -= dt/4.0
            alt = altsun(t, loni, R23, R01)
        t += dt/4.0
        alt = altsun(t, loni, R23, R01)
    day = 0
    altmin = 100.0  # Initialize single-night observation variables
    altmax = 0.0
    score = 0.0
    tvis = 0.0
    # Begin year-long simulation
    while day < Nyr:  # Analysis starts at first dark on first day of the year
        if alt < -12.0:
            dalt, daz = altazdso(t, loni, ra, dec, R23)
            altHorz = np.interp(daz, horz[:, 0], horz[:, 1])
            if dalt > max(altMin, altHorz):
                tvis += dt
                altmax = max(altmax, dalt)
                altmin = min(altmin, dalt)
                score = max(score, tvis/10.25 * altmax/90.0)
            t += dt
            alt = altsun(t, loni, R23, R01)
        else:
            # End of the night clean up
            if month == 0:
                damo = float(month+1) + float(day)/float(dayMonth[month])
            else:
                damo = float(month+1) + float(day-dayMonth[month-1])/float(dayMonth[month]-dayMonth[month-1])
            if altmin > 95.0:
                altmin = 0.0
            hist[day, 0:5] = np.array([damo, altmin, altmax, tvis, score])
            if day > 1:
                # Perform moving average to smooth out curves
                hist[day-1, 1] = np.mean(hist[day-2:day+1, 1])
                hist[day-1, 2] = np.mean(hist[day-2:day+1, 2])
                hist[day-1, 3] = np.mean(hist[day-2:day+1, 3])
                hist[day-1, 4] = np.mean(hist[day-2:day+1, 4])
            altmin = 100.0  # Initialize single-night observation variables
            altmax = 0.0
            score = 0.0
            tvis = 0.0
            day += 1
            if day == dayMonth[month]:
                month += 1
            t, alt, n1 = sunset(t, dt, alt, loni, R23, R01)  # fast forward through daylight to sunset
            # print("Sunset = "+str(n1))
    if max(hist[:, 2]) < altLim or max(hist[:, 3]) < hrLim:
        # print("Object "+targ[0]+" does not satisfy observation criteria")
        return 0  # Cannot see DSO (not high enough and/or not visible for long enough
    else:
        # Find first day when imaging score is maximum
        sMax = 0.97*max(hist[:, 4])  # Use 0.97 to avoid small numerical fluctuation error
        kk = 0
        if hist[0, 4] < sMax:
            while hist[kk, 4] < sMax:
                kk += 1
                kk = min(max(0, kk), 364)
        else:
            kk = Nyr-1
            while hist[kk, 4] >= sMax:
                kk -= 1
                kk = max(0, kk)
            kk += 1
            kk = min(max(0, kk), 364)
        kk = min(max(0, kk), 364)
        mo = int(hist[kk, 0])
        da = max(int((hist[kk, 0]-float(mo))*31.0), 1)
        # TargetName = "Unknown"
        # j = 0
        # while j < nList.size:
        #     if int(targ[nList[j]]) > 0:
        #         TargetName = Tname[j] + targ[nList[j]]
        #         j = nList.size
        #     j += 1
        galaxy = -1
        for i in range(len(ftype)):
            if ftype[i] == targ[5]:
                if i > 5:
                    galaxy = 0
                    print(targ[0] + "  " + TargetName + ": Nebula ["+targ[5]+"] found")
                else:
                    galaxy = 1
                    print(targ[0] + "  " + TargetName + ": Galaxy [" + targ[5] + "] found")
        if galaxy == -1:
            print(targ[0] + "  " + TargetName + ": Unknown Type [" + targ[5] + "] found")
    RA = round(float(targ[1]), 4)
    DEC = round(float(targ[2]), 4)
    size = round(max(float(targ[7]), float(targ[8])), 2)
    sMax = max(hist[:, 4])
    row = [str(targ[0]), TargetName, str(RA), str(DEC), str(galaxy), str(size), str(round(sMax, 2)), str(int(mo)), str(int(da))]
    csvw.writerow(row)
    if TargetName[0] != '_':
        plt.figure(figsize=(8, 8), facecolor=(1.0, 0.8, 0.2))
        ax2 = plt.subplot2grid((3, 1), (1, 0), rowspan=2)
        ax2.set_autoscale_on(False)
        plt.xlabel("Month", fontsize=12)
        plt.ylim([0, 14])
        plt.yticks(np.arange(0, 16, 2))
        ax2.yaxis.set_minor_locator(MultipleLocator(.5))
        plt.ylabel("Hours Visible", fontsize=12)
        plt.grid(visible=True, which='major', axis='both', linestyle=':', linewidth=1)
        ax1 = plt.subplot2grid((3, 1), (0, 0), sharex=ax2)
        ax1.set_autoscale_on(False)
        plt.ylim([0, 90])
        plt.yticks(np.arange(0, 100, 10))
        plt.ylabel("Altitude (deg)", fontsize=12)
        plt.xlim([1, 12.9])
        plt.xticks(np.arange(1, 13, 1))
        ax2.plot(hist[:, 0], hist[:, 3], 'b', linewidth=2, label='Hours')
        ax1.xaxis.set_minor_locator(MultipleLocator(.25))
        ax1.yaxis.set_minor_locator(MultipleLocator(5))
        plt.grid(visible=True, which='major', axis='both', linestyle=':', linewidth=1)
        plt.plot(hist[:, 0], hist[:, 2], 'r', linewidth=1, label='Max Alt')
        plt.plot(hist[:, 0], hist[:, 1], 'g', linewidth=1, label='Min Alt')
        plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
        ptitle = TargetName+': Score = '+str(round(max(hist[:, 4]), 2))+' on '+str(int(mo))+'/'+str(int(da))
        plt.title(ptitle, fontsize=16)
        plt.savefig(TargetName+'.png', format='png')
        plt.close()
        # print(targ[0] + "  " + TargetName + ": Complete")
        fdd.write(TargetName)
        for i in range(Nyr):
            fdd.write(", "+str(round(hist[i, 3], 2)))
        fdd.write('\n')
    return 1


def sunset(t, dt, alt, loni, r23, r01):
    f = 7.0/dt
    n = 0
    while alt > -12.0 or alt < -12.05:
        if alt > -12.0:
            if f < 0.0:
                f = -f/2.0
        if alt < -12.05:
            if f > 0.0:
                f = -f/2.0
        t += f*dt
        alt = altsun(t, loni, r23, r01)
        n += 1
    t += dt
    alt = altsun(t, loni, r23, r01)
    return t, alt, n


def altazdso(t, lon, ra, dec, R23):
    R12 = np.array([[np.cos(Om * t + lon), np.sin(Om * t + lon), 0.0],
                    [-np.sin(Om * t + lon), np.cos(Om * t + lon), 0.0],
                    [0.0, 0.0, 1.0]
                    ])
    rTS = np.array([[-np.sin(ra) * np.cos(dec)],
                    [np.cos(ra) * np.cos(dec)],
                    [np.sin(dec)]
                    ])
    rTP = R23 @ R12 @ rTS  # vector from observation location to DSO
    north = rTP[2, 0]
    west = rTP[0, 0]
    up = rTP[1, 0]
    az = -np.arctan2(west, north) * 180.0 / pi
    if az < 0.0:
        az += 360.0
    if az > 360.0:
        az -= 360.0
    alt = np.arctan2(up, np.sqrt(north ** 2 + west ** 2)) * 180.0 / pi
    return alt, az


def altsun(t, lon, R23, R01):
    R12 = np.array([[np.cos(Om * t + lon), np.sin(Om * t + lon), 0.0],
                    [-np.sin(Om * t + lon), np.cos(Om * t + lon), 0.0],
                    [0.0, 0.0, 1.0]
                    ])
    rES = np.array([[np.sin(w * t)],
                    [-np.cos(w * t)],
                    [0.0]
                    ])
    rSP = -R23 @ R12 @ R01 @ rES  # vector from observation location to Sun
    x = np.sqrt(rSP[0, 0] ** 2 + rSP[2, 0] ** 2)
    altSun = np.arctan2(rSP[1, 0], x) * 180.0 / pi
    return altSun


def writedata(file, a):
    np.savetxt(file, a, fmt='%2.8e', delimiter=' ', newline='\n')
    return a.shape


def readdata(file, nhdr):
    data = np.loadtxt(file, dtype='float', comments='#', delimiter=None, skiprows=nhdr)
    return data
