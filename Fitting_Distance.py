import sys
import math
import sqlite3
from geopy.distance import vincenty
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

N = 1084
Alpha = 0
TopK = N
DeltaDis = 500

def func(x, A, B, C, D, E):
    return A*x*x*x*x + B*x*x*x + C*x*x + D*x + E

def curve(x_data, y_data):
    popt, pcov = curve_fit(func,x_data,y_data)
    plt.plot(x_data, y_data, 'b.')
    plt.plot(x_data, func(x_data, *popt),'r-')
    plt.legend()
    plt.show()
    print(pcov)
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

def kthLargestElement(k, A):
    A = sorted(A, reverse=True)
    return A[k-1]


if __name__ == '__main__':
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    sim = load_sim()
    POI = {}

    ff = open("curve_res_dis.txt", "w")
    for U in range(1, N):
        print(str(U)+':')
        for slot in [("00:00:00","06:00:00"),("06:00:00","15:00:00"),("15:00:00","24:00:00")]:
        # for slot in [("0:00","6:00")]:
        # f = open((slot[0]+"_"+slot[1]+"_curve_res.txt").replace(':',''), "w")

            POI.clear()
            pmax = (0,0.0,0.0)
            TopKth = kthLargestElement(TopK, sim[U])
            for i in range(1, N):
                if  U == i or sim[U][i] >= max(Alpha,TopKth): # Top-K 取前10
                    cur.execute("SELECT [Venue ID],COUNT(*),Latitude,Longitude FROM NYC WHERE [User ID] = ? AND TimeHMS >= ? AND TimeHMS < ? GROUP BY [Venue ID]",(i, slot[0],slot[1]))
                    values = cur.fetchall()
                    xsum = 0
                    for x in values:
                        xsum += x[1]
                    for x in values:
                        p = POI.get(x[0],None)
                        if p == None:
                            POI[x[0]] = (float(x[1])/xsum,float(x[2]),float(x[3]))
                            pmax = max(POI[x[0]],pmax)
                        else:
                            # p[0] = p[0] + int(x[1])
                            p = (p[0]+float(x[1])/xsum,p[1],p[2])
                            pmax = max(p,pmax)
            L = 50
            pres = np.zeros([L])
            dis = np.array(range(0,L*DeltaDis,DeltaDis))
            for x in POI.values():
                tmp = int((vincenty(pmax[1:],x[1:]).meters) / DeltaDis)
                if tmp+1 < L:
                    pres[tmp+1] += 1.0
            for i in range(1, L):
                pres[i] += pres[i - 1]
            for i in range(L):
                pres[i] = 1 - (pres[i] / POI.__len__())
            curve_res = curve(dis,pres)
            ff.write(str(curve_res[0])+'\t'+str(curve_res[1])+'\t')
            print(curve_res)
        # f.close()
        ff.write('\n')
    ff.close()

