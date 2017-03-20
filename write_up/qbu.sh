pdflatex ./pi_report.tex
bibtex ./pi_report.tex
makeindex pi_report.nlo -s nomencl.ist -o pi_report.nls
pdflatex ./pi_report.tex
pdflatex ./pi_report.tex
