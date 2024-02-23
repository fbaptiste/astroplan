
import math
import os.path
import csv
import numpy as np
import orbit as orb
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

pi = math.pi
lat = 0.0
lon = 0.0
hrLim = 4.0
altLim = 30.0
altMin = 15.0
min_size = 10.0
nMin = 1
nMax = 2000
horizon_file = "--Enter Filename--"
if os.path.isfile("astroplan.ini"):
    fp = open("astroplan.ini", "r")
    lat = float(fp.readline().rstrip('\n'))
    lon = float(fp.readline().rstrip('\n'))
    horizon_file = fp.readline().rstrip('\n')
    hrLim = float(fp.readline().rstrip('\n'))
    altLim = float(fp.readline().rstrip('\n'))
    altMin = float(fp.readline().rstrip('\n'))
    min_size = float(fp.readline().rstrip('\n'))
    nMin = int(fp.readline().rstrip('\n'))
    nMax = int(fp.readline().rstrip('\n'))
    fp.close()
lat = float(input("Enter Latitude  ["+str(round(lat, 6))+"]: ") or round(lat, 6))
lon = float(input("Enter Longitude ["+str(round(lon, 6))+"]: ") or round(lon, 6))
horizon_file = input("Enter Local Horizon Filename ["+horizon_file+"]: ") or horizon_file
if not os.path.isfile(horizon_file):
    while not os.path.isfile(horizon_file):
        print("User-defined horizon file ["+horizon_file+"] not found")
        horizon_file = input("Enter Local Horizon Filename [" + horizon_file + "]: ") or horizon_file
hrLim = float(input("Enter Minimum Observation Time  ["+str(round(hrLim, 1))+"]: ") or round(hrLim, 1))
altLim = float(input("Enter Minimum Peak Altitude  ["+str(round(altLim, 1))+"]: ") or round(altLim, 1))
altMin = float(input("Enter Minimum Observation Altitude  [" + str(round(altMin, 1)) + "]: ") or round(altMin, 1))
min_size = float(input("Enter Minimum DSO Size  [" + str(round(min_size, 1)) + "]: ") or round(min_size, 1))
nMin = int(input("Enter Lowest Catalog Number  [" + str(int(nMin)) + "]: ") or int(nMin))
nMax = int(input("Enter Highest Catalog Number  [" + str(int(nMax)) + "]: ") or int(nMax))
# ---------------------------------
fp = open("astroplan.ini", "w")
fp.write(str(round(lat, 6))+'\n')
fp.write(str(round(lon, 6))+'\n')
fp.write(horizon_file+'\n')
fp.write(str(round(hrLim, 1))+'\n')
fp.write(str(round(altLim, 1))+'\n')
fp.write(str(round(altMin, 1))+'\n')
fp.write(str(round(min_size, 1))+'\n')
fp.write(str(int(nMin))+'\n')
fp.write(str(int(nMax))+'\n')
fp.close()
if not os.path.isfile(horizon_file):
    print("ERROR: User-defined local horizon file ["+horizon_file+"] not found.")
    exit()
# -----------------------------------
latdeg = lat
if lat > 0.0:
    declim = lat - 90.0 + altLim
    print("Target DEC limit > "+str(round(declim, 2)))
else:
    declim = lat + 90.0 - altLim
    print("Target DEC limit < " + str(round(declim, 2)))
