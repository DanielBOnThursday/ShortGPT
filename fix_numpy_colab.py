"""
Quick fix for NumPy/Numba compatibility in Google Colab
Run this in a new cell to fix the current session
"""

# Fix NumPy version for Whisper/Numba compatibility
import subprocess
import sys

print("🔧 Fixing NumPy/Numba compatibility...")

# Install compatible versions
subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.26.4", "--force-reinstall", "-q"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "numba==0.59.1", "--force-reinstall", "-q"])

print("✅ NumPy downgraded to 1.26.4")
print("✅ Numba downgraded to 0.59.1") 
print("🔄 Please restart runtime after this completes")
print("💡 Then re-run the notebook from the beginning")