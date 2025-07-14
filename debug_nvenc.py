"""
Debug script to check NVENC availability in Google Colab
Run this in a Colab cell to diagnose GPU encoding issues
"""

import subprocess
import torch
import os

print("🔍 NVENC Debugging Report")
print("=" * 50)

# 1. Check CUDA availability
print("\n1. 🎮 CUDA Status:")
print(f"   CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA Version: {torch.version.cuda}")
else:
    print("   ❌ No CUDA available")

# 2. Check NVIDIA drivers
print("\n2. 🔧 NVIDIA Driver Status:")
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        lines = result.stdout.split('\n')
        for line in lines[:10]:  # First 10 lines contain driver info
            if 'Driver Version' in line or 'CUDA Version' in line:
                print(f"   {line.strip()}")
    else:
        print("   ❌ nvidia-smi failed")
except Exception as e:
    print(f"   ❌ nvidia-smi error: {e}")

# 3. Check FFmpeg encoders
print("\n3. 🎬 FFmpeg Encoder Status:")
try:
    result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                          capture_output=True, text=True, timeout=10)
    
    encoders = result.stdout
    nvenc_encoders = [line.strip() for line in encoders.split('\n') 
                     if 'nvenc' in line.lower()]
    
    if nvenc_encoders:
        print("   ✅ NVENC encoders found:")
        for encoder in nvenc_encoders:
            print(f"      {encoder}")
    else:
        print("   ❌ No NVENC encoders found")
        
    # Also check for hardware acceleration
    hw_accels = [line.strip() for line in encoders.split('\n') 
                if 'cuda' in line.lower() or 'nvenc' in line.lower()]
    if hw_accels:
        print("   🔧 Hardware acceleration:")
        for accel in hw_accels[:5]:  # First 5 matches
            print(f"      {accel}")
            
except Exception as e:
    print(f"   ❌ FFmpeg encoder check failed: {e}")

# 4. Test NVENC directly
print("\n4. 🧪 Direct NVENC Test:")
try:
    # Create a simple test video
    test_cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
        '-c:v', 'h264_nvenc', '-y', '/tmp/test_nvenc.mp4'
    ]
    
    result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("   ✅ NVENC test successful!")
        # Check if file was created
        if os.path.exists('/tmp/test_nvenc.mp4'):
            print("   ✅ Test video file created")
        else:
            print("   ⚠️  Command succeeded but no file created")
    else:
        print("   ❌ NVENC test failed:")
        error_lines = result.stderr.split('\n')
        for line in error_lines[-5:]:  # Last 5 error lines
            if line.strip():
                print(f"      {line.strip()}")
                
except Exception as e:
    print(f"   ❌ NVENC test error: {e}")

# 5. Environment variables
print("\n5. 🌍 Environment Variables:")
gpu_vars = ['CUDA_VISIBLE_DEVICES', 'FFMPEG_GPU', 'MOVIEPY_GPU']
for var in gpu_vars:
    value = os.getenv(var, 'Not set')
    print(f"   {var}: {value}")

# 6. Recommendations
print("\n6. 🎯 Recommendations:")
print("   Based on the results above:")

if not torch.cuda.is_available():
    print("   🔴 Enable GPU runtime: Runtime → Change runtime type → GPU")
else:
    print("   ✅ CUDA is available")

# Check if we can determine the issue
try:
    result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], 
                          capture_output=True, text=True, timeout=10)
    if 'h264_nvenc' not in result.stdout:
        print("   🔴 Install FFmpeg with NVENC support")
        print("   💡 Try: !sudo apt install ffmpeg nvidia-utils-535")
    else:
        print("   ✅ FFmpeg has NVENC support")
        print("   🔴 Likely driver/compatibility issue with A100")
        print("   💡 A100 might need specific NVIDIA drivers")
        print("   💡 Consider using CPU encoding as fallback")

except:
    print("   🔴 FFmpeg not properly installed")

print("\n" + "=" * 50)
print("🏁 Run this script to identify the exact NVENC issue")