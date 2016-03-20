@ECHO OFF
set PATH=c:\python27;c:\python27\Scripts;%PATH%
set PYTHONPATH=%CD%\src\;
python -V >dev.null 2>&1
findstr /c:"Python 2.7.10" dev.null
IF ERRORLEVEL 1 (
        echo "Python 2.7.10 is not installed or PYTHONPATH is incorrect"
        echo "Please install the supplied Python installation"
        pause
) ELSE (
        python -c "import wx" >nul 2>&1
        IF ERRORLEVEL 1 (
                echo "wxPython package is not installed"
                echo "Please install the supplied wxPython installation"
                pause
        ) ELSE (
		set /p file_path="Enter the path of your configuration file: "
                start cmd.exe /k "python ./src/one_click/cmd_app.py %%file_path%%"
        )
)

