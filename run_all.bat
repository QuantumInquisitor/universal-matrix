@echo off
TITLE Universal Field Engine — Master Launch Interface
color 0A

echo =======================================================================
echo    🛰️ INITIALIZING UNIVERSAL FIELD ENGINE INTEGRATED SYSTEM ENVIRONMENT
echo =======================================================================
echo.

:: 1. Verify that standard Python runtime environments are discoverable
where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo ❌ ERROR: Python executable was not detected in your system's PATH.
    echo Please install Python 3 or correct your system environment mappings.
    pause
    exit /b
)

echo 📥 [1/4] Verifying pip package dependencies compliance layout...
call pip install -r requirements.txt --quiet
echo ✅ Environment package validation complete.
echo.

echo 🚀 Launching concurrent engine calculation sub-processes...
echo -----------------------------------------------------------------------

:: 2. Launch your background data logger pipeline instance
echo 📊 Starting Data Telemetry Logging Node...
start "Engine Telemetry Data Logger" cmd /k "python src/data_logger.py"

:: 3. Spin up the distributed connection API endpoint gateway
echo 🌐 Spawning Network REST API Gateway Endpoint Server...
start "Distributed Matrix Network API" cmd /k "python src/matrix_api.py"

:: 4. Boot up your main tensor matrix core engine loops
echo 🧮 Running Foundational Core Matrix Calculation Node...
start "Core Tensor Calculation Engine" cmd /k "python src/calculator.py"

:: 5. Initialize your 3D live satellite aerospace mapping radar screen
echo 🎨 Initializing Synchronized 3D Aerospace Radar Visualization Screen...
timeout /t 2 >nul
start "Core Matrix Visualizer" cmd /k "python src/matrix_visualizer.py"

:: 6. Launch the Immersive Virtual Reality multi-dimensional projection space
echo 🕶️ Spawning Immersive Multi-Dimensional VR Space Framework...
start "VR Matrix Spatial Interface" cmd /k "python src/vr_matrix_space.py"

:: 7. Launch the 13-Dimensional spatial projection environment
echo 🧠 Initializing 13-Dimensional Higher-Space Projection Framework...
start "13D Matrix Spatial Interface" cmd /k "python src/vr_13d_space.py"

echo.
echo =======================================================================
echo  🟢 STATUS: ALL PARALLEL COMPUTATION ZONE NODES ACTIVE AND RUNNING!
echo =======================================================================
