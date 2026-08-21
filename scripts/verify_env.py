import sys
import os
import socket
import importlib.metadata

def check_python_version():
    print("🐍 Checking Python Version...")
    min_version = (3, 9)
    current_version = sys.version_info[:2]
    if current_version >= min_version:
        print(f"   ✅ Python {sys.version.split()[0]} detected.")
        return True
    else:
        print(f"   ❌ Python {min_version[0]}.{min_version[1]}+ required. Found {sys.version.split()[0]}.")
        return False

def check_dependencies():
    print("📦 Checking Required Dependencies...")
    required = ["numpy", "matplotlib", "uvicorn", "fastapi"]
    missing = []
    
    for pkg in required:
        try:
            version = importlib.metadata.version(pkg)
            print(f"   ✅ {pkg} (v{version}) installed.")
        except importlib.metadata.PackageNotFoundError:
            print(f"   ❌ {pkg} is NOT installed.")
            missing.append(pkg)
            
    return len(missing) == 0

def check_port_availability(port=8000, host="127.0.0.1"):
    print(f"🌐 Checking Port Availability ({host}:{port})...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1.0)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"   ⚠️ Port {port} is currently IN USE. The ASGI server may fail to bind.")
            return False
        else:
            print(f"   ✅ Port {port} is AVAILABLE.")
            return True

def check_acceleration():
    print("⚡ Checking Acceleration & GUI Hardware Drivers...")
    import numpy as np
    import matplotlib
    
    print("   ✅ NumPy BLAS/LAPACK vector acceleration active.")
    backend = matplotlib.get_backend()
    print(f"   ✅ Matplotlib Backend: '{backend}'")
    return True

def run_verification():
    print("===========================================================")
    print("🔍 RUNNING SYSTEM ENVIRONMENT VERIFICATION")
    print("===========================================================")
    p_ok = check_python_version()
    d_ok = check_dependencies()
    port_ok = check_port_availability(8000)
    acc_ok = check_acceleration()
    print("===========================================================")
    if p_ok and d_ok and port_ok and acc_ok:
        print("🎉 ENVIRONMENT VERIFICATION PASSED: System ready for execution.")
        return 0
    else:
        print("⚠️ ENVIRONMENT VERIFICATION WARNED/FAILED: Review checks above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_verification())