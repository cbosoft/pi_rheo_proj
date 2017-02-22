for /f %%f in ('dir /b T:\gits\pi_rheo_proj\write_up\figures') DO (
T:\Python\python.exe .\figures\%%f)
REM I hate windows batch scripting