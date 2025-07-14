"""
Integrated Content Engine with Automatic S3 Upload
Combines ShortGPT's content engines with automatic S3 upload and content organization
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Import ShortGPT components
from .content_short_engine import ContentShortEngine
from .content_video_engine import ContentVideoEngine  
from .facts_short_engine import FactsShortEngine
from .reddit_short_engine import RedditShortEngine
from ..upload.s3_uploader import S3Uploader
from ..upload.content_organizer import ContentOrganizer
from ..config.languages import Language


class IntegratedContentEngine:
    """
    Integrated engine that handles content creation and automatic S3 upload
    Uses ShortGPT's native engines with added upload functionality
    """
    
    def __init__(self):
        """Initialize the integrated engine with all components"""
        self.s3_uploader = S3Uploader()
        self.content_organizer = ContentOrganizer()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="shortgpt_integrated_"))
        
        # Track processing sessions
        self.session_stats = {
            'videos_created': 0,
            'videos_uploaded': 0,
            'upload_failures': 0,
            'start_time': datetime.now().isoformat()
        }
        
    def create_and_upload_scientific_facts(
        self,
        num_videos: int = 1,
        language: Language = Language.ENGLISH,
        voice_module: Optional[Any] = None
    ) -> List[Dict]:
        """
        Create scientific facts videos and automatically upload to S3
        
        Args:
            num_videos: Number of videos to create
            language: Language for the videos
            voice_module: Voice module to use (optional)
            
        Returns:
            List of results with video info and upload status
        """
        results = []
        content_type = "scientific_facts"
        
        for i in range(num_videos):
            try:
                print(f"🔬 Creating scientific facts video {i+1}/{num_videos}")
                
                # Create video using FactsShortEngine
                engine = FactsShortEngine(
                    voiceModule=voice_module,
                    language=language,
                    numShorts=1
                )
                
                # Generate the video
                for step in engine.makeContent():
                    pass  # Let the engine complete all steps
                video_path = engine.get_video_output_path()
                
                if video_path and os.path.exists(video_path):
                    self.session_stats['videos_created'] += 1
                    
                    # Get assigned account for this content type
                    assigned_account = self.content_organizer.get_next_account(content_type)
                    
                    # Prepare metadata
                    metadata = {
                        'engine_type': 'FactsShortEngine',
                        'content_category': 'scientific_facts',
                        'language': language.value if hasattr(language, 'value') else str(language),
                        'voice_module': str(type(voice_module).__name__) if voice_module else 'default',
                        'assigned_account_id': assigned_account['id'] if assigned_account else None,
                        'assigned_account_name': assigned_account['name'] if assigned_account else None,
                        'creation_timestamp': datetime.now().isoformat()
                    }
                    
                    # Upload to S3
                    success, s3_result = self.s3_uploader.upload_video(
                        video_path=video_path,
                        content_type=content_type,
                        language=language.value if hasattr(language, 'value') else str(language).lower(),
                        metadata=metadata
                    )
                    
                    if success:
                        self.session_stats['videos_uploaded'] += 1
                    else:
                        self.session_stats['upload_failures'] += 1
                    
                    result = {
                        'video_index': i + 1,
                        'local_path': video_path,
                        'upload_success': success,
                        's3_url': s3_result if success else None,
                        'error': s3_result if not success else None,
                        'assigned_account': assigned_account,
                        'metadata': metadata
                    }
                    
                else:
                    result = {
                        'video_index': i + 1,
                        'local_path': None,
                        'upload_success': False,
                        's3_url': None,
                        'error': 'Video creation failed',
                        'assigned_account': None,
                        'metadata': None
                    }
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error creating scientific facts video {i+1}: {e}")
                results.append({
                    'video_index': i + 1,
                    'local_path': None,
                    'upload_success': False,
                    's3_url': None,
                    'error': str(e),
                    'assigned_account': None,
                    'metadata': None
                })
        
        return results
    
    def create_and_upload_historical_facts(
        self,
        num_videos: int = 1,
        language: Language = Language.ENGLISH,
        voice_module: Optional[Any] = None
    ) -> List[Dict]:
        """
        Create historical facts videos and automatically upload to S3
        
        Args:
            num_videos: Number of videos to create
            language: Language for the videos
            voice_module: Voice module to use (optional)
            
        Returns:
            List of results with video info and upload status
        """
        results = []
        content_type = "historical_facts"
        
        for i in range(num_videos):
            try:
                print(f"🏛️ Creating historical facts video {i+1}/{num_videos}")
                
                # Create video using FactsShortEngine with historical focus
                engine = FactsShortEngine(
                    voiceModule=voice_module,
                    language=language,
                    numShorts=1
                )
                
                # Generate the video
                for step in engine.makeContent():
                    pass  # Let the engine complete all steps
                video_path = engine.get_video_output_path()
                
                if video_path and os.path.exists(video_path):
                    self.session_stats['videos_created'] += 1
                    
                    # Get assigned account for this content type
                    assigned_account = self.content_organizer.get_next_account(content_type)
                    
                    # Prepare metadata
                    metadata = {
                        'engine_type': 'FactsShortEngine',
                        'content_category': 'historical_facts',
                        'language': language.value if hasattr(language, 'value') else str(language),
                        'voice_module': str(type(voice_module).__name__) if voice_module else 'default',
                        'assigned_account_id': assigned_account['id'] if assigned_account else None,
                        'assigned_account_name': assigned_account['name'] if assigned_account else None,
                        'creation_timestamp': datetime.now().isoformat()
                    }
                    
                    # Upload to S3
                    success, s3_result = self.s3_uploader.upload_video(
                        video_path=video_path,
                        content_type=content_type,
                        language=language.value if hasattr(language, 'value') else str(language).lower(),
                        metadata=metadata
                    )
                    
                    if success:
                        self.session_stats['videos_uploaded'] += 1
                    else:
                        self.session_stats['upload_failures'] += 1
                    
                    result = {
                        'video_index': i + 1,
                        'local_path': video_path,
                        'upload_success': success,
                        's3_url': s3_result if success else None,
                        'error': s3_result if not success else None,
                        'assigned_account': assigned_account,
                        'metadata': metadata
                    }
                    
                else:
                    result = {
                        'video_index': i + 1,
                        'local_path': None,
                        'upload_success': False,
                        's3_url': None,
                        'error': 'Video creation failed',
                        'assigned_account': None,
                        'metadata': None
                    }
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error creating historical facts video {i+1}: {e}")
                results.append({
                    'video_index': i + 1,
                    'local_path': None,
                    'upload_success': False,
                    's3_url': None,
                    'error': str(e),
                    'assigned_account': None,
                    'metadata': None
                })
        
        return results
    
    def create_and_upload_reddit_stories(
        self,
        num_videos: int = 1,
        language: Language = Language.ENGLISH,
        voice_module: Optional[Any] = None
    ) -> List[Dict]:
        """
        Create Reddit story videos and automatically upload to S3
        
        Args:
            num_videos: Number of videos to create
            language: Language for the videos
            voice_module: Voice module to use (optional)
            
        Returns:
            List of results with video info and upload status
        """
        results = []
        content_type = "reddit_story"
        
        for i in range(num_videos):
            try:
                print(f"📱 Creating Reddit story video {i+1}/{num_videos}")
                
                # Create video using RedditShortEngine
                engine = RedditShortEngine(
                    voiceModule=voice_module,
                    language=language,
                    numShorts=1
                )
                
                # Generate the video
                for step in engine.makeContent():
                    pass  # Let the engine complete all steps
                video_path = engine.get_video_output_path()
                
                if video_path and os.path.exists(video_path):
                    self.session_stats['videos_created'] += 1
                    
                    # Get assigned account for this content type
                    assigned_account = self.content_organizer.get_next_account(content_type)
                    
                    # Prepare metadata
                    metadata = {
                        'engine_type': 'RedditShortEngine',
                        'content_category': 'reddit_story',
                        'language': language.value if hasattr(language, 'value') else str(language),
                        'voice_module': str(type(voice_module).__name__) if voice_module else 'default',
                        'assigned_account_id': assigned_account['id'] if assigned_account else None,
                        'assigned_account_name': assigned_account['name'] if assigned_account else None,
                        'creation_timestamp': datetime.now().isoformat()
                    }
                    
                    # Upload to S3
                    success, s3_result = self.s3_uploader.upload_video(
                        video_path=video_path,
                        content_type=content_type,
                        language=language.value if hasattr(language, 'value') else str(language).lower(),
                        metadata=metadata
                    )
                    
                    if success:
                        self.session_stats['videos_uploaded'] += 1
                    else:
                        self.session_stats['upload_failures'] += 1
                    
                    result = {
                        'video_index': i + 1,
                        'local_path': video_path,
                        'upload_success': success,
                        's3_url': s3_result if success else None,
                        'error': s3_result if not success else None,
                        'assigned_account': assigned_account,
                        'metadata': metadata
                    }
                    
                else:
                    result = {
                        'video_index': i + 1,
                        'local_path': None,
                        'upload_success': False,
                        's3_url': None,
                        'error': 'Video creation failed',
                        'assigned_account': None,
                        'metadata': None
                    }
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ Error creating Reddit story video {i+1}: {e}")
                results.append({
                    'video_index': i + 1,
                    'local_path': None,
                    'upload_success': False,
                    's3_url': None,
                    'error': str(e),
                    'assigned_account': None,
                    'metadata': None
                })
        
        return results
    
    def create_and_upload_custom_content(
        self,
        script: str,
        content_type: Optional[str] = None,
        language: Language = Language.ENGLISH,
        voice_module: Optional[Any] = None
    ) -> Dict:
        """
        Create custom content video with automatic content type detection and upload
        
        Args:
            script: Custom script for the video
            content_type: Override content type detection (optional)
            language: Language for the video
            voice_module: Voice module to use (optional)
            
        Returns:
            Result dictionary with video info and upload status
        """
        try:
            print(f"🎬 Creating custom content video")
            
            # Detect content type if not provided
            if not content_type:
                content_type = self.content_organizer.detect_content_type_from_script(script)
                print(f"🔍 Detected content type: {content_type}")
            
            # Create video using ContentShortEngine
            engine = ContentShortEngine(
                voiceModule=voice_module,
                script=script,
                language=language
            )
            
            # Generate the video
            video_path = engine.makeShort()
            
            if video_path and os.path.exists(video_path):
                self.session_stats['videos_created'] += 1
                
                # Get assigned account for this content type
                assigned_account = self.content_organizer.get_next_account(content_type)
                
                # Prepare metadata
                metadata = {
                    'engine_type': 'ContentShortEngine',
                    'content_category': content_type,
                    'language': language.value if hasattr(language, 'value') else str(language),
                    'voice_module': str(type(voice_module).__name__) if voice_module else 'default',
                    'assigned_account_id': assigned_account['id'] if assigned_account else None,
                    'assigned_account_name': assigned_account['name'] if assigned_account else None,
                    'creation_timestamp': datetime.now().isoformat(),
                    'custom_script': True
                }
                
                # Upload to S3
                success, s3_result = self.s3_uploader.upload_video(
                    video_path=video_path,
                    content_type=content_type,
                    language=language.value if hasattr(language, 'value') else str(language).lower(),
                    metadata=metadata
                )
                
                if success:
                    self.session_stats['videos_uploaded'] += 1
                else:
                    self.session_stats['upload_failures'] += 1
                
                return {
                    'local_path': video_path,
                    'upload_success': success,
                    's3_url': s3_result if success else None,
                    'error': s3_result if not success else None,
                    'assigned_account': assigned_account,
                    'detected_content_type': content_type,
                    'metadata': metadata
                }
                
            else:
                return {
                    'local_path': None,
                    'upload_success': False,
                    's3_url': None,
                    'error': 'Video creation failed',
                    'assigned_account': None,
                    'detected_content_type': content_type,
                    'metadata': None
                }
                
        except Exception as e:
            print(f"❌ Error creating custom content video: {e}")
            return {
                'local_path': None,
                'upload_success': False,
                's3_url': None,
                'error': str(e),
                'assigned_account': None,
                'detected_content_type': content_type,
                'metadata': None
            }
    
    def get_session_stats(self) -> Dict:
        """Get statistics for the current session"""
        self.session_stats['duration'] = str(datetime.now() - datetime.fromisoformat(self.session_stats['start_time']))
        return self.session_stats.copy()
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up temp directory: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()