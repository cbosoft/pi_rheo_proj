import matplotlib.pyplot as plt
import numpy as np

#Shear Thinning Data (Adapted from "A review of the rheology of filled viscoelastic systems" - pg. 15)
x1 = [120142.42528315245, 134009.23402986198, 153446.9477751839, 
171157.75619735435, 197703.8744026554, 209258.5019541341, 239610.9391515068, 
270793.085742764, 291672.6017933288, 331073.25499599, 347373.72355412133, 
390868.2195382118, 413712.165880282, 432188.9156000758, 479970.36264033575, 
505806.9817910269, 586814.651581953, 640400.427119727, 677828.0619677213, 
708100.4602361716, 782957.4131326054, 904392.0503965411, 978390.7406928303, 
1081821.4736229067, 1249609.1412919841, 1424623.7812660122, 1652784.8328206094, 
1811609.1942004096, 1900804.1933858446, 2157574.7174915913, 2417139.4570237775, 
2866193.4741177335, 3253373.807104445, 3857782.6975154947, 4436687.330978607, 
5169785.043477083, 5919649.801136705, 6574107.662641969, 6958325.552931982]

# y1 = [3800, 2900, 2600, 2200, 1900, 1400, 1050, 780, 550, 400, 280, 195, 45]
y1 = [38783.282706560174, 37091.06160324516, 35477.23552621477, 33548.45373313529, 
31373.84143610764, 30682.07286314387, 28051.582162255447, 25357.13366769018, 
23705.358251021193, 20950.514934605442, 19805.56407212393, 17701.853902445586, 
16361.60666038352, 15467.109503698342, 14138.935496302418, 13068.164939821037, 
10434.98062742774, 9325.198216737324, 8522.427333756457, 7966.0780742489815, 
6728.667753518273, 5433.739116701476, 4910.758371684149, 4101.390590404027, 
3312.0800878148452, 2585.453560506643, 2018.4121869118358, 1685.6749052114244, 
1575.6667652095043, 1258.0413223363698, 993.1059237796526, 749.5650293415773, 
591.7494833356993, 431.76332459351465, 337.05460431213726, 254.37639118101097, 
200.82786712149294, 163.98794401504693, 148.18873650651528]

# MIS READ Y AXIS

y1 = np.array(y1)
x1 = np.array(x1)
y1 = y1 / 150

#data read from figure on second page {figshearthick}
# x2 = [0.0015, 0.02, 0.15, 0.45, 1.5, 11, 250, 1000, 4000, 10000, 20000]
x2 = [0.14085768347941738, 0.19166095165706118, 0.2234743088002736, 
0.2984104952883079, 0.42227712556630037, 0.5219009462611547, 0.7256648737053193, 
1.0903011662399607, 1.4599167142579148, 1.955131982345303, 2.8879082562763854, 
4.615838653774477, 11.800050140149764, 28.45905798548359, 47.30620534280239, 
95.6535589127567, 171.9463888963576, 341.09604359275903, 590.4307909828227, 
1063.6297025858144, 1842.9533463419841, 3524.2208780175333, 6609.668973610229, 
11234.08746915808, 15078.166353228848, 19839.37041018287, 33000.78391144126, 
45137.218305376984, 60535.97541982596, 81163.2647142384]

# y2 = [0.12, 0.12, 0.1, 0.05, 0.02, 0.018, 0.018, 0.02, 0.03, 0.03, 0.03]
y2 = [237.13737056616552, 71.04974114426787, 35.22694651473103, 12.634629176544692, 
3.8542288686231103, 1.7154378963428807, 0.8353625469578271, 0.3398208328942563, 
0.23290965924605506, 0.1654817099943183, 0.12188141848422909, 0.1036632928437699, 
0.08816830667755728, 0.08353625469578278, 0.07233941627366755, 0.06611690262414822, 
0.057254878843583906, 0.05829415347136086, 0.0697830584859867, 0.1000000000000001, 
0.1512472545310625, 0.2738419634264364, 0.5139696800771518, 0.8353625469578271, 
1.000000000000001, 1.1139738599948035, 1.134194403502758, 1.1547819846894594, 
1.1547819846894594, 1.0746078283213196]

#plot 1
f = plt.figure(figsize=(5, 5))
ax1 = f.add_subplot(111)
# ax2 = f.add_subplot(122)
#f.suptitle(r"$\mathrm{Shear\ Thinning}$", fontsize=20)
ax1.plot(x1, y1)
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlabel(r'$\mathrm{Shear\ Stress},\ \sigma\ (Pa)$', ha='center',
va='center', fontsize=12)
ax1.set_ylabel(r'$\mathrm{Viscosity},\ \mu\ (Pa.s)$', ha='center',
va='center', fontsize=12)
plt.grid(which='both', axis='both')
plt.savefig("./fig_shear_behav_thin.png")

#plt.clf()
#plot 2
f = plt.figure(figsize=(5, 5))
ax2 = f.add_subplot(111)
#f.suptitle(r"$\mathrm{Shear\ Thickening}$", fontsize=20)
ax2.plot(x2, y2)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlabel(r'$\mathrm{Shear\ Stress},\ \sigma\ (Pa)$', ha='center',
va='center', fontsize=12)
ax2.set_ylabel(r'$\mathrm{Viscosity},\ \mu\ (Pa.s)$', ha='center',
va='center', rotation='vertical', fontsize=12)
plt.grid(which='both', axis='both')
plt.savefig("./fig_shear_behav_thick.png")

