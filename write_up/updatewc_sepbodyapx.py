# update .tex with wordcount, separate main body from appendix

import wordcount
import time

body = [""] * 0
apx = [""] * 0

# UPDATE WORDCOUNT

print "openning report tex file"
rep_file = open("pi_report.tex","r")
rep = rep_file.readlines()
rep_file.close()


print "creating backup"
rep_file = open("pi_report.BACKUP","w")
rep_file.writelines(rep)
rep_file.close()

print "removing appendix before count"
app_index = len(rep) - 1
# strip appendix
for i in range(0, len(rep)):
    if (rep[i][:14] == "%% APPENDIX %%"):
        app_index = i
rep_na = rep[:app_index]
rep_na.append("\\end{document}")

print "opening report (sans appendix)"
rep_file = open("pi_report.NOAPPENDIX","w")
rep_file.writelines(rep_na)
rep_file.close()

print "getting wordcount"
wc = wordcount.getWords("pi_report.NOAPPENDIX")

if (wc == "1912 words"):
    wc = "something went wrong...      "

print "result: {0}".format(wc)
rep[4] = "\\def\\thewords{" + str(wc)[:-6] + "} % last proper build on " + time.strftime("%a %d %B %Y at %H:%M:%S", time.gmtime())+ "\n"

print "updating tex"
rep_file = open("pi_report.tex","w")
rep_file.writelines(rep)
rep_file.close()

# SEPARATE BODY AND APPENDIX

body_r = False

for i in range(0, len(rep)):
    if rep[i][:15] == "%% COPY HERE %%":
        # stop copying
        body_r = True
    if rep[i][:14] == "%% APPENDIX %%":
        # start copying again
        body_r = False
    elif body_r = False:
        apx.append[rep[i]]

