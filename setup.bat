@echo off
REM careerflow setup script for Windows
REM Creates a workspace folder, copies scripts, installs dependencies, scaffolds templates.

setlocal enabledelayedexpansion

set "REPO_DIR=%~dp0"
set "WORKSPACE=%~1"
if "%WORKSPACE%"=="" set "WORKSPACE=%USERPROFILE%\Documents\careerflow-workspace"

echo careerflow setup
echo   Repo directory:    %REPO_DIR%
echo   Workspace target:  %WORKSPACE%
echo.

REM 1. Create workspace
mkdir "%WORKSPACE%\master\source_documents" 2>nul
mkdir "%WORKSPACE%\scripts" 2>nul
mkdir "%WORKSPACE%\docs" 2>nul
mkdir "%WORKSPACE%\skills\onboarding" 2>nul
mkdir "%WORKSPACE%\skills\application" 2>nul
mkdir "%WORKSPACE%\templates\master" 2>nul
mkdir "%WORKSPACE%\applications" 2>nul

REM 2. Copy scripts/docs/skills/templates
echo Copying scripts...
xcopy /E /I /Y "%REPO_DIR%scripts" "%WORKSPACE%\scripts" >nul
echo Copying docs...
xcopy /E /I /Y "%REPO_DIR%docs" "%WORKSPACE%\docs" >nul
echo Copying skills...
xcopy /E /I /Y "%REPO_DIR%skills" "%WORKSPACE%\skills" >nul
echo Copying templates...
xcopy /E /I /Y "%REPO_DIR%templates" "%WORKSPACE%\templates" >nul

REM 3. Initialize master files from templates if not present
for %%f in ("%WORKSPACE%\templates\master\*.template") do (
    set "fname=%%~nf"
    set "target=%WORKSPACE%\master\!fname!"
    if not exist "!target!" (
        copy "%%f" "!target!" >nul
        echo   Initialized !target!
    )
)

REM 4. Initialize applications.xlsx if not present
if not exist "%WORKSPACE%\applications.xlsx" (
    echo Generating empty applications.xlsx...
    python "%WORKSPACE%\scripts\init_workspace.py" --xlsx "%WORKSPACE%\applications.xlsx"
)

REM 5. Install Python dependencies
echo Installing Python dependencies...
pip install --user openpyxl

REM 6. Install Node dependencies
echo Installing Node dependencies...
if not exist "%WORKSPACE%\node_modules\docx" (
    pushd "%WORKSPACE%"
    call npm init -y >nul
    call npm install docx --silent
    popd
)

echo.
echo Setup complete.
echo.
echo Next steps:
echo   1. Open Claude Code or Cowork mode.
echo   2. Grant Claude access to: %WORKSPACE%
echo   3. Tell Claude: "set up my job search"
echo.
echo Workspace ready at: %WORKSPACE%

endlocal
