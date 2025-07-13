#!/usr/bin/env python3
"""
Example usage of ShortGPT Integrated Content Engine with S3 Upload
Demonstrates automated video creation and upload with content organization
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add ShortGPT to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv()

try:
    from shortGPT.engine.integrated_content_engine import IntegratedContentEngine
    from shortGPT.config.languages import Language
    from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
    from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
    print("✅ ShortGPT integrated engine imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure ShortGPT is properly installed and configured")
    sys.exit(1)


def main():
    """Main example workflow"""
    print("🚀 Starting ShortGPT Integrated Workflow Example")
    print("=" * 60)
    
    # Initialize the integrated engine
    engine = IntegratedContentEngine()
    
    try:
        # Example 1: Create scientific facts videos
        print("\n🔬 Creating Scientific Facts Videos")
        print("-" * 40)
        
        scientific_results = engine.create_and_upload_scientific_facts(
            num_videos=2,
            language=Language.ENGLISH
        )
        
        for result in scientific_results:
            if result['upload_success']:
                print(f"✅ Video {result['video_index']}: {result['s3_url']}")
                print(f"   Assigned to: {result['assigned_account']['name']}")
            else:
                print(f"❌ Video {result['video_index']}: {result['error']}")
        
        # Example 2: Create historical facts videos
        print("\n🏛️ Creating Historical Facts Videos")
        print("-" * 40)
        
        historical_results = engine.create_and_upload_historical_facts(
            num_videos=2,
            language=Language.ENGLISH
        )
        
        for result in historical_results:
            if result['upload_success']:
                print(f"✅ Video {result['video_index']}: {result['s3_url']}")
                print(f"   Assigned to: {result['assigned_account']['name']}")
            else:
                print(f"❌ Video {result['video_index']}: {result['error']}")
        
        # Example 3: Create Reddit story videos
        print("\n📱 Creating Reddit Story Videos")
        print("-" * 40)
        
        reddit_results = engine.create_and_upload_reddit_stories(
            num_videos=2,
            language=Language.ENGLISH
        )
        
        for result in reddit_results:
            if result['upload_success']:
                print(f"✅ Video {result['video_index']}: {result['s3_url']}")
                print(f"   Assigned to: {result['assigned_account']['name']}")
            else:
                print(f"❌ Video {result['video_index']}: {result['error']}")
        
        # Example 4: Create custom content with auto-detection
        print("\n🎬 Creating Custom Content with Auto-Detection")
        print("-" * 40)
        
        custom_scripts = [
            "Did you know that quantum computers use quantum bits that can exist in multiple states simultaneously? This revolutionary technology could solve problems in minutes that would take classical computers thousands of years!",
            "In ancient Rome, wealthy citizens would hire professional mourners called 'praeficae' to cry and wail at funerals. The more mourners you had, the more important you appeared to society.",
            "AITA for refusing to go to my sister's wedding because she didn't invite my girlfriend? We've been together for 3 years and she acts like my girlfriend doesn't exist."
        ]
        
        for i, script in enumerate(custom_scripts, 1):
            print(f"\nProcessing custom script {i}:")
            custom_result = engine.create_and_upload_custom_content(
                script=script,
                language=Language.ENGLISH
            )
            
            if custom_result['upload_success']:
                print(f"✅ Custom video: {custom_result['s3_url']}")
                print(f"   Detected type: {custom_result['detected_content_type']}")
                print(f"   Assigned to: {custom_result['assigned_account']['name']}")
            else:
                print(f"❌ Custom video: {custom_result['error']}")
        
        # Display session statistics
        print("\n📊 Session Statistics")
        print("-" * 40)
        stats = engine.get_session_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        # Display assignment statistics
        print("\n📋 Assignment Statistics")
        print("-" * 40)
        assignment_stats = engine.content_organizer.get_assignment_stats()
        print(f"Total assignments: {assignment_stats['total_assignments']}")
        
        for content_type, type_stats in assignment_stats['by_content_type'].items():
            print(f"\n{content_type}:")
            print(f"  - Count: {type_stats['count']}")
            print(f"  - Available accounts: {type_stats['accounts_available']}")
            if type_stats['last_assigned_account']:
                print(f"  - Last assigned: {type_stats['last_assigned_account']['name']} "
                      f"(ID: {type_stats['last_assigned_account']['id']})")
        
        # Display S3 upload statistics
        print("\n☁️ S3 Upload Statistics")
        print("-" * 40)
        s3_stats = engine.s3_uploader.get_upload_stats()
        print(f"Total files: {s3_stats.get('total_files', 0)}")
        print(f"Total size: {s3_stats.get('total_size', 0)} bytes")
        
        print("\nBy language:")
        for lang, lang_stats in s3_stats.get('by_language', {}).items():
            print(f"  {lang}: {lang_stats['count']} files ({lang_stats['size']} bytes)")
        
        print("\nBy content type:")
        for content_type, type_stats in s3_stats.get('by_content_type', {}).items():
            print(f"  {content_type}: {type_stats['count']} files ({type_stats['size']} bytes)")
        
    except Exception as e:
        print(f"❌ Error during workflow execution: {e}")
    
    finally:
        # Clean up
        engine.cleanup()
        print("\n🎉 Workflow completed!")


def demo_content_organizer():
    """Demonstrate content organizer functionality"""
    print("\n🔧 Content Organizer Demo")
    print("=" * 40)
    
    from shortGPT.upload.content_organizer import ContentOrganizer
    organizer = ContentOrganizer()
    
    # Show available content types
    content_types = organizer.get_content_types()
    print(f"Available content types: {content_types}")
    
    # Show accounts for each type
    for content_type in content_types:
        accounts = organizer.get_accounts_for_content_type(content_type)
        print(f"\n{content_type} accounts:")
        for account in accounts:
            print(f"  - {account['name']} (ID: {account['id']}) - {account['focus']}")
    
    # Test content type detection
    test_scripts = [
        "Scientists have discovered a new quantum computing algorithm",
        "In medieval times, people believed the Earth was flat",
        "My boyfriend and I had a huge fight yesterday"
    ]
    
    print("\nContent type detection tests:")
    for script in test_scripts:
        detected_type = organizer.detect_content_type_from_script(script)
        print(f"'{script[:50]}...' → {detected_type}")


if __name__ == "__main__":
    # Check environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these in your .env file or environment")
        sys.exit(1)
    
    # Run the example
    main()
    
    # Run organizer demo
    demo_content_organizer()