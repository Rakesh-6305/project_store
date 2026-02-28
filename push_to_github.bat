@echo off
echo ========================================
echo StudentProjectHub - GitHub Sync Assistant
echo ========================================
echo.
echo Initializing Git...
git init
echo.
echo Staging files...
git add .
echo.
echo Committing premium refinements...
git commit -m "Final premium Hub with all technical fixes"
echo.
echo Setting branch to main...
git branch -M main
echo.
echo Adding remote origin...
git remote add origin https://github.com/Rakesh-6305/project_store.git
echo.
echo Pushing to GitHub (you may be asked to log in)...
git push -u origin main
echo.
echo Sync complete!
pause
