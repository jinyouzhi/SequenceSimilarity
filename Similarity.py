import sys
import datetime
import sqlite3
import math

def load_seq():
    f = open('Sequence.txt')
    seq = []
    for line in f.readlines():
        lines = line.strip().split("\t")
        if len(lines) < 5:
            continue
        userid = int(lines[0].strip())
        tmp = []
        for i in range(1, len(lines)):
            if i % 2 == 0:
                curT = datetime.datetime.strptime(lines[i].strip(), "%Y-%m-%d %H:%M:%S")
                tmp.append((lines[i - 1].strip(), curT))
        seq.append((userid, tmp))
    f.close()
    return seq


def load_venue():
    f = open('cluster_res.txt')
    dictV = {}
    for line in f.readlines():
        lines = line.strip().split("\t")
        if len(lines) < 4:
            continue
        dictV[lines[0].strip()] = (lines[1].strip(), int(lines[2].strip()), int(lines[3].strip()))
    f.close()
    return dictV


if __name__ == '__main__':
    N = 1084
    sim = [[0.0 for i in range(N)] for i in range(N)]
    seqs = load_seq()
    dictV = load_venue()
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()

    # cur.execute("SELECT * FROM NYC")
    # values = cur.fetchall()
    # print(values)

    for (U, seq) in seqs:
        CTSeq = [0] * N
        CTPoi = [0] * N
        Vs = [0.0] * N
        L = len(seq)
        for i in range(L):
            (V, T) = seq[i]
            (P, C, _) = dictV[V]
            if i == 0:
                dT1 = dT2 = (seq[i + 1][1] - T).total_seconds() / 2
            elif i == L - 1:
                dT1 = dT2 = (T - seq[i - 1][1]).total_seconds() / 2
                dT2 = 0
            else:
                dT1 = (T - seq[i - 1][1]).total_seconds() / 2
                dT2 = (seq[i + 1][1] - T).total_seconds() / 2
            T1 = T - datetime.timedelta(seconds=dT1)
            T2 = T + datetime.timedelta(seconds=dT2)

            cur.execute("SELECT DISTINCT [User ID], [Venue ID] FROM NYC WHERE [Venue category] = ? AND Cluster = ? AND Time >= ? AND Time < ?",
                        (P, C, T1.strftime("%Y/%m/%d %H:%M:%S"), T2.strftime("%Y/%m/%d %H:%M:%S")))
            cseq = cur.fetchall()
            cur.execute("SELECT [User ID], COUNT(*) FROM NYC WHERE [Venue ID] = ? AND Time >= ? AND Time < ? GROUP BY [User ID]",
                        (V, T1.strftime("%Y/%m/%d %H:%M:%S"), T2.strftime("%Y/%m/%d %H:%M:%S")))
            cpoi = cur.fetchall()
            if len(cseq):
                print(cseq)
                tmp = 0.0
                s = 0
                for k in range(len(cseq)):
                    if k == len(cseq) - 1 or cseq[k][0] != cseq[k + 1][0]:
                        CTSeq[int(cseq[k][0])] = CTSeq[int(cseq[k][0])] + 1
                        s = s + 1
                        Vs[int(cseq[k][0])] = Vs[int(cseq[k][0])] + tmp / s
                        s = 0
                        tmp = 0
                    tmp = tmp + math.log(1083.0/int(dictV[cseq[k][1]][2]))
                    s = s + 1

            if len(cpoi):
                # print(cpoi)
                for x in cpoi:
                    CTPoi[int(x[0])] = CTPoi[int(x[0])] + 1
        for Q in range(1,N):
            if CTSeq[Q] != 0:
                sim[U][Q] = sim[U][Q] + Vs[Q] * math.pow(2,CTSeq[Q]) * math.pow(2,CTPoi[Q]) / CTSeq[Q]
    f=open('similarity.txt','w')
    for U in range(1, N):
        f.write(str(sim[U][1]))
        for Q in range(2, N):
            f.write('\t'+str(sim[U][Q]))
        f.write('\n')
    f.close()
    cur.close()
    conn.close()