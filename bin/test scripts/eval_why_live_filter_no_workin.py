import matplotlib.pyplot as plt
import sys
sys.path.append("./..")
from filter import filter

datf = open("./../../logs/long_cal.csv")
datl = datf.readlines()
datf.close()

rv = [0] * 0
t = [0] * 0
st = [0] * 0
pv = [0] * 0
live_filt_rv = [0] * 0
orv = [0] * 0

splt = datl[1].split(",", 5)
tz = float(splt[0])

for i in range(1, len(datl) / 10):
    splt = datl[i].split(",", 5)
    t.append(float(splt[0]))
    st.append(float(splt[0]) - tz)

    rv.append(float(splt[1]))
    pv.append(int(splt[3]))
    
    if i % 100 == 0:
        live_filt_rv.append(filter(st, rv)[-10])
        orv.append(rv[-1])

f = plt.figure()
ax = f.add_subplot(111)

ax.plot(range(0, len(orv)), live_filt_rv)
ax.plot(range(0, len(orv)), orv)

plt.savefig("./whynowork.png")
