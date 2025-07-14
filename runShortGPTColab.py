import os
import sys
from dotenv import load_dotenv

def apply_gpu_optimizations():
    """Apply GPU optimizations for video rendering"""
    try:
        from gpu_video_patch import apply_all_gpu_patches
        print("🎮 Applying GPU optimizations...")
        apply_all_gpu_patches()
    except ImportError:
        print("⚠️  GPU optimization patch not found, using default configuration")
    except Exception as e:
        print(f"⚠️  GPU optimization failed: {e}")

def load_environment():
    """Load environment variables with proper error handling"""
    print("🔧 Loading environment configuration...")
    
    # Try loading from Google Drive first
    drive_env_path = '/content/drive/MyDrive/env/.env'
    local_env_path = './.env'
    
    env_loaded = False
    
    # Attempt to load from Google Drive
    if os.path.exists(drive_env_path):
        try:
            load_dotenv(drive_env_path, override=True)
            print(f"✅ Environment loaded from Google Drive: {drive_env_path}")
            env_loaded = True
        except Exception as e:
            print(f"⚠️  Error loading from Google Drive: {e}")
    
    # Fallback to local .env file
    if not env_loaded and os.path.exists(local_env_path):
        try:
            load_dotenv(local_env_path, override=True)
            print(f"✅ Environment loaded from local file: {local_env_path}")
            env_loaded = True
        except Exception as e:
            print(f"⚠️  Error loading local .env: {e}")
    
    # Set default values for essential variables if not loaded
    if not env_loaded or not os.getenv('OPENAI_API_KEY'):
        print("⚠️  No environment file found or missing OPENAI_API_KEY")
        print("🔧 Using default configuration...")
        
        # Set minimal required environment variables
        default_vars = {
            'DATABASE_TYPE': 'tinydb',
            'LOG_LEVEL': 'INFO',
            'ENVIRONMENT': 'development',
            'DEFAULT_LANGUAGE': 'english',
            'DEFAULT_VIDEO_DURATION': '60',
            'DEFAULT_VIDEO_FORMAT': 'vertical',
            'DEFAULT_VIDEO_QUALITY': '1080p'
        }
        
        for key, value in default_vars.items():
            if not os.getenv(key):
                os.environ[key] = value
    
    # Verify critical API keys
    api_status = {
        'OpenAI': os.getenv('OPENAI_API_KEY') is not None,
        'ElevenLabs': os.getenv('ELEVENLABS_API_KEY') is not None,
        'AWS S3': os.getenv('AWS_ACCESS_KEY_ID') is not None,
        'Pexels': os.getenv('PEXELS_API_KEY') is not None
    }
    
    print("🔑 API Key Status:")
    for service, configured in api_status.items():
        status = "✅ Configured" if configured else "❌ Missing"
        print(f"   {service}: {status}")
    
    return env_loaded

def main():
    """Main application entry point"""
    print("🚀 Starting ShortGPT for Google Colab...")
    
    # Apply GPU optimizations first
    apply_gpu_optimizations()
    
    # Load environment configuration
    load_environment()
    
    # Import and launch GUI
    try:
        from gui.gui_gradio import ShortGptUI
        print("🎮 Initializing ShortGPT interface...")
        
        app = ShortGptUI(colab=True)
        print("🌐 Launching web interface...")
        app.launch()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Please ensure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("🔧 Please check your configuration and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