lat = lat * pi / 180.0
lon = lon * pi / 180.0
# ------------------------------------------------------------------------------
# Definitions
#
# 0-Frame      Sun Centered, Sun Fixed
# 1-Frame      Earth Centered, Tilt 23.4 deg rel 0-Frame, Ry = -23.4 deg
# 2-Frame      Earth Centered, Earth Fixed (rotation+longitude), Rz = wt+lon
# 3-Frame      Location Centered, at Latitude, Rx = lat
#  x = West, y = Up, z = North
# ------------------------------------------------------------------------------
# Catalogues to Include
# NGC IC   M  C  B SH2 VdB RCW LDN LBN Cr Mel PGC UGC Ced Arp VV PK PN SNR ACO HCG ESO VdBH DWB TR St Ru VdB-Ha
#  16 17  18 19 20 21  22  23  24  25  26 28  29  30  31  32  33 34 35  36  37  38  39  40   41 42 43 44   45
filter_type = ["G", "Gx", "AGx", "rG", "IG", "ClG", "SAB(s)c", "NB", "PN", "DN", "RN", "C+N", "HII", "SNR", "BN", "EN", "GNe"]
# -----------------------------------------------------------------------------
Horizon = np.loadtxt(horizon_file, dtype='float', comments='#', delimiter=None, skiprows=0)
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(Horizon[:, 0], Horizon[:, 1])
plt.xlim([0, 360])
plt.xticks(np.arange(0.0, 390.0, 30.0))
plt.yticks(np.arange(0.0, 90, 15.0))
plt.title("Local Horizon", fontsize=16)
axes.xaxis.set_minor_locator(MultipleLocator(10))
axes.yaxis.set_minor_locator(MultipleLocator(5))
plt.grid(b=None, which='both', axis='both', linestyle=':', linewidth=1)
plt.xlabel("Azimuth (deg)", fontsize=12)
plt.ylabel("Altitude (deg)", fontsize=12)
plt.savefig(horizon_file+".png", format='png')
plt.close()
# ------------------------------------------------------------------------------
fd = open("stellarium_catalog.txt", "rt")
fi = open("local_catalog_" + str(nMin) + "_" + str(nMax) + ".txt", "wt")
fo = open("DSO_list_" + str(nMin) + "_" + str(nMax) + ".csv", 'w', newline='')
csvw = csv.writer(fo, dialect='excel')
csvw.writerow(['No.', 'Name', 'RA (deg)', 'DEC (deg)', 'Type', 'Size', 'Score', 'Month', 'Day'])
# -------------------------------------------------------------------------------
n = 0
Nstart = nMin
Nend = nMax
for s in fd:
    j = s.find("#")
    if int(j) != 0:
        lst = s.split('\t')
        for i in range(len(lst)):
            if lst[i] == '':
                lst[i] = 0
        if Nstart <= int(lst[0]) <= Nend:
            dec = float(lst[2])
            go = False
            if latdeg > 0.0 and dec > declim:
                go = True
            if latdeg <= 0.0 and dec < declim:
                go = True
            if not max(float(lst[7]), float(lst[8])) <= min_size and go:
                if filter_type.count(lst[5]) == 1:
                    if len(lst) != 45:
                        print("Stellarium record length not correct: "+str(len(lst)))
                    if orb.dso(lat, lon, Horizon, lst, filter_type, csvw, hrLim, altLim, altMin) == 1:
                        fi.write(s)
    else:
        fi.write(s)
# -------------------------------------------------------------------------------
fd.close()
fi.close()
fo.close()
# -------------------------------------------------------------------------------
targetfile = "DSO_list_" + str(nMin) + "_" + str(nMax) + ".csv"
fo = open(targetfile, 'r', newline='')
line = fo.readline()
ng = 0
nn = 0
for line in fo:
    lst = line.split(',')
    arr = np.array(lst).reshape(1, 9)
    if arr[0, 4] == '1':
        if ng == 0:
            gal = arr
        else:
            gal = np.vstack((gal, arr))
        ng += 1
    else:
        if nn == 0:
            neb = arr
        else:
            neb = np.vstack((neb, arr))
        nn += 1
print("Galaxies = "+str(ng)+"    Nebulae = "+str(nn))
tgal = np.zeros(shape=(ng, 5))
for i in range(ng):
    tgal[i, 0] = float(gal[i, 7])+float(gal[i, 8])/32.0  # Month/day
    tgal[i, 1] = float(gal[i, 6])  # Score
    tgal[i, 2] = float(gal[i, 2])  # RA
    tgal[i, 3] = float(gal[i, 3])  # DEC
    tgal[i, 4] = float(gal[i, 5])  # size
