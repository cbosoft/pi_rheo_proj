# update .tex with wordcount

import wordcount
import time

print "Opening report .tex"
rep_file = open("pi_report.tex","r")
rep = rep_file.readlines()
rep_file.close()


print "Creating backup"
rep_file = open("pi_report.BACKUP","w")
rep_file.writelines(rep)
rep_file.close()

print "Removing appendix before count"
app_index = len(rep) - 1
# strip appendix
for i in range(0, len(rep)):
    if (rep[i][:14] == "%% APPENDIX %%"):
        app_index = i
rep_na = rep[:app_index]
rep_na.append("\\end{document}")

print "Reading report (sans appendix)"
rep_file = open("pi_report.NOAPPENDIX","w")
rep_file.writelines(rep_na)
rep_file.close()

print "Counting words"
wc = wordcount.getWords("pi_report.NOAPPENDIX")

if (wc == "1912 words"):
    wc = "Something went wrong...      "

print "Result: {0}".format(wc)
rep[4] = "\\def\\thewords{" + str(wc)[:-6] + "} % last proper build on " + time.strftime("%a %d %B %Y at %H:%M:%S", time.gmtime())+ "\n"

print "Saving updated .tex"
rep_file = open("pi_report.tex","w")
rep_file.writelines(rep)
rep_file.close()
