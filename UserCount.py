import sys
import sqlite3


if __name__ == '__main__':
    conn = sqlite3.connect('db.db')
    cur = conn.cursor()

    f = open('cluster_res.txt')
    o = open('UserCount.txt','w')
    # T = 0
    for line in f.readlines():
        # T = T + 1
        # if T > 100:
        #     break
        lines = line.strip().split("\t")
        if len(lines) < 3:
            continue
        cur.execute("SELECT COUNT(DISTINCT [User ID]) FROM NYC WHERE [Venue ID] = ?", (lines[0],))
        values = cur.fetchall()
        print(values[0][0])
        o.write(str(values[0][0])+'\n')
    f.close()
    o.close()
