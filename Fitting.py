import sys
import math
import sqlite3

N = 1084
Alpha = 0

def load_sim():
    f = open('similarity.txt')
    sim = [[0.0 for i in range(N)] for i in range(N)]
    for (line,i) in zip(f.readlines(),range(1,N)):
        lines = line.strip().split('\t')
        for (x,j) in zip(lines,range(1, N)):
            sim[i][j] = float(x.strip())
    f.close()
    return sim

if __name__=='__main__':
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()
    load_sim()
    for U in range(1,N):