tneb = np.zeros(shape=(nn, 5))
for i in range(nn):
    tneb[i, 0] = float(neb[i, 7]) + float(neb[i, 8]) / 32.0  # Month/day
    tneb[i, 1] = float(neb[i, 6])  # Score
    tneb[i, 2] = float(neb[i, 2])  # RA
    tneb[i, 3] = float(neb[i, 3])  # DEC
    tneb[i, 4] = float(neb[i, 5])  # size
fo.close()
# -----------------------------------------------------------------------------------
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 0], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='', label="Galaxy ("+str(ng)+")")
plt.plot(tneb[:, 0], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='', label="Nebula ("+str(nn)+")")
plt.xlim([1, 12.9])
plt.xticks(np.arange(1, 13, 1))
plt.ylim([0.0, 1.25])
plt.yticks(np.arange(0, 1.50, 0.25))
axes.xaxis.set_minor_locator(MultipleLocator(0.25))
axes.yaxis.set_minor_locator(MultipleLocator(0.05))
plt.grid(b=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Visible Targets", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Imaging Score", fontsize=12)
plotname = "Visible_DSOs_"+str(nMin)+"-"+str(nMax)+".png"
plt.savefig(plotname, format='png')
plt.close()
# ----------------------------------
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 2], tgal[:, 3], color='b', marker='8', markeredgecolor="black", linestyle='', label="Galaxy ("+str(ng)+")")
plt.plot(tneb[:, 2], tneb[:, 3], color='r', marker='v', markeredgecolor="black", linestyle='', label="Nebula ("+str(nn)+")")
plt.xlim([0, 360])
plt.xticks(np.arange(0, 390, 30))
axes.xaxis.set_minor_locator(MultipleLocator(10))
plt.ylim([-90.0, 90.0])
plt.yticks(np.arange(-90.0, 105.0, 15.0))
axes.yaxis.set_minor_locator(MultipleLocator(5))
plt.grid(b=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Visible DSOs: RA and DEC", fontsize=16)
plt.xlabel("RA (deg)", fontsize=12)
plt.ylabel("DEC (deg)", fontsize=12)
plotname = "Visible_DEC-RA_Map_"+str(nMin)+"-"+str(nMax)+".png"
plt.savefig(plotname, format='png')
plt.close()
# ----------------------------------
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 3], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='', label="Galaxy ("+str(ng)+")")
plt.plot(tneb[:, 3], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='', label="Nebula ("+str(nn)+")")
plt.xlim([-90.0, 90.0])
plt.xticks(np.arange(-90.0, 105.0, 15.0))
axes.xaxis.set_minor_locator(MultipleLocator(5))
plt.ylim([0.0, 1.25])
plt.yticks(np.arange(0, 1.50, 0.25))
axes.yaxis.set_minor_locator(MultipleLocator(0.05))
plt.grid(b=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Imaging Score VS DSO DEC", fontsize=16)
plt.xlabel("DEC (deg)", fontsize=12)
plt.ylabel("Imaging Score", fontsize=12)
plotname = "Visible_Score-DEC_Map_"+str(nMin)+"-"+str(nMax)+".png"
plt.savefig(plotname, format='png')
plt.close()
# ----------------------------------
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscalex_on(True)
axes.set_autoscaley_on(False)
plt.plot(tgal[:, 4], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='', label="Galaxy ("+str(ng)+")")
plt.plot(tneb[:, 4], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='', label="Nebula ("+str(nn)+")")
plt.ylim([0.0, 1.25])
plt.yticks(np.arange(0, 1.50, 0.25))
axes.yaxis.set_minor_locator(MultipleLocator(0.05))
plt.grid(b=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Imaging Score VS DSO Size", fontsize=16)
plt.xlabel("Size (arc-min)", fontsize=12)
plt.ylabel("Imaging Score", fontsize=12)
plotname = "Score_vs_Size_Map_"+str(nMin)+"-"+str(nMax)+".png"
plt.savefig(plotname, format='png')
plt.close()
exit()
