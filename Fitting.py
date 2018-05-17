import sys
import math
import sqlite3
from geopy.distance import vincenty
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

N = 1084
Alpha = 0

def func(x, a, b):
    return a /(x + b)
    # return a * np.exp(b * x) + c* np.exp(d * x)

def curve(x_data, y_data):
    popt, pcov = curve_fit(func,x_data,y_data)
    # plt.plot(x_data, y_data, 'b.')
    # plt.plot(x_data, func(x_data, *popt),'r-')
    # plt.legend()
    # plt.show()
    # print(pcov)
    return popt


def load_sim():
    f = open('similarity.txt')
    sim = [[0.0 for i in range(N)] for i in range(N)]
    for (line, i) in zip(f.readlines(), range(1, N)):
        lines = line.strip().split('\t')
        for (x, j) in zip(lines, range(1, N)):
            sim[i][j] = float(x.strip())
    f.close()
    return sim


if __name__ == '__main__':
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    sim = load_sim()
    POI = {}

    ff = open("curve_res.txt", "w")
    for U in range(1, N):
        print(str(U)+':')
        for slot in [("00:00:00","06:00:00"),("06:00:00","15:00:00"),("15:00:00","24:00:00")]:
        # for slot in [("0:00","6:00")]:
        # f = open((slot[0]+"_"+slot[1]+"_curve_res.txt").replace(':',''), "w")

            POI.clear()
            pmax = (0,0.0,0.0)
            for i in range(1, N):
                if  U == i or sim[U][i] > Alpha:
                    cur.execute("SELECT [Venue ID],COUNT(*),Latitude,Longitude FROM NYC WHERE [User ID] = ? AND TimeHMS >= ? AND TimeHMS < ? GROUP BY [Venue ID]",(i, slot[0],slot[1]))
                    values = cur.fetchall()
                    for x in values:
                        p = POI.get(x[0],None)
                        if p == None:
                            POI[x[0]] = (int(x[1]),float(x[2]),float(x[3]))
                            pmax = max(POI[x[0]],pmax)
                        else:
                            # p[0] = p[0] + int(x[1])
                            p = (p[0]+int(x[1]),p[1],p[2])
                            pmax = max(p,pmax)
            L = POI.__len__()
            res = np.zeros([L, 2])
            for (i,x) in zip(range(L),POI.values()):
                res[i,0] = vincenty(pmax[1:],x[1:]).meters
                res[i,1] = x[0]
            res = res[np.lexsort(res[:,::-1].T)]
            tmp = 0
            pres = np.zeros([L])
            for i in range(len(res)):
                tmp += res[i, 1]
                pres[i]=float(res[i, 1])/float(tmp)
            #     f.write(str(res[i][0])+'\t')
            # f.write('\n')
            # for i in range(len(pres)):
            #     f.write(str(pres[i])+'\t')
            # f.write('\n')
            curve_res = curve(res[:, 0],pres)
            ff.write(str(curve_res[0])+'\t'+str(curve_res[1])+'\t')
            print(curve_res)
        # f.close()
        ff.write('\n')
    ff.close()

