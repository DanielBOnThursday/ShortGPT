import os
import platform
import sys
import subprocess
import subprocess
import tempfile
def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def is_running_in_colab():
    return 'COLAB_GPU' in os.environ

def handle_path(path, extension = ".mp4"):
    # Check for None or empty path
    if path is None:
        raise ValueError("Path cannot be None")
    if not isinstance(path, str):
        raise ValueError(f"Path must be a string, got {type(path)}")
    if not path.strip():
        raise ValueError("Path cannot be empty")
    
    if 'https' in path:
        if is_running_in_colab():
            try:
                print(f"🌐 Processing URL: {path}")
                
                # For YouTube URLs, return the URL directly - it will be processed in handle_videos.py
                if 'youtube.com' in path or 'youtu.be' in path:
                    print("📺 YouTube URL detected, passing to video handler...")
                    return path
                    
                else:
                    # Non-YouTube URL, use FFmpeg
                    print("🌐 Non-YouTube URL, using FFmpeg...")
                    temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
                    command = ['ffmpeg', '-y', '-i', path, temp_file.name]
                    
                    result = subprocess.run(command, check=True, capture_output=True, text=True)
                    temp_file.close()
                    
                    if not os.path.exists(temp_file.name):
                        raise Exception(f"Downloaded file not created: {temp_file.name}")
                    
                    print(f"✅ URL converted successfully: {temp_file.name}")
                    return temp_file.name
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to download/convert URL: {path}")
                print(f"FFmpeg error: {e.stderr}")
                raise Exception(f"URL processing failed: {e}")
            except Exception as e:
                print(f"❌ Error processing URL {path}: {e}")
                raise Exception(f"URL handling failed: {e}")
    return path