rem update wordcount
T:\Python\python.exe .\updatewordcount.py
rem get figures
rem call .\getfigs.bat
rem build pdf
"C:\Program Files\MiKTeX 2.9\miktex\bin\x64\texify.exe" --pdf --synctex --clean ./pi_report.tex
