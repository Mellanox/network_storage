@ECHO OFF
set PATH=c:\python27;c:\python27\Scripts;%PATH%
set PYTHONPATH=%CD%\src\;
python -V 2> dev.null
findstr /c:"Python 2.7.10" dev.null
IF ERRORLEVEL 1 (
	echo "Python 2.7.10 is not installed or PYTHONPATH is incorrect"
	echo "Please install the supplied Python installation"
	pause
) ELSE (
	set /p file_path="Enter the path of your configuration file: "
	start cmd.exe /k "pip.exe install --upgrade  --trusted-host wxpython.org --pre -f http://wxpython.org/Phoenix/snapshot-builds/ wxPython_Phoenix && python ./src/one_click/cmd_app.py %%file_path%%"
)