python updatewordcount.py
echo "(1/5) Initial report build"
pdflatex ./pi_report.tex > /dev/null
echo "(2/5) Building bibliography"
bibtex ./pi_report.tex > /dev/null 2>&1
echo "(3/5) Building nomenclature index"
makeindex pi_report.nlo -s nomencl.ist -o pi_report.nls > /dev/null 2>&1
echo "(4/5) Re-building report"
pdflatex ./pi_report.tex > /dev/null 2>&1
echo "(5/5) Final build"
pdflatex ./pi_report.tex > /dev/null 2>&1
