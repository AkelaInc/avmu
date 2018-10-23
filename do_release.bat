
@echo off

echo "Checking release state"
python check_debug.py  || exit /b !ERRORLEVEL!

echo "doing sdist upload"
python setup.py sdist upload || exit /b !ERRORLEVEL!

echo "Done!"
