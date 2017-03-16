




log_titles = ["Time/s", "Dynamo Reading/V", "HES Reading/V", "Potentiometer Value/7bit", "Filtered Dynamo", "Filtered HES"]
filter_delay=100
logf = open("./logfixtest.csv", "r")
datl = logf.readlines()
logf.close()

cols = [[0] * 0] * 0
for i in range(0, len(log_titles)):
    cols.append([log_titles[i]] * 1)
cols.append(["notes\n"] * 1)

for i in range(1, len(datl)):
    splt = datl[i].split(",", len(log_titles))
    for j in range(0, len(cols)):
        cols[j].append(splt[j])

for i in range(0, len(cols)):
    if cols[i][0][:4] == "Filt":
        title = cols[i][0]
        mv = cols[i][1:filter_delay + 1]
        main_data = cols[i][filter_delay + 1:]
        cols[i] = [title]*1
        for j in range(0, len(main_data)):
            cols[i].append(main_data[j])
        for j in range(0, len(mv)):
            cols[i].append(mv[j])

logf = open("./logfixtest_fixed.csv", "w")
for i in range(0, len(cols[0])):
    line = ""
    for j in range(0, len(cols)):
        line += (str(cols[j][i]) + ",")
    logf.write(line[:-1])
logf.close()
